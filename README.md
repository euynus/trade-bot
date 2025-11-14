# CEX/DEX 价差和资金费率监控系统

一个实时监控中心化交易所(CEX)和去中心化交易所(DEX)之间价差以及资金费率的系统。

## 系统架构

系统由三个核心模块组成：

1. **Frontend Web** - React + TypeScript 前端应用
2. **Backend API** - FastAPI 后端服务
3. **Background Worker** - Celery 后台任务系统

## 技术栈

- **Frontend**: React 18, TypeScript, Vite, Ant Design, ECharts
- **Backend**: Python 3.11+, FastAPI, Pydantic, SQLAlchemy
- **Worker**: Celery, Redis, ccxt
- **Database**: ClickHouse (时序数据), Redis (缓存)
- **部署**: Docker, Docker Compose

## 功能特性

- ✅ 实时监控多个CEX和DEX的价格
- ✅ 自动计算价差（CEX-CEX, CEX-DEX, DEX-DEX）
- ✅ 资金费率监控
- ✅ 套利机会检测
- ✅ 历史数据查询和可视化
- ✅ WebSocket实时数据推送
- ✅ 自定义报警配置

## 快速开始

### 前置要求

- Docker & Docker Compose
- Python 3.11+ (本地开发)
- Node.js 18+ (本地开发)

### 使用Docker Compose启动

```bash
# 克隆项目
git clone <repository-url>
cd trade-bot

# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 访问服务
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

### 本地开发

#### Backend开发

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### Worker开发

```bash
cd worker
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
celery -A src.celery_app worker --loglevel=info
celery -A src.celery_app beat --loglevel=info
```

#### Frontend开发

```bash
cd frontend
npm install
npm run dev
```

## 监控的交易所

### CEX (中心化交易所)
- Binance
- OKX
- Bybit
- Gate.io
- Bitget

### DEX (去中心化交易所)
- Uniswap V3
- PancakeSwap
- SushiSwap

## 监控的交易对

- BTC/USDT
- ETH/USDT
- BNB/USDT
- SOL/USDT
- ARB/USDT

## API文档

启动服务后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 项目结构

```
trade-bot/
├── backend/          # FastAPI后端服务
├── worker/           # Celery后台任务
├── frontend/         # React前端应用
├── shared/           # 共享代码
├── database/         # 数据库配置和迁移
├── docker/           # Docker配置文件
└── docs/             # 文档
```

## 环境变量配置

复制 `.env.example` 到 `.env` 并配置：

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
