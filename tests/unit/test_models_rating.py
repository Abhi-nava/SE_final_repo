import pytest
from datetime import datetime, timezone
from pydantic import ValidationError
import sys
import os


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

BACKEND_DIR = os.path.join(REPO_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from models.rating import RatingCreate, RatingResponse

def test_rating_create_valid_minimal():
    rc = RatingCreate(
        order_id="o1",
        restaurant_id="r1",
        delivery_agent_id=None,
        restaurant_rating=5,
        delivery_rating=4,
        delivery_speed=3,
        food_quality=5,
        packaging_quality=5,
    )
    assert rc.order_id == "o1"
    assert rc.restaurant_id == "r1"
    assert rc.delivery_agent_id is None
    assert 1 <= rc.restaurant_rating <= 5
    assert 1 <= rc.delivery_rating <= 5
    assert 1 <= rc.delivery_speed <= 5
    assert 1 <= rc.food_quality <= 5
    assert 1 <= rc.packaging_quality <= 5
    # created_at is optional
    assert rc.created_at is None


def test_rating_create_with_created_at_iso():
    now = datetime.now(timezone.utc)
    rc = RatingCreate(
        order_id="o1",
        restaurant_id="r1",
        delivery_agent_id="d1",
        restaurant_rating=1,
        delivery_rating=1,
        delivery_speed=1,
        food_quality=1,
        packaging_quality=1,
        created_at=now,
    )
    assert rc.created_at == now


@pytest.mark.parametrize(
    "field,value",
    [
        ("restaurant_rating", 0),
        ("restaurant_rating", 6),
        ("delivery_rating", 0),
        ("delivery_rating", 6),
        ("delivery_speed", 0),
        ("delivery_speed", 6),
        ("food_quality", 0),
        ("food_quality", 6),
        ("packaging_quality", 0),
        ("packaging_quality", 6),
    ],
)
def test_rating_create_bounds_validation(field, value):
    base = dict(
        order_id="o1",
        restaurant_id="r1",
        delivery_agent_id=None,
        restaurant_rating=3,
        delivery_rating=3,
        delivery_speed=3,
        food_quality=3,
        packaging_quality=3,
    )
    base[field] = value
    with pytest.raises(ValidationError):
        RatingCreate(**base)


def test_rating_response_alias_input_and_dump():
    # Accepts alias _id and exposes id
    payload = {
        "_id": "abc123",
        "order_id": "o1",
        "customer_id": "c1",
        "restaurant_id": "r1",
        "delivery_agent_id": None,
        "restaurant_rating": 4,
        "delivery_rating": 5,
        "delivery_speed": 3,
        "food_quality": 5,
        "packaging_quality": 4,
        "created_at": datetime.now(timezone.utc),
    }
    rr = RatingResponse(**payload)
    assert rr.id == "abc123"

    dumped = rr.model_dump(by_alias=True)
    # When dumping by alias, the key should be _id
    assert dumped.get("_id") == "abc123"
    assert "id" not in dumped
