# 🚀 Fortify Monitoring Exporter  
📊 A **Docker-based exporter** that fetches vulnerabilities from **Fortify API** and integrates with **Prometheus & Grafana** for visualization.  

---

## 📌 Project Overview  
This project extracts **security vulnerabilities** from the **Fortify API**, exports them to **Prometheus**, and visualizes the data using **Grafana**.  

- **Prometheus Exporter**: Fetches data from Fortify and converts it into Prometheus-compatible metrics.  
- **Grafana Dashboard**: Provides a clean and insightful UI for monitoring vulnerabilities.  
- **Easy Docker Deployment**: Quickly set up the entire system using **Docker Compose**.  

# Install Dependencies (If Not Using Docker)
pip install -r requirements.txt

# Start the Project with Docker
docker-compose up -d --build

# Verify Services
Exporter: http://localhost:9220/metrics
Prometheus: http://localhost:9090
Grafana: http://localhost:3000 (Username: admin, Password: admin)

# Get Prometheus Metrics
curl http://localhost:9220/metrics

# Fetch All Projects from Fortify
curl http://localhost:9220/projects

# List Security Vulnerabilities
curl http://localhost:9220/issues

# To set up in Grafana
1. Select Prometheus as the data source.
2. Import the dashboard JSON file: grafana/dashboards/fortify-dashboard.json
3. Start monitoring vulnerabilities in real time!

# Example Prometheus Metrics
HELP fortify_vulnerabilities Number of vulnerabilities found
TYPE fortify_vulnerabilities gauge
fortify_vulnerabilities{severity="Critical"} 12
fortify_vulnerabilities{severity="High"} 7
fortify_vulnerabilities{severity="Medium"} 5
fortify_vulnerabilities{severity="Low"} 2
