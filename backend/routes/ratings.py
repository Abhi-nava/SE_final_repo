from fastapi import APIRouter, HTTPException, status, Depends
from models.rating import RatingCreate, RatingResponse
from utils.dependencies import get_current_customer
from database import db

from bson import ObjectId
from datetime import datetime, timezone

router = APIRouter()

@router.post("/create", response_model=dict)
async def create_rating(
    rating_data: RatingCreate,
    current_user = Depends(get_current_customer)
):
    """Submit rating for order"""
    try:
        order = await db.orders.find_one({"_id": ObjectId(rating_data.order_id)})
    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check if already rated
    existing_rating = await db.ratings.find_one({"order_id": rating_data.order_id})
    if existing_rating:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already rated this order"
        )
    
    now = datetime.now(timezone.utc)
    rating_doc = {
        "order_id": rating_data.order_id,
        "customer_id": str(current_user["_id"]),
        "restaurant_id": order["restaurant_id"],
        "delivery_agent_id": order.get("delivery_agent_id"),
        "restaurant_rating": rating_data.restaurant_rating,
        "delivery_rating": rating_data.delivery_rating,
        "restaurant_review": rating_data.restaurant_review,
        "delivery_review": rating_data.delivery_review,
        "created_at": now
    }
    
    result = await db.ratings.insert_one(rating_doc)
    
    # Update restaurant average rating
    restaurant_ratings = await db.ratings.find({
        "restaurant_id": order["restaurant_id"],
        "restaurant_rating": {"$ne": None}
    }).to_list(None)
    
    if restaurant_ratings:
        avg_rating = sum(r.get("restaurant_rating", 0) for r in restaurant_ratings) / len(restaurant_ratings)
        await db.restaurants.update_one(
            {"_id": ObjectId(order["restaurant_id"])},
            {
                "$set": {
                    "rating": avg_rating,
                    "total_ratings": len(restaurant_ratings)
                }
            }
        )
    
    # Update delivery agent rating if exists
    if order.get("delivery_agent_id"):
        delivery_ratings = await db.ratings.find({
            "delivery_agent_id": order["delivery_agent_id"],
            "delivery_rating": {"$ne": None}
        }).to_list(None)
        
        if delivery_ratings:
            avg_rating = sum(r.get("delivery_rating", 0) for r in delivery_ratings) / len(delivery_ratings)
            await db.delivery_agents.update_one(
                {"_id": ObjectId(order["delivery_agent_id"])},
                {
                    "$set": {
                        "rating": avg_rating,
                        "total_deliveries": len(delivery_ratings)
                    }
                }
            )
    
    return {
        "id": str(result.inserted_id),
        "message": "Rating submitted successfully"
    }

@router.get("/restaurant/{restaurant_id}", response_model=list[RatingResponse])
async def get_restaurant_ratings(restaurant_id: str):
    """Get ratings for a restaurant"""
    ratings = await db.ratings.find({
        "restaurant_id": restaurant_id,
        "restaurant_rating": {"$ne": None}
    }).sort("created_at", -1).limit(50).to_list(50)
    
    return [
        RatingResponse(
            id=str(r["_id"]),
            order_id=r["order_id"],
            customer_id=r["customer_id"],
            restaurant_id=r["restaurant_id"],
            delivery_agent_id=r.get("delivery_agent_id"),
            restaurant_rating=r.get("restaurant_rating"),
            delivery_rating=r.get("delivery_rating"),
            restaurant_review=r.get("restaurant_review"),
            delivery_review=r.get("delivery_review"),
            created_at=r["created_at"]
        )
        for r in ratings
    ]

@router.get("/delivery-agent/{agent_id}", response_model=list[RatingResponse])
async def get_agent_ratings(agent_id: str):
    """Get ratings for a delivery agent"""
    ratings = await db.ratings.find({
        "delivery_agent_id": agent_id,
        "delivery_rating": {"$ne": None}
    }).sort("created_at", -1).limit(50).to_list(50)
    
    return [
        RatingResponse(
            id=str(r["_id"]),
            order_id=r["order_id"],
            customer_id=r["customer_id"],
            restaurant_id=r["restaurant_id"],
            delivery_agent_id=r.get("delivery_agent_id"),
            restaurant_rating=r.get("restaurant_rating"),
            delivery_rating=r.get("delivery_rating"),
            restaurant_review=r.get("restaurant_review"),
            delivery_review=r.get("delivery_review"),
            created_at=r["created_at"]
        )
        for r in ratings
    ]
