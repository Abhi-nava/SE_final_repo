import pytest


def test_restaurant_order_status_happy_path(client):
    resp = client.put(
        "/api/orders/restaurant/order/order1/status",
        json={"order_status": "searching"}
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body.get("message") == "Order status updated to searching"


def test_restaurant_order_status_invalid_value(client):
    resp = client.put(
        "/api/orders/restaurant/order/order1/status",
        json={"order_status": "invalid-status"}
    )
    assert resp.status_code == 400
