# Python 3.12 tabanlı bir Docker imajı kullan
FROM python:3.12

# Çalışma dizinini ayarla
WORKDIR /app

# Gerekli bağımlılıkları yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Tüm uygulama dosyalarını container içine kopyala
COPY . .

# Flask ve Prometheus Exporter başlat
CMD ["python", "app.py"]
