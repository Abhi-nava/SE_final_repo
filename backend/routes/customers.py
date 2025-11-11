from datetime import datetime, timezone

from bson import ObjectId
from database import db
from fastapi import APIRouter, Depends, HTTPException, status
from models.restaurant import RestaurantResponse
from models.user import UserResponse, UserUpdate
from utils.dependencies import get_current_customer

router = APIRouter()


@router.get("/restaurants", response_model=list[RestaurantResponse])
async def list_restaurants(
    city: str = None, cuisine: str = None, skip: int = 0, limit: int = 20
):
    """List all restaurants with optional filters"""
    query = {"is_active": True}

    if city:
        query["city"] = {"$regex": city, "$options": "i"}

    if cuisine:
        query["cuisine_types"] = {"$in": [cuisine]}

    restaurants = (
        await db.restaurants.find(query).skip(skip).limit(limit).to_list(limit)
    )

    return [
        RestaurantResponse(
            id=str(r["_id"]),
            owner_id=str(r["owner_id"]),
            name=r["name"],
            description=r.get("description"),
            phone=r["phone"],
            address=r["address"],
            city=r["city"],
            postal_code=r["postal_code"],
            cuisine_types=r["cuisine_types"],
            image_url=r.get("image_url"),
            opening_time=r["opening_time"],
            closing_time=r["closing_time"],
            rating=r.get("rating", 0.0),
            total_ratings=r.get("total_ratings", 0),
            created_at=r["created_at"],
            updated_at=r["updated_at"],
        )
        for r in restaurants
    ]


@router.get("/restaurants/{restaurant_id}", response_model=RestaurantResponse)
async def get_restaurant(restaurant_id: str):
    """Get restaurant details with menu"""
    try:
        restaurant = await db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found"
        )

    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found"
        )

    return RestaurantResponse(
        id=str(restaurant["_id"]),
        owner_id=str(restaurant["owner_id"]),
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
        updated_at=restaurant["updated_at"],
        daily_count=restaurant.get("daily_count", 0),
    )


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdate, current_user=Depends(get_current_customer)
):
    """Update customer profile"""
    update_dict = {}
    if update_data.full_name:
        update_dict["full_name"] = update_data.full_name
    if update_data.phone:
        update_dict["phone"] = update_data.phone
    if update_data.address:
        update_dict["address"] = update_data.address

    if update_dict:
        update_dict["updated_at"] = datetime.now(timezone.utc)
        await db.users.update_one({"_id": current_user["_id"]}, {"$set": update_dict})

    # Fetch updated user
    user = await db.users.find_one({"_id": current_user["_id"]})

    return UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        phone=user["phone"],
        full_name=user["full_name"],
        role=user["role"],
        address=user.get("address"),
        created_at=user["created_at"],
        updated_at=user["updated_at"],
    )
