from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PREPARING = "preparing"
    READY = "ready"
    ASSIGNED = "assigned"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class OrderItemRequest(BaseModel):
    """Order item request schema"""

    menu_item_id: str
    quantity: int = Field(..., gt=0)
    special_instructions: Optional[str] = None


class OrderCreate(BaseModel):
    """Order creation schema"""

    restaurant_id: str
    items: List[OrderItemRequest]
    delivery_address: str
    delivery_phone: str
    payment_method: str = Field(..., description="card, upi, wallet, cod")
    coupon_code: Optional[str] = None
    special_instructions: Optional[str] = None


class OrderUpdate(BaseModel):
    """Order update schema"""

    status: Optional[OrderStatus] = None
    delivery_agent_id: Optional[str] = None


class RestaurantMeta(BaseModel):
    name: str
    image: str | None = None


class OrderResponse(BaseModel):
    id: str
    customer_id: str
    restaurant_id: str
    restaurant: RestaurantMeta | None = None
    items: list
    subtotal: float
    delivery_fee: float
    discount: float
    total: float
    status: str
    delivery_address: str
    delivery_phone: str
    payment_method: str
    delivery_agent_id: str | None = None
    estimated_delivery_time: int | None = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


class OrderStatusUpdate(BaseModel):
    """Order status update schema"""

    status: OrderStatus
    notes: Optional[str] = None
