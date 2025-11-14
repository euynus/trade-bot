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

# Copy project files
COPY pyproject.toml .

# Install dependencies using uv
RUN uv sync --frozen --no-dev || uv sync --no-dev

# Copy application code
COPY . .

# Copy shared module
COPY --from=shared ../shared /app/shared

# Default command (override in docker-compose)
CMD ["uv", "run", "celery", "-A", "src.celery_app", "worker", "--loglevel=info"]
