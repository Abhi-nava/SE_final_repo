from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from utils.security import decode_token
from fastapi import WebSocket



from jose import JWTError, jwt
from database import db


security = HTTPBearer()
SECRET_KEY="your-secret-key-change-this"
ADMIN_ROLE = "admin"
CUSTOMER_ROLE = "customer"
RESTAURANT_ROLE = "restaurant"
DELIVERY_AGENT_ROLE = "delivery_agent"

ALGORITHM= "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
REFRESH_TOKEN_EXPIRE_DAYS: int = 7



async def get_current_user_ws(websocket: WebSocket):
    """Authenticate WebSocket connection using token in query params"""
    from database import db
    token = websocket.query_params.get("token")

    if not token:
        await websocket.close(code=4001, reason="Missing authentication token")
        return None

    payload = decode_token(token)
    if not payload:
        await websocket.close(code=4002, reason="Invalid or expired token")
        return None

    email = payload.get("email")
    if not email:
        await websocket.close(code=4003, reason="Invalid token payload")
        return None

    user = await db.users.find_one({"email": email})
    if not user:
        await websocket.close(code=4004, reason="User not found")
        return None

    return user


# async def get_current_user_http(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     """Authenticate HTTP requests using Bearer token from Authorization header"""
#     from database import db
    
#     print(f"[DEBUG] Credentials received: {credentials}")  # ADD THIS
    
#     token = credentials.credentials if credentials else None
#     if not token:
#         print("[DEBUG] No token provided")  # ADD THIS
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Missing authentication token"
#         )
    
#     payload = decode_token(token)
#     print(f"[DEBUG] Decoded payload: {payload}")  # ADD THIS
    
#     if not payload:
#         print("[DEBUG] Invalid token")  # ADD THIS
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid or expired token"
#         )
    
#     email = payload.get("email")
#     print(f"[DEBUG] Email from token: {email}")  # ADD THIS
    
#     if not email:
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Invalid token payload"
#         )
    
#     user = await db.users.find_one({"email": email})
#     user["_id"]=str(payload.get("sub",""))
#     print(f"[DEBUG] User found: {user is not None}")  # ADD THIS
#     print(f"[DEBUG] User role: {user.get('role') if user else 'N/A'}")  # ADD THIS
#     print(f"[DEBUG] User: {user}")
#     if not user:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,  # <-- THIS IS YOUR 404!
#             detail="User not found"
#         )
    
#     return user




async def get_current_user_http(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Dependency to get current authenticated user for HTTP requests.
    Returns user dict with _id as string (NOT ObjectId).
    """
    print(f"\n[DEPENDENCY DEBUG] ===== get_current_user_http called =====")
    print(f"[DEPENDENCY DEBUG] Credentials: {credentials}")
    
    try:
        token = credentials.credentials
        print(f"[DEPENDENCY DEBUG] Token (first 50 chars): {token[:50]}...")
        
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"[DEPENDENCY DEBUG] Decoded payload: {payload}")
        
        # Get email from payload (adjust field name if different)
        email = payload.get("email") or payload.get("sub")
        print(f"[DEPENDENCY DEBUG] Email from token: {email}")
        
        if email is None:
            print(f"[DEPENDENCY DEBUG] ERROR: No email in token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing email"
            )
        
        # Find user in database
        user = await db.users.find_one({"email": email})
        print(f"[DEPENDENCY DEBUG] User found: {user is not None}")
        
        if user is None:
            print(f"[DEPENDENCY DEBUG] ERROR: User not found in database")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # ✅ CRITICAL: Convert _id to string for consistency
        # This ensures all comparisons work correctly
        user["_id"] = str(user["_id"])
        
        print(f"[DEPENDENCY DEBUG] User _id: {user['_id']} (type: {type(user['_id'])})")
        print(f"[DEPENDENCY DEBUG] User role: {user.get('role')}")
        print(f"[DEPENDENCY DEBUG] Returning user successfully\n")
        
        return user
        
    except JWTError as e:
        print(f"[DEPENDENCY DEBUG] JWT Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[DEPENDENCY DEBUG] Unexpected error: {str(e)}")
        import traceback
        print(f"[DEPENDENCY DEBUG] Traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )


async def get_current_user_http_d(
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    """
    Dependency to get current authenticated user for HTTP requests.
    Returns user dict with _id as string (NOT ObjectId).
    """
    print(f"\n[DEPENDENCY DEBUG] ===== get_current_user_http called =====")
    print(f"[DEPENDENCY DEBUG] Credentials: {credentials}")
    
    try:
        token = credentials.credentials
        print(f"[DEPENDENCY DEBUG] Token (first 50 chars): {token[:50]}...")
        
        # Decode JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"[DEPENDENCY DEBUG] Decoded payload: {payload}")
        
        # Get email from payload (adjust field name if different)
        email = payload.get("email") or payload.get("sub")
        print(f"[DEPENDENCY DEBUG] Email from token: {email}")
        
        if email is None:
            print(f"[DEPENDENCY DEBUG] ERROR: No email in token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing email"
            )
        
        # Find user in database
        user = await db.users.find_one({"email": email})
        print(f"[DEPENDENCY DEBUG] User found: {user is not None}")
        
        if user is None:
            print(f"[DEPENDENCY DEBUG] ERROR: User not found in database")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # ✅ CRITICAL: Convert _id to string for consistency
        # This ensures all comparisons work correctly
        user["_id"] = str(user["_id"])
        
        print(f"[DEPENDENCY DEBUG] User _id: {user['_id']} (type: {type(user['_id'])})")
        print(f"[DEPENDENCY DEBUG] User role: {user.get('role')}")
        print(f"[DEPENDENCY DEBUG] Returning user successfully\n")
        
        return user
        
    except JWTError as e:
        print(f"[DEPENDENCY DEBUG] JWT Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    except HTTPException:
        raise
    except Exception as e:
        print(f"[DEPENDENCY DEBUG] Unexpected error: {str(e)}")
        import traceback
        print(f"[DEPENDENCY DEBUG] Traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )



async def get_current_customer(current_user=Depends(get_current_user_http)):
    """Dependency for customer-only endpoints"""
    if current_user.get("role") != CUSTOMER_ROLE:
        print(f"[DEBUG] Access denied for user role: {current_user.get('role')}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only customers can access this endpoint"
        )
    return current_user


async def get_current_restaurant_owner(current_user=Depends(get_current_user_http)):
    """Dependency for restaurant owner endpoints"""
    if current_user.get("role") != RESTAURANT_ROLE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only restaurant owners can access this endpoint"
        )
    return current_user


async def get_current_delivery_agent(current_user=Depends(get_current_user_http)):
    """Dependency for delivery agent endpoints"""
    if current_user.get("role") != DELIVERY_AGENT_ROLE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only delivery agents can access this endpoint"
        )
    return current_user


async def get_current_admin(current_user=Depends(get_current_user_http)):
    """Dependency for admin-only endpoints"""
    if current_user.get("role") != ADMIN_ROLE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can access this endpoint"
        )
    return current_user
