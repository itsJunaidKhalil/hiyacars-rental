from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class LoyaltyTransactionType(str, Enum):
    EARNED = "earned"  # From booking
    REDEEMED = "redeemed"  # Used for payment
    EXPIRED = "expired"
    ADJUSTMENT = "adjustment"  # Manual adjustment by admin


class LoyaltyPoints(BaseModel):
    id: str
    user_id: str
    total_points: int = 0
    available_points: int = 0
    lifetime_points: int = 0
    updated_at: datetime
    
    class Config:
        from_attributes = True


class LoyaltyTransaction(BaseModel):
    id: str
    user_id: str
    booking_id: Optional[str] = None
    transaction_type: LoyaltyTransactionType
    points: int  # Positive for earned, negative for redeemed
    description: Optional[str] = None
    expires_at: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class LoyaltyEarnRequest(BaseModel):
    booking_id: str
    points: int  # Usually 1 mile = 1 point


class LoyaltyRedeemRequest(BaseModel):
    points: int
    booking_id: Optional[str] = None



