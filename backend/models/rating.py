from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RatingCreate(BaseModel):
    """Rating creation schema"""

    order_id: str
    restaurant_id: str
    delivery_agent_id: Optional[str] = None
    restaurant_rating: int = Field(..., ge=1, le=5)
    delivery_rating: int = Field(..., ge=1, le=5)
    delivery_speed: int = Field(..., ge=1, le=5)
    food_quality: int = Field(..., ge=1, le=5)
    packaging_quality: int = Field(..., ge=1, le=5)
    created_at: Optional[datetime] = None

    class Config:
        populate_by_name = True


class RatingResponse(BaseModel):
    """Rating response schema"""

    id: str = Field(alias="_id")
    order_id: str
    customer_id: str
    restaurant_id: str
    delivery_agent_id: Optional[str]
    restaurant_rating: int
    delivery_rating: int
    delivery_speed: int
    food_quality: int
    packaging_quality: int
    created_at: datetime

    class Config:
        populate_by_name = True
