# Trade Bot Background Worker

Celery-based background task system for data collection and processing.

## Technology Stack

- **Python**: 3.11+
- **Task Queue**: Celery
- **Dependency Management**: uv
- **Message Broker**: Redis
- **Database**: ClickHouse (time-series data)
- **Exchange Integration**: ccxt, hyperliquid-python-sdk

## Prerequisites

- Python 3.11 or higher
- [uv](https://github.com/astral-sh/uv) - Fast Python package installer
- Redis server (for task queue)
- ClickHouse (for data storage)

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
# Navigate to worker directory
cd worker

# Create virtual environment and install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

## Running the Worker

### Development Mode

```bash
# Start Celery worker
uv run celery -A src.celery_app worker --loglevel=info

# Start Celery Beat (scheduler) in another terminal
uv run celery -A src.celery_app beat --loglevel=info
```

### Production Mode

```bash
# Worker with multiple processes
uv run celery -A src.celery_app worker --loglevel=info --concurrency=4

# Beat scheduler
uv run celery -A src.celery_app beat --loglevel=info
```

## Project Structure

```
worker/
├── src/
│   ├── collectors/       # Exchange data collectors
│   │   ├── cex_collector.py    # CEX data collection (ccxt)
│   │   └── hyperliquid_collector.py  # Hyperliquid integration
│   ├── calculators/      # Data processing
│   │   └── spread_calculator.py  # Spread calculations
│   ├── database/         # Database operations
│   │   └── writer.py     # ClickHouse batch inserts
│   ├── tasks.py          # Celery task definitions
│   ├── celery_app.py     # Celery configuration
│   └── config.py         # Configuration management
├── pyproject.toml        # Project dependencies (uv)
├── .python-version       # Python version specification
└── Dockerfile            # Docker container definition
```

## Scheduled Tasks

The worker runs several periodic tasks:

### High Frequency (Every 10 seconds)
- **collect_cex_prices** - Collect spot prices from CEX exchanges
- **collect_hyperliquid_prices** - Collect Hyperliquid perpetual prices
- **calculate_spreads** - Calculate price spreads between exchanges
- **detect_arbitrage** - Detect arbitrage opportunities

### Medium Frequency (Every 60 seconds)
- **collect_funding_rates** - Collect perpetual contract funding rates

### Low Frequency (Every hour)
- **cleanup_old_data** - Remove data older than retention period
- **aggregate_historical_data** - Create aggregated statistics

## Supported Exchanges

### CEX (via ccxt)
- Binance
- OKX
- Bybit
- Gate.io
- Bitget

### Perpetual DEX
- Hyperliquid (native SDK integration)

## Configuration

Configuration is managed through environment variables. See `.env.example` in the project root.

Key variables:

```env
# ClickHouse
CLICKHOUSE_HOST=localhost
CLICKHOUSE_PORT=9000

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2

# Data Collection
COLLECTION_INTERVAL_SECONDS=10
BATCH_INSERT_SIZE=1000

# Exchange API Keys (optional)
BINANCE_API_KEY=
BINANCE_API_SECRET=
HYPERLIQUID_PRIVATE_KEY=
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

### Running Tests

```bash
# Run all tests
uv run pytest

# With coverage
uv run pytest --cov=src
```

### Monitoring Tasks

```bash
# View active tasks
uv run celery -A src.celery_app inspect active

# View registered tasks
uv run celery -A src.celery_app inspect registered

# View worker stats
uv run celery -A src.celery_app inspect stats
```

## Docker

Build and run with Docker:

```bash
# Build image
docker build -t trade-bot-worker .

# Run worker
docker run --env-file ../.env trade-bot-worker

# Run beat scheduler
docker run --env-file ../.env trade-bot-worker \
  uv run celery -A src.celery_app beat --loglevel=info
```

## Task Flow

```
┌─────────────────────────────────────────────────────┐
│              Celery Beat (Scheduler)                │
│  Triggers tasks based on schedule (crontab/interval)│
└────────────────────┬────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────┐
│                Redis (Message Broker)               │
│         Queues tasks for worker processes           │
└────────────────────┬────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────┐
│              Celery Workers (Processes)             │
│                                                     │
│  ┌──────────────┐  ┌──────────────┐               │
│  │ Data         │  │ Calculation  │               │
│  │ Collection   │  │ Tasks        │               │
│  └──────────────┘  └──────────────┘               │
└────────────────────┬────────────────────────────────┘
                     │
                     ↓
┌─────────────────────────────────────────────────────┐
│              ClickHouse & Redis                     │
│        Store results and cache real-time data       │
└─────────────────────────────────────────────────────┘
```

## Troubleshooting

### Worker not picking up tasks
- Check Redis connection
- Verify Celery configuration
- Ensure worker is running

### Database connection errors
- Verify ClickHouse is running
- Check database credentials
- Ensure database is created

### Exchange API errors
- Check API keys (if using private endpoints)
- Verify exchange is supported by ccxt
- Check rate limits

## License

MIT
