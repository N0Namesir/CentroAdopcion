FROM python:3.10-slim

# Instalamos dependencias para MariaDB/MySQL
RUN apt-get update && apt-get install -y \
    libmariadb-dev \
    gcc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-u", "main.py"]