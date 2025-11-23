from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class VehicleStatus(str, Enum):
    AVAILABLE = "available"
    RENTED = "rented"
    MAINTENANCE = "maintenance"
    UNAVAILABLE = "unavailable"


class VehicleCategory(str, Enum):
    SEDAN = "sedan"
    HATCHBACK = "hatchback"
    SUV = "suv"
    LUXURY = "luxury"
    SPORTS = "sports"
    ELECTRIC = "electric"


class Vehicle(BaseModel):
    id: str
    make: str
    model: str
    year: int
    category: VehicleCategory
    seats: int
    transmission: str  # manual, automatic
    fuel_type: str  # petrol, diesel, electric, hybrid
    color: str
    license_plate: str
    vin: Optional[str] = None
    status: VehicleStatus = VehicleStatus.AVAILABLE
    
    # Pricing
    price_per_day: float
    price_per_week: float
    price_per_month: float
    price_per_hour: Optional[float] = None
    
    # Location
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
    # Media
    images: List[str] = []  # URLs
    features: List[str] = []  # e.g., ["GPS", "Bluetooth", "Sunroof"]
    
    # Ownership
    organization_id: str  # Agency/Org that owns the vehicle
    investor_id: Optional[str] = None  # If vehicle is investor-owned
    
    # Metadata
    description: Optional[str] = None
    rating: float = 0.0
    total_reviews: int = 0
    total_bookings: int = 0
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class VehicleCreate(BaseModel):
    make: str
    model: str
    year: int
    category: VehicleCategory
    seats: int
    transmission: str
    fuel_type: str
    color: str
    license_plate: str
    vin: Optional[str] = None
    price_per_day: float
    price_per_week: float
    price_per_month: float
    price_per_hour: Optional[float] = None
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    images: List[str] = []
    features: List[str] = []
    description: Optional[str] = None
    investor_id: Optional[str] = None


class VehicleUpdate(BaseModel):
    make: Optional[str] = None
    model: Optional[str] = None
    year: Optional[int] = None
    category: Optional[VehicleCategory] = None
    seats: Optional[int] = None
    transmission: Optional[str] = None
    fuel_type: Optional[str] = None
    color: Optional[str] = None
    status: Optional[VehicleStatus] = None
    price_per_day: Optional[float] = None
    price_per_week: Optional[float] = None
    price_per_month: Optional[float] = None
    price_per_hour: Optional[float] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    images: Optional[List[str]] = None
    features: Optional[List[str]] = None
    description: Optional[str] = None


class VehicleSearchParams(BaseModel):
    category: Optional[VehicleCategory] = None
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    radius_km: Optional[float] = 50.0
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    seats: Optional[int] = None
    transmission: Optional[str] = None
    fuel_type: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    page: int = 1
    limit: int = 20



