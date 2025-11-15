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


def test_hash_password():
    """Test password hashing using SHA-256"""
    password = "testpassword123"
    hashed = hash_password(password)
    
    # SHA-256 produces 64 character hex string
    assert len(hashed) == 64
    assert isinstance(hashed, str)
    
    # Same password should produce same hash
    hashed2 = hash_password(password)
    assert hashed == hashed2
    
    # Different passwords should produce different hashes
    different = hash_password("differentpassword")
    assert hashed != different


def test_verify_password():
    """Test password verification (currently uses plain comparison)"""
    password = "mypassword"
    
    # verify_password in current implementation compares plain text
    # This matches the actual usage in auth.py where passwords are stored plain
    assert verify_password(password, password) is True
    
    # Different passwords should not verify
    assert verify_password(password, "wrongpassword") is False
    
    # Empty password should not verify against non-empty
    assert verify_password("", password) is False


def test_create_access_token():
    """Test access token creation"""
    data = {"email": "test@example.com", "sub": "user123"}
    token = create_access_token(data)
    
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Token should be decodable
    payload = decode_token(token)
    assert payload is not None
    assert payload["email"] == data["email"]
    assert payload["sub"] == data["sub"]
    assert "exp" in payload


def test_create_access_token_custom_expiry():
    """Test access token with custom expiration"""
    data = {"email": "test@example.com"}
    expires_delta = timedelta(minutes=5)
    token = create_access_token(data, expires_delta=expires_delta)
    
    payload = decode_token(token)
    assert payload is not None
    
    # Check expiration is approximately correct (within 10 seconds)
    exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    expected_exp = datetime.now(timezone.utc) + expires_delta
    time_diff = abs((exp_time - expected_exp).total_seconds())
    assert time_diff < 10


def test_create_refresh_token():
    """Test refresh token creation"""
    data = {"email": "refresh@example.com", "sub": "user456"}
    token = create_refresh_token(data)
    
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Token should be decodable
    payload = decode_token(token)
    assert payload is not None
    assert payload["email"] == data["email"]
    assert payload["sub"] == data["sub"]
    assert "exp" in payload


def test_decode_token_valid():
    """Test decoding a valid token"""
    data = {"email": "decode@example.com", "role": "customer"}
    token = create_access_token(data)
    
    payload = decode_token(token)
    assert payload is not None
    assert payload["email"] == data["email"]
    assert payload["role"] == data["role"]


def test_decode_token_invalid():
    """Test decoding an invalid token"""
    invalid_token = "invalid.token.string"
    payload = decode_token(invalid_token)
    assert payload is None


def test_decode_token_expired():
    """Test decoding an expired token"""
    data = {"email": "expired@example.com"}
    # Create token that expires immediately
    expires_delta = timedelta(seconds=-1)
    token = create_access_token(data, expires_delta=expires_delta)
    
    # Should return None for expired token
    payload = decode_token(token)
    assert payload is None


def test_generate_otp():
    """Test OTP generation"""
    otp = generate_otp()
    
    # Should be a 6-digit string
    assert isinstance(otp, str)
    assert len(otp) == 6
    assert otp.isdigit()
    
    # Should be in valid range
    otp_int = int(otp)
    assert 100000 <= otp_int <= 999999


def test_generate_otp_uniqueness():
    """Test that OTP generation produces different values"""
    otps = [generate_otp() for _ in range(100)]
    
    # Should produce mostly unique values (allowing some duplicates by chance)
    unique_otps = set(otps)
    assert len(unique_otps) > 50  # At least 50% unique


def test_token_data_preservation():
    """Test that all data in token is preserved through encode/decode cycle"""
    data = {
        "email": "full@example.com",
        "sub": "12345",
        "role": "admin",
        "custom_field": "custom_value"
    }
    
    token = create_access_token(data)
    payload = decode_token(token)
    
    assert payload is not None
    for key, value in data.items():
        assert payload[key] == value
