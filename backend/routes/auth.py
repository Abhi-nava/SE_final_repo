from fastapi import APIRouter, HTTPException, status, Depends
from models.user import (
    UserCreate, UserResponse, LoginRequest, TokenResponse,
    OTPVerification, PasswordReset, UserRole, Login2FAResponse, TwoFAVerifyRequest
)
from utils.security import (
    hash_password, verify_password, create_access_token, 
    create_refresh_token, generate_otp, decode_token,
    TwoFactorAuthToken, PasswordResetToken
)
from utils.email import send_otp_email
from utils.dependencies import get_current_user_http
from database import db
from bson import ObjectId
from datetime import datetime, timezone, timedelta
import logging
from typing import Optional, Dict, Any, Union

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", response_model=Login2FAResponse)
async def register(user_data: UserCreate):
    """Register a new user (always requires 2FA to activate session)."""
    # Check if user already exists
    existing_user = await db.users.find_one({"$or": [{"email": user_data.email}, {"phone": user_data.phone}]})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or phone already registered"
        )
    
    # Create new user
    # Frontend already sends SHA-256 hashed password. Store as-is for compatibility.
    now = datetime.now(timezone.utc)
    
    user_doc = {
        "email": user_data.email,
        "phone": user_data.phone,
        "full_name": user_data.full_name,
        "password": user_data.password,
        "role": user_data.role.value,
        "is_active": True,
        "is_email_verified": False,
        "created_at": now,
        "updated_at": now
    }
    
    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    
    # Issue temporary 2FA token
    temp_token = TwoFactorAuthToken.create_temp_token(
        user_id=str(result.inserted_id),
        email=user_data.email
    )

    # Print OTP to console for testing
    token_data = TwoFactorAuthToken.verify_temp_token(temp_token)
    if token_data:
        print(f"\n=== 2FA OTP for {user_data.email} (signup) ===")
        print(f"OTP: {token_data.get('otp')}")
        print("This OTP is valid for 5 minutes")
        print("==============================\n")
        try:
            send_otp_email(user_data.email, token_data.get("otp", ""), purpose="Signup")
        except Exception as e:
            logger.warning(f"Failed to send OTP email (signup) to {user_data.email}: {e}")

    return Login2FAResponse(
        temp_token=temp_token,
        message="2FA verification required to complete signup. Check your email for the OTP."
    )

async def _get_user_by_email(email: str):
    """Helper to get user by email from either users or delivery_agents collection"""
    user = await db.users.find_one({"email": email})
    if not user:
        user = await db.delivery_agents.find_one({"email": email})
    return user

@router.post("/verify-2fa", response_model=TokenResponse)
async def verify_2fa(verify_data: TwoFAVerifyRequest):
    """Verify 2FA OTP using a temporary token, then issue access/refresh tokens."""
    # Verify the temporary token
    token_data = TwoFactorAuthToken.verify_temp_token(verify_data.temp_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired 2FA session"
        )

    # Get the user from token payload
    user = await _get_user_by_email(token_data.get('email'))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Verify OTP against temp token payload
    if not TwoFactorAuthToken.verify_otp(verify_data.temp_token, verify_data.otp):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code"
        )
    
    # Generate tokens
    access_token = create_access_token({
        "sub": str(user["_id"]),
        "email": user["email"],
        "role": user.get("role", "customer")
    })
    
    refresh_token = create_refresh_token({
        "sub": str(user["_id"]),
        "email": user["email"]
    })
    
    # Format response
    user_response = UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        phone=user["phone"],
        full_name=user["full_name"],
        role=user.get("role", "customer"),
        created_at=user["created_at"],
        updated_at=user["updated_at"],
        is_active=user.get("is_active", True)
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_response
    )

@router.post("/login", response_model=Login2FAResponse)
async def login(login_data: LoginRequest):
    """Login step 1: validate credentials, always require 2FA, return temp token."""
    # Fetch user by email
    user = await _get_user_by_email(login_data.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password (supports legacy 'password' field and new 'password_hash')
    stored_hash = user.get("password_hash") or user.get("password", "")
    if not verify_password(login_data.password, stored_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    # Always require 2FA: generate temp token and print OTP to console for testing
    temp_token = TwoFactorAuthToken.create_temp_token(
        user_id=str(user["_id"]),
        email=user["email"]
    )

    token_data = TwoFactorAuthToken.verify_temp_token(temp_token)
    if token_data:
        print(f"\n=== 2FA OTP for {user['email']} ===")
        print(f"OTP: {token_data.get('otp')}")
        print("This OTP is valid for 5 minutes")
        print("==============================\n")
        try:
            send_otp_email(user["email"], token_data.get("otp", ""), purpose="Login")
        except Exception as e:
            logger.warning(f"Failed to send OTP email (login) to {user['email']}: {e}")

    return Login2FAResponse(
        temp_token=temp_token,
        message="2FA verification required. Check your email for the OTP."
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_user_http)):
    """Get current user profile"""
    return UserResponse(
        id=str(current_user["_id"]),
        email=current_user["email"],
        phone=current_user["phone"],
        full_name=current_user["full_name"],
        role=current_user["role"],
        address=current_user.get("address"),
        is_active=current_user.get("is_active", True),
        created_at=current_user["created_at"],
        updated_at=current_user["updated_at"]
    )

@router.post("/request-otp")
async def request_otp(email: str):
    """Request OTP for password reset"""
    user = await db.users.find_one({"email": email})
    if not user:
        # Don't reveal if user exists
        return {"message": "If user exists, OTP will be sent to email"}
    
    otp = generate_otp()
    otp_expiry = datetime.now(timezone.utc)
    from datetime import timedelta
    otp_expiry = otp_expiry + timedelta(minutes=10)
    
    await db.otp_tokens.update_one(
        {"email": email},
        {
            "$set": {
                "otp": otp,
                "created_at": datetime.now(timezone.utc),
                "expires_at": otp_expiry
            }
        },
        upsert=True
    )
    
    # Send OTP via email (with safe fallback to logs)
    try:
        sent = send_otp_email(email, otp, purpose="Password Reset")
        if not sent:
            logger.info(f"SMTP not configured; OTP for {email}: {otp}")
    except Exception as e:
        logger.warning(f"Failed to send OTP email (password reset) to {email}: {e}. OTP: {otp}")
    
    return {"message": "OTP sent to email"}

@router.post("/reset-password")
async def reset_password(reset_data: PasswordReset):
    """Reset password with OTP verification"""
    # Verify OTP
    otp_record = await db.otp_tokens.find_one({"email": reset_data.email})
    
    if not otp_record or otp_record.get("otp") != reset_data.otp:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP"
        )
    
    if datetime.now(timezone.utc) > otp_record.get("expires_at"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP expired"
        )
    
    # Update password
    hashed_password = hash_password(reset_data.new_password)
    result = await db.users.update_one(
        {"email": reset_data.email},
        {
            "$set": {
                "password_hash": hashed_password,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )
    
    # Delete OTP
    await db.otp_tokens.delete_one({"email": reset_data.email})
    
    if result.matched_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "Password reset successfully"}

@router.post("/forgot-password/start")
async def forgot_password_start(payload: Dict[str, Any]):
    """Start password reset: create reset temp token with OTP and email it."""
    email = (payload or {}).get("email")
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is required")

    # Always respond the same even if user doesn't exist
    user = await _get_user_by_email(email)

    # Create a reset temp token regardless; only useful if email exists
    reset_temp_token = PasswordResetToken.create_temp_token(email=email)

    token_data = PasswordResetToken.verify_temp_token(reset_temp_token)
    if token_data and user:
        # Debug: print OTP to terminal like 2FA flow
        print(f"\n=== Password Reset OTP for {email} ===")
        print(f"OTP: {token_data.get('otp')}")
        print("This OTP is valid for 5 minutes")
        print("==============================\n")
        try:
            send_otp_email(email, token_data.get("otp", ""), purpose="Password Reset")
        except Exception as e:
            logger.warning(f"Failed to send OTP email (forgot-password) to {email}: {e}")

    return {
        "reset_temp_token": reset_temp_token,
        "message": "If the email exists, an OTP has been sent."
    }

@router.post("/forgot-password/verify")
async def forgot_password_verify(payload: Dict[str, Any]):
    """Verify reset OTP and return a short-lived reset session token."""
    reset_temp_token = (payload or {}).get("reset_temp_token")
    otp = (payload or {}).get("otp")
    if not reset_temp_token or not otp:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="reset_temp_token and otp are required")

    token_data = PasswordResetToken.verify_temp_token(reset_temp_token)
    if not token_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset session")

    if not PasswordResetToken.verify_otp(reset_temp_token, otp):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")

    email = token_data.get("email")
    # Issue reset session token to allow password change without OTP
    reset_session_token = PasswordResetToken.create_reset_session_token(email=email)
    return {"reset_session_token": reset_session_token}

@router.post("/forgot-password/reset", response_model=TokenResponse)
async def forgot_password_reset(payload: Dict[str, Any]):
    """Set new password using reset session token, then auto-login (bypass 2FA once)."""
    reset_session_token = (payload or {}).get("reset_session_token")
    new_password = (payload or {}).get("new_password")
    if not reset_session_token or not new_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="reset_session_token and new_password are required")

    session_data = PasswordResetToken.verify_reset_session_token(reset_session_token)
    if not session_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset session")

    email = session_data.get("email")
    user = await _get_user_by_email(email)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Update password (frontend already SHA-256 hashes; we re-hash to align with current verify function)
    hashed = hash_password(new_password)
    await db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"password_hash": hashed, "updated_at": datetime.now(timezone.utc)}}
    )

    # Auto-login: issue tokens directly (skip 2FA now). Next logins still go through normal flow.
    access_token = create_access_token({
        "sub": str(user["_id"]),
        "email": user["email"],
        "role": user.get("role", "customer")
    })
    refresh_token = create_refresh_token({
        "sub": str(user["_id"]),
        "email": user["email"]
    })

    user_response = UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        phone=user["phone"],
        full_name=user["full_name"],
        role=user.get("role", "customer"),
        created_at=user["created_at"],
        updated_at=user["updated_at"],
        is_active=user.get("is_active", True)
    )

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_response
    )
