import pytest


@pytest.mark.asyncio
async def test_restaurant_order_status_happy_path(async_client):
    resp = await async_client.put(
        "/api/orders/restaurant/order/order1/status",
        json={"order_status": "searching"}
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body.get("message") == "Order status updated to searching"


@pytest.mark.asyncio
async def test_restaurant_order_status_invalid_value(async_client):
    resp = await async_client.put(
        "/api/orders/restaurant/order/order1/status",
        json={"order_status": "invalid-status"}
    )
    assert resp.status_code == 400
