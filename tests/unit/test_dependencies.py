import sys
import os
import asyncio
from types import SimpleNamespace
from datetime import datetime, timezone, timedelta

import pytest
from bson import ObjectId
from fastapi import HTTPException

# Ensure repository root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

BACKEND_DIR = os.path.join(REPO_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from utils.dependencies import (
    get_current_user_http,
    get_current_user_ws,
    get_current_customer,
    get_current_restaurant_owner,
    get_current_delivery_agent,
    get_current_admin,
    ADMIN_ROLE,
    CUSTOMER_ROLE,
    RESTAURANT_ROLE,
    DELIVERY_AGENT_ROLE
)
from utils.security import create_access_token
import database as database_module


class FakeCredentials:
    """Mock HTTPAuthorizationCredentials"""
    def __init__(self, token):
        self.credentials = token


def test_get_current_user_http_success(monkeypatch):
    """Test get_current_user_http with valid token"""
    user_id = ObjectId()
    fake_user = {
        "_id": user_id,
        "email": "user@example.com",
        "role": CUSTOMER_ROLE,
        "created_at": datetime.now(timezone.utc)
    }
    
    async def find_one(query):
        if query.get("email") == fake_user["email"]:
            return fake_user
        return None
    
    fake_db = SimpleNamespace()
    fake_db.users = SimpleNamespace(find_one=find_one)
    monkeypatch.setattr(database_module, "db", fake_db)
    
    # Create valid token
    token = create_access_token({"email": fake_user["email"], "sub": str(user_id)})
    credentials = FakeCredentials(token)
    
    result = asyncio.run(get_current_user_http(credentials))
    assert result["email"] == fake_user["email"]
    assert result["role"] == CUSTOMER_ROLE


def test_get_current_user_http_missing_token(monkeypatch):
    """Test get_current_user_http with missing token"""
    credentials = FakeCredentials(None)
    
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(get_current_user_http(credentials))
    
    assert exc_info.value.status_code == 401
    assert "Missing authentication token" in exc_info.value.detail


def test_get_current_user_http_invalid_token(monkeypatch):
    """Test get_current_user_http with invalid token"""
    fake_db = SimpleNamespace()
    fake_db.users = SimpleNamespace(find_one=lambda q: None)
    monkeypatch.setattr(database_module, "db", fake_db)
    
    credentials = FakeCredentials("invalid.token.here")
    
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(get_current_user_http(credentials))
    
    assert exc_info.value.status_code == 401
    assert "Invalid or expired token" in exc_info.value.detail


def test_get_current_user_http_user_not_found(monkeypatch):
    """Test get_current_user_http when user doesn't exist in DB"""
    async def find_one(query):
        return None
    
    fake_db = SimpleNamespace()
    fake_db.users = SimpleNamespace(find_one=find_one)
    monkeypatch.setattr(database_module, "db", fake_db)
    
    token = create_access_token({"email": "notfound@example.com", "sub": "123"})
    credentials = FakeCredentials(token)
    
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(get_current_user_http(credentials))
    
    assert exc_info.value.status_code == 404
    assert "User not found" in exc_info.value.detail


def test_get_current_customer_success():
    """Test get_current_customer with customer role"""
    fake_user = {
        "_id": ObjectId(),
        "email": "customer@example.com",
        "role": CUSTOMER_ROLE
    }
    
    result = asyncio.run(get_current_customer(current_user=fake_user))
    assert result["role"] == CUSTOMER_ROLE


def test_get_current_customer_forbidden():
    """Test get_current_customer with non-customer role"""
    fake_user = {
        "_id": ObjectId(),
        "email": "restaurant@example.com",
        "role": RESTAURANT_ROLE
    }
    
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(get_current_customer(current_user=fake_user))
    
    assert exc_info.value.status_code == 403
    assert "Only customers can access this endpoint" in exc_info.value.detail


def test_get_current_restaurant_owner_success():
    """Test get_current_restaurant_owner with restaurant role"""
    fake_user = {
        "_id": ObjectId(),
        "email": "owner@example.com",
        "role": RESTAURANT_ROLE
    }
    
    result = asyncio.run(get_current_restaurant_owner(current_user=fake_user))
    assert result["role"] == RESTAURANT_ROLE


def test_get_current_restaurant_owner_forbidden():
    """Test get_current_restaurant_owner with non-restaurant role"""
    fake_user = {
        "_id": ObjectId(),
        "email": "customer@example.com",
        "role": CUSTOMER_ROLE
    }
    
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(get_current_restaurant_owner(current_user=fake_user))
    
    assert exc_info.value.status_code == 403
    assert "Only restaurant owners can access this endpoint" in exc_info.value.detail


def test_get_current_delivery_agent_success():
    """Test get_current_delivery_agent with delivery agent role"""
    fake_user = {
        "_id": ObjectId(),
        "email": "agent@example.com",
        "role": DELIVERY_AGENT_ROLE
    }
    
    result = asyncio.run(get_current_delivery_agent(current_user=fake_user))
    assert result["role"] == DELIVERY_AGENT_ROLE


def test_get_current_delivery_agent_forbidden():
    """Test get_current_delivery_agent with non-delivery agent role"""
    fake_user = {
        "_id": ObjectId(),
        "email": "customer@example.com",
        "role": CUSTOMER_ROLE
    }
    
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(get_current_delivery_agent(current_user=fake_user))
    
    assert exc_info.value.status_code == 403
    assert "Only delivery agents can access this endpoint" in exc_info.value.detail


def test_get_current_admin_success():
    """Test get_current_admin with admin role"""
    fake_user = {
        "_id": ObjectId(),
        "email": "admin@example.com",
        "role": ADMIN_ROLE
    }
    
    result = asyncio.run(get_current_admin(current_user=fake_user))
    assert result["role"] == ADMIN_ROLE


def test_get_current_admin_forbidden():
    """Test get_current_admin with non-admin role"""
    fake_user = {
        "_id": ObjectId(),
        "email": "customer@example.com",
        "role": CUSTOMER_ROLE
    }
    
    with pytest.raises(HTTPException) as exc_info:
        asyncio.run(get_current_admin(current_user=fake_user))
    
    assert exc_info.value.status_code == 403
    assert "Only admins can access this endpoint" in exc_info.value.detail


def test_role_constants():
    """Test that role constants are defined correctly"""
    assert ADMIN_ROLE == "admin"
    assert CUSTOMER_ROLE == "customer"
    assert RESTAURANT_ROLE == "restaurant"
    assert DELIVERY_AGENT_ROLE == "delivery_agent"


class FakeWebSocket:
    """Mock WebSocket for testing"""
    def __init__(self, query_params):
        self.query_params = query_params
        self.closed = False
        self.close_code = None
        self.close_reason = None
    
    async def close(self, code, reason):
        self.closed = True
        self.close_code = code
        self.close_reason = reason


def test_get_current_user_ws_success(monkeypatch):
    """Test WebSocket authentication with valid token"""
    user_id = ObjectId()
    fake_user = {
        "_id": user_id,
        "email": "ws_user@example.com",
        "role": CUSTOMER_ROLE,
        "created_at": datetime.now(timezone.utc)
    }
    
    async def find_one(query):
        if query.get("email") == fake_user["email"]:
            return fake_user
        return None
    
    fake_db = SimpleNamespace()
    fake_db.users = SimpleNamespace(find_one=find_one)
    monkeypatch.setattr(database_module, "db", fake_db)
    
    # Create valid token
    token = create_access_token({"email": fake_user["email"], "sub": str(user_id)})
    websocket = FakeWebSocket({"token": token})
    
    result = asyncio.run(get_current_user_ws(websocket))
    assert result["email"] == fake_user["email"]
    assert not websocket.closed


def test_get_current_user_ws_missing_token(monkeypatch):
    """Test WebSocket authentication with missing token"""
    fake_db = SimpleNamespace()
    fake_db.users = SimpleNamespace(find_one=lambda q: None)
    monkeypatch.setattr(database_module, "db", fake_db)
    
    websocket = FakeWebSocket({})  # No token
    
    result = asyncio.run(get_current_user_ws(websocket))
    assert result is None
    assert websocket.closed
    assert websocket.close_code == 4001
    assert "Missing authentication token" in websocket.close_reason


def test_get_current_user_ws_invalid_token(monkeypatch):
    """Test WebSocket authentication with invalid token"""
    fake_db = SimpleNamespace()
    fake_db.users = SimpleNamespace(find_one=lambda q: None)
    monkeypatch.setattr(database_module, "db", fake_db)
    
    websocket = FakeWebSocket({"token": "invalid.token.here"})
    
    result = asyncio.run(get_current_user_ws(websocket))
    assert result is None
    assert websocket.closed
    assert websocket.close_code == 4002
    assert "Invalid or expired token" in websocket.close_reason


def test_get_current_user_ws_expired_token(monkeypatch):
    """Test WebSocket authentication with expired token"""
    fake_db = SimpleNamespace()
    fake_db.users = SimpleNamespace(find_one=lambda q: None)
    monkeypatch.setattr(database_module, "db", fake_db)
    
    # Create expired token
    token = create_access_token(
        {"email": "expired@example.com", "sub": "123"},
        expires_delta=timedelta(seconds=-1)
    )
    websocket = FakeWebSocket({"token": token})
    
    result = asyncio.run(get_current_user_ws(websocket))
    assert result is None
    assert websocket.closed
    assert websocket.close_code == 4002


def test_get_current_user_ws_no_email_in_token(monkeypatch):
    """Test WebSocket authentication with token missing email"""
    fake_db = SimpleNamespace()
    fake_db.users = SimpleNamespace(find_one=lambda q: None)
    monkeypatch.setattr(database_module, "db", fake_db)
    
    # Create token without email
    token = create_access_token({"sub": "123"})
    websocket = FakeWebSocket({"token": token})
    
    result = asyncio.run(get_current_user_ws(websocket))
    assert result is None
    assert websocket.closed
    assert websocket.close_code == 4003
    assert "Invalid token payload" in websocket.close_reason


def test_get_current_user_ws_user_not_found(monkeypatch):
    """Test WebSocket authentication when user not in database"""
    async def find_one(query):
        return None
    
    fake_db = SimpleNamespace()
    fake_db.users = SimpleNamespace(find_one=find_one)
    monkeypatch.setattr(database_module, "db", fake_db)
    
    token = create_access_token({"email": "notfound@example.com", "sub": "123"})
    websocket = FakeWebSocket({"token": token})
    
    result = asyncio.run(get_current_user_ws(websocket))
    assert result is None
    assert websocket.closed
    assert websocket.close_code == 4004
    assert "User not found" in websocket.close_reason
