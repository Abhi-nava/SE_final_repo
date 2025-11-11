from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ItemAvailability(str, Enum):
    AVAILABLE = "available"
    OUT_OF_STOCK = "out_of_stock"
    DISCONTINUED = "discontinued"

class MenuItem(BaseModel):
    """Menu item schema"""
    id: str = Field(default=None, alias="_id")
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    price: float = Field(..., gt=0)
    category: str
    image_url: Optional[str] = None
    availability: ItemAvailability = ItemAvailability.AVAILABLE
    is_vegetarian: bool = False
    is_vegan: bool = False
    preparation_time: int = Field(default=30, description="in minutes")
    daily_count: int = 0
    
    class Config:
        populate_by_name = True

class MenuItemUpdate(BaseModel):
    """Menu item update schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    image_url: Optional[str] = None
    is_vegetarian: bool | None = None
    is_vegan: bool | None = None
    availability: Optional[ItemAvailability] = None
    preparation_time: Optional[int] = None
    daily_count: int | None = None

class RestaurantCreate(BaseModel):
    """Restaurant creation schema"""
    name: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    phone: str = Field(..., min_length=10)
    address: str = Field(...)
    city: str
    postal_code: str
    cuisine_types: List[str]
    image_url: Optional[str] = None
    opening_time: str = "09:00"  # HH:MM format
    closing_time: str = "23:00"

class RestaurantUpdate(BaseModel):
    """Restaurant update schema"""
    name: Optional[str] = None
    description: Optional[str] = None
    phone: Optional[str] = None
    opening_time: Optional[str] = None
    closing_time: Optional[str] = None
    image_url: Optional[str] = None

class RestaurantResponse(BaseModel):
    """Restaurant response schema"""
    id: str = Field(alias="_id")
    owner_id: str
    name: str
    description: Optional[str]
    phone: str
    address: str
    city: str
    postal_code: str
    cuisine_types: List[str]
    image_url: Optional[str]
    opening_time: str
    closing_time: str
    rating: float = 0.0
    total_ratings: int = 0
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    class Config:
        populate_by_name = True
