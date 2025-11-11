from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from database import db
from typing import Optional
from bson import ObjectId

router = APIRouter()

class CouponResponse(BaseModel):
    id: str
    code: str
    description: str
    minOrder: float
    discountType: str
    discountValue: float
    maxDiscount: Optional[float] = None

class CouponValidationRequest(BaseModel):
    code: str
    orderTotal: float

class CouponValidationResponse(BaseModel):
    valid: bool
    coupon: Optional[CouponResponse] = None
    discount: float = 0
    message: str = ""

@router.post("/validate", response_model=CouponValidationResponse)
async def validate_coupon(request: CouponValidationRequest):
    """Validate a coupon code and calculate discount"""
    
    # Find coupon by code
    coupon = await db.coupons.find_one({"code": request.code.upper()})
    
    if not coupon:
        return CouponValidationResponse(
            valid=False,
            message="Coupon code not found"
        )
    
    # Check if order meets minimum requirement
    if request.orderTotal < coupon.get("minOrder", 0):
        min_order = coupon.get("minOrder", 0)
        return CouponValidationResponse(
            valid=False,
            message=f"Order total must be at least ₹{min_order} to use this coupon"
        )
    
    # Calculate discount
    discount_type = coupon.get("discountType", "flat")
    discount_value = coupon.get("discountValue", 0)
    
    if discount_type == "percentage":
        # Calculate percentage discount
        discount = (request.orderTotal * discount_value) / 100
        # Cap at maxDiscount if specified
        max_discount = coupon.get("maxDiscount")
        if max_discount and discount > max_discount:
            discount = max_discount
    else:  # flat discount
        discount = discount_value
    
    return CouponValidationResponse(
        valid=True,
        coupon=CouponResponse(
            id=str(coupon["_id"]),
            code=coupon["code"],
            description=coupon.get("description", ""),
            minOrder=coupon.get("minOrder", 0),
            discountType=discount_type,
            discountValue=discount_value,
            maxDiscount=coupon.get("maxDiscount")
        ),
        discount=discount,
        message="Coupon applied successfully"
    )

@router.get("/available")
async def get_available_coupons():
    """Get all available coupons (for promotional display)"""
    coupons = await db.coupons.find().to_list(None)
    
    return [
        {
            "id": str(c["_id"]),
            "code": c["code"],
            "description": c.get("description", ""),
            "minOrder": c.get("minOrder", 0),
            "discountType": c.get("discountType", "flat"),
            "discountValue": c.get("discountValue", 0),
            "maxDiscount": c.get("maxDiscount")
        }
        for c in coupons
    ]
