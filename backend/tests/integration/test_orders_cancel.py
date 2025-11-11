"""
Integration tests for order cancellation functionality.
Tests the full API endpoint with a mock database.
"""
import pytest
from starlette.testclient import TestClient
from bson import ObjectId
from datetime import datetime
from main import app
from database import db
from utils.dependencies import get_current_user_http


# Create test client
client = TestClient(app)


@pytest.fixture
def mock_user_data():
    """Create a mock user data structure"""
    user_data = {
        "_id": ObjectId(),
        "email": "test_cancel@example.com",
        "name": "Test Cancel User",
        "role": "customer",
        "phone": "1234567890"
    }
    return user_data


@pytest.fixture
def mock_other_user_data():
    """Create another mock user for authorization tests"""
    user_data = {
        "_id": ObjectId(),
        "email": "other_cancel@example.com",
        "name": "Other Cancel User",
        "role": "customer",
        "phone": "1234567891"
    }
    return user_data


@pytest.fixture
def mock_restaurant_data():
    """Create a mock restaurant data structure"""
    restaurant_data = {
        "_id": ObjectId(),
        "name": "Test Restaurant",
        "owner_id": str(ObjectId()),
        "address": "123 Test St",
        "phone": "9876543210"
    }
    return restaurant_data


@pytest.fixture
async def setup_test_data(mock_user_data, mock_other_user_data, mock_restaurant_data):
    """Setup test data in mock database"""
    # Insert users
    await db.users.insert_one(mock_user_data)
    await db.users.insert_one(mock_other_user_data)
    
    # Insert restaurant
    await db.restaurants.insert_one(mock_restaurant_data)
    
    yield {
        "user": mock_user_data,
        "other_user": mock_other_user_data,
        "restaurant": mock_restaurant_data
    }
    
    # Cleanup
    await db.users.delete_one({"_id": mock_user_data["_id"]})
    await db.users.delete_one({"_id": mock_other_user_data["_id"]})
    await db.restaurants.delete_one({"_id": mock_restaurant_data["_id"]})


@pytest.fixture
async def create_test_order(setup_test_data):
    """Create a test order in the mock database"""
    async for test_data in setup_test_data:
        order_data = {
            "_id": ObjectId(),
            "customer_id": str(test_data["user"]["_id"]),
            "restaurant_id": str(test_data["restaurant"]["_id"]),
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
        
        await db.orders.insert_one(order_data)
        
        yield order_data
        
        # Cleanup
        await db.orders.delete_one({"_id": order_data["_id"]})


@pytest.mark.asyncio
async def test_cancel_order_endpoint_success(create_test_order, mock_user_data):
    """Test successful order cancellation via API endpoint"""
    async for order in create_test_order:
        order_id = str(order["_id"])
        
        # Mock the authentication dependency
        def override_get_current_user():
            return mock_user_data
        
        app.dependency_overrides[get_current_user_http] = override_get_current_user
        
        try:
            response = client.post(f"/api/orders/{order_id}/cancel")
            
            assert response.status_code == 200
            assert response.json()["message"] == "Order cancelled successfully"
            assert response.json()["status"] == "cancelled"
            
            # Verify order was updated in database
            updated_order = await db.orders.find_one({"_id": ObjectId(order_id)})
            assert updated_order is not None
            assert updated_order["status"] == "cancelled"
            assert "cancelled_at" in updated_order
            assert "updated_at" in updated_order
        finally:
            app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_cancel_order_endpoint_not_found(mock_user_data):
    """Test cancellation endpoint with non-existent order"""
    fake_order_id = str(ObjectId())
    
    def override_get_current_user():
        return mock_user_data
    
    app.dependency_overrides[get_current_user_http] = override_get_current_user
    
    try:
        response = client.post(f"/api/orders/{fake_order_id}/cancel")
        
        assert response.status_code == 404
        assert "Order not found" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_cancel_order_endpoint_unauthorized(create_test_order, mock_other_user_data):
    """Test cancellation endpoint when user doesn't own the order"""
    async for order in create_test_order:
        order_id = str(order["_id"])
        
        def override_get_current_user():
            return mock_other_user_data
        
        app.dependency_overrides[get_current_user_http] = override_get_current_user
        
        try:
            response = client.post(f"/api/orders/{order_id}/cancel")
            
            assert response.status_code == 403
            assert "Not authorized" in response.json()["detail"]
        finally:
            app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_cancel_order_endpoint_already_cancelled(mock_user_data, mock_restaurant_data):
    """Test cancellation endpoint when order is already cancelled"""
    # Create a cancelled order
    cancelled_order = {
        "_id": ObjectId(),
        "customer_id": str(mock_user_data["_id"]),
        "restaurant_id": str(mock_restaurant_data["_id"]),
        "status": "cancelled",
        "order_status": "cancelled",
        "total": 250.0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "cancelled_at": datetime.utcnow()
    }
    
    await db.orders.insert_one(cancelled_order)
    order_id = str(cancelled_order["_id"])
    
    def override_get_current_user():
        return mock_user_data
    
    app.dependency_overrides[get_current_user_http] = override_get_current_user
    
    try:
        response = client.post(f"/api/orders/{order_id}/cancel")
        
        assert response.status_code == 400
        assert "cannot be cancelled" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
        await db.orders.delete_one({"_id": cancelled_order["_id"]})


@pytest.mark.asyncio
async def test_cancel_order_endpoint_delivered(mock_user_data, mock_restaurant_data):
    """Test cancellation endpoint when order is delivered"""
    # Create a delivered order
    delivered_order = {
        "_id": ObjectId(),
        "customer_id": str(mock_user_data["_id"]),
        "restaurant_id": str(mock_restaurant_data["_id"]),
        "status": "delivered",
        "order_status": "delivered",
        "total": 250.0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    await db.orders.insert_one(delivered_order)
    order_id = str(delivered_order["_id"])
    
    def override_get_current_user():
        return mock_user_data
    
    app.dependency_overrides[get_current_user_http] = override_get_current_user
    
    try:
        response = client.post(f"/api/orders/{order_id}/cancel")
        
        assert response.status_code == 400
        assert "cannot be cancelled" in response.json()["detail"]
    finally:
        app.dependency_overrides.clear()
        await db.orders.delete_one({"_id": delivered_order["_id"]})


@pytest.mark.asyncio
async def test_cancel_order_endpoint_all_cancellable_statuses(mock_user_data, mock_restaurant_data):
    """Test cancellation endpoint with all cancellable statuses"""
    cancellable_statuses = ["paid", "pending", "confirmed"]
    
    for status in cancellable_statuses:
        order = {
            "_id": ObjectId(),
            "customer_id": str(mock_user_data["_id"]),
            "restaurant_id": str(mock_restaurant_data["_id"]),
            "status": status,
            "order_status": "preparing",
            "total": 250.0,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        await db.orders.insert_one(order)
        order_id = str(order["_id"])
        
        def override_get_current_user():
            return mock_user_data
        
        app.dependency_overrides[get_current_user_http] = override_get_current_user
        
        try:
            response = client.post(f"/api/orders/{order_id}/cancel")
            
            assert response.status_code == 200, f"Failed for status: {status}"
            assert response.json()["status"] == "cancelled"
            
            # Verify in database
            updated_order = await db.orders.find_one({"_id": ObjectId(order_id)})
            assert updated_order is not None
            assert updated_order["status"] == "cancelled"
        finally:
            app.dependency_overrides.clear()
            await db.orders.delete_one({"_id": order["_id"]})
