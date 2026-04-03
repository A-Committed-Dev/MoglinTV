FROM python:3.11-slim-bookworm

WORKDIR /app

RUN pip install --no-cache-dir flask

COPY . .

CMD ["python", "-u", "app.py"]
