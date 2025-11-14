"""
API routes for the backend
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path to import shared module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from shared.constants import ALL_EXCHANGES, TRADING_PAIRS, ExchangeType
from backend.src.database import clickhouse_client, redis_client

router = APIRouter(prefix="/api/v1")


# Health check
@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}


# Prices endpoints
@router.get("/prices")
async def get_prices(
    symbol: Optional[str] = Query(None, description="Trading symbol (e.g., BTC/USDT)"),
    exchange: Optional[str] = Query(None, description="Exchange name"),
    start_time: Optional[datetime] = Query(None, description="Start time"),
    end_time: Optional[datetime] = Query(None, description="End time"),
    limit: int = Query(1000, le=10000, description="Maximum number of results")
):
    """Get historical price data"""
    try:
        prices = clickhouse_client.get_prices(
            symbol=symbol,
            exchange=exchange,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        return {
            "count": len(prices),
            "data": prices
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prices/latest")
async def get_latest_prices(
    symbol: Optional[str] = Query(None, description="Trading symbol")
):
    """Get latest prices for all exchanges"""
    try:
        # Try to get from cache first
        cached_prices = redis_client.get_all_prices(symbol)
        if cached_prices:
            return {
                "source": "cache",
                "count": len(cached_prices),
                "data": cached_prices
            }

        # Fallback to database
        prices = clickhouse_client.get_latest_prices(symbol)
        return {
            "source": "database",
            "count": len(prices),
            "data": prices
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Spreads endpoints
@router.get("/spreads")
async def get_spreads(
    symbol: Optional[str] = Query(None, description="Trading symbol"),
    spread_type: Optional[str] = Query(None, description="Spread type (CEX-CEX, CEX-DEX, DEX-DEX)"),
    start_time: Optional[datetime] = Query(None, description="Start time"),
    end_time: Optional[datetime] = Query(None, description="End time"),
    min_spread_pct: Optional[float] = Query(None, description="Minimum spread percentage"),
    limit: int = Query(1000, le=10000, description="Maximum number of results")
):
    """Get price spread data"""
    try:
        spreads = clickhouse_client.get_spreads(
            symbol=symbol,
            spread_type=spread_type,
            start_time=start_time,
            end_time=end_time,
            min_spread_pct=min_spread_pct,
            limit=limit
        )
        return {
            "count": len(spreads),
            "data": spreads
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Funding rates endpoints
@router.get("/funding-rates")
async def get_funding_rates(
    symbol: Optional[str] = Query(None, description="Trading symbol"),
    exchange: Optional[str] = Query(None, description="Exchange name"),
    start_time: Optional[datetime] = Query(None, description="Start time"),
    end_time: Optional[datetime] = Query(None, description="End time"),
    limit: int = Query(1000, le=10000, description="Maximum number of results")
):
    """Get funding rate data"""
    try:
        funding_rates = clickhouse_client.get_funding_rates(
            symbol=symbol,
            exchange=exchange,
            start_time=start_time,
            end_time=end_time,
            limit=limit
        )
        return {
            "count": len(funding_rates),
            "data": funding_rates
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Arbitrage endpoints
@router.get("/arbitrage-opportunities")
async def get_arbitrage_opportunities(
    symbol: Optional[str] = Query(None, description="Trading symbol"),
    min_spread_pct: Optional[float] = Query(None, description="Minimum spread percentage"),
    limit: int = Query(100, le=500, description="Maximum number of results")
):
    """Get current arbitrage opportunities"""
    try:
        # Try cache first
        cached_opps = redis_client.get_arbitrage_opportunities(limit)
        if cached_opps and symbol:
            cached_opps = [opp for opp in cached_opps if opp.get('symbol') == symbol]

        if cached_opps:
            return {
                "source": "cache",
                "count": len(cached_opps),
                "data": cached_opps
            }

        # Fallback to database
        opportunities = clickhouse_client.get_arbitrage_opportunities(
            symbol=symbol,
            min_spread_pct=min_spread_pct,
            limit=limit
        )
        return {
            "source": "database",
            "count": len(opportunities),
            "data": opportunities
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Statistics endpoints
@router.get("/statistics/summary")
async def get_statistics_summary(
    symbol: str = Query(..., description="Trading symbol"),
    hours: int = Query(24, description="Number of hours to look back")
):
    """Get statistical summary for a symbol"""
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)

        stats = clickhouse_client.get_spread_statistics(
            symbol=symbol,
            start_time=start_time,
            end_time=end_time
        )

        return {
            "symbol": symbol,
            "period_hours": hours,
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Metadata endpoints
@router.get("/exchanges")
async def get_exchanges():
    """Get list of supported exchanges"""
    try:
        exchanges = clickhouse_client.get_exchanges()
        return {
            "count": len(exchanges),
            "data": exchanges
        }
    except Exception as e:
        # Return static list if database is not available
        return {
            "count": len(ALL_EXCHANGES),
            "data": [
                {"exchange": ex, "type": ExchangeType.CEX.value if ex in ["binance", "okx", "bybit", "gateio", "bitget"] else ExchangeType.DEX.value}
                for ex in ALL_EXCHANGES
            ]
        }


@router.get("/symbols")
async def get_symbols():
    """Get list of supported trading symbols"""
    try:
        symbols = clickhouse_client.get_symbols()
        return {
            "count": len(symbols),
            "data": symbols
        }
    except Exception as e:
        # Return static list if database is not available
        return {
            "count": len(TRADING_PAIRS),
            "data": TRADING_PAIRS
        }
