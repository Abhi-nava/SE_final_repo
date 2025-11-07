import pytest
from pydantic import ValidationError
from datetime import datetime, timezone
import sys
import os

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

BACKEND_DIR = os.path.join(REPO_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from models.delivery import (
    VehicleType,
    DeliveryAgentStatus,
    DeliveryAgentCreate,
    DeliveryAgentUpdate,
    DeliveryAgentResponse,
    LocationUpdate,
    AgentStatsResponse
)


def test_vehicle_type_enum():
    """Test VehicleType enum values"""
    assert VehicleType.BIKE == "bike"
    assert VehicleType.SCOOTER == "scooter"
    assert VehicleType.CAR == "car"
    assert VehicleType.BICYCLE == "bicycle"


def test_delivery_agent_status_enum():
    """Test DeliveryAgentStatus enum values"""
    assert DeliveryAgentStatus.ONLINE == "online"
    assert DeliveryAgentStatus.IN_DELIVERY == "in_delivery"
    assert DeliveryAgentStatus.OFFLINE == "offline"


def test_delivery_agent_create_valid():
    """Test DeliveryAgentCreate with all required fields"""
    agent = DeliveryAgentCreate(
        vehicle_type=VehicleType.BIKE,
        vehicle_number="KA01AB1234",
        vehicle_registration="2024-01-01",
        license_number="DL0000000000",
        bank_account="1234567890",
        ifsc_code="SBIN0000000"
    )
    assert agent.vehicle_type == VehicleType.BIKE
    assert agent.vehicle_number == "KA01AB1234"
    assert agent.license_number == "DL0000000000"
    assert agent.bank_account == "1234567890"
    assert agent.ifsc_code == "SBIN0000000"


def test_delivery_agent_create_with_insurance():
    """Test DeliveryAgentCreate with optional insurance_document"""
    agent = DeliveryAgentCreate(
        vehicle_type=VehicleType.CAR,
        vehicle_number="KA02CD5678",
        vehicle_registration="2024-02-01",
        license_number="DL1111111111",
        insurance_document="insurance.pdf",
        bank_account="9876543210",
        ifsc_code="HDFC0000000"
    )
    assert agent.insurance_document == "insurance.pdf"


def test_delivery_agent_create_all_vehicle_types():
    """Test DeliveryAgentCreate with different vehicle types"""
    for vehicle_type in VehicleType:
        agent = DeliveryAgentCreate(
            vehicle_type=vehicle_type,
            vehicle_number="TEST123",
            vehicle_registration="2024-01-01",
            license_number="DL0000000000",
            bank_account="1234567890",
            ifsc_code="SBIN0000000"
        )
        assert agent.vehicle_type == vehicle_type


def test_delivery_agent_create_missing_required_fields():
    """Test DeliveryAgentCreate validation with missing required fields"""
    with pytest.raises(ValidationError):
        DeliveryAgentCreate(
            vehicle_type=VehicleType.BIKE
            # Missing other required fields
        )


def test_delivery_agent_update_all_optional():
    """Test DeliveryAgentUpdate with all optional fields"""
    update = DeliveryAgentUpdate(
        vehicle_type=VehicleType.SCOOTER,
        vehicle_number="NEW123",
        vehicle_registration="2024-03-01",
        status=DeliveryAgentStatus.ONLINE
    )
    assert update.vehicle_type == VehicleType.SCOOTER
    assert update.vehicle_number == "NEW123"
    assert update.status == DeliveryAgentStatus.ONLINE


def test_delivery_agent_update_partial():
    """Test DeliveryAgentUpdate with only some fields"""
    update = DeliveryAgentUpdate(
        status=DeliveryAgentStatus.OFFLINE
    )
    assert update.status == DeliveryAgentStatus.OFFLINE
    assert update.vehicle_type is None
    assert update.vehicle_number is None


def test_delivery_agent_update_empty():
    """Test DeliveryAgentUpdate with no fields (all None)"""
    update = DeliveryAgentUpdate()
    assert update.vehicle_type is None
    assert update.vehicle_number is None
    assert update.status is None


def test_location_update_valid():
    """Test LocationUpdate with valid coordinates"""
    location = LocationUpdate(
        latitude=12.9716,
        longitude=77.5946
    )
    assert location.latitude == 12.9716
    assert location.longitude == 77.5946
    assert location.accuracy is None


def test_location_update_with_accuracy():
    """Test LocationUpdate with accuracy"""
    location = LocationUpdate(
        latitude=12.9716,
        longitude=77.5946,
        accuracy=10.5
    )
    assert location.accuracy == 10.5


def test_location_update_boundary_values():
    """Test LocationUpdate with boundary coordinate values"""
    # Valid boundaries
    location1 = LocationUpdate(latitude=90.0, longitude=180.0)
    assert location1.latitude == 90.0
    assert location1.longitude == 180.0
    
    location2 = LocationUpdate(latitude=-90.0, longitude=-180.0)
    assert location2.latitude == -90.0
    assert location2.longitude == -180.0


def test_location_update_invalid_latitude():
    """Test LocationUpdate with invalid latitude"""
    with pytest.raises(ValidationError):
        LocationUpdate(latitude=91.0, longitude=77.5946)
    
    with pytest.raises(ValidationError):
        LocationUpdate(latitude=-91.0, longitude=77.5946)


def test_location_update_invalid_longitude():
    """Test LocationUpdate with invalid longitude"""
    with pytest.raises(ValidationError):
        LocationUpdate(latitude=12.9716, longitude=181.0)
    
    with pytest.raises(ValidationError):
        LocationUpdate(latitude=12.9716, longitude=-181.0)


def test_agent_stats_response_valid():
    """Test AgentStatsResponse with all fields"""
    stats = AgentStatsResponse(
        total_deliveries=50,
        avg_rating=4.5,
        total_earnings=1250.75,
        completed_orders=45,
        active_orders=2,
        status="online"
    )
    assert stats.total_deliveries == 50
    assert stats.avg_rating == 4.5
    assert stats.total_earnings == 1250.75
    assert stats.completed_orders == 45
    assert stats.active_orders == 2
    assert stats.status == "online"


def test_agent_stats_response_zero_values():
    """Test AgentStatsResponse with zero values"""
    stats = AgentStatsResponse(
        total_deliveries=0,
        avg_rating=0.0,
        total_earnings=0.0,
        completed_orders=0,
        active_orders=0,
        status="offline"
    )
    assert stats.total_deliveries == 0
    assert stats.avg_rating == 0.0


def test_delivery_agent_response_valid():
    """Test DeliveryAgentResponse with all fields"""
    now = datetime.now(timezone.utc)
    agent = DeliveryAgentResponse(
        id="507f1f77bcf86cd799439011",
        user_id="507f1f77bcf86cd799439012",
        vehicle_type=VehicleType.BIKE,
        vehicle_number="KA01AB1234",
        vehicle_registration="2024-01-01",
        license_number="DL0000000000",
        status=DeliveryAgentStatus.ONLINE,
        rating=4.5,
        total_deliveries=25,
        is_verified=True,
        created_at=now,
        updated_at=now
    )
    assert agent.id == "507f1f77bcf86cd799439011"
    assert agent.user_id == "507f1f77bcf86cd799439012"
    assert agent.vehicle_type == VehicleType.BIKE
    assert agent.status == DeliveryAgentStatus.ONLINE
    assert agent.rating == 4.5
    assert agent.total_deliveries == 25
    assert agent.is_verified is True


def test_delivery_agent_response_defaults():
    """Test DeliveryAgentResponse with default values"""
    now = datetime.now(timezone.utc)
    agent = DeliveryAgentResponse(
        id="507f1f77bcf86cd799439011",
        user_id="507f1f77bcf86cd799439012",
        vehicle_type=VehicleType.BIKE,
        vehicle_number="KA01AB1234",
        vehicle_registration="2024-01-01",
        license_number="DL0000000000",
        created_at=now,
        updated_at=now
    )
    assert agent.status == DeliveryAgentStatus.OFFLINE  # Default
    assert agent.rating == 0.0  # Default
    assert agent.total_deliveries == 0  # Default
    assert agent.is_verified is False  # Default


def test_delivery_agent_response_with_location():
    """Test DeliveryAgentResponse with current_location"""
    now = datetime.now(timezone.utc)
    agent = DeliveryAgentResponse(
        id="507f1f77bcf86cd799439011",
        user_id="507f1f77bcf86cd799439012",
        vehicle_type=VehicleType.BIKE,
        vehicle_number="KA01AB1234",
        vehicle_registration="2024-01-01",
        license_number="DL0000000000",
        current_location={"lat": 12.9716, "lng": 77.5946},
        created_at=now,
        updated_at=now
    )
    assert agent.current_location == {"lat": 12.9716, "lng": 77.5946}

