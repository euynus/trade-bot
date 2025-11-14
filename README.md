# CEX/DEX Spread and Funding Rate Monitoring System

A real-time monitoring system for tracking price spreads and funding rates between Centralized Exchanges (CEX) and Decentralized Exchanges (DEX).

## System Architecture

The system consists of three core modules:

1. **Frontend Web** - React + TypeScript web application
2. **Backend API** - FastAPI backend service with uv dependency management
3. **Background Worker** - Celery background task system

## Technology Stack

- **Frontend**: React 18, TypeScript, Vite, Ant Design, ECharts
- **Backend**: Python 3.11+, FastAPI, Pydantic, uv (dependency management)
- **Worker**: Celery, Redis, ccxt, hyperliquid-python-sdk, uv (dependency management)
- **Database**: ClickHouse (time-series data), Redis (caching)
- **Deployment**: Docker, Docker Compose

## Features

- ✅ Real-time price monitoring across multiple CEX and DEX platforms
- ✅ Automatic spread calculation (CEX-CEX, CEX-DEX, DEX-DEX)
- ✅ Funding rate monitoring
- ✅ Arbitrage opportunity detection
- ✅ Historical data querying and visualization
- ✅ WebSocket real-time data streaming
- ✅ Customizable alert configuration

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)
- [uv](https://github.com/astral-sh/uv) (for backend development)

### Start with Docker Compose

```bash
# Clone the project
git clone <repository-url>
cd trade-bot

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Access services
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Local Development

#### Backend Development (with uv)

```bash
cd backend

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run the server
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### Worker Development (with uv)

```bash
cd worker

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv sync

# Run Celery worker
uv run celery -A src.celery_app worker --loglevel=info

# Run Celery beat (in another terminal)
uv run celery -A src.celery_app beat --loglevel=info
```

#### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

## Monitored Exchanges

### CEX (Centralized Exchanges)
- Binance
- OKX
- Bybit
- Gate.io
- Bitget

### DEX (Decentralized Spot Exchanges)
- Uniswap V3
- PancakeSwap
- SushiSwap

### Perpetual DEX
- **Hyperliquid** - Decentralized perpetual exchange with on-chain order book

## Monitored Trading Pairs

- BTC/USDT
- ETH/USDT
- BNB/USDT
- SOL/USDT
- ARB/USDT

## API Documentation

After starting the services, access:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
trade-bot/
├── backend/          # FastAPI backend service (uv managed)
├── worker/           # Celery background tasks (uv managed)
├── frontend/         # React web application
├── shared/           # Shared code and types
├── database/         # Database configuration and migrations
└── docker-compose.yml
```

## Environment Configuration

Copy `.env.example` to `.env` and configure:

```env
# ClickHouse
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=9000
CLICKHOUSE_USER=default
CLICKHOUSE_PASSWORD=

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# API
API_HOST=0.0.0.0
API_PORT=8000
```

## License

MIT
