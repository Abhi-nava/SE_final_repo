from passlib.context import CryptContext
from jwt import encode, decode, ExpiredSignatureError, InvalidTokenError
from datetime import datetime, timedelta, timezone
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
