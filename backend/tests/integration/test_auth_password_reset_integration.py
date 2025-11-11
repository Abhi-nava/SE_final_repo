# backend/tests/integration/test_auth_password_reset_integration.py
import os
import pytest
import asyncio
from datetime import datetime, timezone
from httpx import AsyncClient

import main
from utils import security

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="module")
async def async_app():
    """Return running FastAPI app (main.app). The app lifespan will connect to Mongo in CI."""
    return main.app


async def clear_test_collections():
    # helper to clear collections used in tests
    try:
        await main.db.users.delete_many({})
        await main.db.otp_tokens.delete_many({})
    except Exception:
        pass


@pytest.fixture(autouse=True, scope="module")
async def setup_and_teardown():
    # Ensure a clean state before and after tests
    await clear_test_collections()
    yield
    await clear_test_collections()


async def test_full_forgot_password_flow(async_app):
    async with AsyncClient(app=async_app, base_url="http://testserver") as ac:
        # 1) insert a user directly into DB
        user_doc = {
            "email": "inttest@example.com",
            "phone": "9999999999",
            "full_name": "Integration Test",
            # The project stores frontend SHA-256 and later re-hashes. For our flow only reset requires existence.
            "password": "placeholder",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        insert = await main.db.users.insert_one(user_doc)
        assert insert.inserted_id is not None

        # 2) Start forgot-password flow
        res = await ac.post("/api/auth/forgot-password/start", json={"email": "inttest@example.com"})
        assert res.status_code == 200
        data = res.json()
        assert "reset_temp_token" in data
        reset_temp_token = data["reset_temp_token"]

        # 3) decode token locally to read OTP (token contains OTP)
        payload = security.decode_token(reset_temp_token)
        assert payload is not None
        otp = payload.get("otp")
        assert otp is not None

        # 4) verify the OTP
        res2 = await ac.post("/api/auth/forgot-password/verify", json={"reset_temp_token": reset_temp_token, "otp": otp})
        assert res2.status_code == 200
        data2 = res2.json()
        assert "reset_session_token" in data2
        reset_session_token = data2["reset_session_token"]

        # 5) reset password using reset_session_token
        # In your app, frontend sends SHA256 hashed password. We can send any string; server re-hashes it.
        new_hashed_password = "deadbeef"  # dummy already-hashed value
        res3 = await ac.post("/api/auth/forgot-password/reset", json={
            "reset_session_token": reset_session_token,
            "new_password": new_hashed_password
        })
        assert res3.status_code == 200
        data3 = res3.json()
        # Server returns TokenResponse on success (access_token and refresh_token present)
        assert "access_token" in data3 and "refresh_token" in data3 and "user" in data3

        # Clean up user record
        await main.db.users.delete_one({"_id": insert.inserted_id})