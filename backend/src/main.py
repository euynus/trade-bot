"""
FastAPI main application
"""

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
import sys
import os

# Add parent directory to path to import shared module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../'))

from backend.src.config import settings
from backend.src.api.routes import router
from backend.src.api.websocket import handle_websocket
from backend.src.database import clickhouse_client, redis_client

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown"""
    # Startup
    logger.info("Starting up application...")
    try:
        clickhouse_client.connect()
        logger.info("Connected to ClickHouse")
    except Exception as e:
        logger.error(f"Failed to connect to ClickHouse: {e}")

    try:
        redis_client.connect()
        logger.info("Connected to Redis")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")

    yield

    # Shutdown
    logger.info("Shutting down application...")
    try:
        clickhouse_client.disconnect()
        logger.info("Disconnected from ClickHouse")
    except Exception as e:
        logger.error(f"Error disconnecting from ClickHouse: {e}")

    try:
        redis_client.disconnect()
        logger.info("Disconnected from Redis")
    except Exception as e:
        logger.error(f"Error disconnecting from Redis: {e}")


# Create FastAPI app
app = FastAPI(
    title="CEX/DEX Spread Monitoring API",
    description="API for monitoring price spreads and funding rates across CEX and DEX exchanges",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router)


# WebSocket endpoint
@app.websocket("/ws/realtime")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time data streaming"""
    await handle_websocket(websocket)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "CEX/DEX Spread Monitoring API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
