FROM python:3.11-slim

WORKDIR /app

# Install curl for healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir flask==3.0.0

COPY server_main.py .

EXPOSE 5000

CMD ["python", "server_main.py"]
