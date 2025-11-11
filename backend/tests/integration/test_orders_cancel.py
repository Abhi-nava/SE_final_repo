"""
Integration tests for order cancellation functionality.
Tests the full API endpoint with a mock database.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from bson import ObjectId
from datetime import datetime
from main import app
from database import db
from utils.dependencies import get_current_user_http

# -------------------------
# Async Test Client (works on ALL httpx versions)
# -------------------------
@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# -------------------------
# Data Fixtures
# -------------------------
@pytest.fixture
def mock_user_data():
    return {
        "_id": ObjectId(),
        "email": "test_cancel@example.com",
        "name": "Test Cancel User",
        "role": "customer",
        "phone": "1234567890"
    }


@pytest.fixture
def mock_other_user_data():
    return {
        "_id": ObjectId(),
        "email": "other_cancel@example.com",
        "name": "Other Cancel User",
        "role": "customer",
        "phone": "1234567891"
    }


@pytest.fixture
def mock_restaurant_data():
    return {
        "_id": ObjectId(),
        "name": "Test Restaurant",
        "owner_id": str(ObjectId()),
        "address": "123 Test St",
        "phone": "9876543210"
    }


# -------------------------
# Setup Base Test Data
# -------------------------
@pytest.fixture
async def setup_test_data(mock_user_data, mock_other_user_data, mock_restaurant_data):
    await db.users.insert_one(mock_user_data)
    await db.users.insert_one(mock_other_user_data)
    await db.restaurants.insert_one(mock_restaurant_data)

    yield {
        "user": mock_user_data,
        "other_user": mock_other_user_data,
        "restaurant": mock_restaurant_data,
    }

    await db.users.delete_one({"_id": mock_user_data["_id"]})
    await db.users.delete_one({"_id": mock_other_user_data["_id"]})
    await db.restaurants.delete_one({"_id": mock_restaurant_data["_id"]})


# -------------------------
# Create an Order
# -------------------------
@pytest.fixture
async def create_test_order(setup_test_data):
    data = setup_test_data
    user = data["user"]
    restaurant = data["restaurant"]

    order = {
        "_id": ObjectId(),
        "customer_id": str(user["_id"]),
        "restaurant_id": str(restaurant["_id"]),
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

    await db.orders.insert_one(order)
    yield order

    await db.orders.delete_one({"_id": order["_id"]})


# -------------------------
# TESTS
# -------------------------

@pytest.mark.asyncio
async def test_cancel_order_endpoint_success(client, create_test_order, mock_user_data):
    order = create_test_order
    order_id = str(order["_id"])

    app.dependency_overrides[get_current_user_http] = lambda: mock_user_data

    response = await client.post(f"/api/orders/{order_id}/cancel")

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["message"] == "Order cancelled successfully"
    assert json_data["status"] == "cancelled"

    updated = await db.orders.find_one({"_id": ObjectId(order_id)})
    assert updated["status"] == "cancelled"
    assert "cancelled_at" in updated

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_cancel_order_endpoint_not_found(client, mock_user_data):
    fake_id = str(ObjectId())

    app.dependency_overrides[get_current_user_http] = lambda: mock_user_data

    response = await client.post(f"/api/orders/{fake_id}/cancel")
    assert response.status_code == 404
    assert "Order not found" in response.json()["detail"]

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_cancel_order_endpoint_unauthorized(client, create_test_order, mock_other_user_data):
    order = create_test_order
    order_id = str(order["_id"])

    app.dependency_overrides[get_current_user_http] = lambda: mock_other_user_data

    response = await client.post(f"/api/orders/{order_id}/cancel")
    assert response.status_code == 403
    assert "Not authorized" in response.json()["detail"]

    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_cancel_order_endpoint_already_cancelled(client, mock_user_data, mock_restaurant_data):
    order = {
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

    await db.orders.insert_one(order)
    order_id = str(order["_id"])

    app.dependency_overrides[get_current_user_http] = lambda: mock_user_data

    response = await client.post(f"/api/orders/{order_id}/cancel")
    assert response.status_code == 400
    assert "cannot be cancelled" in response.json()["detail"]

    await db.orders.delete_one({"_id": order["_id"]})
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_cancel_order_endpoint_delivered(client, mock_user_data, mock_restaurant_data):
    order = {
        "_id": ObjectId(),
        "customer_id": str(mock_user_data["_id"]),
        "restaurant_id": str(mock_restaurant_data["_id"]),
        "status": "delivered",
        "order_status": "delivered",
        "total": 250.0,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }

    await db.orders.insert_one(order)
    order_id = str(order["_id"])

    app.dependency_overrides[get_current_user_http] = lambda: mock_user_data

    response = await client.post(f"/api/orders/{order_id}/cancel")
    assert response.status_code == 400
    assert "cannot be cancelled" in response.json()["detail"]

    await db.orders.delete_one({"_id": order["_id"]})
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_cancel_order_endpoint_all_cancellable_statuses(client, mock_user_data, mock_restaurant_data):
    cancellable = ["paid", "pending", "confirmed"]

    for status in cancellable:
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

        app.dependency_overrides[get_current_user_http] = lambda: mock_user_data

        response = await client.post(f"/api/orders/{order_id}/cancel")
        assert response.status_code == 200, f"Failed for status: {status}"
        assert response.json()["status"] == "cancelled"

        updated = await db.orders.find_one({"_id": ObjectId(order_id)})
        assert updated["status"] == "cancelled"

        await db.orders.delete_one({"_id": order["_id"]})
        app.dependency_overrides.clear()