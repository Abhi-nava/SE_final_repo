import sys
import os
import asyncio
from types import SimpleNamespace
from datetime import datetime, timezone

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
    get_current_customer,
    get_current_restaurant_owner,
    get_current_delivery_agent,
    get_current_admin
)
from utils.security import create_access_token
import database as database_module


class FakeCredentials:
    """Mock HTTPAuthorizationCredentials"""
    def __init__(self, token):
        self.credentials = token


class FakeCollection:
    def __init__(self):
        self._data = {}

    async def find_one(self, query):
        if not query:
            return None
        if "email" in query:
            for v in self._data.values():
                if v.get("email") == query["email"]:
                    return v
        if "_id" in query:
            _id = query["_id"]
            for k, v in self._data.items():
                if str(k) == str(_id) or v.get("_id") == str(_id):
                    return v
        return None

    async def insert_one(self, doc):
        _id = ObjectId()
        doc_copy = dict(doc)
        doc_copy["_id"] = str(_id)
        self._data[str(_id)] = doc_copy
        return SimpleNamespace(inserted_id=_id)


@pytest.fixture
def fake_db(monkeypatch):
    users = FakeCollection()
    fake = SimpleNamespace()
    fake.users = users
    monkeypatch.setattr(database_module, "db", fake)
    return fake


def test_authentication_flow_customer(fake_db):
    """Integration test: Customer user authenticates -> Gets access"""
    # Create customer user
    customer = {
        "_id": ObjectId(),
        "email": "customer@example.com",
        "role": "customer",
        "full_name": "Test Customer",
        "created_at": datetime.now(timezone.utc)
    }
    asyncio.run(fake_db.users.insert_one(customer))
    
    # Create token
    token = create_access_token({"email": customer["email"], "sub": str(customer["_id"])})
    credentials = FakeCredentials(token)
    
    # Authenticate
    user = asyncio.run(get_current_user_http(credentials))
    assert user["email"] == customer["email"]
    assert user["role"] == "customer"
    
    # Customer-specific access should work
    customer_user = asyncio.run(get_current_customer(current_user=user))
    assert customer_user["role"] == "customer"
    
    # Other role access should fail
    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_current_admin(current_user=user))
    assert exc.value.status_code == 403


def test_authentication_flow_restaurant_owner(fake_db):
    """Integration test: Restaurant owner authenticates -> Gets access"""
    # Create restaurant owner
    owner = {
        "_id": ObjectId(),
        "email": "owner@example.com",
        "role": "restaurant",
        "full_name": "Restaurant Owner",
        "created_at": datetime.now(timezone.utc)
    }
    asyncio.run(fake_db.users.insert_one(owner))
    
    # Create token
    token = create_access_token({"email": owner["email"], "sub": str(owner["_id"])})
    credentials = FakeCredentials(token)
    
    # Authenticate
    user = asyncio.run(get_current_user_http(credentials))
    assert user["email"] == owner["email"]
    assert user["role"] == "restaurant"
    
    # Restaurant owner access should work
    owner_user = asyncio.run(get_current_restaurant_owner(current_user=user))
    assert owner_user["role"] == "restaurant"
    
    # Customer access should fail
    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_current_customer(current_user=user))
    assert exc.value.status_code == 403


def test_authentication_flow_delivery_agent(fake_db):
    """Integration test: Delivery agent authenticates -> Gets access"""
    # Create delivery agent
    agent = {
        "_id": ObjectId(),
        "email": "agent@example.com",
        "role": "delivery_agent",
        "full_name": "Delivery Agent",
        "created_at": datetime.now(timezone.utc)
    }
    asyncio.run(fake_db.users.insert_one(agent))
    
    # Create token
    token = create_access_token({"email": agent["email"], "sub": str(agent["_id"])})
    credentials = FakeCredentials(token)
    
    # Authenticate
    user = asyncio.run(get_current_user_http(credentials))
    assert user["email"] == agent["email"]
    assert user["role"] == "delivery_agent"
    
    # Delivery agent access should work
    agent_user = asyncio.run(get_current_delivery_agent(current_user=user))
    assert agent_user["role"] == "delivery_agent"
    
    # Restaurant owner access should fail
    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_current_restaurant_owner(current_user=user))
    assert exc.value.status_code == 403


def test_authentication_flow_admin(fake_db):
    """Integration test: Admin authenticates -> Gets access"""
    # Create admin
    admin = {
        "_id": ObjectId(),
        "email": "admin@example.com",
        "role": "admin",
        "full_name": "System Admin",
        "created_at": datetime.now(timezone.utc)
    }
    asyncio.run(fake_db.users.insert_one(admin))
    
    # Create token
    token = create_access_token({"email": admin["email"], "sub": str(admin["_id"])})
    credentials = FakeCredentials(token)
    
    # Authenticate
    user = asyncio.run(get_current_user_http(credentials))
    assert user["email"] == admin["email"]
    assert user["role"] == "admin"
    
    # Admin access should work
    admin_user = asyncio.run(get_current_admin(current_user=user))
    assert admin_user["role"] == "admin"
    
    # Customer access should fail
    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_current_customer(current_user=user))
    assert exc.value.status_code == 403


def test_token_expiration_handling(fake_db):
    """Integration test: User authenticates with expired token -> Gets error"""
    from datetime import timedelta
    
    # Create user
    user = {
        "_id": ObjectId(),
        "email": "expired@example.com",
        "role": "customer",
        "created_at": datetime.now(timezone.utc)
    }
    asyncio.run(fake_db.users.insert_one(user))
    
    # Create expired token
    token = create_access_token(
        {"email": user["email"], "sub": str(user["_id"])},
        expires_delta=timedelta(seconds=-1)
    )
    credentials = FakeCredentials(token)
    
    # Should fail with 401
    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_current_user_http(credentials))
    assert exc.value.status_code == 401


def test_invalid_token_handling(fake_db):
    """Integration test: User provides invalid token -> Gets error"""
    credentials = FakeCredentials("invalid.token.string")
    
    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_current_user_http(credentials))
    assert exc.value.status_code == 401
    assert "Invalid or expired token" in exc.value.detail


def test_user_not_in_database(fake_db):
    """Integration test: Valid token but user deleted from DB -> Gets error"""
    # Create token for non-existent user
    token = create_access_token({"email": "notfound@example.com", "sub": "123"})
    credentials = FakeCredentials(token)
    
    # Should fail with 404
    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_current_user_http(credentials))
    assert exc.value.status_code == 404
    assert "User not found" in exc.value.detail


def test_multiple_users_concurrent_auth(fake_db):
    """Integration test: Multiple users authenticate simultaneously"""
    # Create multiple users
    users = [
        {"email": "user1@example.com", "role": "customer"},
        {"email": "user2@example.com", "role": "restaurant"},
        {"email": "user3@example.com", "role": "delivery_agent"}
    ]
    
    tokens = {}
    for user_data in users:
        user = {
            "_id": ObjectId(),
            "email": user_data["email"],
            "role": user_data["role"],
            "created_at": datetime.now(timezone.utc)
        }
        asyncio.run(fake_db.users.insert_one(user))
        tokens[user_data["email"]] = create_access_token({
            "email": user_data["email"],
            "sub": str(user["_id"])
        })
    
    # Authenticate all users
    for user_data in users:
        credentials = FakeCredentials(tokens[user_data["email"]])
        authenticated_user = asyncio.run(get_current_user_http(credentials))
        assert authenticated_user["email"] == user_data["email"]
        assert authenticated_user["role"] == user_data["role"]


def test_role_based_access_control_chain(fake_db):
    """Integration test: Test all role-based access functions in sequence"""
    # Create users with different roles
    roles = ["customer", "restaurant", "delivery_agent", "admin"]
    users = {}
    
    for role in roles:
        user = {
            "_id": ObjectId(),
            "email": f"{role}@example.com",
            "role": role,
            "created_at": datetime.now(timezone.utc)
        }
        asyncio.run(fake_db.users.insert_one(user))
        users[role] = user
    
    # Test customer can only access customer endpoints
    customer = users["customer"]
    asyncio.run(get_current_customer(current_user=customer))  # Should pass
    with pytest.raises(HTTPException):
        asyncio.run(get_current_restaurant_owner(current_user=customer))
    with pytest.raises(HTTPException):
        asyncio.run(get_current_delivery_agent(current_user=customer))
    with pytest.raises(HTTPException):
        asyncio.run(get_current_admin(current_user=customer))
    
    # Test restaurant can only access restaurant endpoints
    restaurant = users["restaurant"]
    asyncio.run(get_current_restaurant_owner(current_user=restaurant))  # Should pass
    with pytest.raises(HTTPException):
        asyncio.run(get_current_customer(current_user=restaurant))
    
    # Test delivery agent can only access delivery endpoints
    delivery = users["delivery_agent"]
    asyncio.run(get_current_delivery_agent(current_user=delivery))  # Should pass
    with pytest.raises(HTTPException):
        asyncio.run(get_current_customer(current_user=delivery))
    
    # Test admin can only access admin endpoints
    admin = users["admin"]
    asyncio.run(get_current_admin(current_user=admin))  # Should pass
    with pytest.raises(HTTPException):
        asyncio.run(get_current_customer(current_user=admin))


def test_authentication_with_updated_user_data(fake_db):
    """Integration test: User authenticates -> User data updated -> Re-fetch shows updates"""
    # Create user
    user_id = ObjectId()
    user = {
        "_id": user_id,
        "email": "update@example.com",
        "role": "customer",
        "full_name": "Original Name",
        "created_at": datetime.now(timezone.utc)
    }
    asyncio.run(fake_db.users.insert_one(user))
    
    # Authenticate
    token = create_access_token({"email": user["email"], "sub": str(user_id)})
    credentials = FakeCredentials(token)
    
    fetched_user = asyncio.run(get_current_user_http(credentials))
    assert fetched_user["full_name"] == "Original Name"
    
    # Update user in DB (simulate profile update)
    # Find the actual key used in storage
    for key, stored_user in fake_db.users._data.items():
        if stored_user.get("email") == user["email"]:
            fake_db.users._data[key]["full_name"] = "Updated Name"
            break
    
    # Re-authenticate with same token (should fetch updated data)
    fetched_user_again = asyncio.run(get_current_user_http(credentials))
    assert fetched_user_again["full_name"] == "Updated Name"
