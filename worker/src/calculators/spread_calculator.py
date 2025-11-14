"""
Spread calculator for computing price differences between exchanges
"""

from decimal import Decimal
from datetime import datetime
from typing import List, Dict
from itertools import combinations
import logging
import sys
import os

# Add parent directory to path to import shared module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from shared.types import PriceData, SpreadData, ArbitrageOpportunity
from shared.constants import SpreadType, ExchangeType, CEX_EXCHANGES, DEX_EXCHANGES
from shared.utils import get_current_timestamp, calculate_spread_percentage

logger = logging.getLogger(__name__)


class SpreadCalculator:
    """Calculator for price spreads and arbitrage opportunities"""

    def __init__(self, min_arbitrage_spread_pct: float = 0.5):
        self.min_arbitrage_spread_pct = Decimal(str(min_arbitrage_spread_pct))

    def calculate_spreads(self, price_data_list: List[PriceData]) -> List[SpreadData]:
        """
        Calculate spreads between all exchange pairs for each symbol

        Args:
            price_data_list: List of price data from different exchanges

        Returns:
            List of SpreadData objects
        """
        spread_data_list = []

        # Group prices by symbol
        prices_by_symbol: Dict[str, List[PriceData]] = {}
        for price_data in price_data_list:
            symbol = price_data.symbol
            if symbol not in prices_by_symbol:
                prices_by_symbol[symbol] = []
            prices_by_symbol[symbol].append(price_data)

        # Calculate spreads for each symbol
        for symbol, prices in prices_by_symbol.items():
            if len(prices) < 2:
                continue

            # Calculate spreads for all exchange pairs
            for price_a, price_b in combinations(prices, 2):
                spread_data = self._calculate_spread_pair(price_a, price_b)
                if spread_data:
                    spread_data_list.append(spread_data)

        logger.info(f"Calculated {len(spread_data_list)} spreads")
        return spread_data_list

    def _calculate_spread_pair(self, price_a: PriceData, price_b: PriceData) -> SpreadData:
        """Calculate spread between two price data points"""
        spread_abs = price_a.price - price_b.price
        spread_pct = calculate_spread_percentage(price_a.price, price_b.price)

        # Determine spread type
        spread_type = self._determine_spread_type(price_a.exchange_type, price_b.exchange_type)

        return SpreadData(
            timestamp=get_current_timestamp(),
            symbol=price_a.symbol,
            exchange_a=price_a.exchange,
            exchange_b=price_b.exchange,
            price_a=price_a.price,
            price_b=price_b.price,
            spread_abs=spread_abs,
            spread_pct=spread_pct,
            spread_type=spread_type
        )

    def _determine_spread_type(self, type_a: ExchangeType, type_b: ExchangeType) -> SpreadType:
        """Determine the type of spread based on exchange types"""
        if type_a == ExchangeType.CEX and type_b == ExchangeType.CEX:
            return SpreadType.CEX_CEX
        elif type_a == ExchangeType.DEX and type_b == ExchangeType.DEX:
            return SpreadType.DEX_DEX
        else:
            return SpreadType.CEX_DEX

    def detect_arbitrage_opportunities(
        self,
        price_data_list: List[PriceData]
    ) -> List[ArbitrageOpportunity]:
        """
        Detect arbitrage opportunities based on price spreads

        Args:
            price_data_list: List of price data from different exchanges

        Returns:
            List of ArbitrageOpportunity objects
        """
        opportunities = []

        # Group prices by symbol
        prices_by_symbol: Dict[str, List[PriceData]] = {}
        for price_data in price_data_list:
            symbol = price_data.symbol
            if symbol not in prices_by_symbol:
                prices_by_symbol[symbol] = []
            prices_by_symbol[symbol].append(price_data)

        # Find arbitrage opportunities for each symbol
        for symbol, prices in prices_by_symbol.items():
            if len(prices) < 2:
                continue

            # Find the lowest ask and highest bid
            for price_a, price_b in combinations(prices, 2):
                opportunity = self._check_arbitrage_opportunity(price_a, price_b)
                if opportunity:
                    opportunities.append(opportunity)

        logger.info(f"Detected {len(opportunities)} arbitrage opportunities")
        return opportunities

    def _check_arbitrage_opportunity(
        self,
        price_a: PriceData,
        price_b: PriceData
    ) -> ArbitrageOpportunity | None:
        """Check if there's an arbitrage opportunity between two prices"""
        # Use bid/ask if available, otherwise use price
        buy_price = price_a.ask if price_a.ask else price_a.price
        sell_price = price_b.bid if price_b.bid else price_b.price

        if buy_price == 0 or sell_price == 0:
            return None

        spread_pct = calculate_spread_percentage(sell_price, buy_price)

        # Check if spread is profitable (accounting for fees)
        if spread_pct < self.min_arbitrage_spread_pct:
            return None

        # Estimate profit (simplified, not accounting for all costs)
        # Typical exchange fees are 0.1-0.2% per trade
        estimated_profit = spread_pct - Decimal('0.4')  # Subtract ~0.4% for fees

        if estimated_profit <= 0:
            return None

        # Calculate confidence score based on spread size and volume
        confidence_score = min(float(spread_pct) / 5.0, 1.0)

        # Volume available (use minimum of both)
        volume_available = None
        if price_a.volume_24h and price_b.volume_24h:
            volume_available = min(price_a.volume_24h, price_b.volume_24h)

        return ArbitrageOpportunity(
            timestamp=get_current_timestamp(),
            symbol=price_a.symbol,
            buy_exchange=price_a.exchange,
            sell_exchange=price_b.exchange,
            buy_price=buy_price,
            sell_price=sell_price,
            spread_pct=spread_pct,
            estimated_profit=estimated_profit,
            volume_available=volume_available,
            confidence_score=confidence_score
        )
