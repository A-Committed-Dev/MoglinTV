FROM python:3.11-slim-bookworm

# Install system dependencies for I2C and GPIO access
RUN apt-get update && apt-get install -y --no-install-recommends \
    i2c-tools \
    libgpiod2 \
    libgpiod-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY code/ ./

CMD ["python", "-u", "main.py"]
