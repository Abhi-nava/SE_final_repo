import asyncio
import os
import pytest
import pytest_asyncio
from bson import ObjectId
from datetime import datetime, timezone
import httpx
import sys
from copy import deepcopy

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

BACKEND_DIR = os.path.join(REPO_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from main import app
import database as database_module
from routes import coupons as coupons_routes
from utils import dependencies as deps


pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture(scope="function")
async def client_and_db():
    # Create an in-memory database using dictionaries (namespaces/collections)
    class InMemoryDatabase:
        def __init__(self):
            self._collections = {}
        
        def __getitem__(self, name):
            if name not in self._collections:
                self._collections[name] = InMemoryCollection()
            return self._collections[name]
        
        def __getattr__(self, name):
            # Support attribute access like db.coupons
            return self[name]
    
    class InMemoryCollection:
        def __init__(self):
            self._documents = []
        
        def _match_document(self, doc, filter):
            """Check if document matches filter"""
            for key, value in filter.items():
                doc_value = doc.get(key)
                
                # Handle None values in filter
                if value is None:
                    if doc_value is not None:
                        return False
                    continue
                
                # Handle case-insensitive string comparison for code
                if key == "code" and isinstance(value, str) and isinstance(doc_value, str):
                    if value.upper() != doc_value.upper():
                        return False
                elif doc_value != value:
                    return False
            return True
        
        async def find_one(self, filter):
            for doc in self._documents:
                if self._match_document(doc, filter):
                    result = deepcopy(doc)
                    # Ensure _id is ObjectId
                    if '_id' in result and not isinstance(result['_id'], ObjectId):
                        try:
                            result['_id'] = ObjectId(result['_id'])
                        except:
                            pass
                    return result
            return None
        
        def find(self, filter=None):
            # find() is synchronous in motor - returns cursor immediately
            if filter is None:
                filter = {}
            matching_docs = []
            for doc in self._documents:
                if self._match_document(doc, filter):
                    matching_docs.append(deepcopy(doc))
            return InMemoryCursor(matching_docs)
        
        async def insert_one(self, document):
            doc = deepcopy(document)
            # Ensure _id is set
            if '_id' not in doc:
                doc['_id'] = ObjectId()
            elif isinstance(doc['_id'], str):
                try:
                    doc['_id'] = ObjectId(doc['_id'])
                except:
                    doc['_id'] = ObjectId()
            
            self._documents.append(doc)
            return type('obj', (object,), {'inserted_id': doc['_id']})()
        
        async def update_one(self, filter, update):
            matched_count = 0
            modified_count = 0
            
            for doc in self._documents:
                if self._match_document(doc, filter):
                    matched_count = 1
                    # Handle $set operator
                    if '$set' in update:
                        for key, value in update['$set'].items():
                            if doc.get(key) != value:
                                doc[key] = value
                                modified_count = 1
                    break
            
            return type('obj', (object,), {
                'matched_count': matched_count,
                'modified_count': modified_count
            })()
        
        async def delete_many(self, filter):
            deleted_count = 0
            remaining = []
            for doc in self._documents:
                if self._match_document(doc, filter):
                    deleted_count += 1
                else:
                    remaining.append(doc)
            self._documents = remaining
            return type('obj', (object,), {'deleted_count': deleted_count})()
    
    class InMemoryCursor:
        def __init__(self, documents):
            self._documents = documents
        
        async def to_list(self, length):
            return list(self._documents)
    
    # Create the in-memory database
    async_test_db = InMemoryDatabase()
    
    # Override database in all places
    database_module.db = async_test_db
    coupons_routes.db = async_test_db
    # Also update the module-level db that routes import
    import database
    database.db = async_test_db
    # Update the local db variable in routes that use "from database import db"
    import routes.coupons as coupons_module
    setattr(coupons_module, 'db', async_test_db)

    # Use an allowed host to satisfy TrustedHostMiddleware (defaults to localhost/127.0.0.1)
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://localhost") as async_client:
        # pre-test cleanup to ensure isolation
        for name in ["coupons"]:
            await async_test_db[name].delete_many({})
        yield async_client, async_test_db
        # post-test cleanup while client/loop are still alive
        for name in ["coupons"]:
            await async_test_db[name].delete_many({})


# Helper function for seeding coupons
async def seed_coupon(db, code: str, discount_type: str = "flat", discount_value: float = 50.0, 
                     min_order: float = 100.0, max_discount: float = None, description: str = "Test coupon"):
    """Helper to create a test coupon"""
    coupon = {
        "code": code.upper(),
        "description": description,
        "minOrder": min_order,
        "discountType": discount_type,
        "discountValue": discount_value,
        "maxDiscount": max_discount
    }
    res = await db.coupons.insert_one(coupon)
    coupon["_id"] = res.inserted_id
    return coupon


async def test_validate_coupon_success_flat_discount(client_and_db):
    """Test successful coupon validation with flat discount"""
    client, test_db = client_and_db
    await seed_coupon(test_db, "FLAT50", "flat", 50.0, 100.0)
    
    payload = {
        "code": "FLAT50",
        "orderTotal": 150.0
    }
    
    res = await client.post("/api/coupons/validate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert data["coupon"]["code"] == "FLAT50"
    assert data["coupon"]["discountType"] == "flat"
    assert data["coupon"]["discountValue"] == 50.0
    assert data["discount"] == 50.0
    assert "successfully" in data["message"].lower()


async def test_validate_coupon_success_percentage_discount(client_and_db):
    """Test successful coupon validation with percentage discount"""
    client, test_db = client_and_db
    await seed_coupon(test_db, "SAVE20", "percentage", 20.0, 100.0)
    
    payload = {
        "code": "SAVE20",
        "orderTotal": 200.0
    }
    
    res = await client.post("/api/coupons/validate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert data["coupon"]["code"] == "SAVE20"
    assert data["coupon"]["discountType"] == "percentage"
    assert data["coupon"]["discountValue"] == 20.0
    # 20% of 200 = 40
    assert data["discount"] == pytest.approx(40.0)
    assert "successfully" in data["message"].lower()


async def test_validate_coupon_percentage_with_max_discount(client_and_db):
    """Test percentage discount capped at maxDiscount"""
    client, test_db = client_and_db
    await seed_coupon(test_db, "SAVE30", "percentage", 30.0, 100.0, max_discount=50.0)
    
    # Order total of 500, 30% would be 150, but max is 50
    payload = {
        "code": "SAVE30",
        "orderTotal": 500.0
    }
    
    res = await client.post("/api/coupons/validate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert data["discount"] == pytest.approx(50.0)  # Capped at maxDiscount


async def test_validate_coupon_percentage_without_max_discount(client_and_db):
    """Test percentage discount without max cap"""
    client, test_db = client_and_db
    await seed_coupon(test_db, "SAVE25", "percentage", 25.0, 100.0, max_discount=None)
    
    payload = {
        "code": "SAVE25",
        "orderTotal": 400.0
    }
    
    res = await client.post("/api/coupons/validate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    # 25% of 400 = 100
    assert data["discount"] == pytest.approx(100.0)


async def test_validate_coupon_not_found(client_and_db):
    """Test validation with non-existent coupon code"""
    client, test_db = client_and_db
    
    payload = {
        "code": "INVALID",
        "orderTotal": 150.0
    }
    
    res = await client.post("/api/coupons/validate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is False
    assert data["coupon"] is None
    assert data["discount"] == 0.0
    assert "not found" in data["message"].lower()


async def test_validate_coupon_minimum_order_not_met(client_and_db):
    """Test validation when order total is below minimum requirement"""
    client, test_db = client_and_db
    await seed_coupon(test_db, "MIN100", "flat", 20.0, 100.0)
    
    payload = {
        "code": "MIN100",
        "orderTotal": 50.0  # Below minimum of 100
    }
    
    res = await client.post("/api/coupons/validate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is False
    assert data["coupon"] is None
    assert data["discount"] == 0.0
    assert "at least" in data["message"].lower()
    assert "100" in data["message"]


async def test_validate_coupon_case_insensitive(client_and_db):
    """Test that coupon code matching is case-insensitive"""
    client, test_db = client_and_db
    await seed_coupon(test_db, "SAVE20", "flat", 20.0, 100.0)
    
    # Try with lowercase
    payload = {
        "code": "save20",
        "orderTotal": 150.0
    }
    
    res = await client.post("/api/coupons/validate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert data["coupon"]["code"] == "SAVE20"


async def test_validate_coupon_exact_minimum_order(client_and_db):
    """Test validation when order total exactly meets minimum"""
    client, test_db = client_and_db
    await seed_coupon(test_db, "MIN100", "flat", 20.0, 100.0)
    
    payload = {
        "code": "MIN100",
        "orderTotal": 100.0  # Exactly the minimum
    }
    
    res = await client.post("/api/coupons/validate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert data["discount"] == 20.0


async def test_get_available_coupons_empty(client_and_db):
    """Test getting available coupons when none exist"""
    client, test_db = client_and_db
    
    res = await client.get("/api/coupons/available")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) == 0


async def test_get_available_coupons_multiple(client_and_db):
    """Test getting multiple available coupons"""
    client, test_db = client_and_db
    await seed_coupon(test_db, "FLAT50", "flat", 50.0, 100.0, description="Flat ₹50 off")
    await seed_coupon(test_db, "SAVE20", "percentage", 20.0, 200.0, description="20% off")
    await seed_coupon(test_db, "SAVE30", "percentage", 30.0, 150.0, max_discount=100.0, description="30% off, max ₹100")
    
    res = await client.get("/api/coupons/available")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) == 3
    
    # Check that all coupons are returned with correct structure
    codes = [c["code"] for c in data]
    assert "FLAT50" in codes
    assert "SAVE20" in codes
    assert "SAVE30" in codes
    
    # Verify structure of one coupon
    flat50 = next(c for c in data if c["code"] == "FLAT50")
    assert "id" in flat50
    assert flat50["code"] == "FLAT50"
    assert flat50["description"] == "Flat ₹50 off"
    assert flat50["minOrder"] == 100.0
    assert flat50["discountType"] == "flat"
    assert flat50["discountValue"] == 50.0
    assert flat50["maxDiscount"] is None


async def test_get_available_coupons_structure(client_and_db):
    """Test that available coupons have correct structure"""
    client, test_db = client_and_db
    await seed_coupon(test_db, "TEST", "percentage", 15.0, 50.0, max_discount=25.0)
    
    res = await client.get("/api/coupons/available")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 1
    
    coupon = data[0]
    assert "id" in coupon
    assert "code" in coupon
    assert "description" in coupon
    assert "minOrder" in coupon
    assert "discountType" in coupon
    assert "discountValue" in coupon
    assert "maxDiscount" in coupon


async def test_validate_coupon_zero_order_total(client_and_db):
    """Test validation with zero order total"""
    client, test_db = client_and_db
    await seed_coupon(test_db, "FLAT50", "flat", 50.0, 0.0)  # No minimum
    
    payload = {
        "code": "FLAT50",
        "orderTotal": 0.0
    }
    
    res = await client.post("/api/coupons/validate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["valid"] is True
    assert data["discount"] == 50.0


async def test_validate_coupon_negative_order_total(client_and_db):
    """Test validation with negative order total (should fail minimum order check)"""
    client, test_db = client_and_db
    await seed_coupon(test_db, "FLAT50", "flat", 50.0, 0.0)
    
    payload = {
        "code": "FLAT50",
        "orderTotal": -10.0
    }
    
    res = await client.post("/api/coupons/validate", json=payload)
    assert res.status_code == 200
    data = res.json()
    # Should fail because -10.0 < 0.0 (minimum order check)
    assert data["valid"] is False
    assert "at least" in data["message"].lower()

