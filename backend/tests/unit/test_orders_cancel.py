"""
Unit tests for order cancellation functionality.
Tests the business logic with mocked database operations.
"""
import pytest
from unittest.mock import MagicMock
from fastapi import HTTPException
from bson import ObjectId
from datetime import datetime
from routes.orders import cancel_order


@pytest.fixture
def mock_user():
    """Mock authenticated user"""
    return {
        "_id": "507f1f77bcf86cd799439011",
        "email": "test@example.com",
        "name": "Test User",
        "role": "customer"
    }


@pytest.fixture
def mock_other_user():
    """Mock different user for authorization tests"""
    return {
        "_id": "507f1f77bcf86cd799439012",
        "email": "other@example.com",
        "name": "Other User",
        "role": "customer"
    }


@pytest.fixture
def mock_order_paid():
    """Mock order with 'paid' status"""
    return {
        "_id": ObjectId("507f1f77bcf86cd799439020"),
        "customer_id": "507f1f77bcf86cd799439011",
        "restaurant_id": "507f1f77bcf86cd799439030",
        "items": [{"menu_item_id": "item1", "quantity": 2, "price": 100}],
        "subtotal": 200.0,
        "delivery_fee": 50.0,
        "discount": 0.0,
        "total": 250.0,
        "status": "paid",
        "order_status": "preparing",
        "delivery_address": "123 Test St",
        "delivery_phone": "1234567890",
        "payment_method": "card",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


@pytest.fixture
def mock_order_pending():
    """Mock order with 'pending' status"""
    return {
        "_id": ObjectId("507f1f77bcf86cd799439021"),
        "customer_id": "507f1f77bcf86cd799439011",
        "restaurant_id": "507f1f77bcf86cd799439030",
        "items": [{"menu_item_id": "item1", "quantity": 2, "price": 100}],
        "subtotal": 200.0,
        "delivery_fee": 50.0,
        "discount": 0.0,
        "total": 250.0,
        "status": "pending",
        "order_status": "preparing",
        "delivery_address": "123 Test St",
        "delivery_phone": "1234567890",
        "payment_method": "card",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


@pytest.fixture
def mock_order_confirmed():
    """Mock order with 'confirmed' status"""
    return {
        "_id": ObjectId("507f1f77bcf86cd799439022"),
        "customer_id": "507f1f77bcf86cd799439011",
        "restaurant_id": "507f1f77bcf86cd799439030",
        "items": [{"menu_item_id": "item1", "quantity": 2, "price": 100}],
        "subtotal": 200.0,
        "delivery_fee": 50.0,
        "discount": 0.0,
        "total": 250.0,
        "status": "confirmed",
        "order_status": "preparing",
        "delivery_address": "123 Test St",
        "delivery_phone": "1234567890",
        "payment_method": "card",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


@pytest.fixture
def mock_order_cancelled():
    """Mock order that's already cancelled"""
    return {
        "_id": ObjectId("507f1f77bcf86cd799439023"),
        "customer_id": "507f1f77bcf86cd799439011",
        "restaurant_id": "507f1f77bcf86cd799439030",
        "items": [{"menu_item_id": "item1", "quantity": 2, "price": 100}],
        "subtotal": 200.0,
        "delivery_fee": 50.0,
        "discount": 0.0,
        "total": 250.0,
        "status": "cancelled",
        "order_status": "cancelled",
        "delivery_address": "123 Test St",
        "delivery_phone": "1234567890",
        "payment_method": "card",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "cancelled_at": datetime.utcnow()
    }


@pytest.fixture
def mock_order_delivered():
    """Mock order that's already delivered"""
    return {
        "_id": ObjectId("507f1f77bcf86cd799439024"),
        "customer_id": "507f1f77bcf86cd799439011",
        "restaurant_id": "507f1f77bcf86cd799439030",
        "items": [{"menu_item_id": "item1", "quantity": 2, "price": 100}],
        "subtotal": 200.0,
        "delivery_fee": 50.0,
        "discount": 0.0,
        "total": 250.0,
        "status": "delivered",
        "order_status": "delivered",
        "delivery_address": "123 Test St",
        "delivery_phone": "1234567890",
        "payment_method": "card",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


@pytest.fixture
def mock_order_preparing():
    """Mock order in preparing status (non-cancellable)"""
    return {
        "_id": ObjectId("507f1f77bcf86cd799439025"),
        "customer_id": "507f1f77bcf86cd799439011",
        "restaurant_id": "507f1f77bcf86cd799439030",
        "items": [{"menu_item_id": "item1", "quantity": 2, "price": 100}],
        "subtotal": 200.0,
        "delivery_fee": 50.0,
        "discount": 0.0,
        "total": 250.0,
        "status": "preparing",
        "order_status": "preparing",
        "delivery_address": "123 Test St",
        "delivery_phone": "1234567890",
        "payment_method": "card",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }


@pytest.mark.asyncio
async def test_cancel_order_success_paid(mock_db, mock_user, mock_order_paid):
    """Test successful cancellation of order with 'paid' status"""
    order_id = str(mock_order_paid["_id"])
    
    mock_db.orders.find_one.return_value = mock_order_paid
    mock_db.orders.update_one.return_value = MagicMock(modified_count=1)
    
    response = await cancel_order(order_id, current_user=mock_user)
    
    assert response["message"] == "Order cancelled successfully"
    assert response["status"] == "cancelled"
    mock_db.orders.find_one.assert_called_once()
    mock_db.orders.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_cancel_order_success_pending(mock_db, mock_user, mock_order_pending):
    """Test successful cancellation of order with 'pending' status"""
    order_id = str(mock_order_pending["_id"])
    
    mock_db.orders.find_one.return_value = mock_order_pending
    mock_db.orders.update_one.return_value = MagicMock(modified_count=1)
    
    response = await cancel_order(order_id, current_user=mock_user)
    
    assert response["message"] == "Order cancelled successfully"
    assert response["status"] == "cancelled"
    mock_db.orders.find_one.assert_called_once()
    mock_db.orders.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_cancel_order_success_confirmed(mock_db, mock_user, mock_order_confirmed):
    """Test successful cancellation of order with 'confirmed' status"""
    order_id = str(mock_order_confirmed["_id"])
    
    mock_db.orders.find_one.return_value = mock_order_confirmed
    mock_db.orders.update_one.return_value = MagicMock(modified_count=1)
    
    response = await cancel_order(order_id, current_user=mock_user)
    
    assert response["message"] == "Order cancelled successfully"
    assert response["status"] == "cancelled"
    mock_db.orders.find_one.assert_called_once()
    mock_db.orders.update_one.assert_called_once()


@pytest.mark.asyncio
async def test_cancel_order_not_found(mock_db, mock_user):
    """Test cancellation when order doesn't exist"""
    order_id = "507f1f77bcf86cd799439099"
    
    mock_db.orders.find_one.return_value = None
    
    with pytest.raises(HTTPException) as exc_info:
        await cancel_order(order_id, current_user=mock_user)
    
    assert exc_info.value.status_code == 404
    assert "Order not found" in str(exc_info.value.detail)
    mock_db.orders.find_one.assert_called_once()


@pytest.mark.asyncio
async def test_cancel_order_invalid_objectid(mock_db, mock_user):
    """Test cancellation with invalid ObjectId format"""
    order_id = "invalid_id"
    
    mock_db.orders.find_one.side_effect = Exception("Invalid ObjectId")
    
    with pytest.raises(HTTPException) as exc_info:
        await cancel_order(order_id, current_user=mock_user)
    
    assert exc_info.value.status_code == 404
    assert "Order not found" in str(exc_info.value.detail)


@pytest.mark.asyncio
async def test_cancel_order_unauthorized(mock_db, mock_user, mock_other_user, mock_order_paid):
    """Test cancellation when user doesn't own the order"""
    order_id = str(mock_order_paid["_id"])
    
    mock_db.orders.find_one.return_value = mock_order_paid
    
    with pytest.raises(HTTPException) as exc_info:
        await cancel_order(order_id, current_user=mock_other_user)
    
    assert exc_info.value.status_code == 403
    assert "Not authorized" in str(exc_info.value.detail)
    mock_db.orders.find_one.assert_called_once()


@pytest.mark.asyncio
async def test_cancel_order_already_cancelled(mock_db, mock_user, mock_order_cancelled):
    """Test cancellation when order is already cancelled"""
    order_id = str(mock_order_cancelled["_id"])
    
    mock_db.orders.find_one.return_value = mock_order_cancelled
    
    with pytest.raises(HTTPException) as exc_info:
        await cancel_order(order_id, current_user=mock_user)
    
    assert exc_info.value.status_code == 400
    assert "cannot be cancelled" in str(exc_info.value.detail)
    mock_db.orders.find_one.assert_called_once()


@pytest.mark.asyncio
async def test_cancel_order_delivered(mock_db, mock_user, mock_order_delivered):
    """Test cancellation when order is already delivered"""
    order_id = str(mock_order_delivered["_id"])
    
    mock_db.orders.find_one.return_value = mock_order_delivered
    
    with pytest.raises(HTTPException) as exc_info:
        await cancel_order(order_id, current_user=mock_user)
    
    assert exc_info.value.status_code == 400
    assert "cannot be cancelled" in str(exc_info.value.detail)
    assert "delivered" in str(exc_info.value.detail)
    mock_db.orders.find_one.assert_called_once()


@pytest.mark.asyncio
async def test_cancel_order_preparing_status(mock_db, mock_user, mock_order_preparing):
    """Test cancellation when order is in preparing status (non-cancellable)"""
    order_id = str(mock_order_preparing["_id"])
    
    mock_db.orders.find_one.return_value = mock_order_preparing
    
    with pytest.raises(HTTPException) as exc_info:
        await cancel_order(order_id, current_user=mock_user)
    
    assert exc_info.value.status_code == 400
    assert "cannot be cancelled" in str(exc_info.value.detail)
    assert "preparing" in str(exc_info.value.detail)
    mock_db.orders.find_one.assert_called_once()


@pytest.mark.asyncio
async def test_cancel_order_in_transit(mock_db, mock_user):
    """Test cancellation when order is in transit"""
    order_id = "507f1f77bcf86cd799439026"
    mock_order = {
        "_id": ObjectId(order_id),
        "customer_id": "507f1f77bcf86cd799439011",
        "restaurant_id": "507f1f77bcf86cd799439030",
        "status": "in_transit",
        "order_status": "in-transit",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    mock_db.orders.find_one.return_value = mock_order
    
    with pytest.raises(HTTPException) as exc_info:
        await cancel_order(order_id, current_user=mock_user)
    
    assert exc_info.value.status_code == 400
    assert "cannot be cancelled" in str(exc_info.value.detail)
    mock_db.orders.find_one.assert_called_once()


@pytest.mark.asyncio
async def test_cancel_order_updates_timestamps(mock_db, mock_user, mock_order_paid):
    """Test that cancellation updates cancelled_at and updated_at timestamps"""
    order_id = str(mock_order_paid["_id"])
    
    mock_db.orders.find_one.return_value = mock_order_paid
    mock_db.orders.update_one.return_value = MagicMock(modified_count=1)
    
    await cancel_order(order_id, current_user=mock_user)
    
    # Verify update call
    update_call = mock_db.orders.update_one.call_args
    update_data = update_call[0][1]["$set"]
    
    assert update_data["status"] == "cancelled"
    assert "cancelled_at" in update_data
    assert "updated_at" in update_data
    assert isinstance(update_data["cancelled_at"], datetime)
    assert isinstance(update_data["updated_at"], datetime)
