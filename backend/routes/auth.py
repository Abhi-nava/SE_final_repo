from fastapi import APIRouter, HTTPException, status, Depends
from models.user import (
    UserCreate, UserResponse, LoginRequest, TokenResponse, UserRole
)
from utils.security import hash_password, verify_password, create_access_token, create_refresh_token
from utils.dependencies import get_current_user_http
from database import db
from datetime import datetime, timezone
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/register", response_model=TokenResponse)
async def register(user_data: UserCreate):
    """Register a new user"""
    # Check if user already exists
    existing_user = await db.users.find_one({"$or": [{"email": user_data.email}, {"phone": user_data.phone}]})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or phone already registered"
        )
    
    # Create new user
    hashed_password = hash_password(user_data.password)
    now = datetime.now(timezone.utc)
    
    user_doc = {
        "email": user_data.email,
        "phone": user_data.phone,
        "full_name": user_data.full_name,
        "password_hash": hashed_password,
        "role": user_data.role.value,
        "is_active": True,
        "is_email_verified": False,
        "created_at": now,
        "updated_at": now
    }
    
    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    
    # Generate tokens
    access_token = create_access_token({"email": user_data.email, "sub": str(result.inserted_id)})
    refresh_token = create_refresh_token({"email": user_data.email, "sub": str(result.inserted_id)})
    
    # Format response
    user_response = UserResponse(
        id=str(result.inserted_id),
        email=user_data.email,
        phone=user_data.phone,
        full_name=user_data.full_name,
        role=user_data.role,
        created_at=now,
        updated_at=now
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_response
    )

@router.post("/login", response_model=TokenResponse)
async def login(login_data: LoginRequest):
    """Login user (no dev mode, DB-based only)"""
    # Fetch user by email
    user = await db.users.find_one({"email": login_data.email})
    print(f"Printing user {user}")

    
    if not user:
        user = await db.delivery_agents.find_one({"email": login_data.email})
        print(f"Printing user {user}")
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Cannot find user at all"
            )
    
    # Verify password (SHA256-based)
    if not verify_password(login_data.password, user.get("password", "")) :
        print(f"User: {user}")
        print(f"Sent Password: {login_data.password} ")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )

    # Generate tokens
    access_token = create_access_token({
        "email": user["email"],
        "sub": str(user["_id"]),
        "role": user.get("role", UserRole.CUSTOMER.value)
    })
    refresh_token = create_refresh_token({
        "email": user["email"],
        "sub": str(user["_id"]),
        "role": user.get("role", UserRole.CUSTOMER.value)
    })
    
    role = user.get("role", UserRole.CUSTOMER.value)
    print(f"Original role from DB: {user.get('role', 'N/A')}")
    print(f"Login successful for user {user['email']} with role: {role}")

    user_response = UserResponse(
        id=str(user["_id"]),
        email=user["email"],
        phone=user["phone"],
        full_name=user["full_name"],
        role=role,  
        created_at=user["created_at"],
        updated_at=user["updated_at"],
        is_active=user.get("is_active", True)
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=user_response
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

