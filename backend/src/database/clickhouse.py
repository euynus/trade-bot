"""
ClickHouse database connection and operations
"""

import clickhouse_connect
from typing import List, Dict, Any, Optional
from datetime import datetime
import sys
import os

# Add parent directory to path to import shared module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from shared.types import PriceData, SpreadData, FundingRateData, ArbitrageOpportunity
from backend.src.config import settings


class ClickHouseClient:
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
        return self.client

    def disconnect(self):
        """Disconnect from ClickHouse"""
        if self.client:
            self.client.close()

    # Price queries
    def get_prices(
        self,
        symbol: Optional[str] = None,
        exchange: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Query price data"""
        query = "SELECT * FROM prices WHERE 1=1"
        params = {}

        if symbol:
            query += " AND symbol = %(symbol)s"
            params['symbol'] = symbol

        if exchange:
            query += " AND exchange = %(exchange)s"
            params['exchange'] = exchange

        if start_time:
            query += " AND timestamp >= %(start_time)s"
            params['start_time'] = start_time

        if end_time:
            query += " AND timestamp <= %(end_time)s"
            params['end_time'] = end_time

        query += f" ORDER BY timestamp DESC LIMIT {limit}"

        result = self.client.query(query, parameters=params)
        return result.result_rows

    def get_latest_prices(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get latest prices from materialized view"""
        query = "SELECT * FROM latest_prices_mv WHERE 1=1"
        params = {}

        if symbol:
            query += " AND symbol = %(symbol)s"
            params['symbol'] = symbol

        query += " ORDER BY latest_timestamp DESC"

        result = self.client.query(query, parameters=params)
        return result.result_rows

    # Spread queries
    def get_spreads(
        self,
        symbol: Optional[str] = None,
        spread_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        min_spread_pct: Optional[float] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Query spread data"""
        query = "SELECT * FROM spreads WHERE 1=1"
        params = {}

        if symbol:
            query += " AND symbol = %(symbol)s"
            params['symbol'] = symbol

        if spread_type:
            query += " AND spread_type = %(spread_type)s"
            params['spread_type'] = spread_type

        if start_time:
            query += " AND timestamp >= %(start_time)s"
            params['start_time'] = start_time

        if end_time:
            query += " AND timestamp <= %(end_time)s"
            params['end_time'] = end_time

        if min_spread_pct is not None:
            query += " AND abs(spread_pct) >= %(min_spread_pct)s"
            params['min_spread_pct'] = min_spread_pct

        query += f" ORDER BY timestamp DESC LIMIT {limit}"

        result = self.client.query(query, parameters=params)
        return result.result_rows

    # Funding rate queries
    def get_funding_rates(
        self,
        symbol: Optional[str] = None,
        exchange: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Query funding rate data"""
        query = "SELECT * FROM funding_rates WHERE 1=1"
        params = {}

        if symbol:
            query += " AND symbol = %(symbol)s"
            params['symbol'] = symbol

        if exchange:
            query += " AND exchange = %(exchange)s"
            params['exchange'] = exchange

        if start_time:
            query += " AND timestamp >= %(start_time)s"
            params['start_time'] = start_time

        if end_time:
            query += " AND timestamp <= %(end_time)s"
            params['end_time'] = end_time

        query += f" ORDER BY timestamp DESC LIMIT {limit}"

        result = self.client.query(query, parameters=params)
        return result.result_rows

    # Arbitrage queries
    def get_arbitrage_opportunities(
        self,
        symbol: Optional[str] = None,
        min_spread_pct: Optional[float] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Query arbitrage opportunities"""
        query = """
            SELECT * FROM arbitrage_opportunities
            WHERE timestamp >= now() - INTERVAL 1 HOUR
        """
        params = {}

        if symbol:
            query += " AND symbol = %(symbol)s"
            params['symbol'] = symbol

        if min_spread_pct is not None:
            query += " AND spread_pct >= %(min_spread_pct)s"
            params['min_spread_pct'] = min_spread_pct

        query += f" ORDER BY estimated_profit DESC LIMIT {limit}"

        result = self.client.query(query, parameters=params)
        return result.result_rows

    # Statistics
    def get_spread_statistics(
        self,
        symbol: str,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get spread statistics for a symbol"""
        query = """
            SELECT
                avg(spread_pct) as avg_spread,
                min(spread_pct) as min_spread,
                max(spread_pct) as max_spread,
                stddevPop(spread_pct) as stddev_spread,
                count() as count
            FROM spreads
            WHERE symbol = %(symbol)s
        """
        params = {'symbol': symbol}

        if start_time:
            query += " AND timestamp >= %(start_time)s"
            params['start_time'] = start_time

        if end_time:
            query += " AND timestamp <= %(end_time)s"
            params['end_time'] = end_time

        result = self.client.query(query, parameters=params)
        rows = result.result_rows

        if rows:
            return {
                'avg_spread': float(rows[0][0]) if rows[0][0] else 0,
                'min_spread': float(rows[0][1]) if rows[0][1] else 0,
                'max_spread': float(rows[0][2]) if rows[0][2] else 0,
                'stddev_spread': float(rows[0][3]) if rows[0][3] else 0,
                'count': int(rows[0][4]) if rows[0][4] else 0,
            }
        return {}

    def get_symbols(self) -> List[str]:
        """Get list of all symbols"""
        query = "SELECT DISTINCT symbol FROM prices ORDER BY symbol"
        result = self.client.query(query)
        return [row[0] for row in result.result_rows]

    def get_exchanges(self) -> List[Dict[str, str]]:
        """Get list of all exchanges"""
        query = """
            SELECT DISTINCT exchange, exchange_type
            FROM prices
            ORDER BY exchange
        """
        result = self.client.query(query)
        return [
            {'exchange': row[0], 'type': row[1]}
            for row in result.result_rows
        ]


# Global client instance
clickhouse_client = ClickHouseClient()
