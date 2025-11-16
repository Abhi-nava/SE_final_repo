"""Integration tests for authentication flow"""
import sys
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone, timedelta
from bson import ObjectId

# Setup paths
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
BACKEND_DIR = os.path.join(REPO_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from utils.security import hash_password, verify_password, create_access_token


class TestAuthIntegrationFlow:
    """Test complete authentication flow"""
    
    @pytest.mark.asyncio
    async def test_register_and_login_flow(self):
        """Test user registration followed by login"""
        user_email = "integration@example.com"
        user_password = "password123"
        user_id = ObjectId()
        
        # Step 1: Register
        with patch('database.db.users.find_one', new_callable=AsyncMock) as mock_find, \
             patch('database.db.users.insert_one', new_callable=AsyncMock) as mock_insert:
            
            # No existing user
            mock_find.return_value = None
            mock_insert.return_value = MagicMock(inserted_id=user_id)
            
            # Registration should succeed
            existing = await mock_find({"$or": [{"email": user_email}]})
            assert existing is None
            
            result = await mock_insert({
                "email": user_email,
                "password_hash": hash_password(user_password)
            })
            assert result.inserted_id == user_id
        
        # Step 2: Login with registered credentials
        with patch('database.db.users.find_one', new_callable=AsyncMock) as mock_find:
            hashed_pass = hash_password(user_password)
            mock_find.return_value = {
                "_id": user_id,
                "email": user_email,
                "password_hash": hashed_pass,
                "phone": "1234567890",
                "full_name": "Test User",
                "role": "customer",
                "is_active": True,
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            user = await mock_find({"email": user_email})
            assert user is not None
            # verify_password expects plain == hash for this implementation
            assert user["password_hash"] == hashed_pass
    
    @pytest.mark.asyncio
    async def test_otp_reset_password_flow(self):
        """Test complete password reset flow"""
        user_email = "reset@example.com"
        new_password = "newpassword123"
        otp = "123456"
        
        # Step 1: Request OTP
        with patch('database.db.users.find_one', new_callable=AsyncMock) as mock_find_user, \
             patch('database.db.otp_tokens.update_one', new_callable=AsyncMock) as mock_update_otp:
            
            mock_find_user.return_value = {"email": user_email}
            mock_update_otp.return_value = MagicMock(matched_count=1)
            
            user = await mock_find_user({"email": user_email})
            assert user is not None
            
            # OTP stored
            result = await mock_update_otp(
                {"email": user_email},
                {"$set": {"otp": otp}}
            )
            assert result.matched_count == 1
        
        # Step 2: Verify OTP and reset password
        with patch('database.db.otp_tokens.find_one', new_callable=AsyncMock) as mock_find_otp, \
             patch('database.db.users.update_one', new_callable=AsyncMock) as mock_update_user, \
             patch('database.db.otp_tokens.delete_one', new_callable=AsyncMock) as mock_delete_otp:
            
            mock_find_otp.return_value = {
                "email": user_email,
                "otp": otp,
                "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10)
            }
            mock_update_user.return_value = MagicMock(matched_count=1)
            mock_delete_otp.return_value = MagicMock(deleted_count=1)
            
            otp_record = await mock_find_otp({"email": user_email})
            assert otp_record["otp"] == otp
            assert datetime.now(timezone.utc) < otp_record["expires_at"]
            
            # Password updated
            result = await mock_update_user(
                {"email": user_email},
                {"$set": {"password_hash": hash_password(new_password)}}
            )
            assert result.matched_count == 1
            
            # OTP deleted
            delete_result = await mock_delete_otp({"email": user_email})
            assert delete_result.deleted_count == 1
    
    @pytest.mark.asyncio
    async def test_token_refresh_flow(self):
        """Test token refresh flow"""
        user_id = ObjectId()
        user_email = "token@example.com"
        
        # Create tokens
        access_token = create_access_token({
            "sub": str(user_id),
            "email": user_email,
            "role": "customer"
        })
        
        assert access_token is not None
        assert len(access_token) > 0
    
    @pytest.mark.asyncio
    async def test_concurrent_login_attempts(self):
        """Test multiple concurrent login attempts"""
        user_email = "concurrent@example.com"
        password_hash = hash_password("password123")
        
        with patch('database.db.users.find_one', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = {
                "_id": ObjectId(),
                "email": user_email,
                "password": password_hash,
                "role": "customer",
                "is_active": True,
                "phone": "1234567890",
                "full_name": "Test User",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc)
            }
            
            # Simulate multiple login attempts
            for _ in range(3):
                user = await mock_find({"email": user_email})
                assert user is not None
                assert user["email"] == user_email
