import pytest
from pydantic import ValidationError
import sys
import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

BACKEND_DIR = os.path.join(REPO_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from routes.coupons import (
    CouponResponse,
    CouponValidationRequest,
    CouponValidationResponse
)


def test_coupon_response_valid():
    """Test CouponResponse with all fields"""
    coupon = CouponResponse(
        id="507f1f77bcf86cd799439011",
        code="SAVE20",
        description="Save 20% on orders",
        minOrder=100.0,
        discountType="percentage",
        discountValue=20.0,
        maxDiscount=50.0
    )
    assert coupon.id == "507f1f77bcf86cd799439011"
    assert coupon.code == "SAVE20"
    assert coupon.description == "Save 20% on orders"
    assert coupon.minOrder == 100.0
    assert coupon.discountType == "percentage"
    assert coupon.discountValue == 20.0
    assert coupon.maxDiscount == 50.0


def test_coupon_response_without_max_discount():
    """Test CouponResponse without optional maxDiscount"""
    coupon = CouponResponse(
        id="507f1f77bcf86cd799439011",
        code="FLAT50",
        description="Flat ₹50 off",
        minOrder=200.0,
        discountType="flat",
        discountValue=50.0
    )
    assert coupon.maxDiscount is None


def test_coupon_validation_request_valid():
    """Test CouponValidationRequest with valid data"""
    request = CouponValidationRequest(
        code="SAVE20",
        orderTotal=150.0
    )
    assert request.code == "SAVE20"
    assert request.orderTotal == 150.0


def test_coupon_validation_request_negative_order_total():
    """Test CouponValidationRequest with negative order total"""
    # Pydantic doesn't validate negative numbers by default for float
    # But we can test that it accepts it (validation should be in business logic)
    request = CouponValidationRequest(
        code="SAVE20",
        orderTotal=-10.0
    )
    assert request.orderTotal == -10.0


def test_coupon_validation_request_empty_code():
    """Test CouponValidationRequest with empty code"""
    request = CouponValidationRequest(
        code="",
        orderTotal=100.0
    )
    assert request.code == ""


def test_coupon_validation_response_valid():
    """Test CouponValidationResponse with valid coupon"""
    coupon_data = CouponResponse(
        id="507f1f77bcf86cd799439011",
        code="SAVE20",
        description="Save 20%",
        minOrder=100.0,
        discountType="percentage",
        discountValue=20.0
    )
    response = CouponValidationResponse(
        valid=True,
        coupon=coupon_data,
        discount=30.0,
        message="Coupon applied successfully"
    )
    assert response.valid is True
    assert response.coupon is not None
    assert response.coupon.code == "SAVE20"
    assert response.discount == 30.0
    assert response.message == "Coupon applied successfully"


def test_coupon_validation_response_invalid():
    """Test CouponValidationResponse for invalid coupon"""
    response = CouponValidationResponse(
        valid=False,
        coupon=None,
        discount=0.0,
        message="Coupon code not found"
    )
    assert response.valid is False
    assert response.coupon is None
    assert response.discount == 0.0
    assert response.message == "Coupon code not found"


def test_coupon_validation_response_defaults():
    """Test CouponValidationResponse with default values"""
    response = CouponValidationResponse(valid=False)
    assert response.valid is False
    assert response.coupon is None
    assert response.discount == 0.0
    assert response.message == ""


def test_coupon_response_missing_required_fields():
    """Test CouponResponse validation with missing required fields"""
    with pytest.raises(ValidationError):
        CouponResponse(
            code="SAVE20",
            # Missing id, description, minOrder, discountType, discountValue
        )


def test_coupon_validation_request_missing_fields():
    """Test CouponValidationRequest validation with missing required fields"""
    with pytest.raises(ValidationError):
        CouponValidationRequest(
            code="SAVE20"
            # Missing orderTotal
        )


def test_coupon_response_discount_types():
    """Test CouponResponse with different discount types"""
    # Percentage discount
    coupon_percent = CouponResponse(
        id="1",
        code="PERCENT20",
        description="20% off",
        minOrder=100.0,
        discountType="percentage",
        discountValue=20.0
    )
    assert coupon_percent.discountType == "percentage"
    
    # Flat discount
    coupon_flat = CouponResponse(
        id="2",
        code="FLAT50",
        description="₹50 off",
        minOrder=200.0,
        discountType="flat",
        discountValue=50.0
    )
    assert coupon_flat.discountType == "flat"

