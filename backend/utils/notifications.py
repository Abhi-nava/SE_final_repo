import logging
from datetime import datetime, timezone
from enum import Enum

from database import db

logger = logging.getLogger(__name__)


class NotificationType(str, Enum):
    ORDER_PLACED = "order_placed"
    ORDER_CONFIRMED = "order_confirmed"
    ORDER_PREPARING = "order_preparing"
    ORDER_READY = "order_ready"
    ORDER_PICKED_UP = "order_picked_up"
    ORDER_IN_TRANSIT = "order_in_transit"
    ORDER_DELIVERED = "order_delivered"
    ORDER_CANCELLED = "order_cancelled"
    DELIVERY_ASSIGNED = "delivery_assigned"


class NotificationService:
    @staticmethod
    async def send_notification(
        user_id: str,
        notification_type: NotificationType,
        title: str,
        message: str,
        data: dict = None,
    ):
        """Send notification to user"""
        try:
            notification = {
                "user_id": user_id,
                "type": notification_type.value,
                "title": title,
                "message": message,
                "data": data or {},
                "is_read": False,
                "created_at": datetime.now(timezone.utc),
            }

            result = await db.notifications.insert_one(notification)
            logger.info(f"Notification sent to user {user_id}: {notification_type}")

            # TODO: Send SMS/Email using external service
            # await send_sms(user_phone, message)
            # await send_email(user_email, title, message)

            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return None

    @staticmethod
    async def get_user_notifications(user_id: str, skip: int = 0, limit: int = 10):
        """Get user notifications"""
        try:
            notifications = (
                await db.notifications.find({"user_id": user_id})
                .sort("created_at", -1)
                .skip(skip)
                .limit(limit)
                .to_list(limit)
            )

            return notifications
        except Exception as e:
            logger.error(f"Error fetching notifications: {e}")
            return []

    @staticmethod
    async def mark_as_read(notification_id: str):
        """Mark notification as read"""
        try:
            from bson import ObjectId

            await db.notifications.update_one(
                {"_id": ObjectId(notification_id)}, {"$set": {"is_read": True}}
            )
        except Exception as e:
            logger.error(f"Error marking notification as read: {e}")

    @staticmethod
    async def notify_order_status_change(order_id: str, new_status: str):
        """Notify users about order status change"""
        try:
            order = await db.orders.find_one({"_id": order_id})
            if not order:
                return

            customer_id = order.get("customer_id")

            status_messages = {
                "pending": "Your order has been placed successfully!",
                "confirmed": "Your order has been confirmed by the restaurant.",
                "preparing": "Your food is being prepared.",
                "ready": "Your food is ready for pickup.",
                "assigned": "A delivery agent has been assigned to your order.",
                "picked_up": "Your order has been picked up.",
                "in_transit": "Your order is on the way!",
                "delivered": "Your order has been delivered. Enjoy your meal!",
                "cancelled": "Your order has been cancelled.",
            }

            message = status_messages.get(
                new_status, f"Order status updated to {new_status}"
            )

            await NotificationService.send_notification(
                user_id=customer_id,
                notification_type=NotificationType[new_status.upper()],
                title=f"Order {order_id}",
                message=message,
                data={"order_id": str(order_id), "status": new_status},
            )
        except Exception as e:
            logger.error(f"Error notifying order status change: {e}")
