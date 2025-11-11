print("[STARTUP] restaurants.py is being imported")
from datetime import datetime, timezone

from bson import ObjectId
from database import db
from fastapi import APIRouter, Depends, HTTPException, status
from models.menu_items import MenuItemResponse
from models.restaurant import (
    MenuItem,
    MenuItemUpdate,
    RestaurantCreate,
    RestaurantResponse,
    RestaurantUpdate,
)
from utils.dependencies import get_current_restaurant_owner

router = APIRouter()
print("[STARTUP] Router created in restaurants.py")


@router.post("/create", response_model=RestaurantResponse)
async def create_restaurant(
    restaurant_data: RestaurantCreate,
    current_user=Depends(get_current_restaurant_owner),
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
        "updated_at": now,
    }

    result = await db.restaurants.insert_one(restaurant_doc)
    restaurant_doc["_id"] = result.inserted_id

    return RestaurantResponse(
        id=str(result.inserted_id),
        owner_id=str(current_user["_id"]),
        **{k: v for k, v in restaurant_data.dict().items()},
    )


@router.get("/my-restaurant", response_model=RestaurantResponse)
async def get_my_restaurant(current_user=Depends(get_current_restaurant_owner)):
    """Get current user's restaurant"""
    restaurant = await db.restaurants.find_one({"owner_id": str(current_user["_id"])})

    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found"
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
        updated_at=restaurant["updated_at"],
    )


@router.put("/my-restaurant", response_model=RestaurantResponse)
async def update_my_restaurant(
    update_data: RestaurantUpdate, current_user=Depends(get_current_restaurant_owner)
):
    """Update restaurant details"""
    restaurant = await db.restaurants.find_one({"owner_id": str(current_user["_id"])})

    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found"
        )

    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    if update_dict:
        update_dict["updated_at"] = datetime.now(timezone.utc)
        await db.restaurants.update_one(
            {"_id": restaurant["_id"]}, {"$set": update_dict}
        )

    updated_restaurant = await db.restaurants.find_one({"_id": restaurant["_id"]})

    return RestaurantResponse(
        id=str(updated_restaurant["_id"]),
        owner_id=updated_restaurant["owner_id"],
        name=updated_restaurant["name"],
        description=updated_restaurant.get("description"),
        phone=updated_restaurant["phone"],
        address=updated_restaurant["address"],
        city=updated_restaurant["city"],
        postal_code=updated_restaurant["postal_code"],
        cuisine_types=updated_restaurant["cuisine_types"],
        image_url=updated_restaurant.get("image_url"),
        opening_time=updated_restaurant["opening_time"],
        closing_time=updated_restaurant["closing_time"],
        rating=updated_restaurant.get("rating", 0.0),
        total_ratings=updated_restaurant.get("total_ratings", 0),
        created_at=updated_restaurant["created_at"],
        updated_at=updated_restaurant["updated_at"],
    )


@router.get("/stats/dashboard-summary")
async def restaurant_dashboard_summary(
    current_user=Depends(get_current_restaurant_owner),
):
    """Get comprehensive dashboard summary for restaurant owner"""
    try:
        owner_oid = ObjectId(current_user["_id"])
        print("[DEBUG] Owner ID:", owner_oid)
        restaurant = await db.restaurants.find_one({"owner_id": owner_oid})
        # print("[DEBUG] Fetched restaurant:", restaurant)
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        restaurant_id = str(restaurant["_id"])

        # Get all orders for this restaurant
        orders = await db.orders.find({"restaurant_id": restaurant_id}).to_list(None)

        # Calculate stats
        total_orders = len(orders)
        pending_orders = len(
            [o for o in orders if o["order_status"] not in ["delivered", "cancelled"]]
        )

        # Get today's date range
        from datetime import datetime, timezone

        today_start = datetime.now(timezone.utc).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        # completed_today = len([
        #     o for o in orders
        #     if o["order_status"] == "delivered" and o.get("updated_at", o["created_at"]) >= today_start
        # ])

        # revenue_today = sum([
        #     o["total"] for o in orders
        #     if o["order_status"] == "delivered" and o.get("updated_at", o["created_at"]) >= today_start
        # ])
        completed_today = 0
        revenue_today = 0

        for o in orders:
            ts = o.get("updated_at", o["created_at"])

            # Ensure timezone-aware
            if ts.tzinfo is None:
                ts = ts.replace(tzinfo=timezone.utc)

            if o["order_status"] == "delivered" and ts >= today_start:
                completed_today += 1
                revenue_today += o["total"]

        # Get ratings summary using aggregation
        ratings_pipeline = [
            {"$match": {"restaurant_id": restaurant_id}},
            {
                "$group": {
                    "_id": None,
                    "count": {"$sum": 1},
                    "avg_restaurant": {"$avg": "$restaurant_rating"},
                    "avg_delivery": {"$avg": "$delivery_rating"},
                    "avg_food_quality": {"$avg": "$food_quality"},
                    "avg_delivery_speed": {"$avg": "$delivery_speed"},
                    "avg_packaging_quality": {"$avg": "$packaging_quality"},
                }
            },
        ]

        ratings_result = await db.ratings.aggregate(ratings_pipeline).to_list(1)

        if ratings_result:
            r = ratings_result[0]
            ratings_summary = {
                "count": r["count"],
                "avg_restaurant": round(r.get("avg_restaurant", 0), 2),
                "avg_delivery": round(r.get("avg_delivery", 0), 2),
                "avg_food_quality": round(r.get("avg_food_quality", 0), 2),
                "avg_delivery_speed": round(r.get("avg_delivery_speed", 0), 2),
                "avg_packaging_quality": round(r.get("avg_packaging_quality", 0), 2),
            }
        else:
            ratings_summary = {
                "count": 0,
                "avg_restaurant": 0,
                "avg_delivery": 0,
                "avg_food_quality": 0,
                "avg_delivery_speed": 0,
                "avg_packaging_quality": 0,
            }

        return {
            "restaurant": {
                "id": restaurant_id,
                "name": restaurant["name"],
                "phone": restaurant["phone"],
                "address": restaurant["address"],
                "opening_time": restaurant["opening_time"],
                "closing_time": restaurant["closing_time"],
            },
            "stats": {
                "total_orders": total_orders,
                "pending_orders": pending_orders,
                "completed_today": completed_today,
                "revenue_today": revenue_today,
            },
            "ratings": ratings_summary,
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] dashboard_summary: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error fetching dashboard data: {str(e)}"
        )


@router.get("/stats/rating-summary")
async def get_ratings_summary(current_user=Depends(get_current_restaurant_owner)):
    """Get detailed ratings summary for restaurant"""
    try:
        owner_id = ObjectId(current_user["_id"])
        restaurant = await db.restaurants.find_one({"owner_id": owner_id})
        print(
            "[DEBUG] Fetched restaurant for ratings summary:",
            restaurant,
            " Owner ID:",
            owner_id,
        )
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        pipeline = [
            {"$match": {"restaurant_id": str(restaurant["_id"])}},
            {
                "$group": {
                    "_id": None,
                    "count": {"$sum": 1},
                    "avg_restaurant": {"$avg": "$restaurant_rating"},
                    "avg_delivery": {"$avg": "$delivery_rating"},
                    "avg_food_quality": {"$avg": "$food_quality"},
                    "avg_delivery_speed": {"$avg": "$delivery_speed"},
                    "avg_packaging_quality": {"$avg": "$packaging_quality"},
                }
            },
        ]

        agg = await db.ratings.aggregate(pipeline).to_list(1)

        if not agg:
            return {
                "count": 0,
                "avg_restaurant": 0,
                "avg_delivery": 0,
                "avg_food_quality": 0,
                "avg_delivery_speed": 0,
                "avg_packaging_quality": 0,
            }

        x = agg[0]
        return {
            "count": x["count"],
            "avg_restaurant": round(x.get("avg_restaurant", 0), 2),
            "avg_delivery": round(x.get("avg_delivery", 0), 2),
            "avg_food_quality": round(x.get("avg_food_quality", 0), 2),
            "avg_delivery_speed": round(x.get("avg_delivery_speed", 0), 2),
            "avg_packaging_quality": round(x.get("avg_packaging_quality", 0), 2),
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] rating_summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching ratings: {str(e)}")


@router.post("/menu-items", response_model=dict)
async def add_menu_item(
    item_data: MenuItem, current_user=Depends(get_current_restaurant_owner)
):
    """Add menu item to restaurant"""
    # Restaurant lookup — store restaurant_id as ObjectId
    restaurant = await db.restaurants.find_one(
        {"owner_id": ObjectId(current_user["_id"])}
    )

    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found"
        )

    menu_item_doc = {
        "restaurant_id": ObjectId(restaurant["_id"]),
        "name": item_data.name,
        "description": item_data.description,
        "price": item_data.price,
        "category": item_data.category,
        "image_url": item_data.image_url,
        "availability": (
            item_data.availability.value
            if hasattr(item_data.availability, "value")
            else item_data.availability
        ),
        "is_vegetarian": item_data.is_vegetarian,
        "is_vegan": item_data.is_vegan,
        "preparation_time": item_data.preparation_time,
        "daily_count": getattr(item_data, "daily_count", 0),
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    }

    result = await db.menu_items.insert_one(menu_item_doc)

    return {"id": str(result.inserted_id), "message": "Menu item added successfully"}


@router.get("/menu-items")
async def get_menu_items(
    restaurant_id: str = None, current_user=Depends(get_current_restaurant_owner)
):
    """Get menu items for restaurant"""
    print("[DEBUG] get_menu_items called with current_user:", current_user)
    owner_id = ObjectId(current_user["_id"])
    if not restaurant_id:
        restaurant = await db.restaurants.find_one({"owner_id": owner_id})
        if not restaurant:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Restaurant not found"
            )
        restaurant_id = ObjectId(str(restaurant["_id"]))

    try:
        # items = await db.menu_items.find({"restaurant_id": restaurant_id}).to_list(None)
        items = await db.menu_items.find(
            {"restaurant_id": ObjectId(restaurant_id)}
        ).to_list(None)

    except Exception:
        items = []
    print(f"[DEBUG] Fetched {len(items)} menu items for restaurant ID {restaurant_id}")
    print("[DEBUG] Menu items:", items)
    return [
        {
            "id": str(item["_id"]),
            "name": item["name"],
            "description": item.get("description"),
            "price": item["price"],
            "category": item["category"],
            "image_url": item.get("image_url"),
            "availability": item["availability"],
            "is_vegetarian": item.get("is_vegetarian", False),
            "is_vegan": item.get("is_vegan", False),
            "preparation_time": item.get("preparation_time", 30),
            "daily_count": (
                int(item.get("daily_count", 0))
                if isinstance(item.get("daily_count", 0), (int, str))
                and str(item.get("daily_count", 0)).isdigit()
                else item.get("daily_count", 0)
            ),
        }
        for item in items
    ]


@router.get("/menu-items/{menu_item_id}")
async def get_menu_item(
    menu_item_id: str, current_user=Depends(get_current_restaurant_owner)
):
    """Fetch a single menu item by ID"""
    try:
        menu_item = await db.menu_items.find_one({"_id": ObjectId(menu_item_id)})
        print(f"[DEBUG] Fetched menu item: {menu_item}")
        if not menu_item:
            raise HTTPException(status_code=404, detail="Menu item not found")

        # Ownership verification
        restaurant = await db.restaurants.find_one(
            {"_id": ObjectId(menu_item["restaurant_id"])}
        )
        if restaurant["owner_id"] != ObjectId(current_user["_id"]):
            raise HTTPException(
                status_code=403, detail="Not authorized to view this menu item"
            )

        return {
            "id": str(menu_item["_id"]),
            "name": menu_item["name"],
            "description": menu_item.get("description", ""),
            "price": menu_item["price"],
            "category": menu_item.get("category", "General"),
            "image_url": menu_item.get("image_url", ""),
            "availability": menu_item.get("availability", "available"),
            "is_vegetarian": menu_item.get("is_vegetarian", False),
            "is_vegan": menu_item.get("is_vegan", False),
            "preparation_time": menu_item.get("preparation_time", 0),
            "daily_count": (
                int(menu_item.get("daily_count", 0))
                if isinstance(menu_item.get("daily_count", 0), (int, str))
                and str(menu_item.get("daily_count", 0)).isdigit()
                else menu_item.get("daily_count", 0)
            ),
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] get_menu_item: {e}")
        raise HTTPException(status_code=500, detail="Error fetching menu item")


@router.put("/menu-items/{menu_item_id}")
async def update_menu_item(
    menu_item_id: str,
    update_data: MenuItemUpdate,
    current_user=Depends(get_current_restaurant_owner),
):
    """Update menu item"""
    try:
        menu_item = await db.menu_items.find_one({"_id": ObjectId(menu_item_id)})
        if not menu_item:
            raise HTTPException(status_code=404, detail="Menu item not found")

        # Verify ownership
        restaurant = await db.restaurants.find_one(
            {"_id": ObjectId(menu_item["restaurant_id"])}
        )
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        if str(restaurant["owner_id"]) != str(current_user["_id"]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this menu item",
            )

        update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
        if update_dict:
            update_dict["updated_at"] = datetime.now(timezone.utc)
            await db.menu_items.update_one(
                {"_id": ObjectId(menu_item_id)}, {"$set": update_dict}
            )

        return {"message": "Menu item updated successfully"}

    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] update_menu_item: {e}")
        raise HTTPException(status_code=500, detail="Error updating menu item")


# @router.put("/menu-items/{menu_item_id}")
# async def update_menu_item(
#     menu_item_id: str,
#     update_data: MenuItemUpdate,
#     current_user = Depends(get_current_restaurant_owner)
# ):
#     """Update menu item"""
#     try:
#         menu_item = await db.menu_items.find_one({"_id": ObjectId(menu_item_id)})
#     except:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Menu item not found"
#         )

#     if not menu_item:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Menu item not found"
#         )

#     # Verify ownership
#     restaurant = await db.restaurants.find_one({"_id": ObjectId(menu_item["restaurant_id"])})
#     if restaurant["owner_id"] != str(current_user["_id"]):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized to update this menu item"
#         )

#     update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
#     if update_dict:
#         update_dict["updated_at"] = datetime.now(timezone.utc)
#         await db.menu_items.update_one(
#             {"_id": ObjectId(menu_item_id)},
#             {"$set": update_dict}
#         )

#     return {"message": "Menu item updated successfully"}


@router.get("/{restaurant_id}/menu", response_model=list[MenuItemResponse])
async def get_restaurant_menu(restaurant_id: str):
    """Fetch all menu items for a given restaurant"""
    try:
        restaurant = await db.restaurants.find_one({"_id": ObjectId(restaurant_id)})
        if not restaurant:
            raise HTTPException(status_code=404, detail="Restaurant not found")

        menu_items = await db.menu_items.find(
            {"restaurant_id": ObjectId(restaurant_id)}
        ).to_list(None)

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
                daily_count=item.get("daily_count", 0),
            )
            for item in menu_items
        ]
    except Exception as e:
        print(f"[ERROR] get_restaurant_menu: {e}")
        raise HTTPException(status_code=500, detail="Error fetching menu items")


@router.delete("/menu-items/{menu_item_id}")
async def delete_menu_item(
    menu_item_id: str, current_user=Depends(get_current_restaurant_owner)
):
    """Delete menu item"""
    try:
        menu_item = await db.menu_items.find_one({"_id": ObjectId(menu_item_id)})
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found"
        )

    if not menu_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Menu item not found"
        )

    # Verify ownership
    restaurant = await db.restaurants.find_one(
        {"_id": ObjectId(menu_item["restaurant_id"])}
    )
    if restaurant["owner_id"] != ObjectId(current_user["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this menu item",
        )

    await db.menu_items.delete_one({"_id": ObjectId(menu_item_id)})

    return {"message": "Menu item deleted successfully"}
