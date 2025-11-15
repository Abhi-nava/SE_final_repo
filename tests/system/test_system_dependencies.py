import sys
import os
import asyncio
from datetime import datetime, timezone
from types import SimpleNamespace

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

from models.user import UserCreate
import routes.auth as auth_module
from utils.dependencies import (
    get_current_user_http,
    get_current_customer,
    get_current_restaurant_owner,
    get_current_delivery_agent,
    get_current_admin
)
from utils.security import create_access_token, decode_token
import database as database_module


class FakeCredentials:
    def __init__(self, token):
        self.credentials = token


class FakeCollection:
    def __init__(self):
        self._data = {}

    async def find_one(self, query):
        if not query:
            return None
        if "$or" in query:
            for cond in query["$or"]:
                if "email" in cond:
                    for v in self._data.values():
                        if v.get("email") == cond["email"]:
                            return v
                if "phone" in cond:
                    for v in self._data.values():
                        if v.get("phone") == cond["phone"]:
                            return v
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
    monkeypatch.setattr(auth_module, "db", fake)
    return fake


def test_system_customer_access_control_flow(fake_db):
    """System test: Customer registers -> Logs in -> Accesses customer-only endpoints"""
    # 1) Register customer
    customer_data = UserCreate(
        email="system_customer@example.com",
        phone="1112223333",
        full_name="System Customer",
        password="CustomerPass123",
        role="customer"
    )
    token_resp = asyncio.run(auth_module.register(customer_data))
    
    # 2) Use token to authenticate
    credentials = FakeCredentials(token_resp.access_token)
    user = asyncio.run(get_current_user_http(credentials))
    assert user["email"] == customer_data.email
    
    # 3) Access customer-specific endpoint
    customer = asyncio.run(get_current_customer(current_user=user))
    assert customer["role"] == "customer"
    
    # 4) Try to access restaurant endpoint (should fail)
    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_current_restaurant_owner(current_user=user))
    assert exc.value.status_code == 403


def test_system_restaurant_owner_access_control_flow(fake_db):
    """System test: Restaurant owner registers -> Logs in -> Accesses restaurant endpoints"""
    # 1) Register restaurant owner
    owner_data = UserCreate(
        email="system_owner@example.com",
        phone="4445556666",
        full_name="System Owner",
        password="OwnerPass123",
        role="restaurant"
    )
    token_resp = asyncio.run(auth_module.register(owner_data))
    
    # 2) Authenticate
    credentials = FakeCredentials(token_resp.access_token)
    user = asyncio.run(get_current_user_http(credentials))
    
    # 3) Access restaurant owner endpoint
    owner = asyncio.run(get_current_restaurant_owner(current_user=user))
    assert owner["role"] == "restaurant"
    
    # 4) Cannot access customer endpoint
    with pytest.raises(HTTPException):
        asyncio.run(get_current_customer(current_user=user))


def test_system_delivery_agent_access_control_flow(fake_db):
    """System test: Delivery agent registers -> Logs in -> Accesses delivery endpoints"""
    # 1) Register delivery agent
    agent_data = UserCreate(
        email="system_agent@example.com",
        phone="7778889999",
        full_name="System Agent",
        password="AgentPass123",
        role="delivery_agent"
    )
    token_resp = asyncio.run(auth_module.register(agent_data))
    
    # 2) Authenticate
    credentials = FakeCredentials(token_resp.access_token)
    user = asyncio.run(get_current_user_http(credentials))
    
    # 3) Access delivery agent endpoint
    agent = asyncio.run(get_current_delivery_agent(current_user=user))
    assert agent["role"] == "delivery_agent"
    
    # 4) Cannot access admin endpoint
    with pytest.raises(HTTPException):
        asyncio.run(get_current_admin(current_user=user))


def test_system_admin_access_control_flow(fake_db):
    """System test: Admin created -> Logs in -> Accesses admin endpoints"""
    # 1) Create admin user directly (admins typically aren't registered via public endpoint)
    admin = {
        "_id": ObjectId(),
        "email": "system_admin@example.com",
        "phone": "0001112222",
        "full_name": "System Admin",
        "role": "admin",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }
    asyncio.run(fake_db.users.insert_one(admin))
    
    # 2) Create token for admin
    token = create_access_token({"email": admin["email"], "sub": str(admin["_id"])})
    credentials = FakeCredentials(token)
    
    # 3) Authenticate
    user = asyncio.run(get_current_user_http(credentials))
    
    # 4) Access admin endpoint
    admin_user = asyncio.run(get_current_admin(current_user=user))
    assert admin_user["role"] == "admin"
    
    # 5) Cannot access customer endpoint
    with pytest.raises(HTTPException):
        asyncio.run(get_current_customer(current_user=user))


def test_system_role_segregation_across_all_roles(fake_db):
    """System test: Create all role types -> Verify each can only access their own endpoints"""
    # 1) Create users of all roles
    roles_data = [
        ("customer@example.com", "1111111111", "customer"),
        ("restaurant@example.com", "2222222222", "restaurant"),
        ("delivery@example.com", "3333333333", "delivery_agent"),
        ("admin@example.com", "4444444444", "admin")
    ]
    
    users = {}
    for email, phone, role in roles_data:
        if role == "admin":
            # Create admin directly
            user = {
                "_id": ObjectId(),
                "email": email,
                "phone": phone,
                "full_name": f"Test {role}",
                "role": role,
                "created_at": datetime.now(timezone.utc)
            }
            asyncio.run(fake_db.users.insert_one(user))
            token = create_access_token({"email": email, "sub": str(user["_id"])})
        else:
            # Register via normal flow
            user_data = UserCreate(
                email=email,
                phone=phone,
                full_name=f"Test {role}",
                password="TestPass123",
                role=role
            )
            token_resp = asyncio.run(auth_module.register(user_data))
            token = token_resp.access_token
        
        users[role] = token
    
    # 2) Test customer
    credentials = FakeCredentials(users["customer"])
    user = asyncio.run(get_current_user_http(credentials))
    asyncio.run(get_current_customer(current_user=user))  # Should work
    with pytest.raises(HTTPException):
        asyncio.run(get_current_restaurant_owner(current_user=user))
    
    # 3) Test restaurant
    credentials = FakeCredentials(users["restaurant"])
    user = asyncio.run(get_current_user_http(credentials))
    asyncio.run(get_current_restaurant_owner(current_user=user))  # Should work
    with pytest.raises(HTTPException):
        asyncio.run(get_current_delivery_agent(current_user=user))
    
    # 4) Test delivery agent
    credentials = FakeCredentials(users["delivery_agent"])
    user = asyncio.run(get_current_user_http(credentials))
    asyncio.run(get_current_delivery_agent(current_user=user))  # Should work
    with pytest.raises(HTTPException):
        asyncio.run(get_current_admin(current_user=user))
    
    # 5) Test admin
    credentials = FakeCredentials(users["admin"])
    user = asyncio.run(get_current_user_http(credentials))
    asyncio.run(get_current_admin(current_user=user))  # Should work
    with pytest.raises(HTTPException):
        asyncio.run(get_current_customer(current_user=user))


def test_system_authentication_after_account_deletion(fake_db):
    """System test: User registers -> Gets token -> Account deleted -> Token no longer works"""
    # 1) Register user
    user_data = UserCreate(
        email="deleted@example.com",
        phone="5556667777",
        full_name="Deleted User",
        password="DeletePass123",
        role="customer"
    )
    token_resp = asyncio.run(auth_module.register(user_data))
    token = token_resp.access_token
    
    # 2) Token works initially
    credentials = FakeCredentials(token)
    user = asyncio.run(get_current_user_http(credentials))
    assert user["email"] == user_data.email
    
    # 3) Delete user from database
    fake_db.users._data.clear()
    
    # 4) Token no longer works
    with pytest.raises(HTTPException) as exc:
        asyncio.run(get_current_user_http(credentials))
    assert exc.value.status_code == 404


def test_system_multiple_concurrent_authenticated_requests(fake_db):
    """System test: Multiple users make authenticated requests simultaneously"""
    # 1) Register multiple users
    users_tokens = []
    for i in range(5):
        user_data = UserCreate(
            email=f"concurrent{i}@example.com",
            phone=f"88888888{i}0",
            full_name=f"Concurrent User {i}",
            password=f"Pass{i}123",
            role="customer"
        )
        token_resp = asyncio.run(auth_module.register(user_data))
        users_tokens.append((user_data.email, token_resp.access_token))
    
    # 2) All users authenticate "simultaneously"
    for email, token in users_tokens:
        credentials = FakeCredentials(token)
        user = asyncio.run(get_current_user_http(credentials))
        assert user["email"] == email
        
        # Each can access customer endpoints
        customer = asyncio.run(get_current_customer(current_user=user))
        assert customer["role"] == "customer"


def test_system_token_decode_and_user_fetch_consistency(fake_db):
    """System test: Token contains user data -> Fetch from DB -> Data matches"""
    # 1) Register user
    user_data = UserCreate(
        email="consistency@example.com",
        phone="9990001111",
        full_name="Consistency User",
        password="ConsistentPass123",
        role="restaurant"
    )
    token_resp = asyncio.run(auth_module.register(user_data))
    
    # 2) Decode token
    decoded = decode_token(token_resp.access_token)
    assert decoded["email"] == user_data.email
    
    # 3) Fetch user from DB using token
    credentials = FakeCredentials(token_resp.access_token)
    fetched_user = asyncio.run(get_current_user_http(credentials))
    
    # 4) Verify consistency
    assert fetched_user["email"] == decoded["email"]
    assert fetched_user["role"] == user_data.role.value
