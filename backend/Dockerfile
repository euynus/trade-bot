FROM python:3.11-slim

WORKDIR /app

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && curl -LsSf https://astral.sh/uv/install.sh | sh

# Add uv to PATH
ENV PATH="/root/.cargo/bin:$PATH"

# Copy shared module first
COPY shared/ /app/shared/

# Copy backend project files
COPY backend/pyproject.toml /app/backend/

# Set working directory to backend
WORKDIR /app/backend

# Install dependencies using uv
RUN uv sync --frozen --no-dev || uv sync --no-dev

# Copy backend application code
COPY backend/ /app/backend/

# Expose port
EXPOSE 8000

# Run the application using uv
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
