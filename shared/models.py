from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class UserRole(str, Enum):
    RIDER = "rider"
    DRIVER = "driver"

class User(BaseModel):
    id: str
    email: str
    name: str
    role: UserRole
    phone: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Location(BaseModel):
    latitude: float
    longitude: float
    address: Optional[str] = None

class RideStatus(str, Enum):
    REQUESTED = "requested"
    ACCEPTED = "accepted"
    PICKED_UP = "picked_up"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Trip(BaseModel):
    id: str
    rider_id: str
    driver_id: Optional[str] = None
    pickup_location: Location
    dropoff_location: Location
    status: RideStatus = RideStatus.REQUESTED
    fare: Optional[float] = None
    distance: Optional[float] = None
    duration: Optional[int] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Payment(BaseModel):
    id: str
    trip_id: str
    rider_id: str
    amount: float
    status: PaymentStatus = PaymentStatus.PENDING
    payment_method: str
    transaction_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
