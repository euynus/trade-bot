FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy shared module
COPY --from=shared ../shared /app/shared

# Default command (override in docker-compose)
CMD ["celery", "-A", "src.celery_app", "worker", "--loglevel=info"]
