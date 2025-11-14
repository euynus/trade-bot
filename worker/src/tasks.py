"""
Celery tasks for data collection and processing
"""

from celery import Task
import redis
import logging
import json
import sys
import os

# Add parent directory to path to import shared module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from shared.constants import TRADING_PAIRS
from worker.src.config import settings
from worker.src.collectors import CEXCollector
from worker.src.calculators import SpreadCalculator
from worker.src.database import clickhouse_writer

logger = logging.getLogger(__name__)

# Initialize Redis for caching
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
    decode_responses=True
)

# Initialize collectors and calculators
cex_collector = CEXCollector()
spread_calculator = SpreadCalculator()


class DatabaseTask(Task):
    """Base task with database connection"""
    _db = None

    @property
    def db(self):
        if self._db is None:
            self._db = clickhouse_writer
            self._db.connect()
        return self._db


def collect_and_process_data(celery_app):
    """Main task factory"""

    @celery_app.task(base=DatabaseTask, name='tasks.collect_cex_prices')
    def collect_cex_prices():
        """Collect price data from CEX exchanges"""
        try:
            logger.info("Collecting CEX prices...")
            price_data_list = cex_collector.fetch_all_tickers(TRADING_PAIRS)

            if not price_data_list:
                logger.warning("No price data collected")
                return

            # Cache prices in Redis
            for price_data in price_data_list:
                key = f"price:{price_data.exchange}:{price_data.symbol}"
                value = {
                    'price': float(price_data.price),
                    'bid': float(price_data.bid) if price_data.bid else None,
                    'ask': float(price_data.ask) if price_data.ask else None,
                    'timestamp': price_data.timestamp.isoformat(),
                    'volume_24h': float(price_data.volume_24h) if price_data.volume_24h else None,
                }
                redis_client.setex(key, 300, json.dumps(value))  # 5 minute TTL

            # Insert into ClickHouse
            inserted = collect_cex_prices.db.insert_prices(price_data_list)
            logger.info(f"Collected and stored {inserted} CEX prices")

            return len(price_data_list)

        except Exception as e:
            logger.error(f"Error in collect_cex_prices: {e}")
            raise

    @celery_app.task(base=DatabaseTask, name='tasks.collect_funding_rates')
    def collect_funding_rates():
        """Collect funding rate data from CEX exchanges"""
        try:
            logger.info("Collecting funding rates...")
            funding_data_list = cex_collector.fetch_all_funding_rates(TRADING_PAIRS)

            if not funding_data_list:
                logger.warning("No funding rate data collected")
                return

            # Cache funding rates in Redis
            for funding_data in funding_data_list:
                key = f"funding:{funding_data.exchange}:{funding_data.symbol}"
                value = {
                    'funding_rate': float(funding_data.funding_rate),
                    'predicted_rate': float(funding_data.predicted_rate) if funding_data.predicted_rate else None,
                    'next_funding_time': funding_data.next_funding_time.isoformat() if funding_data.next_funding_time else None,
                    'timestamp': funding_data.timestamp.isoformat(),
                }
                redis_client.setex(key, 300, json.dumps(value))

            # Insert into ClickHouse
            inserted = collect_funding_rates.db.insert_funding_rates(funding_data_list)
            logger.info(f"Collected and stored {inserted} funding rates")

            return len(funding_data_list)

        except Exception as e:
            logger.error(f"Error in collect_funding_rates: {e}")
            raise

    @celery_app.task(base=DatabaseTask, name='tasks.calculate_spreads')
    def calculate_spreads():
        """Calculate price spreads from cached price data"""
        try:
            logger.info("Calculating spreads...")

            # Get all cached prices
            price_data_list = []
            for symbol in TRADING_PAIRS:
                pattern = f"price:*:{symbol}"
                keys = redis_client.keys(pattern)

                for key in keys:
                    data = redis_client.get(key)
                    if data:
                        # Parse price data from cache
                        # This is a simplified version
                        pass

            # For now, recollect prices for spread calculation
            price_data_list = cex_collector.fetch_all_tickers(TRADING_PAIRS)

            if len(price_data_list) < 2:
                logger.warning("Not enough price data for spread calculation")
                return

            # Calculate spreads
            spread_data_list = spread_calculator.calculate_spreads(price_data_list)

            # Cache spreads
            spreads_by_symbol = {}
            for spread in spread_data_list:
                if spread.symbol not in spreads_by_symbol:
                    spreads_by_symbol[spread.symbol] = []
                spreads_by_symbol[spread.symbol].append({
                    'exchange_a': spread.exchange_a,
                    'exchange_b': spread.exchange_b,
                    'price_a': float(spread.price_a),
                    'price_b': float(spread.price_b),
                    'spread_pct': float(spread.spread_pct),
                    'spread_type': spread.spread_type.value,
                })

            for symbol, spreads in spreads_by_symbol.items():
                key = f"spread:{symbol}"
                redis_client.setex(key, 300, json.dumps(spreads))

            # Insert into ClickHouse
            inserted = calculate_spreads.db.insert_spreads(spread_data_list)
            logger.info(f"Calculated and stored {inserted} spreads")

            return len(spread_data_list)

        except Exception as e:
            logger.error(f"Error in calculate_spreads: {e}")
            raise

    @celery_app.task(base=DatabaseTask, name='tasks.detect_arbitrage')
    def detect_arbitrage():
        """Detect arbitrage opportunities"""
        try:
            logger.info("Detecting arbitrage opportunities...")

            # Get current prices
            price_data_list = cex_collector.fetch_all_tickers(TRADING_PAIRS)

            if len(price_data_list) < 2:
                logger.warning("Not enough price data for arbitrage detection")
                return

            # Detect opportunities
            opportunities = spread_calculator.detect_arbitrage_opportunities(price_data_list)

            if not opportunities:
                logger.info("No arbitrage opportunities detected")
                return 0

            # Cache top opportunities in Redis sorted set
            for opp in opportunities:
                score = float(opp.estimated_profit)
                value = json.dumps({
                    'symbol': opp.symbol,
                    'buy_exchange': opp.buy_exchange,
                    'sell_exchange': opp.sell_exchange,
                    'buy_price': float(opp.buy_price),
                    'sell_price': float(opp.sell_price),
                    'spread_pct': float(opp.spread_pct),
                    'estimated_profit': float(opp.estimated_profit),
                    'confidence_score': opp.confidence_score,
                    'timestamp': opp.timestamp.isoformat(),
                })
                redis_client.zadd('arbitrage:opportunities', {value: score})

            # Keep only top 100
            redis_client.zremrangebyrank('arbitrage:opportunities', 0, -101)

            # Insert into ClickHouse
            inserted = detect_arbitrage.db.insert_arbitrage_opportunities(opportunities)
            logger.info(f"Detected and stored {inserted} arbitrage opportunities")

            return len(opportunities)

        except Exception as e:
            logger.error(f"Error in detect_arbitrage: {e}")
            raise

    return {
        'collect_cex_prices': collect_cex_prices,
        'collect_funding_rates': collect_funding_rates,
        'calculate_spreads': calculate_spreads,
        'detect_arbitrage': detect_arbitrage,
    }
