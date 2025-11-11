import pytest
import pytest_asyncio
import sys
import os
from datetime import datetime, timezone
from bson import ObjectId
import httpx
from copy import deepcopy

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

BACKEND_DIR = os.path.join(REPO_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

pytestmark = pytest.mark.asyncio

from main import app
import database as database_module
from routes import auth as auth_routes
from utils import dependencies as deps
from utils.security import TwoFactorAuthToken, PasswordResetToken, hash_password


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
                return any(self._match_document(doc, sub_filter) for sub_filter in value)
            
            if value is None:
                if doc_value is not None:
                    return False
                continue
            
            if key == '_id' or key.endswith('_id'):
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
            elif isinstance(value, dict) and '$ne' in value:
                if doc_value == value['$ne']:
                    return False
            elif doc_value != value:
                return False
        return True
    
    async def find_one(self, filter):
        for doc in self._documents:
            if self._match_document(doc, filter):
                result = deepcopy(doc)
                if '_id' in result and not isinstance(result['_id'], ObjectId):
                    try:
                        result['_id'] = ObjectId(result['_id'])
                    except:
                        pass
                return result
        return None
    
    async def insert_one(self, document):
        doc = deepcopy(document)
        if '_id' not in doc:
            doc['_id'] = ObjectId()
        elif isinstance(doc['_id'], str):
            try:
                doc['_id'] = ObjectId(doc['_id'])
            except:
                doc['_id'] = ObjectId()
        
        self._documents.append(doc)
        return type('obj', (object,), {'inserted_id': doc['_id']})()
    
    async def update_one(self, filter, update):
        matched_count = 0
        modified_count = 0
        
        for doc in self._documents:
            if self._match_document(doc, filter):
                matched_count = 1
                if '$set' in update:
                    for key, value in update['$set'].items():
                        if doc.get(key) != value:
                            doc[key] = value
                            modified_count = 1
                break
        
        return type('obj', (object,), {
            'matched_count': matched_count,
            'modified_count': modified_count
        })()
    
    async def delete_one(self, filter):
        deleted_count = 0
        remaining = []
        for doc in self._documents:
            if self._match_document(doc, filter) and deleted_count == 0:
                deleted_count = 1
            else:
                remaining.append(doc)
        self._documents = remaining
        return type('obj', (object,), {'deleted_count': deleted_count})()
    
    async def delete_many(self, filter):
        deleted_count = 0
        remaining = []
        for doc in self._documents:
            if self._match_document(doc, filter):
                deleted_count += 1
            else:
                remaining.append(doc)
        self._documents = remaining
        return type('obj', (object,), {'deleted_count': deleted_count})()


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
    setattr(auth_module, 'db', async_test_db)
    
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://localhost") as async_client:
        for name in ["users", "delivery_agents", "otp_tokens"]:
            await async_test_db[name].delete_many({})
        yield async_client, async_test_db
        for name in ["users", "delivery_agents", "otp_tokens"]:
            await async_test_db[name].delete_many({})


async def test_complete_registration_and_login_flow(client_and_db):
    """Test complete user journey: register -> verify 2FA -> login -> verify 2FA"""
    client, test_db = client_and_db
    
    # Step 1: Register
    register_payload = {
        "email": "flowtest@example.com",
        "phone": "1234567890",
        "full_name": "Flow Test User",
        "password": hash_password("testpassword123"),
        "role": "customer"
    }
    
    reg_res = await client.post("/api/auth/register", json=register_payload)
    assert reg_res.status_code == 200
    reg_data = reg_res.json()
    temp_token_1 = reg_data["temp_token"]
    
    # Step 2: Verify 2FA for registration
    token_data_1 = TwoFactorAuthToken.verify_temp_token(temp_token_1)
    otp_1 = token_data_1["otp"]
    
    verify_payload_1 = {
        "temp_token": temp_token_1,
        "otp": otp_1
    }
    
    verify_res_1 = await client.post("/api/auth/verify-2fa", json=verify_payload_1)
    assert verify_res_1.status_code == 200
    verify_data_1 = verify_res_1.json()
    
    assert "access_token" in verify_data_1
    assert "user" in verify_data_1
    
    # Step 3: Login with same credentials
    login_payload = {
        "email": "flowtest@example.com",
        "password": hash_password("testpassword123")
    }
    
    login_res = await client.post("/api/auth/login", json=login_payload)
    assert login_res.status_code == 200
    login_data = login_res.json()
    temp_token_2 = login_data["temp_token"]
    
    # Step 4: Verify 2FA for login
    token_data_2 = TwoFactorAuthToken.verify_temp_token(temp_token_2)
    otp_2 = token_data_2["otp"]
    
    verify_payload_2 = {
        "temp_token": temp_token_2,
        "otp": otp_2
    }
    
    verify_res_2 = await client.post("/api/auth/verify-2fa", json=verify_payload_2)
    assert verify_res_2.status_code == 200
    verify_data_2 = verify_res_2.json()
    
    assert "access_token" in verify_data_2
    assert verify_data_2["user"]["email"] == "flowtest@example.com"


async def test_complete_password_reset_flow(client_and_db):
    """Test complete password reset journey"""
    client, test_db = client_and_db
    
    # Step 1: Create user
    old_password = "oldpassword123"
    await test_db.users.insert_one({
        "email": "resetflow@example.com",
        "phone": "1234567890",
        "full_name": "Reset Flow User",
        "password": hash_password(old_password),
        "role": "customer",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    })
    
    # Step 2: Start password reset
    start_payload = {"email": "resetflow@example.com"}
    start_res = await client.post("/api/auth/forgot-password/start", json=start_payload)
    assert start_res.status_code == 200
    start_data = start_res.json()
    reset_temp_token = start_data["reset_temp_token"]
    
    # Step 3: Verify OTP
    token_data = PasswordResetToken.verify_temp_token(reset_temp_token)
    correct_otp = token_data["otp"]
    
    verify_payload = {
        "reset_temp_token": reset_temp_token,
        "otp": correct_otp
    }
    
    verify_res = await client.post("/api/auth/forgot-password/verify", json=verify_payload)
    assert verify_res.status_code == 200
    verify_data = verify_res.json()
    reset_session_token = verify_data["reset_session_token"]
    
    # Step 4: Reset password
    new_password = "newpassword456"
    new_password_hashed = hash_password(new_password)
    reset_payload = {
        "reset_session_token": reset_session_token,
        "new_password": new_password  # Send plain password (will be hashed by endpoint)
    }
    
    reset_res = await client.post("/api/auth/forgot-password/reset", json=reset_payload)
    assert reset_res.status_code == 200
    reset_data = reset_res.json()
    
    assert "access_token" in reset_data
    assert "user" in reset_data
    
    # Step 5: Verify old password doesn't work
    login_old = {
        "email": "resetflow@example.com",
        "password": hash_password(old_password)
    }
    
    old_res = await client.post("/api/auth/login", json=login_old)
    assert old_res.status_code == 401
    
    # Step 6: Verify new password works (use hashed version since endpoint will hash what we send)
    login_new = {
        "email": "resetflow@example.com",
        "password": new_password_hashed  # Use the hashed version
    }
    
    new_res = await client.post("/api/auth/login", json=login_new)
    assert new_res.status_code == 200


async def test_multiple_failed_login_attempts(client_and_db):
    """Test multiple failed login attempts"""
    client, test_db = client_and_db
    
    # Create user
    await test_db.users.insert_one({
        "email": "failedlogin@example.com",
        "phone": "1234567890",
        "full_name": "Failed Login User",
        "password": hash_password("correctpassword"),
        "role": "customer",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    })
    
    # Attempt multiple failed logins
    for _ in range(3):
        login_payload = {
            "email": "failedlogin@example.com",
            "password": hash_password("wrongpassword")
        }
        
        res = await client.post("/api/auth/login", json=login_payload)
        assert res.status_code == 401
        assert "Invalid email or password" in res.json()["detail"]
    
    # Verify correct password still works
    correct_login = {
        "email": "failedlogin@example.com",
        "password": hash_password("correctpassword")
    }
    
    res = await client.post("/api/auth/login", json=correct_login)
    assert res.status_code == 200


async def test_concurrent_registration_attempts(client_and_db):
    """Test concurrent registration with same email"""
    client, test_db = client_and_db
    
    payload = {
        "email": "concurrent@example.com",
        "phone": "1234567890",
        "full_name": "Concurrent User",
        "password": hash_password("password123"),
        "role": "customer"
    }
    
    # First registration should succeed
    res1 = await client.post("/api/auth/register", json=payload)
    assert res1.status_code == 200
    
    # Second registration with same email should fail
    payload2 = payload.copy()
    payload2["phone"] = "9999999999"  # Different phone
    res2 = await client.post("/api/auth/register", json=payload2)
    assert res2.status_code == 400
    assert "already registered" in res2.json()["detail"]


async def test_2fa_token_expiry_behavior(client_and_db):
    """Test behavior when 2FA token expires"""
    client, test_db = client_and_db
    
    user_id = ObjectId()
    await test_db.users.insert_one({
        "_id": user_id,
        "email": "expiry@example.com",
        "phone": "1234567890",
        "full_name": "Expiry User",
        "password": hash_password("password123"),
        "role": "customer",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    })
    
    # Create token with very short expiry
    temp_token = TwoFactorAuthToken.create_temp_token(str(user_id), "expiry@example.com", expires_in=1)
    token_data = TwoFactorAuthToken.verify_temp_token(temp_token)
    correct_otp = token_data["otp"]
    
    # Wait for token to expire
    import time
    time.sleep(2)
    
    # Try to verify with expired token
    verify_payload = {
        "temp_token": temp_token,
        "otp": correct_otp
    }
    
    res = await client.post("/api/auth/verify-2fa", json=verify_payload)
    assert res.status_code == 400
    assert "Invalid or expired" in res.json()["detail"]


async def test_password_reset_without_existing_user(client_and_db):
    """Test password reset flow for non-existent email"""
    client, test_db = client_and_db
    
    # Start reset for non-existent email
    start_payload = {"email": "nonexistent@example.com"}
    start_res = await client.post("/api/auth/forgot-password/start", json=start_payload)
    
    # Should return success to avoid revealing if user exists
    assert start_res.status_code == 200
    assert "reset_temp_token" in start_res.json()


async def test_register_different_roles(client_and_db):
    """Test registration with different user roles"""
    client, test_db = client_and_db
    
    roles = ["customer", "restaurant", "delivery_agent"]
    
    for i, role in enumerate(roles):
        payload = {
            "email": f"{role}@example.com",
            "phone": f"123456789{i}",
            "full_name": f"{role.title()} User",
            "password": hash_password("password123"),
            "role": role
        }
        
        res = await client.post("/api/auth/register", json=payload)
        assert res.status_code == 200, f"Failed for role: {role}"
        
        # Verify user was created with correct role
        user = await test_db.users.find_one({"email": f"{role}@example.com"})
        assert user is not None
        assert user["role"] == role


async def test_login_with_password_hash_field(client_and_db):
    """Test login works with password_hash field (new schema)"""
    client, test_db = client_and_db
    
    password = "testpassword123"
    hashed = hash_password(password)
    await test_db.users.insert_one({
        "email": "newhash@example.com",
        "phone": "1234567890",
        "full_name": "New Hash User",
        "password_hash": hashed,  # Using password_hash field
        "role": "customer",
        "is_active": True,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)
    })
    
    login_payload = {
        "email": "newhash@example.com",
        "password": hashed  # Use the hashed password
    }
    
    res = await client.post("/api/auth/login", json=login_payload)
    assert res.status_code == 200
    assert "temp_token" in res.json()


async def test_invalid_2fa_verification_payloads(client_and_db):
    """Test 2FA verification with invalid payloads"""
    client, test_db = client_and_db
    
    # Missing temp_token
    res1 = await client.post("/api/auth/verify-2fa", json={"otp": "123456"})
    assert res1.status_code == 422  # Validation error
    
    # Missing OTP
    res2 = await client.post("/api/auth/verify-2fa", json={"temp_token": "sometoken"})
    assert res2.status_code == 422
    
    # Empty payload
    res3 = await client.post("/api/auth/verify-2fa", json={})
    assert res3.status_code == 422


async def test_forgot_password_invalid_payloads(client_and_db):
    """Test forgot password endpoints with invalid payloads"""
    client, test_db = client_and_db
    
    # Missing email in start
    res1 = await client.post("/api/auth/forgot-password/start", json={})
    assert res1.status_code == 400
    
    # Missing fields in verify
    res2 = await client.post("/api/auth/forgot-password/verify", json={"otp": "123456"})
    assert res2.status_code == 400
    
    # Missing fields in reset
    res3 = await client.post("/api/auth/forgot-password/reset", json={"new_password": "newpass"})
    assert res3.status_code == 400
