"""
Hyperliquid (Perpetual DEX) data collector

Hyperliquid is a decentralized perpetual exchange built on its own L1 blockchain.
It offers low-latency perpetual futures trading with on-chain order book.
"""

from decimal import Decimal
from datetime import datetime, timezone
from typing import List, Optional, Dict
import logging
import sys
import os

# Add parent directory to path to import shared module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from shared.types import PriceData, FundingRateData
from shared.constants import ExchangeType
from shared.utils import get_current_timestamp, safe_decimal, parse_symbol

logger = logging.getLogger(__name__)

try:
    from hyperliquid.info import Info
    from hyperliquid.utils import constants
    HYPERLIQUID_AVAILABLE = True
except ImportError:
    logger.warning("hyperliquid-python-sdk not installed. Hyperliquid support disabled.")
    HYPERLIQUID_AVAILABLE = False


class HyperliquidCollector:
    """Collector for Hyperliquid perpetual DEX data"""

    def __init__(self, testnet: bool = False):
        """
        Initialize Hyperliquid collector

        Args:
            testnet: Use testnet instead of mainnet
        """
        self.testnet = testnet
        self.info = None

        if HYPERLIQUID_AVAILABLE:
            try:
                # Initialize Hyperliquid Info API
                base_url = constants.TESTNET_API_URL if testnet else constants.MAINNET_API_URL
                self.info = Info(base_url=base_url, skip_ws=True)
                logger.info(f"Initialized Hyperliquid collector (testnet={testnet})")
            except Exception as e:
                logger.error(f"Failed to initialize Hyperliquid: {e}")
                self.info = None
        else:
            logger.warning("Hyperliquid SDK not available")

    def fetch_perpetual_price(self, symbol: str) -> Optional[PriceData]:
        """
        Fetch perpetual contract price from Hyperliquid

        Args:
            symbol: Trading symbol (e.g., 'BTC/USDT')
                   Will be converted to Hyperliquid format (e.g., 'BTC')

        Returns:
            PriceData object or None if failed
        """
        if not self.info:
            return None

        try:
            # Convert symbol format: "BTC/USDT" -> "BTC"
            # Hyperliquid uses base currency only for perps
            base_currency, quote_currency = parse_symbol(symbol)
            hl_symbol = base_currency

            # Get all mids (market data)
            all_mids = self.info.all_mids()

            if hl_symbol not in all_mids:
                logger.warning(f"Symbol {hl_symbol} not found on Hyperliquid")
                return None

            mid_price = safe_decimal(all_mids[hl_symbol])

            # Get market metadata for more details
            meta = self.info.meta()
            asset_info = None
            for asset in meta.get('universe', []):
                if asset.get('name') == hl_symbol:
                    asset_info = asset
                    break

            # Get funding rate
            funding_info = self._get_funding_rate(hl_symbol)

            price_data = PriceData(
                timestamp=get_current_timestamp(),
                exchange="hyperliquid",
                exchange_type=ExchangeType.PERP_DEX,
                symbol=symbol,  # Keep original format for consistency
                base_currency=base_currency,
                quote_currency=quote_currency,
                price=mid_price,
                bid=None,  # Hyperliquid doesn't expose bid/ask directly in this API
                ask=None,
                volume_24h=safe_decimal(asset_info.get('dayNtlVlm')) if asset_info else None
            )

            logger.debug(f"Fetched {symbol} from Hyperliquid: {price_data.price}")
            return price_data

        except Exception as e:
            logger.error(f"Error fetching {symbol} from Hyperliquid: {e}")
            return None

    def fetch_all_perpetual_prices(self, symbols: List[str]) -> List[PriceData]:
        """
        Fetch prices for multiple perpetual contracts

        Args:
            symbols: List of trading symbols in standard format (e.g., ['BTC/USDT', 'ETH/USDT'])

        Returns:
            List of PriceData objects
        """
        price_data_list = []

        for symbol in symbols:
            price_data = self.fetch_perpetual_price(symbol)
            if price_data:
                price_data_list.append(price_data)

        logger.info(f"Fetched {len(price_data_list)} prices from Hyperliquid")
        return price_data_list

    def _get_funding_rate(self, hl_symbol: str) -> Optional[Dict]:
        """
        Get funding rate for a symbol

        Args:
            hl_symbol: Hyperliquid symbol (base currency only)

        Returns:
            Funding rate info dict or None
        """
        try:
            meta = self.info.meta()
            for asset in meta.get('universe', []):
                if asset.get('name') == hl_symbol:
                    return {
                        'funding': safe_decimal(asset.get('funding')),
                        'premium': safe_decimal(asset.get('premium'))
                    }
            return None
        except Exception as e:
            logger.error(f"Error getting funding rate for {hl_symbol}: {e}")
            return None

    def fetch_funding_rate(self, symbol: str) -> Optional[FundingRateData]:
        """
        Fetch funding rate for a perpetual contract

        Args:
            symbol: Trading symbol (e.g., 'BTC/USDT')

        Returns:
            FundingRateData object or None if failed
        """
        if not self.info:
            return None

        try:
            base_currency, _ = parse_symbol(symbol)
            hl_symbol = base_currency

            # Get metadata with funding info
            meta = self.info.meta()
            asset_info = None
            for asset in meta.get('universe', []):
                if asset.get('name') == hl_symbol:
                    asset_info = asset
                    break

            if not asset_info:
                logger.warning(f"Asset {hl_symbol} not found for funding rate")
                return None

            # Hyperliquid funding rates are 8-hour rates
            funding_rate = safe_decimal(asset_info.get('funding', 0))
            premium = safe_decimal(asset_info.get('premium'))

            funding_data = FundingRateData(
                timestamp=get_current_timestamp(),
                exchange="hyperliquid",
                symbol=symbol,
                funding_rate=funding_rate,
                predicted_rate=premium,  # Premium can be used as predicted rate
                next_funding_time=None,  # Hyperliquid doesn't provide this in meta
                mark_price=None,
                index_price=None
            )

            logger.debug(f"Fetched funding rate for {symbol} from Hyperliquid: {funding_rate}")
            return funding_data

        except Exception as e:
            logger.error(f"Error fetching funding rate for {symbol} from Hyperliquid: {e}")
            return None

    def fetch_all_funding_rates(self, symbols: List[str]) -> List[FundingRateData]:
        """
        Fetch funding rates for multiple perpetual contracts

        Args:
            symbols: List of trading symbols

        Returns:
            List of FundingRateData objects
        """
        funding_data_list = []

        for symbol in symbols:
            funding_data = self.fetch_funding_rate(symbol)
            if funding_data:
                funding_data_list.append(funding_data)

        logger.info(f"Fetched {len(funding_data_list)} funding rates from Hyperliquid")
        return funding_data_list

    def get_available_symbols(self) -> List[str]:
        """
        Get list of available trading symbols on Hyperliquid

        Returns:
            List of symbols in standard format (e.g., ['BTC/USDT', 'ETH/USDT'])
        """
        if not self.info:
            return []

        try:
            meta = self.info.meta()
            symbols = []

            for asset in meta.get('universe', []):
                # Convert Hyperliquid format to standard format
                base = asset.get('name')
                # Hyperliquid perps are quoted in USD/USDC
                symbols.append(f"{base}/USDT")

            logger.info(f"Found {len(symbols)} symbols on Hyperliquid")
            return symbols

        except Exception as e:
            logger.error(f"Error fetching available symbols from Hyperliquid: {e}")
            return []
