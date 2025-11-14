"""
Utility functions shared across modules
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional


def get_current_timestamp() -> datetime:
    """Get current UTC timestamp"""
    return datetime.now(timezone.utc)


def calculate_spread_percentage(price_a: Decimal, price_b: Decimal) -> Decimal:
    """
    Calculate percentage spread between two prices

    Args:
        price_a: First price
        price_b: Second price

    Returns:
        Percentage spread (positive if price_a > price_b)
    """
    if price_b == 0:
        return Decimal(0)
    return ((price_a - price_b) / price_b) * 100


def parse_symbol(symbol: str) -> tuple[str, str]:
    """
    Parse trading symbol into base and quote currencies

    Args:
        symbol: Trading symbol (e.g., "BTC/USDT")

    Returns:
        Tuple of (base_currency, quote_currency)
    """
    parts = symbol.split("/")
    if len(parts) != 2:
        raise ValueError(f"Invalid symbol format: {symbol}")
    return parts[0], parts[1]


def format_decimal(value: Decimal, precision: int = 8) -> str:
    """
    Format decimal value with specified precision

    Args:
        value: Decimal value
        precision: Number of decimal places

    Returns:
        Formatted string
    """
    return f"{value:.{precision}f}"


def safe_decimal(value: Optional[float | str | Decimal]) -> Decimal:
    """
    Safely convert value to Decimal

    Args:
        value: Value to convert

    Returns:
        Decimal value or Decimal(0) if None
    """
    if value is None:
        return Decimal(0)
    try:
        return Decimal(str(value))
    except (ValueError, TypeError):
        return Decimal(0)
