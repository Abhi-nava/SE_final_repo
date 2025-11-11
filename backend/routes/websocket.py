import json
import logging
from datetime import datetime, timezone

from database import db
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()
logger = logging.getLogger(__name__)


# Store active WebSocket connections
class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, client_id: str, websocket: WebSocket):
        await websocket.accept()
        if client_id not in self.active_connections:
            self.active_connections[client_id] = []
        self.active_connections[client_id].append(websocket)
        logger.info(f"Client {client_id} connected")

    def disconnect(self, client_id: str, websocket: WebSocket):
        self.active_connections[client_id].remove(websocket)
        if not self.active_connections[client_id]:
            del self.active_connections[client_id]
        logger.info(f"Client {client_id} disconnected")

    async def broadcast(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            dead_connections = []
            for connection in self.active_connections[client_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending message: {e}")
                    dead_connections.append(connection)

            for connection in dead_connections:
                self.active_connections[client_id].remove(connection)

    async def broadcast_to_user(self, user_id: str, message: dict):
        """Broadcast to all connections of a specific user"""
        await self.broadcast(f"user_{user_id}", message)

    async def broadcast_to_order(self, order_id: str, message: dict):
        """Broadcast to all users viewing an order"""
        await self.broadcast(f"order_{order_id}", message)


manager = ConnectionManager()


@router.websocket("/ws/order/{order_id}")
async def websocket_order_tracking(websocket: WebSocket, order_id: str):
    """WebSocket endpoint for real-time order tracking"""
    user_id = websocket.query_params.get("user_id")

    if not user_id:
        await websocket.close(code=4000, reason="user_id required")
        return

    await manager.connect(f"order_{order_id}", websocket)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
            elif message.get("type") == "get_order_status":
                order = await db.orders.find_one({"_id": order_id})
                if order:
                    await websocket.send_json(
                        {
                            "type": "order_status",
                            "status": order.get("status"),
                            "data": {
                                "order_id": str(order.get("_id")),
                                "status": order.get("status"),
                                "estimated_delivery": order.get(
                                    "estimated_delivery_time"
                                ),
                                "delivery_agent_id": order.get("delivery_agent_id"),
                            },
                        }
                    )
    except WebSocketDisconnect:
        manager.disconnect(f"order_{order_id}", websocket)
        logger.info(f"Client disconnected from order {order_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(f"order_{order_id}", websocket)


@router.websocket("/ws/delivery-tracking/{delivery_agent_id}")
async def websocket_delivery_tracking(websocket: WebSocket, delivery_agent_id: str):
    """WebSocket endpoint for delivery agent location tracking"""
    await manager.connect(f"delivery_{delivery_agent_id}", websocket)

    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            if message.get("type") == "location_update":
                latitude = message.get("latitude")
                longitude = message.get("longitude")
                order_id = message.get("order_id")

                if latitude and longitude and order_id:
                    # Update delivery agent location
                    await db.delivery_agents.update_one(
                        {"_id": delivery_agent_id},
                        {
                            "$set": {
                                "current_location": {
                                    "latitude": latitude,
                                    "longitude": longitude,
                                    "timestamp": datetime.now(timezone.utc),
                                },
                                "updated_at": datetime.now(timezone.utc),
                            }
                        },
                    )

                    # Broadcast location to order watchers
                    await manager.broadcast_to_order(
                        order_id,
                        {
                            "type": "delivery_location_update",
                            "data": {
                                "latitude": latitude,
                                "longitude": longitude,
                                "delivery_agent_id": delivery_agent_id,
                            },
                        },
                    )

                    await websocket.send_json(
                        {"type": "ack", "message": "Location updated"}
                    )

            elif message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})
    except WebSocketDisconnect:
        manager.disconnect(f"delivery_{delivery_agent_id}", websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(f"delivery_{delivery_agent_id}", websocket)
