from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class PaymentMethod(str, Enum):
    STRIPE_CARD = "stripe_card"
    WALLET = "wallet"
    LOYALTY_POINTS = "loyalty_points"
    MIXED = "mixed"  # Combination of methods


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    PARTIALLY_REFUNDED = "partially_refunded"


class Payment(BaseModel):
    id: str
    booking_id: str
    customer_id: str
    
    amount: float
    currency: str = "AED"
    method: PaymentMethod
    status: PaymentStatus
    
    # Stripe specific
    stripe_payment_intent_id: Optional[str] = None
    stripe_charge_id: Optional[str] = None
    
    # Wallet/Loyalty
    wallet_amount: float = 0.0
    loyalty_points_used: int = 0
    
    # Metadata
    description: Optional[str] = None
    failure_reason: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PaymentCreate(BaseModel):
    booking_id: str
    method: PaymentMethod
    amount: float
    wallet_amount: Optional[float] = 0.0
    loyalty_points_used: Optional[int] = 0
    stripe_payment_method_id: Optional[str] = None  # For Stripe


class PaymentIntentResponse(BaseModel):
    client_secret: str
    payment_intent_id: str
    amount: float
    currency: str



