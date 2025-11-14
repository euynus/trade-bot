FROM python:3.11-slim

WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH
ENV PATH="/root/.cargo/bin:$PATH"

# Copy shared module first
COPY shared/ /app/shared/

# Copy worker project files
COPY worker/pyproject.toml /app/worker/

# Set working directory to worker
WORKDIR /app/worker

# Install dependencies using uv
RUN uv sync --frozen --no-dev || uv sync --no-dev

# Copy worker application code
COPY worker/ /app/worker/

# Default command (override in docker-compose)
CMD ["uv", "run", "celery", "-A", "src.celery_app", "worker", "--loglevel=info"]
