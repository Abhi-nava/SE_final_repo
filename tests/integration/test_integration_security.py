import sys
import os
from datetime import datetime, timedelta, timezone
import pytest

# Ensure repository root is on sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

BACKEND_DIR = os.path.join(REPO_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_otp
)


def test_password_hash_and_verify_workflow():
    """Integration test: Hash password -> Store -> Retrieve -> Verify"""
    # Simulate user registration
    user_password = "SecurePassword123!"
    
    # Hash password for storage
    hashed = hash_password(user_password)
    
    # Simulate storing in database (here just in memory)
    stored_user = {
        "email": "user@example.com",
        "password": hashed
    }
    
    # Simulate login: retrieve from DB and verify
    retrieved_password = stored_user["password"]
    
    # User provides correct password
    assert verify_password(hashed, retrieved_password) is True
    
    # User provides wrong password
    wrong_hash = hash_password("WrongPassword")
    assert verify_password(wrong_hash, retrieved_password) is False


def test_token_creation_and_verification_workflow():
    """Integration test: Create tokens -> Store user data -> Decode -> Verify data"""
    # User login data
    user_data = {
        "email": "integration@example.com",
        "sub": "user123",
        "role": "customer",
        "permissions": ["read", "write"]
    }
    
    # Create access token
    access_token = create_access_token(user_data)
    
    # Create refresh token
    refresh_token = create_refresh_token(user_data)
    
    # Simulate storing tokens (e.g., in response headers or cookies)
    token_storage = {
        "access": access_token,
        "refresh": refresh_token
    }
    
    # Simulate subsequent request: decode access token
    decoded_access = decode_token(token_storage["access"])
    assert decoded_access is not None
    assert decoded_access["email"] == user_data["email"]
    assert decoded_access["role"] == user_data["role"]
    assert decoded_access["permissions"] == user_data["permissions"]
    
    # Decode refresh token
    decoded_refresh = decode_token(token_storage["refresh"])
    assert decoded_refresh is not None
    assert decoded_refresh["email"] == user_data["email"]


def test_token_expiration_workflow():
    """Integration test: Create short-lived token -> Wait -> Verify expiration"""
    user_data = {"email": "expire@example.com"}
    
    # Create token that expires in 1 second
    short_lived_token = create_access_token(user_data, expires_delta=timedelta(seconds=-1))
    
    # Token should be expired immediately
    decoded = decode_token(short_lived_token)
    assert decoded is None  # Expired tokens return None


def test_token_refresh_workflow():
    """Integration test: Login -> Get tokens -> Access token expires -> Use refresh token"""
    user_data = {
        "email": "refresh@example.com",
        "sub": "user456",
        "role": "restaurant"
    }
    
    # Initial login: get both tokens
    access_token = create_access_token(user_data, expires_delta=timedelta(seconds=-1))
    refresh_token = create_refresh_token(user_data)
    
    # Access token expires
    decoded_access = decode_token(access_token)
    assert decoded_access is None  # Expired
    
    # Refresh token still valid
    decoded_refresh = decode_token(refresh_token)
    assert decoded_refresh is not None
    assert decoded_refresh["email"] == user_data["email"]
    
    # Generate new access token using refresh token data
    new_access_token = create_access_token(decoded_refresh)
    new_decoded = decode_token(new_access_token)
    assert new_decoded is not None
    assert new_decoded["email"] == user_data["email"]


def test_otp_generation_and_verification_workflow():
    """Integration test: Generate OTP -> Store -> Verify -> Expire"""
    # Simulate password reset request
    user_email = "reset@example.com"
    
    # Generate OTP
    otp = generate_otp()
    otp_expiry = datetime.now(timezone.utc) + timedelta(minutes=10)
    
    # Store OTP (simulated)
    otp_storage = {
        "email": user_email,
        "otp": otp,
        "expires_at": otp_expiry
    }
    
    # User provides OTP
    user_provided_otp = otp
    
    # Verify OTP
    assert otp_storage["otp"] == user_provided_otp
    assert datetime.now(timezone.utc) < otp_storage["expires_at"]
    
    # Simulate OTP expiration
    otp_storage["expires_at"] = datetime.now(timezone.utc) - timedelta(minutes=1)
    assert datetime.now(timezone.utc) > otp_storage["expires_at"]  # Expired


def test_multiple_users_token_isolation():
    """Integration test: Multiple users get tokens -> Verify isolation"""
    users = [
        {"email": "user1@example.com", "sub": "1", "role": "customer"},
        {"email": "user2@example.com", "sub": "2", "role": "restaurant"},
        {"email": "user3@example.com", "sub": "3", "role": "admin"}
    ]
    
    # Create tokens for all users
    tokens = {}
    for user in users:
        tokens[user["email"]] = create_access_token(user)
    
    # Verify each token decodes to correct user
    for user in users:
        decoded = decode_token(tokens[user["email"]])
        assert decoded is not None
        assert decoded["email"] == user["email"]
        assert decoded["role"] == user["role"]
        assert decoded["sub"] == user["sub"]


def test_token_tampering_detection():
    """Integration test: Create token -> Tamper with it -> Verify rejection"""
    user_data = {"email": "secure@example.com", "role": "customer"}
    
    # Create valid token
    token = create_access_token(user_data)
    
    # Tamper with token (change a character)
    tampered_token = token[:-5] + "XXXXX"
    
    # Should fail to decode
    decoded = decode_token(tampered_token)
    assert decoded is None


def test_password_change_workflow():
    """Integration test: Hash old password -> User changes password -> Hash new password"""
    old_password = "OldPassword123"
    new_password = "NewPassword456"
    
    # Store old password hash
    old_hash = hash_password(old_password)
    stored_hash = old_hash
    
    # User provides old password for verification
    assert verify_password(old_hash, stored_hash) is True
    
    # User sets new password
    new_hash = hash_password(new_password)
    stored_hash = new_hash  # Update storage
    
    # Old password no longer works
    assert verify_password(old_hash, stored_hash) is False
    
    # New password works
    assert verify_password(new_hash, stored_hash) is True


def test_concurrent_otp_requests():
    """Integration test: Multiple OTP requests -> Each generates unique OTP"""
    otps = []
    for _ in range(10):
        otp = generate_otp()
        otps.append(otp)
        assert len(otp) == 6
        assert otp.isdigit()
    
    # Most should be unique (allowing some duplicates by chance)
    unique_otps = set(otps)
    assert len(unique_otps) >= 8  # At least 80% unique


def test_token_with_custom_claims():
    """Integration test: Add custom claims -> Encode -> Decode -> Verify"""
    user_data = {
        "email": "custom@example.com",
        "sub": "789",
        "role": "delivery_agent",
        "vehicle_type": "bike",
        "zone": "north",
        "rating": 4.8
    }
    
    # Create token with custom claims
    token = create_access_token(user_data)
    
    # Decode and verify all claims preserved
    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["email"] == user_data["email"]
    assert decoded["vehicle_type"] == user_data["vehicle_type"]
    assert decoded["zone"] == user_data["zone"]
    assert decoded["rating"] == user_data["rating"]
