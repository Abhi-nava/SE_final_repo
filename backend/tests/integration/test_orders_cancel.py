import pytest
from httpx import AsyncClient, ASGITransport
from bson import ObjectId
from main import app
from database import db
from utils.dependencies import get_current_user_http


# ------------------------------------------------------------
# TEST CLIENT FIXTURE — WITH AUTH DEPENDENCY OVERRIDE
# ------------------------------------------------------------
@pytest.fixture
async def client():
    # Default authenticated user for all normal tests
    app.dependency_overrides[get_current_user_http] = lambda: {"_id": "test_customer_id"}

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()


# ------------------------------------------------------------
# Helper to insert test user + restaurant
# ------------------------------------------------------------
async def insert_user_and_restaurant():
    user = {"_id": ObjectId("64dd00000000000000000001"), "name": "Test User"}
    restaurant = {"_id": ObjectId("64dd00000000000000000002"), "name": "Test Rest", "owner_id": "owner123"}

    await db.users.insert_one(user)
    await db.restaurants.insert_one(restaurant)

    return str(user["_id"]), str(restaurant["_id"])


# ------------------------------------------------------------
# TEST 1: SUCCESSFUL CANCELLATION
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_cancel_order_endpoint_success(client):
    user_id, restaurant_id = await insert_user_and_restaurant()

    order = {
        "_id": ObjectId(),
        "customer_id": "test_customer_id",
        "restaurant_id": restaurant_id,
        "status": "paid",
    }
    await db.orders.insert_one(order)

    response = await client.post(f"/orders/{order['_id']}/cancel")

    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"


# ------------------------------------------------------------
# TEST 2: ORDER NOT FOUND
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_cancel_order_endpoint_not_found(client):
    invalid_id = ObjectId()
    response = await client.post(f"/orders/{invalid_id}/cancel")
    assert response.status_code == 404


# ------------------------------------------------------------
# TEST 3: UNAUTHORIZED (different user)
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_cancel_order_endpoint_unauthorized(client):
    # Override to simulate different user
    app.dependency_overrides[get_current_user_http] = lambda: {"_id": "other_user"}

    order = {
        "_id": ObjectId(),
        "customer_id": "test_customer_id",  # belongs to someone else
        "restaurant_id": "64dd00000000000000000002",
        "status": "paid",
    }
    await db.orders.insert_one(order)

    response = await client.post(f"/orders/{order['_id']}/cancel")
    assert response.status_code == 403

    app.dependency_overrides.clear()


# ------------------------------------------------------------
# TEST 4: ALREADY CANCELLED
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_cancel_order_endpoint_already_cancelled(client):
    order = {
        "_id": ObjectId(),
        "customer_id": "test_customer_id",
        "restaurant_id": "64dd00000000000000000002",
        "status": "cancelled",
    }
    await db.orders.insert_one(order)

    response = await client.post(f"/orders/{order['_id']}/cancel")

    assert response.status_code == 400
    assert "cannot be cancelled" in response.json()["detail"]


# ------------------------------------------------------------
# TEST 5: DELIVERED (cannot be cancelled)
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_cancel_order_endpoint_delivered(client):
    order = {
        "_id": ObjectId(),
        "customer_id": "test_customer_id",
        "restaurant_id": "64dd00000000000000000002",
        "status": "delivered",
    }
    await db.orders.insert_one(order)

    response = await client.post(f"/orders/{order['_id']}/cancel")

    assert response.status_code == 400
    assert "cannot be cancelled" in response.json()["detail"]


# ------------------------------------------------------------
# TEST 6: TEST EACH CANCELLABLE STATUS
# ------------------------------------------------------------
@pytest.mark.asyncio
async def test_cancel_order_endpoint_all_cancellable_statuses(client):
    cancellable = ["paid", "pending", "confirmed"]

    for status in cancellable:
        order = {
            "_id": ObjectId(),
            "customer_id": "test_customer_id",
            "restaurant_id": "64dd00000000000000000002",
            "status": status,
        }
        await db.orders.insert_one(order)

        response = await client.post(f"/orders/{order['_id']}/cancel")
        assert response.status_code == 200, f"Failed for status: {status}"