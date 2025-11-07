from fastapi import APIRouter, HTTPException, status, Depends
from models.order import OrderCreate, OrderResponse, OrderStatusUpdate, OrderStatus
from utils.dependencies import get_current_user_http, get_current_restaurant_owner, get_current_customer
from database import db

from bson import ObjectId
from datetime import datetime, timezone, timedelta
from decimal import Decimal

router = APIRouter()

# Delivery fee calculation
DELIVERY_FEE = 50  # Base delivery fee in rupees


# @router.get("/details/{order_id}")
# async def test_details_with_param(order_id:str,current_user=Depends(get_current_customer)):
#     print(current_user)
#     """Test if /details/ path works at all"""
#     print("[TEST] Details test route hit!")
#     return {"message": "Details path works!", "path": "/details/test"}


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

        # order_customer_id = str(order.get("customer_id", ""))
        # current_user_id = current_user.get("_id")  # Already a string from dependency
        
        # print(f"[DEBUG] Order customer_id (string): '{order_customer_id}'")
        # print(f"[DEBUG] Current user _id (string): '{current_user_id}'")
        # print(f"[DEBUG] Are they equal? {order_customer_id == current_user_id}")
        
        # # Verify ownership
        # if order_customer_id != current_user_id:
        #     print(f"[DEBUG] AUTHORIZATION FAILED!")
        #     print(f"[DEBUG] Order belongs to: {order_customer_id}")
        #     print(f"[DEBUG] Current user is: {current_user_id}")
        #     raise HTTPException(
        #         status_code=403, 
        #         detail=f"Not authorized to view this order"
        #     )
        
        # print(f"[DEBUG] Authorization successful!")
        
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



# @router.get("/my-orders", response_model=list[OrderResponse])
# async def get_my_orders(
#     current_user = Depends(get_current_user_http),
#     skip: int = 0,
#     limit: int = 20
# ):
#     orders = await db.orders.find({
#         "customer_id": str(current_user["_id"])
#     }).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)

#     response_list = []

#     for o in orders:
#         restaurant = await db.restaurants.find_one(
#             {"_id": ObjectId(o["restaurant_id"])},
#             {"name": 1, "image_url": 1}
#         )

#         response_list.append(
#             OrderResponse(
#                 id=str(o["_id"]),
#                 customer_id=o["customer_id"],
#                 restaurant_id=o["restaurant_id"],
#                 restaurant={
#                     "name": restaurant["name"] if restaurant else "",
#                     "image": restaurant.get("image_url") if restaurant else None
#                 },
#                 items=o["items"],
#                 subtotal=o["subtotal"],
#                 delivery_fee=o["delivery_fee"],
#                 discount=o["discount"],
#                 total=o["total"],
#                 status=o["status"],
#                 delivery_address=o["delivery_address"],
#                 delivery_phone=o["delivery_phone"],
#                 payment_method=o["payment_method"],
#                 delivery_agent_id=o.get("delivery_agent_id"),
#                 estimated_delivery_time=o.get("estimated_delivery_time"),
#                 created_at=o["created_at"],
#                 updated_at=o["updated_at"]
#             )
#         )

#     return response_list



# Restaurant Routes

@router.get("/dashboard-summary")
async def restaurant_dashboard_summary(current_user = Depends(get_current_restaurant_owner)):
    restaurant = await db.restaurants.find_one({"owner_id": str(current_user["_id"])})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    restaurant_id = str(restaurant["_id"])

    # Load orders
    orders = await db.orders.find({"restaurant_id": restaurant_id}).to_list(None)
    total_orders = len(orders)
    pending_orders = len([o for o in orders if o["status"] not in ["delivered", "cancelled"]])
    completed_today = len([o for o in orders if o["status"] == "delivered"])
    revenue_today = sum([o["total"] for o in orders if o["status"] == "delivered"])

    # Ratings aggregate
    pipeline = [
        {"$match": {"restaurant_id": restaurant_id}},
        {"$group": {
            "_id": "$restaurant_id",
            "count": {"$sum": 1},
            "avg_restaurant": {"$avg": "$restaurant_rating"},
            "avg_delivery": {"$avg": "$delivery_rating"},
            "avg_food_quality": {"$avg": "$food_quality"},
            "avg_delivery_speed": {"$avg": "$delivery_speed"},
            "avg_packaging_quality": {"$avg": "$packaging_quality"},
        }}
    ]

    ratings = await db.ratings.aggregate(pipeline).to_list(1)
    if ratings:
        r = ratings[0]
        ratings_summary = {
            "count": r["count"],
            "avg_restaurant": round(r["avg_restaurant"], 2),
            "avg_delivery": round(r["avg_delivery"], 2),
            "avg_food_quality": round(r["avg_food_quality"], 2),
            "avg_delivery_speed": round(r["avg_delivery_speed"], 2),
            "avg_packaging_quality": round(r["avg_packaging_quality"], 2),
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
            "revenue_today": revenue_today
        },
        "ratings": ratings_summary
    }


# --- NEW: ratings summary for a restaurant (avg scores + counts) ---
@router.get("/restaurant/ratings/summary")
async def get_ratings_summary(current_user = Depends(get_current_restaurant_owner)):
    restaurant = await db.restaurants.find_one({"owner_id": str(current_user["_id"])})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    pipeline = [
        {"$match": {"restaurant_id": str(restaurant["_id"])}},
        {"$group": {
            "_id": "$restaurant_id",
            "count": {"$sum": 1},
            "avg_restaurant": {"$avg": "$restaurant_rating"},
            "avg_delivery": {"$avg": "$delivery_rating"},
            "avg_food_quality": {"$avg": "$food_quality"},
            "avg_delivery_speed": {"$avg": "$delivery_speed"},
            "avg_packaging_quality": {"$avg": "$packaging_quality"},
        }}
    ]
    agg = await db.ratings.aggregate(pipeline).to_list(1)
    if not agg:
        return {"count": 0, "avg_restaurant": 0, "avg_delivery": 0, "avg_food_quality": 0, "avg_delivery_speed": 0, "avg_packaging_quality": 0}
    x = agg[0]
    return {
        "count": x["count"],
        "avg_restaurant": round(x["avg_restaurant"], 2),
        "avg_delivery": round(x["avg_delivery"], 2),
        "avg_food_quality": round(x["avg_food_quality"], 2),
        "avg_delivery_speed": round(x["avg_delivery_speed"], 2),
        "avg_packaging_quality": round(x["avg_packaging_quality"], 2),
    }




# @router.get("/restaurant-ratings")
# async def get_restaurant_ratings(current_user = Depends(get_current_restaurant_owner)):
#     restaurant = await db.restaurants.find_one({"owner_id": str(current_user["_id"])})
#     if not restaurant:
#         raise HTTPException(status_code=404, detail="Restaurant not found")

#     ratings = await db.ratings.find({
#         "restaurant_id": str(restaurant["_id"])
#     }).to_list(None)

#     return ratings



# @router.post("/{order_id}/process-payment", response_model=dict)
# async def process_payment(
#     order_id: str,
#     payment_details: dict,
#     current_user = Depends(get_current_user_http)
# ):
#     """Process payment for order"""
#     try:
#         order = await db.orders.find_one({"_id": ObjectId(order_id)})
#     except:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Order not found"
#         )
    
#     if not order:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Order not found"
#         )
    
#     if order["customer_id"] != str(current_user["_id"]):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized"
#         )
    
#     payment_result = await PaymentService.process_payment(
#         payment_id=order.get("payment_id"),
#         payment_method=order["payment_method"],
#         payment_details=payment_details
#     )
    
#     if payment_result["status"] in ["success", "pending"]:
#         await db.orders.update_one(
#             {"_id": ObjectId(order_id)},
#             {
#                 "$set": {
#                     "status": OrderStatus.CONFIRMED.value,
#                     "updated_at": datetime.now(timezone.utc)
#                 }
#             }
#         )
        
#         await NotificationService.send_notification(
#             user_id=order["customer_id"],
#             notification_type=NotificationType.ORDER_CONFIRMED,
#             title="Order Confirmed",
#             message="Your order has been confirmed by the restaurant",
#             data={"order_id": order_id}
#         )
        
#         return {
#             "status": "success",
#             "message": "Payment processed successfully",
#             "order_id": order_id
#         }
#     else:
#         return {
#             "status": "failed",
#             "message": "Payment processing failed",
#             "error": payment_result.get("error")
#         }

# # @router.get("/{order_id}", response_model=OrderResponse)
# # async def get_order(order_id: str, current_user = Depends(get_current_user_http)):
# #     """Get order details"""
# #     try:
# #         order = await db.orders.find_one({"_id": ObjectId(order_id)})
# #     except:
# #         raise HTTPException(
# #             status_code=status.HTTP_404_NOT_FOUND,
# #             detail="Order not found"
# #         )
    
# #     if not order:
# #         raise HTTPException(
# #             status_code=status.HTTP_404_NOT_FOUND,
# #             detail="Order not found"
# #         )
    
# #     # Verify ownership
# #     if order["customer_id"] != str(current_user["_id"]):
# #         raise HTTPException(
# #             status_code=status.HTTP_403_FORBIDDEN,
# #             detail="Not authorized to view this order"
# #         )
    
# #     return OrderResponse(
# #         id=str(order["_id"]),
# #         customer_id=order["customer_id"],
# #         restaurant_id=order["restaurant_id"],
# #         items=order["items"],
# #         subtotal=order["subtotal"],
# #         delivery_fee=order["delivery_fee"],
# #         discount=order["discount"],
# #         total=order["total"],
# #         status=order["status"],
# #         delivery_address=order["delivery_address"],
# #         delivery_phone=order["delivery_phone"],
# #         payment_method=order["payment_method"],
# #         delivery_agent_id=order.get("delivery_agent_id"),
# #         estimated_delivery_time=order.get("estimated_delivery_time"),
# #         created_at=order["created_at"],
# #         updated_at=order["updated_at"]
# #     )


# @router.post("/{order_id}/cancel")
# async def cancel_order(
#     order_id: str,
#     current_user = Depends(get_current_user_http)
# ):
#     """Cancel order before preparation"""
#     try:
#         order = await db.orders.find_one({"_id": ObjectId(order_id)})
#     except:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Order not found"
#         )
    
#     if not order:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Order not found"
#         )
    
#     if order["customer_id"] != str(current_user["_id"]):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Not authorized"
#         )
    
#     if order["status"] not in [OrderStatus.PENDING.value, OrderStatus.CONFIRMED.value]:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Order cannot be cancelled at this stage"
#         )
    
#     await db.orders.update_one(
#         {"_id": ObjectId(order_id)},
#         {
#             "$set": {
#                 "status": OrderStatus.CANCELLED.value,
#                 "updated_at": datetime.now(timezone.utc)
#             }
#         }
#     )
    
#     await NotificationService.send_notification(
#         user_id=order["customer_id"],
#         notification_type=NotificationType.ORDER_CANCELLED,
#         title="Order Cancelled",
#         message="Your order has been cancelled",
#         data={"order_id": order_id}
#     )
    
#     if order.get("payment_id"):
#         await PaymentService.refund_payment(
#             payment_id=order["payment_id"],
#             reason="Order cancelled by customer"
#         )
    
#     return {"message": "Order cancelled successfully"}

def safe_str(val):
    if val is None:
        return ""
    if isinstance(val, ObjectId):
        return str(val)
    return str(val)

# @router.get("/restaurant", response_model=list[OrderResponse])
# async def get_restaurant_orders1(current_user = Depends(get_current_restaurant_owner)):
#     restaurant = await db.restaurants.find_one({"owner_id": ObjectId(current_user["_id"])})
#     if not restaurant:
#         raise HTTPException(status_code=404, detail="Restaurant not found")

#     orders = await db.orders.find({
#         "restaurant_id": str(restaurant["_id"])
#     }).sort("created_at", -1).to_list(None)

#     response = []

#     for o in orders:
#         # Normalize problematic fields
#         customer_id = safe_str(o.get("customer_id"))
#         restaurant_id = safe_str(o.get("restaurant_id"))
#         delivery_address = o.get("delivery_address") or "Not provided"
#         delivery_phone = o.get("delivery_phone") or ""
#         payment_method = o.get("payment_method") or "unknown"

#         response.append(
#             OrderResponse(
#                 id=str(o["_id"]),
#                 customer_id=customer_id,
#                 restaurant_id=restaurant_id,
#                 restaurant=None,
#                 items=o.get("items", []),
#                 subtotal=o.get("subtotal", 0),
#                 delivery_fee=o.get("delivery_fee", 0),
#                 discount=o.get("discount", 0),
#                 total=o.get("total", 0),
#                 status=o.get("status", "unknown"),
#                 delivery_address=delivery_address,
#                 delivery_phone=delivery_phone,
#                 payment_method=payment_method,
#                 delivery_agent_id=safe_str(o.get("delivery_agent_id")),
#                 estimated_delivery_time=o.get("estimated_delivery_time"),
#                 created_at=o.get("created_at"),
#                 updated_at=o.get("updated_at")
#             )
#         )

#     return response


@router.get("/restaurant/orders")
async def get_restaurant_orders(current_user = Depends(get_current_restaurant_owner)):
    """Fetch all orders belonging to the restaurant"""
    restaurant = await db.restaurants.find_one({"owner_id": ObjectId(current_user["_id"])})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    orders = await db.orders.find({"restaurant_id": str(restaurant["_id"])}).sort("created_at", -1).to_list(None)

    return [
        {
            "id": str(o["_id"]),
            "order_status": o.get("order_status", "preparing"),
            "total": o["total"],
            "items": o["items"],
            "delivery_address": o.get("delivery_address", ""),
            "delivery_phone": o.get("delivery_phone", ""),
            "created_at": o["created_at"],
            "delivery_agent_id": o.get("delivery_agent_id")
        }
        for o in orders
    ]

@router.put("/restaurant/order/{order_id}/status")
async def update_order_statu1(
    order_id: str,
    payload: dict,
    current_user = Depends(get_current_restaurant_owner)
):
    new_status = payload.get("order_status")
    if not new_status:
        raise HTTPException(status_code=400, detail="order_status required")

    allowed_statuses = ["preparing", "searching", "arriving", "in-transit", "delivered"]
    if new_status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid order_status. Must be one of {allowed_statuses}")

    restaurant = await db.restaurants.find_one({"owner_id": ObjectId(current_user["_id"])})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    order = await db.orders.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if str(order["restaurant_id"]) != str(restaurant["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized")

    current_status = order.get("order_status", "preparing")

    # ✅ Enforce allowed transitions
    transitions = {
        "preparing": ["searching"],
        "searching": ["arriving"],  # after assignment
        "arriving": ["in-transit"],
        "in-transit": ["delivered"],
        "delivered": []
    }

    if new_status not in transitions.get(current_status, []):
        raise HTTPException(
            status_code=400,
            detail=f"Cannot transition from {current_status} to {new_status}"
        )

    await db.orders.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"order_status": new_status, "updated_at": datetime.utcnow()}}
    )

    return {"message": f"Order status updated to {new_status}"}


@router.put("/restaurant/order/{order_id}/status")
async def update_order_status(
    order_id: str,
    payload: dict,
    current_user = Depends(get_current_restaurant_owner)
):
    """Update order_status with extended logic"""
    new_status = payload.get("order_status")
    if not new_status:
        raise HTTPException(status_code=400, detail="order_status required")

    valid_statuses = ["preparing", "searching", "arriving", "waiting", "in-transit", "delivered"]
    if new_status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid order_status. Must be one of {valid_statuses}")

    restaurant = await db.restaurants.find_one({"owner_id": ObjectId(current_user["_id"])})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    order = await db.orders.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if str(order["restaurant_id"]) != str(restaurant["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized")

    await db.orders.update_one(
        {"_id": ObjectId(order_id)},
        {"$set": {"order_status": new_status, "updated_at": datetime.utcnow()}}
    )

    return {"message": f"Order status updated to {new_status}"}

@router.put("/{order_id}/status", response_model=dict)
async def update_order_status(
    order_id: str,
    status_update: OrderStatusUpdate,
    current_user = Depends(get_current_restaurant_owner)
):
    """Update order status by restaurant"""
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
    
    restaurant = await db.restaurants.find_one({"owner_id": ObjectId(current_user["_id"])})
    if not restaurant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Restaurant not found"
        )
    if order["restaurant_id"] != ObjectId(restaurant["_id"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    await db.orders.update_one(
        {"_id": ObjectId(order_id)},
        {
            "$set": {
                "status": status_update.status.value,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    await NotificationService.notify_order_status_change(
        order_id=order_id,
        new_status=status_update.status.value
    )
    
    return {"message": f"Order status updated to {status_update.status.value}"}



# --- NEW: list verified agents for assignment (used by restaurant UI) ---
@router.get("/restaurant/agents")
async def list_verified_agents(current_user = Depends(get_current_restaurant_owner)):
    restaurant = await db.restaurants.find_one({"owner_id": ObjectId(current_user["_id"])})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    agents = await db.delivery_agents.find({"is_verified": True}).to_list(None)

    def safe_str(val):
        from bson import ObjectId
        if isinstance(val, ObjectId):
            return str(val)
        return val

    result = []
    for a in agents:
        result.append({
            "id": str(a["_id"]),
            "user_id": safe_str(a.get("user_id")),
            "name": a.get("name", "Unknown Agent"),
            "rating": float(a.get("rating", 0.0)),
            "vehicle_number": a.get("vehicle_number", "N/A")
        })

    return result


# @router.post("/{order_id}/assign-agent")
# async def assign_delivery_agent(
#     order_id: str,
#     body: dict,
#     current_user = Depends(get_current_restaurant_owner)
# ):
#     from bson import ObjectId

#     agent_id = body.get("delivery_agent_id")
#     if not agent_id:
#         raise HTTPException(status_code=400, detail="delivery_agent_id is required")

#     # Fetch the order
#     order = await db.orders.find_one({"_id": ObjectId(order_id)})
#     if not order:
#         raise HTTPException(status_code=404, detail="Order not found")

#     # ✅ Fetch restaurant owned by the current user
#     restaurant = await db.restaurants.find_one({"owner_id": ObjectId(current_user["_id"])})
#     if not restaurant:
#         raise HTTPException(status_code=404, detail="Restaurant not found")

#     # ✅ Ownership check (string comparison)
#     if str(order["restaurant_id"]) != str(restaurant["_id"]):
#         raise HTTPException(status_code=403, detail="Not authorized for this order")

#     # Verify that the agent exists and is verified
#     agent = await db.delivery_agents.find_one({
#         "_id": ObjectId(agent_id),
#         "is_verified": True
#     })
#     if not agent:
#         raise HTTPException(status_code=404, detail="Delivery agent not found or not verified")

#     # ✅ Assign agent & update order status to "searching"
#     await db.orders.update_one(
#         {"_id": ObjectId(order_id)},
#         {
#             "$set": {
#                 "delivery_agent_id": str(agent["_id"]),
#                 "order_status": "searching",
#                 "status": "assigned",
#                 "estimated_delivery_time": order.get("estimated_delivery_time", 45),
#                 "updated_at": datetime.utcnow(),
#             }
#         }
#     )

#     return {
#         "message": f"Delivery agent assigned and order set to 'searching'",
#         "order_id": order_id,
#         "delivery_agent_id": str(agent["_id"]),
#     }


# # --- NEW: restaurant-side order details (includes customer basics) ---
@router.get("/restaurant/{order_id}")
async def get_restaurant_order_details(order_id: str, current_user = Depends(get_current_restaurant_owner)):
    try:
        order = await db.orders.find_one({"_id": ObjectId(order_id)})
    except:
        raise HTTPException(status_code=404, detail="Order not found")
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    restaurant = await db.restaurants.find_one({"_id": ObjectId(order["restaurant_id"])})
    if not restaurant or restaurant["owner_id"] != ObjectId(current_user["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized")

    customer = await db.users.find_one({"_id": ObjectId(order["customer_id"])}, {"name": 1, "phone": 1})
    return {
        **{k: v for k, v in order.items() if k != "_id"},
        "id": str(order["_id"]),
        "customer": {"name": customer.get("name",""), "phone": customer.get("phone","")} if customer else None
    }

@router.post("/{order_id}/assign-agent")
async def assign_delivery_agent(
    order_id: str,
    body: dict,
    current_user = Depends(get_current_restaurant_owner)
):
    """Assign agent and automatically move to 'arriving'"""
    agent_id = body.get("delivery_agent_id")
    if not agent_id:
        raise HTTPException(status_code=400, detail="delivery_agent_id required")

    restaurant = await db.restaurants.find_one({"owner_id": ObjectId(current_user["_id"])})
    if not restaurant:
        raise HTTPException(status_code=404, detail="Restaurant not found")

    order = await db.orders.find_one({"_id": ObjectId(order_id)})
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if str(order["restaurant_id"]) != str(restaurant["_id"]):
        raise HTTPException(status_code=403, detail="Not authorized")

    agent = await db.delivery_agents.find_one({"_id": ObjectId(agent_id), "is_verified": True})
    if not agent:
        raise HTTPException(status_code=404, detail="Delivery agent not found")

    await db.orders.update_one(
        {"_id": ObjectId(order_id)},
        {
            "$set": {
                "delivery_agent_id": str(agent["_id"]),
                "order_status": "arriving",  # 🚀 move directly to arriving
                "updated_at": datetime.utcnow(),
            }
        }
    )

    return {"message": "Agent assigned, driver arriving", "order_status": "arriving"}


