from passlib.context import CryptContext
from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta, timezone
import json
import secrets
from typing import Dict, Any, Optional
from config import settings
from typing import Optional, Dict, Any
import os
import hashlib

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Compare SHA-256 hashes"""
    return plain_password == hashed_password

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(data: Dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        return decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except (ExpiredSignatureError, InvalidTokenError):
        return None

def generate_otp() -> str:
    """Generate 6-digit OTP"""
    import random
    return str(random.randint(100000, 999999))

def generate_2fa_token() -> str:
    """Generate a secure random token for 2FA"""
    return secrets.token_urlsafe(32)

class TwoFactorAuthToken:
    """Handles 2FA token generation and validation"""
    
    @staticmethod
    def create_temp_token(user_id: str, email: str, expires_in: int = 300) -> str:
        """Create a temporary token for 2FA verification"""
        payload = {
            'sub': user_id,
            'email': email,
            'exp': datetime.now(timezone.utc) + timedelta(seconds=expires_in),
            'type': '2fa_temp',
            'otp': generate_otp()
        }
        return encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    
    @staticmethod
    def verify_temp_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify temporary 2FA token and return payload if valid"""
        try:
            payload = decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get('type') != '2fa_temp':
                return None
            return payload
        except (ExpiredSignatureError, InvalidTokenError):
            return None
    
    @staticmethod
    def verify_otp(token: str, otp: str) -> bool:
        """Verify if the provided OTP matches the one in the token"""
        try:
            payload = decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload.get('otp') == otp
        except (ExpiredSignatureError, InvalidTokenError):
            return False

class PasswordResetToken:
    @staticmethod
    def create_temp_token(email: str, expires_in: int = 300) -> str:
        payload = {
            'email': email,
            'exp': datetime.now(timezone.utc) + timedelta(seconds=expires_in),
            'type': 'reset_temp',
            'otp': generate_otp()
        }
        return encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def verify_temp_token(token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get('type') != 'reset_temp':
                return None
            return payload
        except (ExpiredSignatureError, InvalidTokenError):
            return None

    @staticmethod
    def verify_otp(token: str, otp: str) -> bool:
        try:
            payload = decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload.get('type') == 'reset_temp' and payload.get('otp') == otp
        except (ExpiredSignatureError, InvalidTokenError):
            return False

    @staticmethod
    def create_reset_session_token(email: str, expires_in: int = 900) -> str:
        payload = {
            'email': email,
            'exp': datetime.now(timezone.utc) + timedelta(seconds=expires_in),
            'type': 'reset_session'
        }
        return encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def verify_reset_session_token(token: str) -> Optional[Dict[str, Any]]:
        try:
            payload = decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            if payload.get('type') != 'reset_session':
                return None
            return payload
        except (ExpiredSignatureError, InvalidTokenError):
            return None
