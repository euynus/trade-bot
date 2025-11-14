"""
Redis connection and caching operations
"""

import redis
import json
from typing import Optional, Any, List
from datetime import datetime
import sys
import os

# Add parent directory to path to import shared module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from backend.src.config import settings


class RedisClient:
    def __init__(self):
        self.client = None

    def connect(self):
        """Connect to Redis"""
        self.client = redis.Redis(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            password=settings.REDIS_PASSWORD if settings.REDIS_PASSWORD else None,
            db=settings.REDIS_DB,
            decode_responses=True
        )
        return self.client

    def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            self.client.close()

    # Price caching
    def set_price(self, exchange: str, symbol: str, price_data: dict, ttl: int = 300):
        """Cache price data"""
        key = f"price:{exchange}:{symbol}"
        self.client.setex(key, ttl, json.dumps(price_data))

    def get_price(self, exchange: str, symbol: str) -> Optional[dict]:
        """Get cached price data"""
        key = f"price:{exchange}:{symbol}"
        data = self.client.get(key)
        return json.loads(data) if data else None

    def get_all_prices(self, symbol: Optional[str] = None) -> List[dict]:
        """Get all cached prices"""
        pattern = f"price:*:{symbol}" if symbol else "price:*"
        keys = self.client.keys(pattern)

        prices = []
        for key in keys:
            data = self.client.get(key)
            if data:
                price_data = json.loads(data)
                # Extract exchange and symbol from key
                parts = key.split(':')
                price_data['exchange'] = parts[1]
                price_data['symbol'] = parts[2]
                prices.append(price_data)

        return prices

    # Spread caching
    def set_spread(self, symbol: str, spread_data: dict, ttl: int = 300):
        """Cache spread data"""
        key = f"spread:{symbol}"
        self.client.setex(key, ttl, json.dumps(spread_data))

    def get_spread(self, symbol: str) -> Optional[dict]:
        """Get cached spread data"""
        key = f"spread:{symbol}"
        data = self.client.get(key)
        return json.loads(data) if data else None

    # Funding rate caching
    def set_funding_rate(self, exchange: str, symbol: str, funding_data: dict, ttl: int = 300):
        """Cache funding rate data"""
        key = f"funding:{exchange}:{symbol}"
        self.client.setex(key, ttl, json.dumps(funding_data))

    def get_funding_rate(self, exchange: str, symbol: str) -> Optional[dict]:
        """Get cached funding rate data"""
        key = f"funding:{exchange}:{symbol}"
        data = self.client.get(key)
        return json.loads(data) if data else None

    # Arbitrage opportunities
    def add_arbitrage_opportunity(self, opportunity: dict):
        """Add arbitrage opportunity to sorted set"""
        key = "arbitrage:opportunities"
        score = float(opportunity.get('estimated_profit', 0))
        value = json.dumps(opportunity)
        self.client.zadd(key, {value: score})
        # Keep only top 100
        self.client.zremrangebyrank(key, 0, -101)

    def get_arbitrage_opportunities(self, limit: int = 100) -> List[dict]:
        """Get top arbitrage opportunities"""
        key = "arbitrage:opportunities"
        # Get from highest to lowest score
        data = self.client.zrevrange(key, 0, limit - 1)
        return [json.loads(item) for item in data]

    # Pub/Sub for real-time updates
    def publish_price_update(self, channel: str, data: dict):
        """Publish price update to channel"""
        self.client.publish(channel, json.dumps(data))

    def subscribe(self, channels: List[str]):
        """Subscribe to channels"""
        pubsub = self.client.pubsub()
        pubsub.subscribe(*channels)
        return pubsub


# Global client instance
redis_client = RedisClient()
