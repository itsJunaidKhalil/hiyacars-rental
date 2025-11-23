from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class RentalType(str, Enum):
    HOUR = "hour"
    DAY = "day"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class Booking(BaseModel):
    id: str
    customer_id: str
    vehicle_id: str
    organization_id: str  # Agency/Org
    
    # Booking details
    pickup_date: datetime
    return_date: datetime
    rental_type: RentalType
    pickup_location: str
    return_location: Optional[str] = None
    
    # Pricing
    base_price: float
    surge_multiplier: float = 1.0
    driver_fee: float = 0.0
    platform_fee: float
    total_price: float
    
    # Status
    status: BookingStatus = BookingStatus.PENDING
    
    # Additional info
    with_driver: bool = False
    driver_id: Optional[str] = None
    customer_gender: Optional[str] = None
    special_requests: Optional[str] = None
    
    # Contract
    contract_id: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class BookingCreate(BaseModel):
    vehicle_id: str
    pickup_date: datetime
    return_date: datetime
    rental_type: RentalType
    pickup_location: str
    return_location: Optional[str] = None
    with_driver: bool = False
    customer_gender: Optional[str] = None
    special_requests: Optional[str] = None


class BookingUpdate(BaseModel):
    pickup_date: Optional[datetime] = None
    return_date: Optional[datetime] = None
    pickup_location: Optional[str] = None
    return_location: Optional[str] = None
    status: Optional[BookingStatus] = None
    special_requests: Optional[str] = None


class BookingResponse(BaseModel):
    id: str
    customer_id: str
    vehicle_id: str
    vehicle: dict  # Vehicle details
    pickup_date: datetime
    return_date: datetime
    rental_type: RentalType
    pickup_location: str
    return_location: Optional[str] = None
    base_price: float
    surge_multiplier: float
    driver_fee: float
    platform_fee: float
    total_price: float
    status: BookingStatus
    with_driver: bool
    contract_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True



