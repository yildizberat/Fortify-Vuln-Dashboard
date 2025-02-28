import requests
import json
import time
import threading
from flask import Flask, Response
from prometheus_client import Gauge, generate_latest, CONTENT_TYPE_LATEST

# Fortify API ve Token bilgileri
BASE_URL = "https://fortify.hepsiburada.com/ssc/api/v1"
TOKEN = "NGU5YWRkNGMtZjIxNS00NzczLTkxMmEtY2MyZTliOTBiZGNl"  # Gerçek tokeni kullan
HEADERS = {
    "Authorization": f"FortifyToken {TOKEN}",
    "Accept": "application/json"
}

# Prometheus metrikleri
fortify_vulnerabilities = Gauge("fortify_vulnerabilities", "Number of vulnerabilities found", ["severity"])

# Flask Uygulaması (Prometheus için)
app = Flask(__name__)

@app.route("/metrics")
def metrics():
    """Prometheus için metrikleri döndürür."""
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

def get_projects():
    """Tüm projeleri Fortify API'den çeker."""
    try:
        response = requests.get(f"{BASE_URL}/projects?fields=id,name&limit=200", headers=HEADERS)
        response.raise_for_status()
        return response.json().get("data", [])
    except requests.exceptions.RequestException as e:
        print(f"❌ API Hatası (Projeler): {e}")
        return []

def get_project_versions(project_id):
    """Belirli bir projenin versiyonlarını çeker."""
    try:
        response = requests.get(f"{BASE_URL}/projects/{project_id}/versions", headers=HEADERS)
        response.raise_for_status()
        return response.json().get("data", [])
    except requests.exceptions.RequestException as e:
        print(f"❌ API Hatası (Versiyonlar): {e}")
        return []

def get_issues(version_id):
    """Belirli bir versiyonun güvenlik açıklarını çeker."""
    start = 0
    limit = 500
    all_issues = []

    while True:
        try:
            response = requests.get(
                f"{BASE_URL}/projectVersions/{version_id}/issues?fields=id,issueName,severity&start={start}&limit={limit}",
                headers=HEADERS
            )
            response.raise_for_status()
            data = response.json()
            issues = data.get("data", [])

            if not issues:
                break

            for i in issues:
                severity = i.get("severity")

                # Eğer severity None veya string formatındaysa float'a çeviriyoruz
                try:
                    severity = float(severity)
                except (TypeError, ValueError):
                    print(f"⚠️ Hata: Issue ID {i['id']} için severity geçersiz! Varsayılan 0.0 atanıyor.")
                    severity = 0.0

                print(f"✅ İşlendi: Issue ID: {i['id']}, Severity: {severity}")

                all_issues.append({
                    "Issue ID": i["id"],
                    "Issue Name": i["issueName"],
                    "Severity": severity
                })

            start += limit

        except requests.exceptions.RequestException as e:
            print(f"❌ API Hatası (Zafiyetler): {e}")
            break

    return all_issues

def update_metrics():
    """Prometheus metriklerini günceller."""
    while True:
        print("📡 Fortify API'den veri çekiliyor...")

        projects = get_projects()
        severity_counts = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}

        for project in projects:
            project_id = project["id"]
            versions = get_project_versions(project_id)

            for version in versions:
                version_id = version["id"]
                issues = get_issues(version_id)

                for issue in issues:
                    severity = issue["Severity"]
                    
                    # API'den gelen severity değerini doğrudan alıyoruz
                    if severity >= 4.0:
                        severity_counts["Critical"] += 1
                    elif severity >= 2.5:
                        severity_counts["High"] += 1
                    elif severity > 0:
                        severity_counts["Medium"] += 1
                    else:
                        severity_counts["Low"] += 1

        # Prometheus metriklerini güncelle
        for severity, count in severity_counts.items():
            fortify_vulnerabilities.labels(severity=severity).set(count)

        print(f"✅ Metrikler güncellendi: {severity_counts}")
        
        # 10 dakika bekle
        time.sleep(600)

if __name__ == "__main__":
    # Prometheus metriklerini güncelleyen thread başlat
    thread = threading.Thread(target=update_metrics, daemon=True)
    thread.start()

    # Flask uygulamasını **9220** portunda başlat
    app.run(host="0.0.0.0", port=9220, debug=True)
