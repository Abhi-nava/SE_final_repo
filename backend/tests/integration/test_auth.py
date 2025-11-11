import os
import sys
from copy import deepcopy
from datetime import datetime, timezone

import httpx
import pytest
import pytest_asyncio
from bson import ObjectId

# Setup paths before imports
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

BACKEND_DIR = os.path.join(REPO_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

pytestmark = pytest.mark.asyncio

import database as database_module  # noqa: E402
from main import app  # noqa: E402
from routes import auth as auth_routes  # noqa: E402
from utils import dependencies as deps  # noqa: E402
from utils.security import PasswordResetToken  # noqa: E402
from utils.security import TwoFactorAuthToken, hash_password


# In-memory database implementation
class InMemoryDatabase:
    def __init__(self):
        self._collections = {}

    def __getitem__(self, name):
        if name not in self._collections:
            self._collections[name] = InMemoryCollection()
        return self._collections[name]

    def __getattr__(self, name):
        return self[name]


class InMemoryCollection:
    def __init__(self):
        self._documents = []

    def _match_document(self, doc, filter):
        for key, value in filter.items():
            doc_value = doc.get(key)

            if key == "$or":
                return any(
                    self._match_document(doc, sub_filter) for sub_filter in value
                )

            if value is None:
                if doc_value is not None:
                    return False
                continue

            if key == "_id" or key.endswith("_id"):
                if isinstance(value, ObjectId):
                    value_str = str(value)
                elif isinstance(value, str):
                    value_str = value
                else:
                    value_str = str(value) if value else None

                if isinstance(doc_value, ObjectId):
                    doc_value_str = str(doc_value)
                elif isinstance(doc_value, str):
                    doc_value_str = doc_value
                else:
                    doc_value_str = str(doc_value) if doc_value else None

                if value_str != doc_value_str:
                    return False
            elif isinstance(value, dict) and "$ne" in value:
                if doc_value == value["$ne"]:
                    return False
            elif doc_value != value:
                return False
        return True

    async def find_one(self, filter):
        for doc in self._documents:
            if self._match_document(doc, filter):
                result = deepcopy(doc)
                if "_id" in result and not isinstance(result["_id"], ObjectId):
                    try:
                        result["_id"] = ObjectId(result["_id"])
                    except Exception:
                        pass
                return result
        return None

    async def insert_one(self, document):
        doc = deepcopy(document)
        if "_id" not in doc:
            doc["_id"] = ObjectId()
        elif isinstance(doc["_id"], str):
            try:
                doc["_id"] = ObjectId(doc["_id"])
            except Exception:
                doc["_id"] = ObjectId()

        self._documents.append(doc)
        return type("obj", (object,), {"inserted_id": doc["_id"]})()

    async def update_one(self, filter, update):
        matched_count = 0
        modified_count = 0

        for doc in self._documents:
            if self._match_document(doc, filter):
                matched_count = 1
                if "$set" in update:
                    for key, value in update["$set"].items():
                        if doc.get(key) != value:
                            doc[key] = value
                            modified_count = 1
                break

        return type(
            "obj",
            (object,),
            {"matched_count": matched_count, "modified_count": modified_count},
        )()

    async def delete_one(self, filter):
        deleted_count = 0
        remaining = []
        for doc in self._documents:
            if self._match_document(doc, filter) and deleted_count == 0:
                deleted_count = 1
            else:
                remaining.append(doc)
        self._documents = remaining
        return type("obj", (object,), {"deleted_count": deleted_count})()

    async def delete_many(self, filter):
        deleted_count = 0
        remaining = []
        for doc in self._documents:
            if self._match_document(doc, filter):
                deleted_count += 1
            else:
                remaining.append(doc)
        self._documents = remaining
        return type("obj", (object,), {"deleted_count": deleted_count})()


@pytest_asyncio.fixture(scope="function")
async def client_and_db():
    """Fixture providing test client and in-memory database"""

    # Create in-memory database
    async_test_db = InMemoryDatabase()

    # Override database
    database_module.db = async_test_db
    auth_routes.db = async_test_db
    import database

    database.db = async_test_db

    import routes.auth as auth_module

    setattr(auth_module, "db", async_test_db)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://localhost"
    ) as async_client:
        for name in ["users", "delivery_agents", "otp_tokens"]:
            await async_test_db[name].delete_many({})
        yield async_client, async_test_db
        for name in ["users", "delivery_agents", "otp_tokens"]:
            await async_test_db[name].delete_many({})


async def test_register_new_user_success(client_and_db):
    """Test successful user registration"""
    client, test_db = client_and_db

    payload = {
        "email": "newuser@example.com",
        "phone": "1234567890",
        "full_name": "New User",
        "password": hash_password("password123"),
        "role": "customer",
    }

    res = await client.post("/api/auth/register", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()

    assert "temp_token" in data
    assert "message" in data
    assert "2FA verification required" in data["message"]

    # Verify user was created in database
    user = await test_db.users.find_one({"email": "newuser@example.com"})
    assert user is not None
    assert user["full_name"] == "New User"
    assert user["phone"] == "1234567890"
    assert user["role"] == "customer"


async def test_register_duplicate_email(client_and_db):
    """Test registration with existing email"""
    client, test_db = client_and_db

    # Create existing user
    await test_db.users.insert_one(
        {
            "email": "existing@example.com",
            "phone": "9999999999",
            "full_name": "Existing User",
            "password": hash_password("pass"),
            "role": "customer",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )

    payload = {
        "email": "existing@example.com",
        "phone": "1111111111",
        "full_name": "New User",
        "password": hash_password("password123"),
        "role": "customer",
    }

    res = await client.post("/api/auth/register", json=payload)
    assert res.status_code == 400
    assert "already registered" in res.json()["detail"]


async def test_register_duplicate_phone(client_and_db):
    """Test registration with existing phone"""
    client, test_db = client_and_db

    # Create existing user
    await test_db.users.insert_one(
        {
            "email": "user1@example.com",
            "phone": "5555555555",
            "full_name": "User One",
            "password": hash_password("pass"),
            "role": "customer",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )

    payload = {
        "email": "user2@example.com",
        "phone": "5555555555",  # Same phone
        "full_name": "User Two",
        "password": hash_password("password123"),
        "role": "customer",
    }

    res = await client.post("/api/auth/register", json=payload)
    assert res.status_code == 400
    assert "already registered" in res.json()["detail"]


async def test_verify_2fa_success(client_and_db):
    """Test successful 2FA verification"""
    client, test_db = client_and_db

    # Create user
    user_id = ObjectId()
    await test_db.users.insert_one(
        {
            "_id": user_id,
            "email": "2fa@example.com",
            "phone": "1234567890",
            "full_name": "2FA User",
            "password": hash_password("password123"),
            "role": "customer",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )

    # Create temp token with OTP
    temp_token = TwoFactorAuthToken.create_temp_token(str(user_id), "2fa@example.com")
    token_data = TwoFactorAuthToken.verify_temp_token(temp_token)
    correct_otp = token_data["otp"]

    # Verify 2FA
    verify_payload = {"temp_token": temp_token, "otp": correct_otp}

    res = await client.post("/api/auth/verify-2fa", json=verify_payload)
    assert res.status_code == 200, res.text
    data = res.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert "user" in data
    assert data["user"]["email"] == "2fa@example.com"


async def test_verify_2fa_invalid_otp(client_and_db):
    """Test 2FA verification with wrong OTP"""
    client, test_db = client_and_db

    user_id = ObjectId()
    await test_db.users.insert_one(
        {
            "_id": user_id,
            "email": "wrong2fa@example.com",
            "phone": "1234567890",
            "full_name": "Wrong OTP User",
            "password": hash_password("password123"),
            "role": "customer",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )

    temp_token = TwoFactorAuthToken.create_temp_token(
        str(user_id), "wrong2fa@example.com"
    )

    verify_payload = {"temp_token": temp_token, "otp": "000000"}  # Wrong OTP

    res = await client.post("/api/auth/verify-2fa", json=verify_payload)
    assert res.status_code == 400
    assert "Invalid verification code" in res.json()["detail"]


async def test_login_success(client_and_db):
    """Test successful login flow"""
    client, test_db = client_and_db

    # Create user
    password = "loginpass123"
    hashed = hash_password(password)
    await test_db.users.insert_one(
        {
            "email": "login@example.com",
            "phone": "1234567890",
            "full_name": "Login User",
            "password": hashed,
            "role": "customer",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )

    login_payload = {
        "email": "login@example.com",
        "password": hashed,  # Send hashed password
    }

    res = await client.post("/api/auth/login", json=login_payload)
    assert res.status_code == 200, res.text
    data = res.json()

    assert "temp_token" in data
    assert "2FA verification required" in data["message"]


async def test_login_invalid_email(client_and_db):
    """Test login with non-existent email"""
    client, test_db = client_and_db

    login_payload = {"email": "nonexistent@example.com", "password": "anypassword"}

    res = await client.post("/api/auth/login", json=login_payload)
    assert res.status_code == 401
    assert "Invalid email or password" in res.json()["detail"]


async def test_login_invalid_password(client_and_db):
    """Test login with wrong password"""
    client, test_db = client_and_db

    # Create user
    correct_password = "correctpassword"
    await test_db.users.insert_one(
        {
            "email": "wrongpass@example.com",
            "phone": "1234567890",
            "full_name": "Wrong Pass User",
            "password": hash_password(correct_password),
            "role": "customer",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )

    login_payload = {
        "email": "wrongpass@example.com",
        "password": hash_password("wrongpassword"),  # Wrong password, hashed
    }

    res = await client.post("/api/auth/login", json=login_payload)
    assert res.status_code == 401
    assert "Invalid email or password" in res.json()["detail"]


async def test_login_inactive_user(client_and_db):
    """Test login with deactivated account"""
    client, test_db = client_and_db

    password = "password123"
    hashed = hash_password(password)
    await test_db.users.insert_one(
        {
            "email": "inactive@example.com",
            "phone": "1234567890",
            "full_name": "Inactive User",
            "password": hashed,
            "role": "customer",
            "is_active": False,  # Deactivated
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )

    login_payload = {
        "email": "inactive@example.com",
        "password": hashed,  # Send hashed password
    }

    res = await client.post("/api/auth/login", json=login_payload)
    assert res.status_code == 403
    assert "deactivated" in res.json()["detail"]


async def test_get_me_authenticated(client_and_db):
    """Test getting current user profile"""
    client, test_db = client_and_db

    # Create user
    user_id = ObjectId()
    await test_db.users.insert_one(
        {
            "_id": user_id,
            "email": "getme@example.com",
            "phone": "1234567890",
            "full_name": "Get Me User",
            "password": hash_password("password123"),
            "role": "customer",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )

    # Mock authentication dependency
    async def mock_get_current_user():
        return {
            "_id": user_id,
            "email": "getme@example.com",
            "phone": "1234567890",
            "full_name": "Get Me User",
            "role": "customer",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }

    app.dependency_overrides[deps.get_current_user_http] = mock_get_current_user

    res = await client.get("/api/auth/me")
    assert res.status_code == 200, res.text
    data = res.json()

    assert data["email"] == "getme@example.com"
    assert data["full_name"] == "Get Me User"
    assert data["role"] == "customer"

    # Cleanup
    app.dependency_overrides.clear()


async def test_forgot_password_start(client_and_db):
    """Test starting password reset flow"""
    client, test_db = client_and_db

    # Create user
    await test_db.users.insert_one(
        {
            "email": "forgot@example.com",
            "phone": "1234567890",
            "full_name": "Forgot User",
            "password": hash_password("oldpassword"),
            "role": "customer",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )

    payload = {"email": "forgot@example.com"}

    res = await client.post("/api/auth/forgot-password/start", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()

    assert "reset_temp_token" in data
    assert "message" in data


async def test_forgot_password_verify_otp(client_and_db):
    """Test verifying OTP for password reset"""
    client, test_db = client_and_db

    # Create user
    await test_db.users.insert_one(
        {
            "email": "verify-reset@example.com",
            "phone": "1234567890",
            "full_name": "Verify Reset User",
            "password": hash_password("oldpassword"),
            "role": "customer",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )

    # Start reset
    reset_temp_token = PasswordResetToken.create_temp_token("verify-reset@example.com")
    token_data = PasswordResetToken.verify_temp_token(reset_temp_token)
    correct_otp = token_data["otp"]

    # Verify OTP
    verify_payload = {"reset_temp_token": reset_temp_token, "otp": correct_otp}

    res = await client.post("/api/auth/forgot-password/verify", json=verify_payload)
    assert res.status_code == 200, res.text
    data = res.json()

    assert "reset_session_token" in data


async def test_forgot_password_reset(client_and_db):
    """Test completing password reset"""
    client, test_db = client_and_db

    # Create user
    user_id = ObjectId()
    await test_db.users.insert_one(
        {
            "_id": user_id,
            "email": "complete-reset@example.com",
            "phone": "1234567890",
            "full_name": "Complete Reset User",
            "password": hash_password("oldpassword"),
            "role": "customer",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
        }
    )

    # Create reset session token
    reset_session_token = PasswordResetToken.create_reset_session_token(
        "complete-reset@example.com"
    )

    # Reset password
    new_password = hash_password("newpassword123")
    reset_payload = {
        "reset_session_token": reset_session_token,
        "new_password": new_password,
    }

    res = await client.post("/api/auth/forgot-password/reset", json=reset_payload)
    assert res.status_code == 200, res.text
    data = res.json()

    assert "access_token" in data
    assert "refresh_token" in data
    assert "user" in data

    # Verify password was updated
    user = await test_db.users.find_one({"_id": user_id})
    assert user["password_hash"] == hash_password(new_password)


async def test_forgot_password_invalid_otp(client_and_db):
    """Test password reset with wrong OTP"""
    client, test_db = client_and_db

    reset_temp_token = PasswordResetToken.create_temp_token("test@example.com")

    verify_payload = {
        "reset_temp_token": reset_temp_token,
        "otp": "000000",  # Wrong OTP
    }

    res = await client.post("/api/auth/forgot-password/verify", json=verify_payload)
    assert res.status_code == 400
    assert "Invalid OTP" in res.json()["detail"]
