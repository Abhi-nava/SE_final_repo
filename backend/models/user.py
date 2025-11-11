from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    CUSTOMER = "customer"
    RESTAURANT = "restaurant"
    DELIVERY_AGENT = "delivery_agent"
    ADMIN = "admin"

class UserCreate(BaseModel):
    """User creation schema"""
    email: EmailStr
    phone: str = Field(..., min_length=10, max_length=15)
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.CUSTOMER

class UserUpdate(BaseModel):
    """User update schema"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None

class User2FASettings(BaseModel):
    """2FA settings for user"""
    is_enabled: bool = False
    secret_key: Optional[str] = None
    email_verified: bool = False

class UserResponse(BaseModel):
    """User response schema"""
    id: str = Field(alias="_id")
    email: str
    phone: str
    full_name: str
    role: UserRole
    address: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool = True
    two_factor_auth: User2FASettings = User2FASettings()
    
    class Config:
        populate_by_name = True

class LoginRequest(BaseModel):
    """Login request schema"""
    email: str
    password: str

class TokenResponse(BaseModel):
    """Token response schema"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse

class OTPVerification(BaseModel):
    """OTP verification schema"""
    email: str
    otp: str
    is_login_attempt: bool = False  # To distinguish between login and other OTP verifications

class PasswordReset(BaseModel):
    """Password reset schema"""
    email: str
    new_password: str = Field(..., min_length=8)
    otp: str

class Login2FAResponse(BaseModel):
    """Response for login when 2FA is required"""
    requires_2fa: bool = True
    temp_token: str
    message: str = "2FA verification required"

class TwoFAVerifyRequest(BaseModel):
    """2FA verification request"""
    temp_token: str
    otp: str
