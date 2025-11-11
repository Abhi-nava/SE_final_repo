from datetime import datetime, timezone

from bson import ObjectId
from database import db
from fastapi import APIRouter, Depends, HTTPException, status
from models.rating import RatingCreate, RatingResponse
from utils.dependencies import get_current_customer

router = APIRouter()


@router.post("/create", response_model=dict)
async def create_rating(
    rating_data: RatingCreate, current_user=Depends(get_current_customer)
):
    """Submit rating for order"""
    print(f"\n{'='*60}")
    print(f"[RATING] Create rating endpoint called")
    print(f"[RATING] Rating data received: {rating_data.dict()}")
    print(f"[RATING] Current user ID: {current_user['_id']}")
    print(f"{'='*60}\n")

    try:
        order = await db.orders.find_one({"_id": ObjectId(rating_data.order_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )

    # Check if current customer already rated this order
    existing_rating = await db.ratings.find_one(
        {"order_id": rating_data.order_id, "customer_id": str(current_user["_id"])}
    )
    if existing_rating:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already rated this order",
        )

    now = rating_data.created_at or datetime.now(timezone.utc)
    rating_doc = {
        "order_id": rating_data.order_id,
        "customer_id": str(current_user["_id"]),
        "restaurant_id": rating_data.restaurant_id,
        "delivery_agent_id": rating_data.delivery_agent_id,
        "restaurant_rating": rating_data.restaurant_rating,
        "delivery_rating": rating_data.delivery_rating,
        "delivery_speed": rating_data.delivery_speed,
        "food_quality": rating_data.food_quality,
        "packaging_quality": rating_data.packaging_quality,
        "created_at": now,
    }

    print(f"[RATING] Saving rating document: {rating_doc}")
    result = await db.ratings.insert_one(rating_doc)
    print(f"[RATING] Rating saved with ID: {result.inserted_id}")

    # Update restaurant average rating (based on restaurant_rating and food_quality)
    restaurant_ratings = await db.ratings.find(
        {"restaurant_id": rating_data.restaurant_id, "restaurant_rating": {"$ne": None}}
    ).to_list(None)

    if restaurant_ratings:
        avg_rating = sum(
            r.get("restaurant_rating", 0) for r in restaurant_ratings
        ) / len(restaurant_ratings)
        await db.restaurants.update_one(
            {"_id": ObjectId(rating_data.restaurant_id)},
            {"$set": {"rating": avg_rating, "total_ratings": len(restaurant_ratings)}},
        )

    # Update delivery agent rating if exists
    if rating_data.delivery_agent_id:
        delivery_ratings = await db.ratings.find(
            {
                "delivery_agent_id": rating_data.delivery_agent_id,
                "delivery_rating": {"$ne": None},
            }
        ).to_list(None)

        if delivery_ratings:
            avg_rating = sum(
                r.get("delivery_rating", 0) for r in delivery_ratings
            ) / len(delivery_ratings)
            await db.delivery_agents.update_one(
                {"_id": ObjectId(rating_data.delivery_agent_id)},
                {
                    "$set": {
                        "rating": avg_rating,
                        "total_deliveries": len(delivery_ratings),
                    }
                },
            )

    return {"id": str(result.inserted_id), "message": "Rating submitted successfully"}


@router.get("/check/{order_id}")
async def check_order_rating(order_id: str, current_user=Depends(get_current_customer)):
    """Check if the current customer has rated this order"""
    try:
        existing_rating = await db.ratings.find_one(
            {"order_id": order_id, "customer_id": str(current_user["_id"])}
        )
        return {"has_rating": existing_rating is not None}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/restaurant/{restaurant_id}", response_model=list[RatingResponse])
async def get_restaurant_ratings(restaurant_id: str):
    """Get ratings for a restaurant"""
    ratings = (
        await db.ratings.find(
            {"restaurant_id": restaurant_id, "restaurant_rating": {"$ne": None}}
        )
        .sort("created_at", -1)
        .limit(50)
        .to_list(50)
    )

    return [
        RatingResponse(
            id=str(r["_id"]),
            order_id=r["order_id"],
            customer_id=r["customer_id"],
            restaurant_id=r["restaurant_id"],
            delivery_agent_id=r.get("delivery_agent_id"),
            restaurant_rating=r.get("restaurant_rating"),
            delivery_rating=r.get("delivery_rating"),
            delivery_speed=r.get("delivery_speed"),
            food_quality=r.get("food_quality"),
            packaging_quality=r.get("packaging_quality"),
            created_at=r["created_at"],
        )
        for r in ratings
    ]


@router.get("/delivery-agent/{agent_id}", response_model=list[RatingResponse])
async def get_agent_ratings(agent_id: str):
    """Get ratings for a delivery agent"""
    ratings = (
        await db.ratings.find(
            {"delivery_agent_id": agent_id, "delivery_rating": {"$ne": None}}
        )
        .sort("created_at", -1)
        .limit(50)
        .to_list(50)
    )

    return [
        RatingResponse(
            id=str(r["_id"]),
            order_id=r["order_id"],
            customer_id=r["customer_id"],
            restaurant_id=r["restaurant_id"],
            delivery_agent_id=r.get("delivery_agent_id"),
            restaurant_rating=r.get("restaurant_rating"),
            delivery_rating=r.get("delivery_rating"),
            delivery_speed=r.get("delivery_speed"),
            food_quality=r.get("food_quality"),
            packaging_quality=r.get("packaging_quality"),
            created_at=r["created_at"],
        )
        for r in ratings
    ]
