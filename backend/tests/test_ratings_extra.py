import asyncio
import os
import pytest
import pytest_asyncio
from bson import ObjectId
from datetime import datetime, timezone
import httpx
from motor.motor_asyncio import AsyncIOMotorClient
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
from routes import ratings as ratings_routes
from routes import restaurants as restaurants_routes
from utils import dependencies as deps


pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture(scope="function")
async def client_and_db():
    async def fake_get_current_customer():
        return {"_id": "cust1", "email": "c@x.com", "role": deps.CUSTOMER_ROLE}

    async def fake_get_current_restaurant_owner():
        return {"_id": "507f1f77bcf86cd799439011", "email": "r@x.com", "role": deps.RESTAURANT_ROLE}

    app.dependency_overrides[deps.get_current_customer] = fake_get_current_customer
    app.dependency_overrides[deps.get_current_restaurant_owner] = fake_get_current_restaurant_owner

    # Create an in-memory database using dictionaries (namespaces/collections)
    class InMemoryDatabase:
        def __init__(self):
            self._collections = {}
        
        def __getitem__(self, name):
            if name not in self._collections:
                self._collections[name] = InMemoryCollection()
            return self._collections[name]
        
        def __getattr__(self, name):
            # Support attribute access like db.restaurants
            return self[name]
    
    class InMemoryCollection:
        def __init__(self):
            self._documents = []
            self._next_id = 1
        
        def _normalize_objectid(self, value):
            """Convert ObjectId to string for comparison, or return as-is"""
            if isinstance(value, ObjectId):
                return str(value)
            if isinstance(value, str) and len(value) == 24:
                try:
                    # Validate it's a valid ObjectId string
                    ObjectId(value)
                    return value
                except:
                    return value
            return value
        
        def _match_document(self, doc, filter):
            """Check if document matches filter"""
            for key, value in filter.items():
                doc_value = doc.get(key)
                
                # Handle None values in filter - they should match None in document
                if value is None:
                    if doc_value is not None:
                        return False
                    # Both are None, so they match
                    continue
                
                # Handle ObjectId comparisons - normalize both sides
                if key == '_id' or key.endswith('_id'):
                    # Always normalize ObjectIds for ID fields
                    # Convert both to strings for comparison
                    if isinstance(value, ObjectId):
                        value_str = str(value)
                    elif isinstance(value, str):
                        value_str = value
                    else:
                        value_str = str(value) if value else None
                    
                    if isinstance(doc_value, ObjectId):
                        doc_value_str = str(doc_value)
                    elif isinstance(doc_value, str):
                        doc_value_str = doc_value
                    else:
                        doc_value_str = str(doc_value) if doc_value else None
                    
                    if value_str != doc_value_str:
                        return False
                # Handle $ne operator
                elif isinstance(value, dict) and '$ne' in value:
                    if doc_value == value['$ne']:
                        return False
                # Handle regular comparison
                elif doc_value != value:
                    return False
            return True
        
        async def find_one(self, filter):
            # Don't normalize filter here - let _match_document handle it
            # Check for special flag to simulate exception for testing
            if filter.get("_raise_exception") is True:
                raise Exception("Simulated database error")
            for doc in self._documents:
                if self._match_document(doc, filter):
                    # Return a deep copy to avoid mutation
                    result = deepcopy(doc)
                    # Ensure _id is ObjectId
                    if '_id' in result and not isinstance(result['_id'], ObjectId):
                        try:
                            result['_id'] = ObjectId(result['_id'])
                        except:
                            pass
                    return result
            return None
        
        def find(self, filter):
            # find() is synchronous in motor - returns cursor immediately
            # Don't normalize filter here - let _match_document handle it
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
            # Don't normalize filter here - let _match_document handle it
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
            # Don't normalize filter here - let _match_document handle it
            deleted_count = 0
            remaining = []
            for doc in self._documents:
                if self._match_document(doc, filter):
                    deleted_count += 1
                else:
                    remaining.append(doc)
            self._documents = remaining
            return type('obj', (object,), {'deleted_count': deleted_count})()
        
        def aggregate(self, pipeline):
            # Simple aggregation implementation
            results = list(self._documents)
            
            for stage in pipeline:
                if '$match' in stage:
                    filter = stage['$match']  # Don't normalize - let _match_document handle it
                    results = [doc for doc in results if self._match_document(doc, filter)]
                elif '$group' in stage:
                    group = stage['$group']
                    grouped = {}
                    for doc in results:
                        group_id = group.get('_id')
                        if group_id is None:
                            group_id = 'all'
                        
                        if group_id not in grouped:
                            grouped[group_id] = {
                                '_id': group_id,
                                'count': 0,
                                'sum_restaurant': 0,
                                'sum_delivery': 0,
                                'sum_food_quality': 0,
                                'sum_delivery_speed': 0,
                                'sum_packaging_quality': 0,
                            }
                        
                        g = grouped[group_id]
                        g['count'] += 1
                        if 'restaurant_rating' in doc:
                            g['sum_restaurant'] += doc.get('restaurant_rating', 0)
                        if 'delivery_rating' in doc:
                            g['sum_delivery'] += doc.get('delivery_rating', 0)
                        if 'food_quality' in doc:
                            g['sum_food_quality'] += doc.get('food_quality', 0)
                        if 'delivery_speed' in doc:
                            g['sum_delivery_speed'] += doc.get('delivery_speed', 0)
                        if 'packaging_quality' in doc:
                            g['sum_packaging_quality'] += doc.get('packaging_quality', 0)
                    
                    # Calculate averages
                    final_results = []
                    for g in grouped.values():
                        result = {'_id': g['_id'], 'count': g['count']}
                        if g['count'] > 0:
                            result['avg_restaurant'] = g['sum_restaurant'] / g['count']
                            result['avg_delivery'] = g['sum_delivery'] / g['count']
                            result['avg_food_quality'] = g['sum_food_quality'] / g['count']
                            result['avg_delivery_speed'] = g['sum_delivery_speed'] / g['count']
                            result['avg_packaging_quality'] = g['sum_packaging_quality'] / g['count']
                        else:
                            result['avg_restaurant'] = 0
                            result['avg_delivery'] = 0
                            result['avg_food_quality'] = 0
                            result['avg_delivery_speed'] = 0
                            result['avg_packaging_quality'] = 0
                        final_results.append(result)
                    results = final_results
            
            return InMemoryCursor(results)
        
    
    class InMemoryCursor:
        def __init__(self, documents):
            self._documents = documents
            self._sort_key = None
            self._sort_direction = None
            self._limit_val = None
        
        async def to_list(self, length):
            items = list(self._documents)
            
            # Apply sort if specified
            if self._sort_key:
                reverse = self._sort_direction == -1
                items.sort(key=lambda x: x.get(self._sort_key), reverse=reverse)
            
            # Apply limit
            if self._limit_val is not None:
                items = items[:self._limit_val]
            
            # Apply length limit
            if length is not None:
                items = items[:length]
            
            return items
        
        def sort(self, key, direction):
            self._sort_key = key
            self._sort_direction = direction
            return self
        
        def limit(self, n):
            self._limit_val = n
            return self
    
    # Create the in-memory database
    async_test_db = InMemoryDatabase()
    
    # Override database in all places
    database_module.db = async_test_db
    ratings_routes.db = async_test_db
    restaurants_routes.db = async_test_db
    # Also update the module-level db that routes import
    import database
    database.db = async_test_db
    # Update the local db variable in routes that use "from database import db"
    # Since "from database import db" creates a local reference, we need to update it
    import routes.ratings as ratings_module
    import sys
    # Force update the route module's db by setting it directly
    setattr(ratings_module, 'db', async_test_db)
    # Also update restaurants routes if needed
    import routes.restaurants as restaurants_module
    if hasattr(restaurants_module, 'db'):
        setattr(restaurants_module, 'db', async_test_db)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://localhost") as async_client:
        # pre-test cleanup to ensure isolation
        for name in ["users", "orders", "restaurants", "ratings", "delivery_agents"]:
            await async_test_db[name].delete_many({})
        yield async_client, async_test_db
        # post-test cleanup while client/loop are still alive
        for name in ["users", "orders", "restaurants", "ratings", "delivery_agents"]:
            await async_test_db[name].delete_many({})


# removed separate clean_db; cleanup handled inside client_and_db


# Helper functions for seeding test data
async def seed_restaurant(owner_oid: ObjectId, db):
    restaurant = {
        "owner_id": owner_oid,
        "name": "Test Resto",
        "phone": "000",
        "address": "addr",
        "opening_time": "09:00",
        "closing_time": "22:00",
        "rating": 0,
        "total_ratings": 0,
    }
    res = await db.restaurants.insert_one(restaurant)
    restaurant["_id"] = res.inserted_id
    return restaurant


async def seed_order(restaurant_id: str, db, customer_id: str = "cust1"):
    order = {
        "customer_id": customer_id,
        "restaurant_id": restaurant_id,
        "delivery_agent_id": None,
        "order_status": "delivered",
        "total": 100,
        "created_at": datetime.now(timezone.utc),
    }
    res = await db.orders.insert_one(order)
    order["_id"] = res.inserted_id
    return order


async def test_create_rating_validation_error_422(client_and_db):
    client, test_db = client_and_db
    # Missing required order in DB should be 404, but here we first create an order/restaurant
    owner_oid = ObjectId("507f1f77bcf86cd799439011")
    resto = {
        "owner_id": owner_oid,
        "name": "Test Resto",
        "phone": "000",
        "address": "addr",
        "opening_time": "09:00",
        "closing_time": "22:00",
        "rating": 0,
        "total_ratings": 0,
    }
    rres = await test_db.restaurants.insert_one(resto)
    resto_id = str(rres.inserted_id)

    order = {
        "customer_id": "cust1",
        "restaurant_id": resto_id,
        "delivery_agent_id": None,
        "order_status": "delivered",
        "total": 100,
        "created_at": datetime.now(timezone.utc),
    }
    ores = await test_db.orders.insert_one(order)

    # Send invalid rating out of bounds to trigger FastAPI/Pydantic 422
    bad = {
        "order_id": str(ores.inserted_id),
        "restaurant_id": resto_id,
        "delivery_agent_id": None,
        "restaurant_rating": 0,  # invalid, should be >=1
        "delivery_rating": 10,   # invalid, should be <=5
        "delivery_speed": 3,
        "food_quality": 3,
        "packaging_quality": 3,
    }
    res = await client.post("/api/ratings/create", json=bad)
    assert res.status_code == 422


async def test_list_endpoints_empty_lists(client_and_db):
    client, _ = client_and_db
    # No ratings yet for this restaurant/agent
    rid = str(ObjectId())
    aid = str(ObjectId())

    r_res = await client.get(f"/api/ratings/restaurant/{rid}")
    assert r_res.status_code == 200
    assert r_res.json() == []

    a_res = await client.get(f"/api/ratings/delivery-agent/{aid}")
    assert a_res.status_code == 200
    assert a_res.json() == []


async def test_check_order_rating_exception_handling(client_and_db):
    """Test exception handling in check_order_rating endpoint"""
    client, test_db = client_and_db
    owner_oid = ObjectId("507f1f77bcf86cd799439011")
    resto = await seed_restaurant(owner_oid, test_db)
    order = await seed_order(str(resto["_id"]), test_db)
    
    # Normal case - should work
    res = await client.get(f"/api/ratings/check/{str(order['_id'])}")
    assert res.status_code == 200
    assert "has_rating" in res.json()
    
    # Test exception path by making find_one raise an exception
    # We'll patch the ratings collection to raise an exception
    original_find_one = test_db.ratings.find_one
    async def failing_find_one(filter):
        raise Exception("Database error for testing")
    test_db.ratings.find_one = failing_find_one
    
    # Also update the route module's db
    import routes.ratings as ratings_module
    setattr(ratings_module, 'db', test_db)
    
    res = await client.get(f"/api/ratings/check/{str(order['_id'])}")
    assert res.status_code == 500
    assert "error" in res.json()["detail"].lower() or "Database error" in res.json()["detail"]
    
    # Restore original
    test_db.ratings.find_one = original_find_one
    setattr(ratings_module, 'db', test_db)


async def test_create_rating_with_delivery_agent(client_and_db):
    """Test creating rating with delivery agent to cover delivery agent update logic"""
    client, test_db = client_and_db
    owner_oid = ObjectId("507f1f77bcf86cd799439011")
    resto = await seed_restaurant(owner_oid, test_db)
    order = await seed_order(str(resto["_id"]), test_db)
    
    # Create a delivery agent
    agent_id = ObjectId()
    await test_db.delivery_agents.insert_one({
        "_id": agent_id,
        "name": "Test Agent",
        "rating": 0,
        "total_deliveries": 0
    })
    
    payload = {
        "order_id": str(order["_id"]),
        "restaurant_id": str(resto["_id"]),
        "delivery_agent_id": str(agent_id),
        "restaurant_rating": 5,
        "delivery_rating": 4,
        "delivery_speed": 4,
        "food_quality": 5,
        "packaging_quality": 5,
    }
    
    res = await client.post("/api/ratings/create", json=payload)
    assert res.status_code == 200
    
    # Verify delivery agent was updated
    agent = await test_db.delivery_agents.find_one({"_id": agent_id})
    assert agent["rating"] == pytest.approx(4.0)
    assert agent["total_deliveries"] == 1


async def test_create_rating_invalid_objectid(client_and_db):
    """Test creating rating with invalid ObjectId to cover exception handler"""
    client, test_db = client_and_db
    owner_oid = ObjectId("507f1f77bcf86cd799439011")
    resto = await seed_restaurant(owner_oid, test_db)
    
    # Use invalid ObjectId string to trigger exception handler
    payload = {
        "order_id": "invalid_objectid",
        "restaurant_id": str(resto["_id"]),
        "delivery_agent_id": None,
        "restaurant_rating": 5,
        "delivery_rating": 4,
        "delivery_speed": 4,
        "food_quality": 5,
        "packaging_quality": 5,
    }
    
    res = await client.post("/api/ratings/create", json=payload)
    # Should return 404 due to exception handler
    assert res.status_code == 404
    assert "Order not found" in res.json()["detail"]
