from datetime import datetime, timedelta, timezone

from bson import ObjectId
from database import db
from fastapi import APIRouter, Depends, HTTPException, status
from utils.dependencies import get_current_admin

router = APIRouter()


@router.get("/analytics/overview")
async def get_analytics_overview(current_user=Depends(get_current_admin)):
    """Get overall platform analytics"""
    try:
        now = datetime.now(timezone.utc)
        thirty_days_ago = now - timedelta(days=30)

        # Total orders and revenue
        orders = await db.orders.find(
            {"created_at": {"$gte": thirty_days_ago}}
        ).to_list(None)

        total_orders = len(orders)
        total_revenue = sum(order.get("total", 0) for order in orders)

        # Active restaurants
        active_restaurants = await db.restaurants.count_documents({"is_active": True})

        # Active delivery agents
        active_delivery_agents = await db.delivery_agents.count_documents(
            {"is_active": True}
        )

        # Average order value
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0

        # Orders by status
        status_breakdown = {}
        for order in orders:
            status = order.get("status", "unknown")
            status_breakdown[status] = status_breakdown.get(status, 0) + 1

        return {
            "total_orders": total_orders,
            "total_revenue": round(total_revenue, 2),
            "active_restaurants": active_restaurants,
            "active_delivery_agents": active_delivery_agents,
            "avg_order_value": round(avg_order_value, 2),
            "status_breakdown": status_breakdown,
            "period": "30_days",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/restaurants")
async def get_all_restaurants(
    current_user=Depends(get_current_admin), skip: int = 0, limit: int = 20
):
    """Get all restaurants with stats"""
    try:
        restaurants = await db.restaurants.find().skip(skip).limit(limit).to_list(limit)

        result = []
        for restaurant in restaurants:
            # Get restaurant orders
            orders = await db.orders.find(
                {"restaurant_id": str(restaurant["_id"])}
            ).to_list(None)

            revenue = sum(order.get("total", 0) for order in orders)

            result.append(
                {
                    "id": str(restaurant["_id"]),
                    "name": restaurant.get("name"),
                    "email": restaurant.get("email"),
                    "phone": restaurant.get("phone"),
                    "orders_count": len(orders),
                    "revenue": round(revenue, 2),
                    "is_active": restaurant.get("is_active", True),
                    "created_at": restaurant.get("created_at"),
                }
            )

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/delivery-agents")
async def get_all_delivery_agents(
    current_user=Depends(get_current_admin), skip: int = 0, limit: int = 20
):
    """Get all delivery agents with stats"""
    try:
        agents = await db.delivery_agents.find().skip(skip).limit(limit).to_list(limit)

        result = []
        for agent in agents:
            # Get agent deliveries
            deliveries = await db.orders.find(
                {"delivery_agent_id": str(agent["_id"])}
            ).to_list(None)

            completed = len([d for d in deliveries if d.get("status") == "delivered"])

            result.append(
                {
                    "id": str(agent["_id"]),
                    "name": agent.get("name"),
                    "email": agent.get("email"),
                    "phone": agent.get("phone"),
                    "total_deliveries": len(deliveries),
                    "completed_deliveries": completed,
                    "rating": agent.get("rating", 0),
                    "is_active": agent.get("is_active", True),
                    "created_at": agent.get("created_at"),
                }
            )

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/users")
async def get_all_users(
    current_user=Depends(get_current_admin), skip: int = 0, limit: int = 20
):
    """Get all users with stats"""
    try:
        users = (
            await db.users.find({"role": "customer"})
            .skip(skip)
            .limit(limit)
            .to_list(limit)
        )

        result = []
        for user in users:
            # Get user orders
            orders = await db.orders.find({"customer_id": str(user["_id"])}).to_list(
                None
            )

            spent = sum(order.get("total", 0) for order in orders)

            result.append(
                {
                    "id": str(user["_id"]),
                    "name": user.get("name"),
                    "email": user.get("email"),
                    "phone": user.get("phone"),
                    "orders_count": len(orders),
                    "total_spent": round(spent, 2),
                    "created_at": user.get("created_at"),
                }
            )

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/orders")
async def get_all_orders(
    current_user=Depends(get_current_admin), skip: int = 0, limit: int = 20
):
    """Get all orders"""
    try:
        orders = (
            await db.orders.find()
            .sort("created_at", -1)
            .skip(skip)
            .limit(limit)
            .to_list(limit)
        )

        result = []
        for order in orders:
            result.append(
                {
                    "id": str(order["_id"]),
                    "customer_id": order.get("customer_id"),
                    "restaurant_id": order.get("restaurant_id"),
                    "total": order.get("total"),
                    "status": order.get("status"),
                    "payment_method": order.get("payment_method"),
                    "created_at": order.get("created_at"),
                }
            )

        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/revenue/daily")
async def get_daily_revenue(current_user=Depends(get_current_admin), days: int = 30):
    """Get daily revenue for last N days"""
    try:
        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=days)

        pipeline = [
            {"$match": {"created_at": {"$gte": start_date}}},
            {
                "$group": {
                    "_id": {
                        "$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}
                    },
                    "revenue": {"$sum": "$total"},
                    "orders": {"$sum": 1},
                }
            },
            {"$sort": {"_id": 1}},
        ]

        result = await db.orders.aggregate(pipeline).to_list(None)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
