from fastapi import APIRouter, HTTPException, status, Depends
from models.delivery import (
    DeliveryAgentCreate, DeliveryAgentUpdate, DeliveryAgentResponse,
    LocationUpdate, AgentStatsResponse
)
from models.order import OrderResponse, OrderStatus
from utils.dependencies import get_current_delivery_agent
from database import db
from bson import ObjectId
from datetime import datetime, timezone

router = APIRouter()

async def find_available_agent():
    """Find an available delivery agent (online & not currently delivering)."""
    agent = await db.delivery_agents.find_one({"status": "online"})
    return agent


@router.post("/auto_create")
async def auto_create_agents():
    """Auto-create delivery_agent entries for all users with role='delivery_agent'."""
    users = db.users
    agents = db.delivery_agents

    async for user in users.find({"role": "delivery_agent"}):
        existing = await agents.find_one({"user_id": user["_id"]})
        if not existing:
            doc = {
                "user_id": user["_id"],
                "email": user["email"],
                "password": user["password"],
                "vehicle_type": "bike",
                "vehicle_number": "KA01AB1234",
                "vehicle_registration": "2024-01-01",
                "license_number": "DL0000000000",
                "insurance_document": "N/A",
                "bank_account": "0000000000",
                "ifsc_code": "SBIN0000000",
                "status": "offline",
                "rating": 5.0,
                "total_deliveries": 0,
                "current_location": {"lat": 12.9716, "lng": 77.5946},
                "is_verified": False,
                "role": "delivery_agent",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
            }
            await agents.insert_one(doc)
    return {"message": "All delivery agents synced successfully!"}


@router.get("/stats/{agent_id}", response_model=AgentStatsResponse)
async def get_agent_stats(agent_id: str):
    """Get delivery agent dashboard data."""
    agent = await db.delivery_agents.find_one({"_id": ObjectId(agent_id)})
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    total_deliveries = agent.get("total_deliveries", 0)
    rating = agent.get("rating", 0)
    total_earnings = total_deliveries * 50  

    active_orders = await db.orders.count_documents({
        "delivery_agent_id": str(agent["_id"]),
        "order_status": {"$in": ["arriving", "in-transit", "waiting"]}
    })

    completed_orders = await db.orders.count_documents({
        "delivery_agent_id": str(agent["_id"]),
        "order_status": "delivered"
    })

    return AgentStatsResponse(
        total_deliveries=total_deliveries,
        avg_rating=rating,
        total_earnings=total_earnings,
        completed_orders=completed_orders,
        active_orders=active_orders,
        status=agent["status"]
    )


@router.post("/update_status/{agent_id}")
async def update_agent_status(agent_id: str, status: str):
    """Toggle delivery agent's status (online/offline/on_delivery)."""
    result = await db.delivery_agents.update_one(
        {"_id": ObjectId(agent_id)},
        {"$set": {"status": status, "updated_at": datetime.utcnow()}}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Agent not found or no update made")
    return {"message": "Status updated successfully"}


@router.post("/update_location/{agent_id}")
async def update_agent_location(agent_id: str, lat: float, lng: float):
    """Update delivery agent's current location."""
    await db.delivery_agents.update_one(
        {"_id": ObjectId(agent_id)},
        {"$set": {"current_location": {"lat": lat, "lng": lng}, "updated_at": datetime.utcnow()}}
    )
    return {"message": "Location updated successfully"}


@router.get("/assigned_orders/{agent_id}")
async def get_assigned_orders(agent_id: str):
    """Fetch all current assigned orders for a delivery agent."""
    orders_cursor = db.orders.find({
        "delivery_agent_id": agent_id,
        "order_status": {"$in": ["arriving", "waiting", "in-transit"]}
    })
    orders = []
    async for o in orders_cursor:
        restaurant = await db.restaurants.find_one({"_id": ObjectId(o["restaurant_id"])})
        items = []
        for item in o["items"]:
            menu_item = await db.menu_items.find_one({"_id": ObjectId(item["menu_item_id"])})
            if menu_item:
                item["image_url"] = menu_item.get("image_url", "")
            items.append(item)
        orders.append({
            "order_id": str(o["_id"]),
            "restaurant_name": restaurant["name"] if restaurant else "Unknown",
            "order_status": o["order_status"],
            "items": items,
            "total": o["total"],
            "delivery_address": o["delivery_address"],
            "delivery_phone": o["delivery_phone"]
        })
    return {"orders": orders}


@router.post("/assign_order/{order_id}")
async def assign_order(order_id: str):
    """Assign an available delivery agent to an order."""
    available_agent = await find_available_agent()
    if not available_agent:
        raise HTTPException(status_code=404, detail="No available delivery agents")

    await db.orders.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"delivery_agent_id": str(available_agent["_id"]), "order_status": "arriving"}}
    )

    await db.delivery_agents.update_one(
        {"_id": available_agent["_id"]},
        {"$set": {"status": "on_delivery"}}
    )

    return {"message": f"Order assigned to agent {available_agent['email']}"}

@router.post("/register", response_model=dict)
async def register_delivery_agent(
    agent_data: DeliveryAgentCreate,
    current_user = Depends(get_current_delivery_agent)
):
    """Register as delivery agent with KYC details"""
    # Check if already registered
    existing_agent = await db.delivery_agents.find_one({"user_id": str(current_user["_id"])})
    if existing_agent:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already registered as delivery agent"
        )
    
    now = datetime.now(timezone.utc)
    agent_doc = {
        "user_id": str(current_user["_id"]),
        "vehicle_type": agent_data.vehicle_type.value,
        "vehicle_number": agent_data.vehicle_number,
        "vehicle_registration": agent_data.vehicle_registration,
        "license_number": agent_data.license_number,
        "insurance_document": agent_data.insurance_document,
        "bank_account": agent_data.bank_account,
        "ifsc_code": agent_data.ifsc_code,
        "status": "offline",
        "rating": 0.0,
        "total_deliveries": 0,
        "is_verified": False,
        "created_at": now,
        "updated_at": now
    }
    
    result = await db.delivery_agents.insert_one(agent_doc)
    
    return {
        "id": str(result.inserted_id),
        "message": "Registered successfully. Awaiting KYC verification."
    }

#

@router.get("/profile", response_model=DeliveryAgentResponse)
async def get_agent_profile(current_user = Depends(get_current_delivery_agent)):
    """Get delivery agent profile"""
    agent = await db.delivery_agents.find_one({"user_id": ObjectId(current_user["_id"])})
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent profile not found"
        )
    print(f"Agent data: {agent}")
    return DeliveryAgentResponse(
    id=str(agent["_id"]),
    user_id=str(agent["user_id"]),  
    vehicle_type=agent["vehicle_type"],
    vehicle_number=agent["vehicle_number"],
    vehicle_registration=agent["vehicle_registration"],
    license_number=agent["license_number"],
    status=agent.get("status", "offline"),
    rating=agent.get("rating", 0.0),
    total_deliveries=agent.get("total_deliveries", 0),
    is_verified=agent.get("is_verified", False),
    created_at=agent["created_at"],
    updated_at=agent["updated_at"]
)

@router.put("/profile", response_model=DeliveryAgentResponse)
async def update_agent_profile(
    update_data: DeliveryAgentUpdate,
    current_user = Depends(get_current_delivery_agent)
):
    """Update delivery agent profile"""
    agent = await db.delivery_agents.find_one({"user_id": str(current_user["_id"])})
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent profile not found"
        )
    
    update_dict = {k: v for k, v in update_data.dict().items() if v is not None}
    if update_dict:
        update_dict["updated_at"] = datetime.now(timezone.utc)
        await db.delivery_agents.update_one(
            {"_id": agent["_id"]},
            {"$set": update_dict}
        )
    
    updated_agent = await db.delivery_agents.find_one({"_id": agent["_id"]})
    
    return DeliveryAgentResponse(
        id=str(updated_agent["_id"]),
        user_id=updated_agent["user_id"],
        vehicle_type=updated_agent["vehicle_type"],
        vehicle_number=updated_agent["vehicle_number"],
        vehicle_registration=updated_agent["vehicle_registration"],
        license_number=updated_agent["license_number"],
        status=updated_agent.get("status", "offline"),
        rating=updated_agent.get("rating", 0.0),
        total_deliveries=updated_agent.get("total_deliveries", 0),
        is_verified=updated_agent.get("is_verified", False),
        created_at=updated_agent["created_at"],
        updated_at=updated_agent["updated_at"]
    )

@router.post("/location")
async def update_location(
    location_data: LocationUpdate,
    current_user = Depends(get_current_delivery_agent)
):
    """Update delivery agent's current location"""
    agent = await db.delivery_agents.find_one({"user_id": str(current_user["_id"])})
    
    if not agent:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent profile not found"
        )
    
    await db.delivery_agents.update_one(
        {"_id": agent["_id"]},
        {
            "$set": {
                "current_location": {
                    "lat": location_data.latitude,
                    "lng": location_data.longitude,
                    "accuracy": location_data.accuracy,
                    "timestamp": datetime.now(timezone.utc)
                }
            }
        }
    )
    
    return {"message": "Location updated"}

@router.get("/available-orders", response_model=list[OrderResponse])
async def get_available_orders(
    current_user = Depends(get_current_delivery_agent)
):
    """Get available orders for delivery"""
    agent = await db.delivery_agents.find_one({"user_id": ObjectId(current_user["_id"])})
    
    if not agent or not agent.get("is_verified"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Agent not verified"
        )
    
    orders = await db.orders.find({
        "status": OrderStatus.READY.value,
        "delivery_agent_id": None
    }).limit(10).to_list(10)
    
    return [
        OrderResponse(
            id=str(o["_id"]),
            customer_id=o["customer_id"],
            restaurant_id=o["restaurant_id"],
            items=o["items"],
            subtotal=o["subtotal"],
            delivery_fee=o["delivery_fee"],
            discount=o["discount"],
            total=o["total"],
            status=o["status"],
            delivery_address=o["delivery_address"],
            delivery_phone=o["delivery_phone"],
            payment_method=o["payment_method"],
            created_at=o["created_at"],
            updated_at=o["updated_at"]
        )
        for o in orders
    ]

@router.post("/{order_id}/accept")
async def accept_delivery(
    order_id: str,
    current_user = Depends(get_current_delivery_agent)
):
    """Accept order for delivery"""
    try:
        order = await db.orders.find_one({"_id": ObjectId(order_id)})
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
    
    if order["status"] != OrderStatus.READY.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order not available for delivery"
        )
    
    agent = await db.delivery_agents.find_one({"user_id": str(current_user["_id"])})
    
    await db.orders.update_one(
        {"_id": ObjectId(order_id)},
        {
            "$set": {
                "delivery_agent_id": str(agent["_id"]),
                "status": OrderStatus.ASSIGNED.value,
                "estimated_delivery_time": 30,  # 30 minutes estimated
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    return {"message": "Order accepted for delivery"}

@router.put("/{order_id}/status")
async def update_delivery_status(
    order_id: str,
    status: str,
    current_user = Depends(get_current_delivery_agent)
):
    """Update delivery status"""
    try:
        order = await db.orders.find_one({"_id": ObjectId(order_id)})
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
    
    agent = await db.delivery_agents.find_one({"user_id": str(current_user["_id"])})
    if order.get("delivery_agent_id") != str(agent["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    await db.orders.update_one(
        {"_id": ObjectId(order_id)},
        {
            "$set": {
                "status": status,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    return {"message": f"Delivery status updated to {status}"}

@router.get("/my-deliveries", response_model=list[OrderResponse])
async def get_my_deliveries(
    current_user = Depends(get_current_delivery_agent)
):
    """Get all deliveries for agent"""
    agent = await db.delivery_agents.find_one({"user_id": str(current_user["_id"])})
    
    orders = await db.orders.find({
        "delivery_agent_id": str(agent["_id"])
    }).sort("created_at", -1).to_list(None)
    
    return [
        OrderResponse(
            id=str(o["_id"]),
            customer_id=o["customer_id"],
            restaurant_id=o["restaurant_id"],
            items=o["items"],
            subtotal=o["subtotal"],
            delivery_fee=o["delivery_fee"],
            discount=o["discount"],
            total=o["total"],
            status=o["status"],
            delivery_address=o["delivery_address"],
            delivery_phone=o["delivery_phone"],
            payment_method=o["payment_method"],
            created_at=o["created_at"],
            updated_at=o["updated_at"]
        )
        for o in orders
    ]
