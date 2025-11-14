# Trade Bot Backend API

FastAPI-based backend service for the CEX/DEX spread monitoring system.

## Technology Stack

- **Python**: 3.11+
- **Framework**: FastAPI
- **Dependency Management**: uv
- **Database**: ClickHouse (time-series data)
- **Cache**: Redis
- **API Documentation**: OpenAPI/Swagger

## Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer

## Installation

### Install uv

```bash
# macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Setup Development Environment

```bash
# Navigate to backend directory
cd backend

# Create virtual environment and install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

## Running the Server

### Development Mode

```bash
# With uv
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Or activate venv first
source .venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once the server is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Project Structure

```
backend/
├── src/
│   ├── api/              # API routes and websocket handlers
│   │   ├── routes.py     # REST API endpoints
│   │   └── websocket.py  # WebSocket real-time streaming
│   ├── database/         # Database clients
│   │   ├── clickhouse.py # ClickHouse queries
│   │   └── redis.py      # Redis caching
│   ├── config.py         # Configuration management
│   └── main.py           # FastAPI application entry point
├── pyproject.toml        # Project dependencies (uv)
├── .python-version       # Python version specification
└── Dockerfile            # Docker container definition
```

## API Endpoints

### Health & Metadata

- `GET /api/v1/health` - Health check
- `GET /api/v1/exchanges` - List supported exchanges
- `GET /api/v1/symbols` - List monitored trading pairs

### Price Data

- `GET /api/v1/prices` - Historical price data
- `GET /api/v1/prices/latest` - Latest prices from all exchanges

### Spreads

- `GET /api/v1/spreads` - Price spread data with filtering

### Funding Rates

- `GET /api/v1/funding-rates` - Funding rate data for perpetual contracts

### Arbitrage

- `GET /api/v1/arbitrage-opportunities` - Current arbitrage opportunities

### Statistics

- `GET /api/v1/statistics/summary` - Statistical summary for a symbol

### WebSocket

- `WS /ws/realtime` - Real-time data streaming

## Configuration

Configuration is managed through environment variables. See `.env.example` in the project root.

Key variables:

```env
# ClickHouse
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=9000
CLICKHOUSE_HTTP_PORT=8123

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# API
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

## Development

### Adding Dependencies

```bash
# Add a new dependency
uv add <package-name>

# Add a development dependency
uv add --dev <package-name>

# Update dependencies
uv sync
```

### Code Quality

```bash
# Format code (add ruff if needed)
uv run ruff format src/

# Lint code
uv run ruff check src/
```

## Docker

Build and run with Docker:

```bash
# Build image
docker build -t trade-bot-backend .

# Run container
docker run -p 8000:8000 --env-file ../.env trade-bot-backend
```

## Testing

```bash
# Run tests (once implemented)
uv run pytest

# With coverage
uv run pytest --cov=src
```

## License

MIT
