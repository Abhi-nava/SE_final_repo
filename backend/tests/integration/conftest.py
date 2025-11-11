"""
Pytest configuration for integration tests using a full in-memory MongoDB replacement.
This version ensures that ALL imports of `db` anywhere in the app
(main.py, routes, services, helpers, etc.) get patched reliably.
"""

import pytest
from unittest.mock import patch, AsyncMock
from bson import ObjectId
from copy import deepcopy
import sys
from httpx import AsyncClient, ASGITransport


# ---------------------------------------------------------------------------
# In-memory DB implementation (same behavior as Motor)
# ---------------------------------------------------------------------------
class InMemoryCollection:
    def __init__(self):
        self.data = []

    async def insert_one(self, doc):
        doc = deepcopy(doc)
        if "_id" not in doc:
            doc["_id"] = ObjectId()
        self.data.append(doc)
        return type("Result", (), {"inserted_id": doc["_id"]})

    async def find_one(self, filter_dict):
        for doc in self.data:
            if all(str(doc.get(k)) == str(v) for k, v in filter_dict.items()):
                return deepcopy(doc)
        return None

    async def delete_one(self, filter_dict):
        for i, doc in enumerate(self.data):
            if all(str(doc.get(k)) == str(v) for k, v in filter_dict.items()):
                self.data.pop(i)
                return type("Result", (), {"deleted_count": 1})
        return type("Result", (), {"deleted_count": 0})

    async def update_one(self, filter_dict, update_dict):
        for doc in self.data:
            if all(str(doc.get(k)) == str(v) for k, v in filter_dict.items()):
                if "$set" in update_dict:
                    doc.update(update_dict["$set"])
                else:
                    doc.update(update_dict)
                return type("Result", (), {"modified_count": 1})
        return type("Result", (), {"modified_count": 0})

    async def find(self, filter_dict=None):
        result = []
        for doc in self.data:
            if not filter_dict or all(str(doc.get(k)) == str(v) for k, v in filter_dict.items()):
                result.append(deepcopy(doc))
        return result
    
    async def create_index(self, *args, **kwargs):
        """Mock create_index for in-memory database (no-op)"""
        pass


class InMemoryDatabase:
    def __init__(self):
        self._collections = {}

    def __getattr__(self, name):
        if name not in self._collections:
            self._collections[name] = InMemoryCollection()
        return self._collections[name]
    
    async def list_collection_names(self):
        """Mock list_collection_names for in-memory database"""
        return list(self._collections.keys())


# ---------------------------------------------------------------------------
# Autouse fixture: replaces ALL db imports everywhere in the project
# ---------------------------------------------------------------------------
@pytest.fixture(scope="session", autouse=True)
def patch_all_db_imports():
    mock_db = InMemoryDatabase()

    patches = []

    # Patch AsyncIOMotorClient to return a mock that uses our in-memory DB
    from motor.motor_asyncio import AsyncIOMotorClient
    
    class MockAdmin:
        async def command(self, command):
            return {"ok": 1}
    
    class MockMotorClient:
        def __init__(self, *args, **kwargs):
            self._admin = MockAdmin()
        
        def __getitem__(self, name):
            return mock_db
        
        async def close(self):
            pass
        
        @property
        def admin(self):
            return self._admin
    
    patches.append(patch('motor.motor_asyncio.AsyncIOMotorClient', MockMotorClient))

    # apply patches first
    for p in patches:
        p.start()

    # Now import main to ensure it uses the patched AsyncIOMotorClient
    import main
    # Patch main's db and db_client
    main.db = mock_db
    main.db_client = MockMotorClient()

    # automatically find all modules that imported "db"
    for module in list(sys.modules.values()):
        if not module:
            continue

        if hasattr(module, "db") and module.db is not mock_db:
            patches.append(patch.object(module, "db", mock_db))
            patches[-1].start()

    yield mock_db

    # remove patches
    for p in patches:
        p.stop()


# ---------------------------------------------------------------------------
# Fixture: Expose mock_db for tests
# ---------------------------------------------------------------------------
@pytest.fixture
def mock_db(patch_all_db_imports):
    """Expose the mock database for use in tests"""
    return patch_all_db_imports


# ---------------------------------------------------------------------------
# Fixture: Test client with mocked authentication
# ---------------------------------------------------------------------------
@pytest.fixture
async def client(mock_db):
    """Create a test client with mocked authentication"""
    from main import app
    
    # Mock the authentication dependency to return a test user
    async def mock_get_current_user_http():
        return {
            "_id": "user123",
            "email": "test@example.com",
            "role": "customer"
        }
    
    # Override the dependency
    app.dependency_overrides = {}
    from utils.dependencies import get_current_user_http
    app.dependency_overrides[get_current_user_http] = mock_get_current_user_http
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    # Clean up
    app.dependency_overrides.clear()