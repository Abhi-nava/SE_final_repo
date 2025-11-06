print("[STARTUP] restaurants.py is being imported")
from fastapi import APIRouter, HTTPException, status, Depends
from models.restaurant import (
    RestaurantCreate, RestaurantUpdate, RestaurantResponse,
    MenuItem, MenuItemUpdate
)
from utils.dependencies import get_current_restaurant_owner
from database import db
from bson import ObjectId
from datetime import datetime, timezone
from models.menu_items import MenuItemResponse  

router = APIRouter()
print("[STARTUP] Router created in restaurants.py")
@router.post("/create", response_model=RestaurantResponse)
async def create_restaurant(
    restaurant_data: RestaurantCreate,
    current_user = Depends(get_current_restaurant_owner)
):
    """Create a new restaurant"""
    now = datetime.now(timezone.utc)
    
    restaurant_doc = {
        "owner_id": str(current_user["_id"]),
        "name": restaurant_data.name,
        "description": restaurant_data.description,
        "phone": restaurant_data.phone,
        "address": restaurant_data.address,
        "city": restaurant_data.city,
        "postal_code": restaurant_data.postal_code,
        "cuisine_types": restaurant_data.cuisine_types,
        "image_url": restaurant_data.image_url,
        "opening_time": restaurant_data.opening_time,
        "closing_time": restaurant_data.closing_time,
        "rating": 0.0,
        "total_ratings": 0,
        "is_active": True,
        "created_at": now,
        "updated_at": now
    }
    
    result = await db.restaurants.insert_one(restaurant_doc)
    restaurant_doc["_id"] = result.inserted_id
    
    return RestaurantResponse(
        id=str(result.inserted_id),
        owner_id=str(current_user["_id"]),
        **{k: v for k, v in restaurant_data.dict().items()}
    )

@router.get("/my-restaurant", response_model=RestaurantResponse)
async def get_my_restaurant(current_user = Depends(get_current_restaurant_owner)):
    """Get current user's restaurant"""
    restaurant = await db.restaurants.find_one({"owner_id": str(current_user["_id"])})
    
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    
    return RestaurantResponse(
        id=str(restaurant["_id"]),
        owner_id=restaurant["owner_id"],
        name=restaurant["name"],
        description=restaurant.get("description"),
        phone=restaurant["phone"],
        address=restaurant["address"],
        city=restaurant["city"],
        postal_code=restaurant["postal_code"],
        cuisine_types=restaurant["cuisine_types"],
        image_url=restaurant.get("image_url"),
        opening_time=restaurant["opening_time"],
        closing_time=restaurant["closing_time"],
        rating=restaurant.get("rating", 0.0),
        total_ratings=restaurant.get("total_ratings", 0),
        created_at=restaurant["created_at"],
        updated_at=restaurant["updated_at"]
    )


@router.get("/{restaurant_id}/menu", response_model=list[MenuItemResponse])
async def get_restaurant_menu(restaurant_id: str):
    """Fetch all menu items for a given restaurant"""
    try:
        restaurant = await db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        menu_items = await db.menu_items.find({"restaurant_id": ObjectId(restaurant_id)}).to_list(None)

        return [
            MenuItemResponse(
                id=str(item["_id"]),
                restaurant_id=str(item["restaurant_id"]),
                name=item["name"],
                description=item.get("description", ""),
                price=item["price"],
                category=item.get("category", "General"),
                image_url=item.get("image_url", ""),
                availability=item.get("availability", "available"),
                is_vegetarian=item.get("is_vegetarian", False),
                is_vegan=item.get("is_vegan", False),
                preparation_time=item.get("preparation_time", 0),
                created_at=item["created_at"],
                updated_at=item["updated_at"],
                daily_count=item.get("daily_count",0)
            )
            for item in menu_items
        ]
    except Exception as e:
        print(f"[ERROR] get_restaurant_menu: {e}")
        raise HTTPException(status_code=500, detail="Error fetching menu items")

