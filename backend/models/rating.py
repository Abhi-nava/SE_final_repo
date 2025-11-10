from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class RatingCreate(BaseModel):
    """Rating creation schema"""
    order_id: str
    restaurant_rating: Optional[int] = Field(None, ge=1, le=5)
    delivery_rating: Optional[int] = Field(None, ge=1, le=5)
    restaurant_review: Optional[str] = None
    delivery_review: Optional[str] = None
    food_quality: Optional[int] = Field(None, ge=1, le=5)
    delivery_speed: Optional[int] = Field(None, ge=1, le=5)
    packaging_quality: Optional[int] = Field(None, ge=1, le=5)

class RatingResponse(BaseModel):
    """Rating response schema"""
    id: str = Field(alias="_id")
    order_id: str
    customer_id: str
    restaurant_id: str
    delivery_agent_id: Optional[str]
    restaurant_rating: Optional[int]
    delivery_rating: Optional[int]
    restaurant_review: Optional[str]
    delivery_review: Optional[str]
    created_at: datetime
    
    class Config:
        populate_by_name = True
