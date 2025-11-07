import pytest


@pytest.mark.asyncio
async def test_update_main_status_happy_path(async_client):
    # Update core "status" field via /api/orders/{order_id}/status
    resp = await async_client.put(
        "/api/orders/order1/status",
        json={"status": "confirmed"}
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert "message" in body and "confirmed" in body["message"]


@pytest.mark.asyncio
async def test_update_main_status_order_not_found(async_client, monkeypatch):
    # Temporarily make orders collection empty to simulate 404
    from backend.routes import orders as orders_router
    orig = orders_router.db.orders.data
    try:
        orders_router.db.orders.data = []
        resp = await async_client.put(
            "/api/orders/order1/status",
            json={"status": "confirmed"}
        )
        assert resp.status_code == 404
    finally:
        orders_router.db.orders.data = orig


@pytest.mark.asyncio
async def test_update_main_status_unauthorized_restaurant(async_client, monkeypatch):
    # Change restaurant owner id to mismatch
    from backend.routes import orders as orders_router
    orig_rest = orders_router.db.restaurants.data[0].copy()
    try:
        orders_router.db.restaurants.data[0]["owner_id"] = "other-owner"
        resp = await async_client.put(
            "/api/orders/order1/status",
            json={"status": "confirmed"}
        )
        assert resp.status_code in (403, 404)
    finally:
        orders_router.db.restaurants.data[0] = orig_rest
