"""
Constants used across the application
"""

from enum import Enum
from typing import List

# Exchange Types
class ExchangeType(str, Enum):
    CEX = "CEX"
    DEX = "DEX"

# Spread Types
class SpreadType(str, Enum):
    CEX_CEX = "CEX-CEX"
    CEX_DEX = "CEX-DEX"
    DEX_DEX = "DEX-DEX"

# Supported CEX Exchanges
CEX_EXCHANGES: List[str] = [
    "binance",
    "okx",
    "bybit",
    "gateio",
    "bitget",
]

# Supported DEX Exchanges
DEX_EXCHANGES: List[str] = [
    "uniswap",
    "pancakeswap",
    "sushiswap",
]

# All supported exchanges
ALL_EXCHANGES: List[str] = CEX_EXCHANGES + DEX_EXCHANGES

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
