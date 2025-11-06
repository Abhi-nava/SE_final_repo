from fastapi import APIRouter, HTTPException, status, Depends
from models.order import OrderCreate, OrderResponse, OrderStatusUpdate, OrderStatus
from utils.dependencies import get_current_user_http, get_current_restaurant_owner, get_current_customer
from utils.notifications import NotificationService, NotificationType
from utils.payment import PaymentService
from database import db

from bson import ObjectId
from datetime import datetime, timezone, timedelta
from decimal import Decimal

router = APIRouter()

# Delivery fee calculation
DELIVERY_FEE = 50  # Base delivery fee in rupees



@router.get("/details/{order_id}")
async def get_order_details(
    order_id: str):
    """Get single order details for customer"""
    print(f"\n{'='*60}")
    print(f"{'='*60}\n")
    
    try:
        order = await db.orders.find_one({"_id": ObjectId(order_id)})
        print(f"[DEBUG] Order found: {order is not None}")
        
        if not order:
            print(f"[DEBUG] Order not found in database")
            raise HTTPException(status_code=404, detail="Order not found")
        
        print(f"[DEBUG] Order customer_id from DB: {order.get('customer_id')} (type: {type(order.get('customer_id'))})")

        
        # Get restaurant data
        restaurant = None
        try:
            restaurant = await db.restaurants.find_one(
                {"_id": ObjectId(order["restaurant_id"])},
                {"name": 1, "image_url": 1}
            )
            print(f"[DEBUG] Restaurant found: {restaurant is not None}")
        except Exception as e:
            print(f"[DEBUG] Error fetching restaurant: {str(e)}")
        
        response_data = {
            "id": str(order["_id"]),
            "customer_id": str(order.get("customer_id", "")),
            "restaurant_id": str(order.get("restaurant_id", "")),
            "restaurant": {
                "name": restaurant["name"] if restaurant else "",
                "image": restaurant.get("image_url") if restaurant else None
            } if restaurant else None,
            "items": order.get("items", []),
            "subtotal": float(order.get("subtotal", 0)),
            "delivery_fee": float(order.get("delivery_fee", 0)),
            "discount": float(order.get("discount", 0)),
            "total": float(order.get("total", 0)),
            "status": str(order.get("status", "")),
            "order_status": str(order.get("order_status", "preparing")),
            "delivery_address": str(order.get("delivery_address", "")),
            "delivery_phone": str(order.get("delivery_phone", "")),
            "payment_method": str(order.get("payment_method", "")),
            "delivery_agent_id": str(order.get("delivery_agent_id")) if order.get("delivery_agent_id") else None,
            "estimated_delivery_time": int(order.get("estimated_delivery_time")) if order.get("estimated_delivery_time") else None,
            "created_at": order.get("created_at"),
            "updated_at": order.get("updated_at")
        }
        
        print(f"[DEBUG] Returning response successfully")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[DEBUG] UNEXPECTED ERROR: {str(e)}")
        print(f"[DEBUG] Error type: {type(e)}")
        import traceback
        print(f"[DEBUG] Traceback:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Customer Routes
@router.post("/create")
async def create_order(
    payload: dict,
    user: dict = Depends(get_current_user_http)
):
    """
    Create an order:
    ✅ Validate payload
    ✅ Update menu_items daily_count (string → int → string)
    ✅ Save order in DB
    ✅ Set status to 'paid'
    """

    required = [
        "restaurant_id", "items", "delivery_address",
        "delivery_phone", "payment_method", "subtotal",
        "delivery_fee", "discount", "total"
    ]

    for f in required:
        if f not in payload:
            raise HTTPException(status_code=400, detail=f"Missing field: {f}")

    restaurant_id = payload["restaurant_id"]
    items = payload["items"]

    # ✅ Validate restaurant
    restaurant = await db["restaurants"].find_one({"_id": ObjectId(restaurant_id)})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    processed_items = []

    # ✅ Handle daily_count update
    for item in items:

        # Accept menuItemId (frontend) or menu_item_id (backend normalized)
        menu_item_id = item.get("menuItemId") or item.get("menu_item_id")
        if not menu_item_id:
            raise HTTPException(status_code=400, detail="Missing menuItemId in item")

        qty = int(item.get("quantity", 0))
        if qty <= 0:
            raise HTTPException(status_code=400, detail="Invalid quantity")

        menu_item = await db["menu_items"].find_one({"_id": ObjectId(menu_item_id)})
        if not menu_item:
            raise HTTPException(status_code=404, detail=f"Menu item {menu_item_id} not found")

        # ✅ Convert daily_count to int safely
        try:
            current_count = int(menu_item.get("daily_count", "0"))
        except:
            current_count = 0

        if current_count < qty:
            raise HTTPException(
                status_code=400,
                detail=f"{menu_item['name']} is sold out (remaining: {current_count})"
            )

        # ✅ Deduct count
        new_count = max(current_count - qty, 0)

        await db["menu_items"].update_one(
            {"_id": ObjectId(menu_item_id)},
            {"$set": {"daily_count": str(new_count)}}  # Store back as string
        )

        processed_items.append({
            "menu_item_id": menu_item_id,
            "name": menu_item["name"],
            "quantity": qty,
            "price": menu_item["price"]
        })

    # ✅ Create order document
    order_doc = {
        "customer_id": str(user["_id"]),
        "restaurant_id": restaurant_id,
        "items": processed_items,
        "subtotal": payload["subtotal"],
        "delivery_fee": payload["delivery_fee"],
        "discount": payload["discount"],
        "total": payload["total"],
        "delivery_address": payload["delivery_address"],
        "delivery_phone": payload["delivery_phone"],
        "payment_method": payload["payment_method"],

        "status": "paid",
        "order_status": "preparing",

        "delivery_agent_id": None,
        "estimated_delivery_time": 45,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
    }

    # ✅ Insert to DB
    result = await db["orders"].insert_one(order_doc)
    order_doc["_id"] = str(result.inserted_id)

    return {
        "id": order_doc["_id"],
        "message": "Order placed successfully",
        "status": "paid"
    }

@router.get("/my-orders", response_model=list[OrderResponse])
async def get_my_orders(
    current_user = Depends(get_current_user_http),
    skip: int = 0,
    limit: int = 20
):
    # fetch raw orders for this customer (customer_id stored as string)
    orders = await db.orders.find({
        "customer_id": str(current_user["_id"])
    }).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)

    response_list = []

    for o in orders:
        # safe lookups / fallbacks
        try:
            restaurant = await db.restaurants.find_one(
                {"_id": ObjectId(o.get("restaurant_id"))},
                {"name": 1, "image_url": 1}
            )
        except Exception:
            restaurant = None

        # normalize values so Pydantic gets only expected types
        customer_id = o.get("customer_id") or ""
        restaurant_id = o.get("restaurant_id") or ""
        items = o.get("items", [])
        subtotal = o.get("subtotal", 0.0) or 0.0
        delivery_fee = o.get("delivery_fee", 0.0) or 0.0
        discount = o.get("discount", 0.0) or 0.0
        total = o.get("total", 0.0) or 0.0
        status = o.get("status", "")
        delivery_address = o.get("delivery_address") or ""            # <<< important fallback
        delivery_phone = o.get("delivery_phone") or ""
        payment_method = o.get("payment_method") or ""
        delivery_agent_id = o.get("delivery_agent_id")
        estimated_delivery_time = o.get("estimated_delivery_time")
        created_at = o.get("created_at")
        updated_at = o.get("updated_at")

        response_list.append(
            OrderResponse(
                id=str(o["_id"]),
                customer_id=str(customer_id),
                restaurant_id=str(restaurant_id),
                restaurant={
                    "name": restaurant["name"] if restaurant and "name" in restaurant else "",
                    "image": restaurant.get("image_url") if restaurant and restaurant.get("image_url") else None
                } if restaurant else None,
                items=items,
                subtotal=float(subtotal),
                delivery_fee=float(delivery_fee),
                discount=float(discount),
                total=float(total),
                status=str(status),
                delivery_address=str(delivery_address),     # <<< safe string
                delivery_phone=str(delivery_phone),
                payment_method=str(payment_method),
                delivery_agent_id=str(delivery_agent_id) if delivery_agent_id else None,
                estimated_delivery_time=int(estimated_delivery_time) if estimated_delivery_time is not None else None,
                created_at=created_at,
                updated_at=updated_at
            )
        )

    return response_list


