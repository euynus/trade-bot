"""
CEX (Centralized Exchange) data collector using ccxt
"""

import ccxt
from decimal import Decimal
from datetime import datetime, timezone
from typing import List, Optional, Dict
import logging
import sys
import os

# Add parent directory to path to import shared module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from shared.types import PriceData, FundingRateData
from shared.constants import CEX_EXCHANGES, ExchangeType
from shared.utils import get_current_timestamp, safe_decimal, parse_symbol

logger = logging.getLogger(__name__)


class CEXCollector:
    """Collector for CEX price and funding rate data"""

    def __init__(self, api_keys: Optional[Dict[str, Dict[str, str]]] = None):
        self.exchanges: Dict[str, ccxt.Exchange] = {}
        self.api_keys = api_keys or {}
        self._initialize_exchanges()

    def _initialize_exchanges(self):
        """Initialize exchange connections"""
        for exchange_id in CEX_EXCHANGES:
            try:
                exchange_class = getattr(ccxt, exchange_id)
                config = {
                    'enableRateLimit': True,
                    'timeout': 10000,
                }

                # Add API keys if provided
                if exchange_id in self.api_keys:
                    config.update(self.api_keys[exchange_id])

                self.exchanges[exchange_id] = exchange_class(config)
                logger.info(f"Initialized {exchange_id} exchange")
            except Exception as e:
                logger.error(f"Failed to initialize {exchange_id}: {e}")

    def fetch_ticker(self, exchange_id: str, symbol: str) -> Optional[PriceData]:
        """
        Fetch ticker data for a symbol from an exchange

        Args:
            exchange_id: Exchange identifier
            symbol: Trading symbol (e.g., 'BTC/USDT')

        Returns:
            PriceData object or None if failed
        """
        if exchange_id not in self.exchanges:
            logger.warning(f"Exchange {exchange_id} not initialized")
            return None

        try:
            exchange = self.exchanges[exchange_id]
            ticker = exchange.fetch_ticker(symbol)

            base_currency, quote_currency = parse_symbol(symbol)

            price_data = PriceData(
                timestamp=get_current_timestamp(),
                exchange=exchange_id,
                exchange_type=ExchangeType.CEX,
                symbol=symbol,
                base_currency=base_currency,
                quote_currency=quote_currency,
                price=safe_decimal(ticker.get('last')),
                bid=safe_decimal(ticker.get('bid')),
                ask=safe_decimal(ticker.get('ask')),
                volume_24h=safe_decimal(ticker.get('baseVolume'))
            )

            logger.debug(f"Fetched {symbol} from {exchange_id}: {price_data.price}")
            return price_data

        except ccxt.NetworkError as e:
            logger.error(f"Network error fetching {symbol} from {exchange_id}: {e}")
        except ccxt.ExchangeError as e:
            logger.error(f"Exchange error fetching {symbol} from {exchange_id}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error fetching {symbol} from {exchange_id}: {e}")

        return None

    def fetch_all_tickers(self, symbols: List[str]) -> List[PriceData]:
        """
        Fetch ticker data for multiple symbols from all exchanges

        Args:
            symbols: List of trading symbols

        Returns:
            List of PriceData objects
        """
        price_data_list = []

        for exchange_id in self.exchanges.keys():
            for symbol in symbols:
                price_data = self.fetch_ticker(exchange_id, symbol)
                if price_data:
                    price_data_list.append(price_data)

        logger.info(f"Fetched {len(price_data_list)} prices from CEX exchanges")
        return price_data_list

    def fetch_funding_rate(self, exchange_id: str, symbol: str) -> Optional[FundingRateData]:
        """
        Fetch funding rate for a perpetual contract

        Args:
            exchange_id: Exchange identifier
            symbol: Trading symbol

        Returns:
            FundingRateData object or None if failed
        """
        if exchange_id not in self.exchanges:
            return None

        try:
            exchange = self.exchanges[exchange_id]

            # Check if exchange supports funding rates
            if not hasattr(exchange, 'fetch_funding_rate'):
                return None

            funding = exchange.fetch_funding_rate(symbol)

            funding_data = FundingRateData(
                timestamp=get_current_timestamp(),
                exchange=exchange_id,
                symbol=symbol,
                funding_rate=safe_decimal(funding.get('fundingRate')),
                predicted_rate=safe_decimal(funding.get('predictedRate')),
                next_funding_time=datetime.fromtimestamp(
                    funding.get('fundingTimestamp', 0) / 1000, tz=timezone.utc
                ) if funding.get('fundingTimestamp') else None,
                mark_price=safe_decimal(funding.get('markPrice')),
                index_price=safe_decimal(funding.get('indexPrice'))
            )

            logger.debug(f"Fetched funding rate for {symbol} from {exchange_id}: {funding_data.funding_rate}")
            return funding_data

        except Exception as e:
            logger.error(f"Error fetching funding rate for {symbol} from {exchange_id}: {e}")
            return None

    def fetch_all_funding_rates(self, symbols: List[str]) -> List[FundingRateData]:
        """
        Fetch funding rates for multiple symbols from all exchanges

        Args:
            symbols: List of trading symbols

        Returns:
            List of FundingRateData objects
        """
        funding_data_list = []

        for exchange_id in self.exchanges.keys():
            for symbol in symbols:
                funding_data = self.fetch_funding_rate(exchange_id, symbol)
                if funding_data:
                    funding_data_list.append(funding_data)

        logger.info(f"Fetched {len(funding_data_list)} funding rates from CEX exchanges")
        return funding_data_list

    def close(self):
        """Close all exchange connections"""
        for exchange_id, exchange in self.exchanges.items():
            try:
                if hasattr(exchange, 'close'):
                    exchange.close()
                logger.info(f"Closed {exchange_id} exchange")
            except Exception as e:
                logger.error(f"Error closing {exchange_id}: {e}")
