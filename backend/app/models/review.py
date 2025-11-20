from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class Review(BaseModel):
    id: str
    booking_id: str
    customer_id: str
    vehicle_id: str
    
    rating: float  # 1.0 to 5.0
    comment: Optional[str] = None
    
    # Review categories
    cleanliness_rating: Optional[float] = None
    comfort_rating: Optional[float] = None
    value_rating: Optional[float] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ReviewCreate(BaseModel):
    booking_id: str
    rating: float
    comment: Optional[str] = None
    cleanliness_rating: Optional[float] = None
    comfort_rating: Optional[float] = None
    value_rating: Optional[float] = None


class ReviewUpdate(BaseModel):
    rating: Optional[float] = None
    comment: Optional[str] = None
    cleanliness_rating: Optional[float] = None
    comfort_rating: Optional[float] = None
    value_rating: Optional[float] = None



