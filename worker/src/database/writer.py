"""
Database writer for batch inserting data into ClickHouse
"""

import clickhouse_connect
from typing import List
import logging
import sys
import os

# Add parent directory to path to import shared module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from shared.types import PriceData, SpreadData, FundingRateData, ArbitrageOpportunity
from worker.src.config import settings

logger = logging.getLogger(__name__)


class ClickHouseWriter:
    """Writer for batch inserting data into ClickHouse"""

    def __init__(self):
        self.client = None

    def connect(self):
        """Connect to ClickHouse"""
        self.client = clickhouse_connect.get_client(
            host=settings.CLICKHOUSE_HOST,
            port=settings.CLICKHOUSE_HTTP_PORT,
            username=settings.CLICKHOUSE_USER,
            password=settings.CLICKHOUSE_PASSWORD,
            database=settings.CLICKHOUSE_DATABASE,
        )
        logger.info("Connected to ClickHouse")
        return self.client

    def disconnect(self):
        """Disconnect from ClickHouse"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from ClickHouse")

    def insert_prices(self, price_data_list: List[PriceData]) -> int:
        """
        Batch insert price data into ClickHouse

        Args:
            price_data_list: List of PriceData objects

        Returns:
            Number of rows inserted
        """
        if not price_data_list:
            return 0

        try:
            data = [
                [
                    price.timestamp,
                    price.exchange,
                    price.exchange_type.value,
                    price.symbol,
                    price.base_currency,
                    price.quote_currency,
                    float(price.price),
                    float(price.bid) if price.bid else None,
                    float(price.ask) if price.ask else None,
                    float(price.volume_24h) if price.volume_24h else None,
                ]
                for price in price_data_list
            ]

            self.client.insert(
                'prices',
                data,
                column_names=[
                    'timestamp', 'exchange', 'exchange_type', 'symbol',
                    'base_currency', 'quote_currency', 'price', 'bid', 'ask', 'volume_24h'
                ]
            )

            logger.info(f"Inserted {len(data)} price records into ClickHouse")
            return len(data)

        except Exception as e:
            logger.error(f"Error inserting prices into ClickHouse: {e}")
            return 0

    def insert_spreads(self, spread_data_list: List[SpreadData]) -> int:
        """
        Batch insert spread data into ClickHouse

        Args:
            spread_data_list: List of SpreadData objects

        Returns:
            Number of rows inserted
        """
        if not spread_data_list:
            return 0

        try:
            data = [
                [
                    spread.timestamp,
                    spread.symbol,
                    spread.exchange_a,
                    spread.exchange_b,
                    float(spread.price_a),
                    float(spread.price_b),
                    float(spread.spread_abs),
                    float(spread.spread_pct),
                    spread.spread_type.value,
                ]
                for spread in spread_data_list
            ]

            self.client.insert(
                'spreads',
                data,
                column_names=[
                    'timestamp', 'symbol', 'exchange_a', 'exchange_b',
                    'price_a', 'price_b', 'spread_abs', 'spread_pct', 'spread_type'
                ]
            )

            logger.info(f"Inserted {len(data)} spread records into ClickHouse")
            return len(data)

        except Exception as e:
            logger.error(f"Error inserting spreads into ClickHouse: {e}")
            return 0

    def insert_funding_rates(self, funding_data_list: List[FundingRateData]) -> int:
        """
        Batch insert funding rate data into ClickHouse

        Args:
            funding_data_list: List of FundingRateData objects

        Returns:
            Number of rows inserted
        """
        if not funding_data_list:
            return 0

        try:
            data = [
                [
                    funding.timestamp,
                    funding.exchange,
                    funding.symbol,
                    float(funding.funding_rate),
                    float(funding.predicted_rate) if funding.predicted_rate else None,
                    funding.next_funding_time,
                    float(funding.mark_price) if funding.mark_price else None,
                    float(funding.index_price) if funding.index_price else None,
                ]
                for funding in funding_data_list
            ]

            self.client.insert(
                'funding_rates',
                data,
                column_names=[
                    'timestamp', 'exchange', 'symbol', 'funding_rate',
                    'predicted_rate', 'next_funding_time', 'mark_price', 'index_price'
                ]
            )

            logger.info(f"Inserted {len(data)} funding rate records into ClickHouse")
            return len(data)

        except Exception as e:
            logger.error(f"Error inserting funding rates into ClickHouse: {e}")
            return 0

    def insert_arbitrage_opportunities(self, opportunities: List[ArbitrageOpportunity]) -> int:
        """
        Batch insert arbitrage opportunities into ClickHouse

        Args:
            opportunities: List of ArbitrageOpportunity objects

        Returns:
            Number of rows inserted
        """
        if not opportunities:
            return 0

        try:
            data = [
                [
                    opp.timestamp,
                    opp.symbol,
                    opp.buy_exchange,
                    opp.sell_exchange,
                    float(opp.buy_price),
                    float(opp.sell_price),
                    float(opp.spread_pct),
                    float(opp.estimated_profit),
                    float(opp.volume_available) if opp.volume_available else None,
                    opp.confidence_score,
                ]
                for opp in opportunities
            ]

            self.client.insert(
                'arbitrage_opportunities',
                data,
                column_names=[
                    'timestamp', 'symbol', 'buy_exchange', 'sell_exchange',
                    'buy_price', 'sell_price', 'spread_pct', 'estimated_profit',
                    'volume_available', 'confidence_score'
                ]
            )

            logger.info(f"Inserted {len(data)} arbitrage opportunity records into ClickHouse")
            return len(data)

        except Exception as e:
            logger.error(f"Error inserting arbitrage opportunities into ClickHouse: {e}")
            return 0


# Global writer instance
clickhouse_writer = ClickHouseWriter()
