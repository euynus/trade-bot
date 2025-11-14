"""
Mock FastAPI server for demonstration purposes
This provides sample data without requiring ClickHouse or Redis
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime, timedelta
import random
from decimal import Decimal

app = FastAPI(
    title="CEX/DEX Spread Monitoring API (Mock)",
    description="Mock API for demonstration",
    version="1.0.0-mock"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock data generators
EXCHANGES = ["binance", "okx", "bybit", "gateio", "bitget"]
SYMBOLS = ["BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "ARB/USDT"]

def generate_price(base_price: float, variance: float = 0.02) -> float:
    """Generate random price with variance"""
    return base_price * (1 + random.uniform(-variance, variance))

def generate_mock_prices():
    """Generate mock price data"""
    base_prices = {
        "BTC/USDT": 43000,
        "ETH/USDT": 2300,
        "BNB/USDT": 310,
        "SOL/USDT": 98,
        "ARB/USDT": 1.2
    }

    prices = []
    for symbol in SYMBOLS:
        base_price = base_prices[symbol]
        for exchange in EXCHANGES:
            price = generate_price(base_price, 0.01)
            prices.append({
                "timestamp": datetime.utcnow().isoformat(),
                "exchange": exchange,
                "exchange_type": "CEX",
                "symbol": symbol,
                "base_currency": symbol.split("/")[0],
                "quote_currency": symbol.split("/")[1],
                "price": price,
                "bid": price * 0.9999,
                "ask": price * 1.0001,
                "volume_24h": random.uniform(1000, 100000)
            })

    return prices

def generate_mock_spreads():
    """Generate mock spread data"""
    spreads = []
    base_prices = {
        "BTC/USDT": 43000,
        "ETH/USDT": 2300,
        "BNB/USDT": 310,
        "SOL/USDT": 98,
        "ARB/USDT": 1.2
    }

    for symbol in SYMBOLS:
        base_price = base_prices[symbol]
        for i in range(len(EXCHANGES)):
            for j in range(i + 1, len(EXCHANGES)):
                price_a = generate_price(base_price, 0.01)
                price_b = generate_price(base_price, 0.01)
                spread_abs = abs(price_a - price_b)
                spread_pct = (spread_abs / price_b) * 100

                spreads.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "symbol": symbol,
                    "exchange_a": EXCHANGES[i],
                    "exchange_b": EXCHANGES[j],
                    "price_a": price_a,
                    "price_b": price_b,
                    "spread_abs": spread_abs,
                    "spread_pct": spread_pct,
                    "spread_type": "CEX-CEX"
                })

    return spreads

def generate_mock_arbitrage():
    """Generate mock arbitrage opportunities"""
    opportunities = []
    base_prices = {
        "BTC/USDT": 43000,
        "ETH/USDT": 2300,
        "BNB/USDT": 310,
        "SOL/USDT": 98,
        "ARB/USDT": 1.2
    }

    for symbol in SYMBOLS:
        base_price = base_prices[symbol]
        # Generate 3-5 opportunities per symbol
        for _ in range(random.randint(3, 5)):
            buy_price = generate_price(base_price, 0.005)
            sell_price = buy_price * (1 + random.uniform(0.005, 0.03))
            spread_pct = ((sell_price - buy_price) / buy_price) * 100
            estimated_profit = spread_pct - 0.4  # Subtract fees

            if estimated_profit > 0:
                opportunities.append({
                    "timestamp": datetime.utcnow().isoformat(),
                    "symbol": symbol,
                    "buy_exchange": random.choice(EXCHANGES),
                    "sell_exchange": random.choice(EXCHANGES),
                    "buy_price": buy_price,
                    "sell_price": sell_price,
                    "spread_pct": spread_pct,
                    "estimated_profit": estimated_profit,
                    "volume_available": random.uniform(10, 1000),
                    "confidence_score": random.uniform(0.6, 0.95)
                })

    # Sort by estimated profit
    opportunities.sort(key=lambda x: x["estimated_profit"], reverse=True)
    return opportunities[:50]

def generate_mock_funding_rates():
    """Generate mock funding rate data"""
    funding_rates = []

    for symbol in SYMBOLS:
        for exchange in EXCHANGES[:3]:  # Only some exchanges have funding rates
            funding_rate = random.uniform(-0.0001, 0.0001)
            funding_rates.append({
                "timestamp": datetime.utcnow().isoformat(),
                "exchange": exchange,
                "symbol": symbol,
                "funding_rate": funding_rate,
                "predicted_rate": funding_rate * random.uniform(0.8, 1.2),
                "next_funding_time": (datetime.utcnow() + timedelta(hours=8)).isoformat(),
                "mark_price": None,
                "index_price": None
            })

    return funding_rates

# API Endpoints

@app.get("/")
async def root():
    return {
        "name": "CEX/DEX Spread Monitoring API (Mock)",
        "version": "1.0.0-mock",
        "docs": "/docs",
        "note": "This is a mock server with sample data for demonstration"
    }

@app.get("/api/v1/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat(), "mode": "mock"}

@app.get("/api/v1/prices/latest")
async def get_latest_prices(symbol: str = None):
    prices = generate_mock_prices()
    if symbol:
        prices = [p for p in prices if p["symbol"] == symbol]
    return {"source": "mock", "count": len(prices), "data": prices}

@app.get("/api/v1/prices")
async def get_prices():
    return {"count": len(generate_mock_prices()), "data": generate_mock_prices()}

@app.get("/api/v1/spreads")
async def get_spreads(symbol: str = None, spread_type: str = None):
    spreads = generate_mock_spreads()
    if symbol:
        spreads = [s for s in spreads if s["symbol"] == symbol]
    if spread_type:
        spreads = [s for s in spreads if s["spread_type"] == spread_type]
    return {"count": len(spreads), "data": spreads}

@app.get("/api/v1/funding-rates")
async def get_funding_rates(symbol: str = None, exchange: str = None):
    funding_rates = generate_mock_funding_rates()
    if symbol:
        funding_rates = [f for f in funding_rates if f["symbol"] == symbol]
    if exchange:
        funding_rates = [f for f in funding_rates if f["exchange"] == exchange]
    return {"count": len(funding_rates), "data": funding_rates}

@app.get("/api/v1/arbitrage-opportunities")
async def get_arbitrage_opportunities(symbol: str = None, min_spread_pct: float = None):
    opportunities = generate_mock_arbitrage()
    if symbol:
        opportunities = [o for o in opportunities if o["symbol"] == symbol]
    if min_spread_pct:
        opportunities = [o for o in opportunities if o["spread_pct"] >= min_spread_pct]
    return {"source": "mock", "count": len(opportunities), "data": opportunities}

@app.get("/api/v1/statistics/summary")
async def get_statistics(symbol: str, hours: int = 24):
    return {
        "symbol": symbol,
        "period_hours": hours,
        "statistics": {
            "avg_spread": random.uniform(0.1, 1.0),
            "min_spread": random.uniform(0.01, 0.1),
            "max_spread": random.uniform(1.0, 3.0),
            "stddev_spread": random.uniform(0.1, 0.5),
            "count": random.randint(1000, 10000)
        }
    }

@app.get("/api/v1/exchanges")
async def get_exchanges():
    return {
        "count": len(EXCHANGES),
        "data": [{"exchange": ex, "type": "CEX"} for ex in EXCHANGES]
    }

@app.get("/api/v1/symbols")
async def get_symbols():
    return {
        "count": len(SYMBOLS),
        "data": SYMBOLS
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Mock Backend Server...")
    print("📡 API Docs: http://localhost:8000/docs")
    print("🔄 This server provides mock data for demonstration")
    uvicorn.run(app, host="0.0.0.0", port=8000)
