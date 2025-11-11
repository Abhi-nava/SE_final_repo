from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class VehicleType(str, Enum):
    BIKE = "bike"
    SCOOTER = "scooter"
    CAR = "car"
    BICYCLE = "bicycle"


class DeliveryAgentStatus(str, Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    ON_DELIVERY = "on_delivery"
    BREAK = "break"


class AgentStatsResponse(BaseModel):
    total_deliveries: int
    avg_rating: float
    total_earnings: float
    completed_orders: int
    active_orders: int
    status: str


class DeliveryAgentCreate(BaseModel):
    """Delivery agent profile creation"""

    vehicle_type: VehicleType
    vehicle_number: str
    vehicle_registration: str
    license_number: str
    insurance_document: Optional[str] = None
    bank_account: str
    ifsc_code: str


class DeliveryAgentUpdate(BaseModel):
    """Delivery agent profile update"""

    vehicle_type: Optional[VehicleType] = None
    vehicle_number: Optional[str] = None
    vehicle_registration: Optional[str] = None
    status: Optional[DeliveryAgentStatus] = None


class DeliveryAgentResponse(BaseModel):
    """Delivery agent response schema"""

    id: str = Field(alias="_id")
    user_id: str
    vehicle_type: VehicleType
    vehicle_number: str
    vehicle_registration: str
    license_number: str
    status: DeliveryAgentStatus = DeliveryAgentStatus.OFFLINE
    rating: float = 0.0
    total_deliveries: int = 0
    current_location: Optional[dict] = None  # {lat: float, lng: float}
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True


class LocationUpdate(BaseModel):
    """Location update schema"""

    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    accuracy: Optional[float] = None
