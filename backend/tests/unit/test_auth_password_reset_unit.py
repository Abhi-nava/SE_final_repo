# backend/tests/unit/test_auth_password_reset_unit.py
import asyncio
import pytest
from datetime import datetime, timezone, timedelta
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import routes.auth as auth
from models.user import PasswordReset  # model used by reset_password endpoint
import utils.email as email_utils
import database

pytestmark = pytest.mark.asyncio


@pytest.fixture(autouse=True)
def patch_send_email():
    # Prevent real emails during tests
    with patch.object(email_utils, "send_otp_email", autospec=True) as mock_send:
        mock_send.return_value = True
        yield mock_send


async def async_return(value):
    return value


@pytest.fixture
def fake_db(monkeypatch):
    """Create a fake database object with async methods like Motor client."""
    users = MagicMock()
    otp_tokens = MagicMock()

    # Attach AsyncMock functions
    users.find_one = AsyncMock()
    users.update_one = AsyncMock()
    otp_tokens.update_one = AsyncMock()
    otp_tokens.find_one = AsyncMock()
    otp_tokens.delete_one = AsyncMock()

    fake = SimpleNamespace(users=users, otp_tokens=otp_tokens)
    monkeypatch.setattr(database, "db", fake)
    return fake


async def test_request_otp_user_not_found(fake_db):
    fake_db.users.find_one.return_value = None

    res = await auth.request_otp("noone@example.com")
    assert isinstance(res, dict)
    assert "If user exists" in res.get("message", "")

    # Since user not found, otp_tokens.update_one should not be called
    fake_db.otp_tokens.update_one.assert_not_called()


async def test_request_otp_user_exists_saves_and_sends(fake_db, patch_send_email):
    # Simulate user exists
    fake_db.users.find_one.return_value = {"email": "u@example.com", "phone": "123"}
    fake_db.otp_tokens.update_one.return_value = AsyncMock()

    res = await auth.request_otp("u@example.com")
    assert isinstance(res, dict)
    assert "OTP sent" in res.get("message", "")

    # Ensure we attempted to save OTP record
    fake_db.otp_tokens.update_one.assert_called_once()
    patch_send_email.assert_called()


async def test_reset_password_invalid_otp(fake_db):
    # Prepare OTP record that doesn't match provided OTP
    fake_db.otp_tokens.find_one.return_value = {
        "email": "u@example.com",
        "otp": "111111",
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=5)
    }

    payload = PasswordReset(email="u@example.com", otp="222222", new_password="newpass123")
    with pytest.raises(Exception) as excinfo:
        # auth.reset_password raises HTTPException which is derived from Exception
        await auth.reset_password(payload)
    assert "Invalid OTP" in str(excinfo.value) or "Invalid" in str(excinfo.value)


async def test_reset_password_expired_otp(fake_db):
    # Prepare OTP record that is expired
    fake_db.otp_tokens.find_one.return_value = {
        "email": "u@example.com",
        "otp": "999999",
        "expires_at": datetime.now(timezone.utc) - timedelta(minutes=1)
    }

    payload = PasswordReset(email="u@example.com", otp="999999", new_password="newpass123")
    with pytest.raises(Exception) as excinfo:
        await auth.reset_password(payload)
    assert "OTP expired" in str(excinfo.value) or "expired" in str(excinfo.value)


async def test_reset_password_success_updates_user_and_deletes_otp(fake_db):
    # Prepare valid OTP record
    fake_db.otp_tokens.find_one.return_value = {
        "email": "u@example.com",
        "otp": "444444",
        "expires_at": datetime.now(timezone.utc) + timedelta(minutes=5)
    }

    # Simulate update_one result with matched_count
    fake_update_result = SimpleNamespace(matched_count=1)
    fake_db.users.update_one.return_value = fake_update_result
    fake_db.otp_tokens.delete_one.return_value = AsyncMock()

    payload = PasswordReset(email="u@example.com", otp="444444", new_password="newpass123")
    res = await auth.reset_password(payload)
    assert isinstance(res, dict)
    assert "Password reset successfully" in res.get("message", "")

    fake_db.users.update_one.assert_called_once()
    fake_db.otp_tokens.delete_one.assert_called_once()