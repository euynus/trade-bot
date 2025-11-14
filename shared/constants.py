"""
Constants used across the application

This module defines all constant values including supported exchanges,
trading pairs, and default configuration values.
"""

from enum import Enum
from typing import List

# Exchange Types
class ExchangeType(str, Enum):
    CEX = "CEX"  # Centralized Exchange
    DEX = "DEX"  # Decentralized Exchange (AMM-based)
    PERP_DEX = "PERP_DEX"  # Decentralized Perpetual Exchange

# Spread Types
class SpreadType(str, Enum):
    CEX_CEX = "CEX-CEX"
    CEX_DEX = "CEX-DEX"
    DEX_DEX = "DEX-DEX"
    CEX_PERP = "CEX-PERP"
    PERP_PERP = "PERP-PERP"

# Supported CEX Exchanges (Spot & Perpetual)
CEX_EXCHANGES: List[str] = [
    "binance",
    "okx",
    "bybit",
    "gateio",
    "bitget",
]

# Supported DEX Exchanges (AMM-based Spot)
DEX_EXCHANGES: List[str] = [
    "uniswap",
    "pancakeswap",
    "sushiswap",
]

# Supported Perpetual DEX Exchanges
PERP_DEX_EXCHANGES: List[str] = [
    "hyperliquid",
]

# All supported exchanges
ALL_EXCHANGES: List[str] = CEX_EXCHANGES + DEX_EXCHANGES + PERP_DEX_EXCHANGES

# Trading pairs to monitor
TRADING_PAIRS: List[str] = [
    "BTC/USDT",
    "ETH/USDT",
    "BNB/USDT",
    "SOL/USDT",
    "ARB/USDT",
]

# Data collection settings
COLLECTION_INTERVAL_SECONDS = 10
BATCH_INSERT_SIZE = 1000
PRICE_CACHE_TTL_SECONDS = 300  # 5 minutes

# Alert thresholds
DEFAULT_SPREAD_ALERT_THRESHOLD_PCT = 1.0  # 1%
DEFAULT_FUNDING_RATE_ALERT_THRESHOLD_PCT = 0.1  # 0.1%

# Data retention
DATA_RETENTION_DAYS = 90
