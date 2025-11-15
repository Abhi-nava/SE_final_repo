import sys
import os
import asyncio
from types import SimpleNamespace
from datetime import datetime, timedelta, timezone

import pytest
from bson import ObjectId

# Ensure repository root is on sys.path so imports like `backend.main` work
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Also add the backend folder to sys.path because modules under `backend` import `routes` as a top-level package
BACKEND_DIR = os.path.join(REPO_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from models.user import UserCreate, LoginRequest, PasswordReset

import backend.main as main_app
import routes.auth as auth_module
import utils.dependencies as dependencies_module
import database as database_module


def test_register_success(monkeypatch):
    """Register endpoint returns tokens when user does not exist"""
    app = main_app.app

    # Fake DB behavior
    async def users_find_one(query):
        return None

    class InsertOneResult:
        def __init__(self, inserted_id):
            self.inserted_id = inserted_id

    async def users_insert_one(doc):
        return InsertOneResult(ObjectId())

    fake_db = SimpleNamespace()
    fake_db.users = SimpleNamespace(find_one=users_find_one, insert_one=users_insert_one)

    # Patch database references used by modules
    monkeypatch.setattr(database_module, "db", fake_db)
    monkeypatch.setattr(auth_module, "db", fake_db)

    payload = {
        "email": "test@example.com",
        "phone": "9999999999",
        "full_name": "Test User",
        "password": "secret123",
        "role": "customer"
    }

    # Call the route function directly (async) via asyncio
    user_create = UserCreate(**payload)
    result = asyncio.run(auth_module.register(user_create))

    # register returns TokenResponse (pydantic model as dict when returned by FastAPI),
    # but because we call the function directly, we get the raw return (TokenResponse instance)
    assert hasattr(result, "access_token")
    assert hasattr(result, "refresh_token")
    assert hasattr(result, "user")
    assert result.user.email == payload["email"]


def test_login_success(monkeypatch):
    """Login returns tokens when credentials match"""
    app = main_app.app

    # Prepare a fake user record; note auth.login uses `user.get("password", "")`
    fake_user = {
        "_id": ObjectId(),
        "email": "login@example.com",
        "phone": "8888888888",
        "full_name": "Login User",
        # auth.login compares plain text to this field (see repo's verify_password), so set it equal
        "password": "mypassword",
        "role": "customer",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }

    async def users_find_one(query):
        return fake_user

    fake_db = SimpleNamespace()
    fake_db.users = SimpleNamespace(find_one=users_find_one)

    monkeypatch.setattr(database_module, "db", fake_db)
    monkeypatch.setattr(auth_module, "db", fake_db)

    payload = {"email": fake_user["email"], "password": "mypassword"}

    login_req = LoginRequest(**payload)
    result = asyncio.run(auth_module.login(login_req))

    assert hasattr(result, "access_token")
    assert hasattr(result, "refresh_token")
    assert result.user.email == fake_user["email"]


def test_get_me_with_dependency_override(monkeypatch):
    """GET /me should return the current user when dependency is overridden"""
    app = main_app.app

    fake_user = {
        "_id": ObjectId(),
        "email": "me@example.com",
        "phone": "7777777777",
        "full_name": "Me User",
        "role": "customer",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    }

    # Call the route function directly, passing the user object
    result = asyncio.run(auth_module.get_me(current_user=fake_user))
    assert result.email == fake_user["email"]