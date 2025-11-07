from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional
import logging

# Import routers
from routes import auth, customers, restaurants, orders, delivery, ratings, websocket, admin
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# MongoDB connection
MONGO_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "food_delivery")

db_client: Optional[AsyncIOMotorClient] = None
db: Optional[AsyncIOMotorDatabase] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global db_client, db
    db_client = AsyncIOMotorClient(MONGO_URL)
    db = db_client[DATABASE_NAME]
    
    # Create indexes
    try:
        # Users collection indexes
        await db.users.create_index("email", unique=True)
        await db.users.create_index("phone", unique=True)
        
        # Restaurants collection indexes
        await db.restaurants.create_index("owner_id")
        await db.restaurants.create_index("location")
        
        # Orders collection indexes
        await db.orders.create_index("customer_id")
        await db.orders.create_index("restaurant_id")
        await db.orders.create_index("delivery_agent_id")
        await db.orders.create_index("status")
        await db.orders.create_index("created_at", expireAfterSeconds=2592000)  # 30 days TTL
        
        # Menu items indexes
        await db.menu_items.create_index("restaurant_id")
        
        # Ratings indexes
        await db.ratings.create_index("order_id")
        await db.ratings.create_index("rated_restaurant")
        await db.ratings.create_index("rated_delivery_agent")
        
        logger.info("Database indexes created successfully")
    except Exception as e:
        logger.error(f"Error creating indexes: {e}")
    
    yield
    
    # Shutdown
    if db_client:
        db_client.close()

app = FastAPI(
    title="Food Delivery API",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS origins and trusted hosts (include both localhost and 127.0.0.1 by default)
_cors_env = os.getenv("CORS_ORIGINS")
if _cors_env:
    _allow_origins = [o.strip() for o in _cors_env.split(",") if o.strip()]
else:
    # Include both hostname and 127.0.0.1 which browsers commonly use during dev
    _allow_origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware (TrustedHost)
_hosts_env = os.getenv("ALLOWED_HOSTS")
if _hosts_env:
    _allowed_hosts = [h.strip() for h in _hosts_env.split(",") if h.strip()]
else:
    _allowed_hosts = ["localhost", "127.0.0.1"]

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=_allowed_hosts
)



# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(customers.router, prefix="/api/customers", tags=["Customers"])
app.include_router(restaurants.router, prefix="/api/restaurants", tags=["Restaurants"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(delivery.router, prefix="/api/delivery", tags=["Delivery"])
app.include_router(ratings.router, prefix="/api/ratings", tags=["Ratings"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])  # Added admin router
app.include_router(websocket.router, tags=["WebSocket"])

print("\n[DEBUG] Registered routes:")
for route in app.routes:
    if hasattr(route, 'methods') and hasattr(route, 'path'):
        print(f"  {route.methods} {route.path}")
print("\n")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Food Delivery API"}

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    # Build response and ensure CORS headers are present even for error responses.
    # Some middleware/hosts may return early for errors; explicitly set Access-Control-Allow-Origin
    # based on configured CORS_ORIGINS (fall back to wildcard if not set).
    # Use the configured origins list (if available) to set a compatible Access-Control-Allow-Origin
    try:
        origin_header = _allow_origins[0] if _allow_origins and len(_allow_origins) > 0 else "*"
    except NameError:
        # Fallback if variables aren't defined for some reason
        origin_header = os.getenv("CORS_ORIGINS", "*")

    response = JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail, "status": "error"}
    )
    # Set CORS headers to match CORSMiddleware behavior for error responses
    if origin_header:
        response.headers["Access-Control-Allow-Origin"] = origin_header
    else:
        response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Catch-all exception handler so error responses include CORS headers.

    Without this, uncaught exceptions produce 500 responses that lack
    Access-Control-Allow-Origin and browsers block the response.
    """
    logger.exception("Unhandled exception: %s", exc)

    try:
        origin_header = _allow_origins[0] if _allow_origins and len(_allow_origins) > 0 else "*"
    except NameError:
        origin_header = os.getenv("CORS_ORIGINS", "*")

    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "status": "error"},
    )

    # Mirror CORS middleware headers for the error response
    response.headers["Access-Control-Allow-Origin"] = origin_header if origin_header else "*"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"

    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000))
    )
