"""
Celery application configuration
"""

from celery import Celery
from celery.schedules import crontab
import logging
import sys
import os

# Add parent directory to path to import shared module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from worker.src.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create Celery app
app = Celery(
    'trade-bot-worker',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Celery configuration
app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Import and register tasks
from worker.src.tasks import collect_and_process_data
tasks = collect_and_process_data(app)

# Celery Beat schedule for periodic tasks
app.conf.beat_schedule = {
    # Collect CEX prices every 10 seconds
    'collect-cex-prices': {
        'task': 'tasks.collect_cex_prices',
        'schedule': settings.COLLECTION_INTERVAL_SECONDS,
    },
    # Collect funding rates every 60 seconds
    'collect-funding-rates': {
        'task': 'tasks.collect_funding_rates',
        'schedule': 60.0,
    },
    # Calculate spreads every 10 seconds (after price collection)
    'calculate-spreads': {
        'task': 'tasks.calculate_spreads',
        'schedule': settings.COLLECTION_INTERVAL_SECONDS,
    },
    # Detect arbitrage opportunities every 10 seconds
    'detect-arbitrage': {
        'task': 'tasks.detect_arbitrage',
        'schedule': settings.COLLECTION_INTERVAL_SECONDS,
    },
}

logger.info("Celery app initialized with beat schedule")

if __name__ == '__main__':
    app.start()
