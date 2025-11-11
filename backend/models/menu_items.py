from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class MenuItemResponse(BaseModel):
    id: str
    restaurant_id: str
    name: str
    description: Optional[str]
    price: float
    category: Optional[str]
    image_url: Optional[str]
    availability: str
    is_vegetarian: bool
    is_vegan: Optional[bool] = False
    preparation_time: int
    created_at: datetime
    updated_at: datetime
    daily_count: int
