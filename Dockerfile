FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/
COPY .env.example .env

# Expose metrics port
EXPOSE 9090

# Expose API port (if using FastAPI)
EXPOSE 8080

# Run the application
CMD ["python", "-m", "src.main", "--monitor", "--interval", "3600"]
