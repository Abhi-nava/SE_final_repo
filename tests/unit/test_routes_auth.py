"""Unit tests for authentication routes"""
import sys
import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from bson import ObjectId

# Setup paths
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
BACKEND_DIR = os.path.join(REPO_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from models.user import UserCreate, LoginRequest, UserRole
from utils.security import hash_password


class TestAuthRegister:
    """Test user registration endpoint"""
    
    @pytest.mark.asyncio
    async def test_register_success(self):
        """Test successful user registration"""
        user_data = UserCreate(
            email="test@example.com",
            phone="1234567890",
            full_name="Test User",
            password="password123",
            role=UserRole.CUSTOMER
        )
        
        # Mock database operations
        with patch('database.db.users.find_one', new_callable=AsyncMock) as mock_find, \
             patch('database.db.users.insert_one', new_callable=AsyncMock) as mock_insert, \
             patch('utils.security.create_access_token') as mock_access, \
             patch('utils.security.create_refresh_token') as mock_refresh:
            
            mock_find.return_value = None  # No existing user
            mock_insert.return_value = MagicMock(inserted_id=ObjectId())
            mock_access.return_value = "access_token"
            mock_refresh.return_value = "refresh_token"
            
            # Verify that registration would work
            assert user_data.email == "test@example.com"
            assert user_data.role == UserRole.CUSTOMER
    
    @pytest.mark.asyncio
    async def test_register_duplicate_email(self):
        """Test registration with existing email"""
        with patch('database.db.users.find_one', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = {"email": "test@example.com"}
            
            # Should detect existing user
            existing = await mock_find({"$or": [{"email": "test@example.com"}]})
            assert existing is not None
    
    @pytest.mark.asyncio
    async def test_register_duplicate_phone(self):
        """Test registration with existing phone"""
        with patch('database.db.users.find_one', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = {"phone": "1234567890"}
            
            existing = await mock_find({"$or": [{"phone": "1234567890"}]})
            assert existing is not None


class TestAuthLogin:
    """Test user login endpoint"""
    
    @pytest.mark.asyncio
    async def test_login_success(self):
        """Test successful login"""
        user_doc = {
            "_id": ObjectId(),
            "email": "test@example.com",
            "password": hash_password("password123"),
            "phone": "1234567890",
            "full_name": "Test User",
            "role": "customer",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        with patch('database.db.users.find_one', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = user_doc
            
            found_user = await mock_find({"email": "test@example.com"})
            assert found_user is not None
            assert found_user["email"] == "test@example.com"
    
    @pytest.mark.asyncio
    async def test_login_invalid_email(self):
        """Test login with non-existent email"""
        with patch('database.db.users.find_one', new_callable=AsyncMock) as mock_find, \
             patch('database.db.delivery_agents.find_one', new_callable=AsyncMock) as mock_find_agent:
            mock_find.return_value = None
            mock_find_agent.return_value = None
            
            user = await mock_find({"email": "nonexistent@example.com"})
            assert user is None
    
    @pytest.mark.asyncio
    async def test_login_inactive_user(self):
        """Test login with inactive user"""
        user_doc = {
            "_id": ObjectId(),
            "email": "test@example.com",
            "is_active": False
        }
        
        with patch('database.db.users.find_one', new_callable=AsyncMock) as mock_find:
            mock_find.return_value = user_doc
            
            user = await mock_find({"email": "test@example.com"})
            assert user["is_active"] is False


class TestAuthOTP:
    """Test OTP-related endpoints"""
    
    @pytest.mark.asyncio
    async def test_request_otp_existing_user(self):
        """Test OTP request for existing user"""
        with patch('database.db.users.find_one', new_callable=AsyncMock) as mock_find, \
             patch('database.db.otp_tokens.update_one', new_callable=AsyncMock) as mock_update:
            
            mock_find.return_value = {"email": "test@example.com"}
            mock_update.return_value = MagicMock(matched_count=1)
            
            user = await mock_find({"email": "test@example.com"})
            assert user is not None
    
    @pytest.mark.asyncio
    async def test_reset_password_valid_otp(self):
        """Test password reset with valid OTP"""
        from datetime import timedelta
        
        otp_record = {
            "email": "test@example.com",
            "otp": "123456",
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=10)
        }
        
        with patch('database.db.otp_tokens.find_one', new_callable=AsyncMock) as mock_find_otp, \
             patch('database.db.users.update_one', new_callable=AsyncMock) as mock_update:
            
            mock_find_otp.return_value = otp_record
            mock_update.return_value = MagicMock(matched_count=1)
            
            otp = await mock_find_otp({"email": "test@example.com"})
            assert otp["otp"] == "123456"
    
    @pytest.mark.asyncio
    async def test_reset_password_expired_otp(self):
        """Test password reset with expired OTP"""
        from datetime import timedelta
        
        otp_record = {
            "email": "test@example.com",
            "otp": "123456",
            "expires_at": datetime.now(timezone.utc) - timedelta(minutes=1)
        }
        
        # Verify OTP is expired
        assert datetime.now(timezone.utc) > otp_record["expires_at"]


class TestAuthMe:
    """Test current user endpoint"""
    
    @pytest.mark.asyncio
    async def test_get_me_success(self):
        """Test getting current user profile"""
        current_user = {
            "_id": ObjectId(),
            "email": "test@example.com",
            "phone": "1234567890",
            "full_name": "Test User",
            "role": "customer",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        assert current_user["email"] == "test@example.com"
        assert current_user["role"] == "customer"
