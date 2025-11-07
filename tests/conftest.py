import asyncio
import sys
from pathlib import Path
import pytest
import httpx

# Ensure project root is on sys.path so `import backend` works and `from routes` resolves
PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

# Import the FastAPI app
from fastapi import FastAPI
from backend.routes import orders as orders_router

# Patch the orders router db to a simple in-memory fake
class FakeCollection:
    def __init__(self, data):
        self.data = data

    async def find_one(self, query, *args, **kwargs):
        # Very small matcher supporting {"_id": ObjectId(...)} or simple equality
        for doc in self.data:
            match = True
            for k, v in query.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                return doc
        return None

    async def update_one(self, query, update):
        for i, doc in enumerate(self.data):
            match = True
            for k, v in query.items():
                if doc.get(k) != v:
                    match = False
                    break
            if match:
                # Only supports $set
                fields = update.get("$set", {})
                self.data[i] = {**doc, **fields}
                return type("Res", (), {"modified_count": 1})()
        return type("Res", (), {"modified_count": 0})()

    async def find(self, query):
        # minimal iterable with to_list
        results = []
        for doc in self.data:
            ok = True
            for k, v in query.items():
                if doc.get(k) != v:
                    ok = False
                    break
            if ok:
                results.append(doc)
        class Cursor:
            def __init__(self, docs):
                self.docs = docs
            def sort(self, *args, **kwargs):
                return self
            def skip(self, *args, **kwargs):
                return self
            def limit(self, *args, **kwargs):
                return self
            async def to_list(self, *_):
                return self.docs
        return Cursor(results)

class FakeDB:
    def __init__(self, restaurants, orders):
        self.restaurants = FakeCollection(restaurants)
        self.orders = FakeCollection(orders)
        self.menu_items = FakeCollection([])
        self.ratings = FakeCollection([])
        self.delivery_agents = FakeCollection([])

@pytest.fixture
def seed_data():
    # Use simple string IDs to avoid needing ObjectId instances in tests
    restaurant_id = "rest1"
    restaurant = {"_id": restaurant_id, "owner_id": "owner1", "name": "Test R"}

    order_id = "order1"
    order = {
        "_id": order_id,
        "restaurant_id": restaurant_id,
        "customer_id": "cust1",
        "items": [],
        "subtotal": 0.0,
        "delivery_fee": 0.0,
        "discount": 0.0,
        "total": 0.0,
        "status": "pending",
        "order_status": "preparing",
        "delivery_address": "addr",
        "delivery_phone": "000",
        "payment_method": "cod",
        "created_at": None,
        "updated_at": None,
    }
    return {"restaurant": restaurant, "order": order}

@pytest.fixture(autouse=True)
def override_dependencies(monkeypatch, seed_data):
    # Override db used inside orders router
    fake_db = FakeDB(restaurants=[seed_data["restaurant"]], orders=[seed_data["order"]])
    monkeypatch.setattr(orders_router, "db", fake_db)

    # Replace ObjectId in this module with identity so we can use simple strings
    monkeypatch.setattr(orders_router, "ObjectId", lambda x: x)

    # Override auth dependency at FastAPI layer to return a fake owner with _id "owner1"
    from utils.dependencies import get_current_restaurant_owner as real_dep

    def fake_owner():
        return {"_id": "owner1", "role": "restaurant"}

    # Override NotificationService to no-op
    class FakeNotif:
        @staticmethod
        async def notify_order_status_change(order_id: str, new_status: str):
            return None
    # Apply monkeypatch in both module and source package to be safe
    monkeypatch.setattr(orders_router, "NotificationService", FakeNotif, raising=False)
    try:
        import utils.notifications as notif_mod
        monkeypatch.setattr(notif_mod, "NotificationService", FakeNotif, raising=False)
    except Exception:
        pass

    # Save for later cleanup
    override_dependencies.real_dep = real_dep
    override_dependencies.fake_owner = fake_owner

    yield

@pytest.fixture
async def async_client(monkeypatch):
    # Build a minimal app that only mounts orders router
    app = FastAPI()

    # Apply dependency override here
    app.dependency_overrides[override_dependencies.real_dep] = override_dependencies.fake_owner

    app.include_router(orders_router.router, prefix="/api/orders")

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
