"""
Type definitions and Pydantic models shared across modules
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field
from .constants import ExchangeType, SpreadType


class PriceData(BaseModel):
    """Price data from an exchange"""
    timestamp: datetime
    exchange: str
    exchange_type: ExchangeType
    symbol: str
    base_currency: str
    quote_currency: str
    price: Decimal
    bid: Optional[Decimal] = None
    ask: Optional[Decimal] = None
    volume_24h: Optional[Decimal] = None

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat(),
        }


class SpreadData(BaseModel):
    """Price spread between two exchanges"""
    timestamp: datetime
    symbol: str
    exchange_a: str
    exchange_b: str
    price_a: Decimal
    price_b: Decimal
    spread_abs: Decimal
    spread_pct: Decimal
    spread_type: SpreadType

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat(),
        }


class FundingRateData(BaseModel):
    """Funding rate data from perpetual contracts"""
    timestamp: datetime
    exchange: str
    symbol: str
    funding_rate: Decimal
    predicted_rate: Optional[Decimal] = None
    next_funding_time: Optional[datetime] = None
    mark_price: Optional[Decimal] = None
    index_price: Optional[Decimal] = None

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat(),
        }


class ArbitrageOpportunity(BaseModel):
    """Detected arbitrage opportunity"""
    timestamp: datetime
    symbol: str
    buy_exchange: str
    sell_exchange: str
    buy_price: Decimal
    sell_price: Decimal
    spread_pct: Decimal
    estimated_profit: Decimal
    volume_available: Optional[Decimal] = None
    confidence_score: float = Field(ge=0.0, le=1.0)

    class Config:
        json_encoders = {
            Decimal: lambda v: float(v),
            datetime: lambda v: v.isoformat(),
        }


class ExchangeInfo(BaseModel):
    """Information about an exchange"""
    id: str
    name: str
    type: ExchangeType
    enabled: bool = True


class SymbolInfo(BaseModel):
    """Information about a trading symbol"""
    symbol: str
    base_currency: str
    quote_currency: str
    enabled: bool = True
