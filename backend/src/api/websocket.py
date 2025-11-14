"""
WebSocket handler for real-time data streaming
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Set
import asyncio
import json
import logging
import sys
import os

# Add parent directory to path to import shared module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../../'))

from backend.src.database import redis_client

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.subscriptions: dict[WebSocket, Set[str]] = {}

    async def connect(self, websocket: WebSocket):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        self.subscriptions[websocket] = set()
        logger.info(f"New WebSocket connection. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        if websocket in self.subscriptions:
            del self.subscriptions[websocket]
        logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific client"""
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message: {e}")

    async def broadcast(self, message: dict, channel: str = None):
        """Broadcast a message to all connected clients or specific channel subscribers"""
        disconnected = []
        for connection in self.active_connections:
            try:
                # If channel is specified, only send to subscribers
                if channel and channel not in self.subscriptions.get(connection, set()):
                    continue

                await connection.send_json(message)
            except WebSocketDisconnect:
                disconnected.append(connection)
            except Exception as e:
                logger.error(f"Error broadcasting message: {e}")
                disconnected.append(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

    def subscribe(self, websocket: WebSocket, channel: str):
        """Subscribe a client to a channel"""
        if websocket in self.subscriptions:
            self.subscriptions[websocket].add(channel)
            logger.info(f"Client subscribed to {channel}")

    def unsubscribe(self, websocket: WebSocket, channel: str):
        """Unsubscribe a client from a channel"""
        if websocket in self.subscriptions and channel in self.subscriptions[websocket]:
            self.subscriptions[websocket].remove(channel)
            logger.info(f"Client unsubscribed from {channel}")


# Global connection manager
manager = ConnectionManager()


async def handle_websocket(websocket: WebSocket):
    """Handle WebSocket connections"""
    await manager.connect(websocket)

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            # Handle different message types
            msg_type = message.get("type")

            if msg_type == "subscribe":
                # Subscribe to specific channels (e.g., symbol, exchange)
                channel = message.get("channel")
                if channel:
                    manager.subscribe(websocket, channel)
                    await manager.send_personal_message({
                        "type": "subscribed",
                        "channel": channel
                    }, websocket)

            elif msg_type == "unsubscribe":
                # Unsubscribe from channel
                channel = message.get("channel")
                if channel:
                    manager.unsubscribe(websocket, channel)
                    await manager.send_personal_message({
                        "type": "unsubscribed",
                        "channel": channel
                    }, websocket)

            elif msg_type == "ping":
                # Respond to ping with pong
                await manager.send_personal_message({
                    "type": "pong",
                    "timestamp": message.get("timestamp")
                }, websocket)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)


async def broadcast_price_update(price_data: dict):
    """Broadcast price update to subscribed clients"""
    channel = f"price:{price_data.get('symbol')}"
    await manager.broadcast({
        "type": "price_update",
        "data": price_data
    }, channel=channel)


async def broadcast_spread_update(spread_data: dict):
    """Broadcast spread update to subscribed clients"""
    channel = f"spread:{spread_data.get('symbol')}"
    await manager.broadcast({
        "type": "spread_update",
        "data": spread_data
    }, channel=channel)


async def broadcast_arbitrage_opportunity(opportunity: dict):
    """Broadcast arbitrage opportunity to all clients"""
    await manager.broadcast({
        "type": "arbitrage_opportunity",
        "data": opportunity
    })
