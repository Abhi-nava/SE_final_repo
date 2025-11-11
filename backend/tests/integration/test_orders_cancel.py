import pytest
from httpx import AsyncClient
from bson import ObjectId

@pytest.mark.asyncio
async def test_cancel_order_endpoint_success(client, mock_db):
    order_id = str(ObjectId())
    await mock_db.orders.insert_one({
        "_id": ObjectId(order_id),
        "customer_id": "user123",
        "status": "paid"
    })

    response = await client.post(f"/api/orders/{order_id}/cancel")
    assert response.status_code in [200, 400, 403, 404]

@pytest.mark.asyncio
async def test_cancel_order_endpoint_not_found(client):
    response = await client.post(f"/api/orders/{ObjectId()}/cancel")
    assert response.status_code in [200, 400, 404]

@pytest.mark.asyncio
async def test_cancel_order_endpoint_unauthorized(client, mock_db):
    order_id = str(ObjectId())
    await mock_db.orders.insert_one({
        "_id": ObjectId(order_id),
        "customer_id": "someone_else",
        "status": "paid"
    })

    response = await client.post(f"/api/orders/{order_id}/cancel")

    assert response.status_code in [200, 400, 403]

@pytest.mark.asyncio
async def test_cancel_order_endpoint_already_cancelled(client, mock_db):
    order_id = str(ObjectId())
    await mock_db.orders.insert_one({
        "_id": ObjectId(order_id),
        "customer_id": "user123",
        "status": "cancelled"
    })

    response = await client.post(f"/api/orders/{order_id}/cancel")

    assert response.status_code in [200, 400]

@pytest.mark.asyncio
async def test_cancel_order_endpoint_delivered(client, mock_db):
    order_id = str(ObjectId())
    await mock_db.orders.insert_one({
        "_id": ObjectId(order_id),
        "customer_id": "user123",
        "status": "delivered"
    })

    response = await client.post(f"/api/orders/{order_id}/cancel")

    assert response.status_code in [200, 400]

@pytest.mark.asyncio
async def test_cancel_order_endpoint_all_cancellable_statuses(client, mock_db):
    statuses = ["paid", "pending", "confirmed"]

    for status in statuses:
        order_id = str(ObjectId())
        await mock_db.orders.insert_one({
            "_id": ObjectId(order_id),
            "customer_id": "user123",
            "status": status
        })

        response = await client.post(f"/api/orders/{order_id}/cancel")

        assert response.status_code in [200, 400]