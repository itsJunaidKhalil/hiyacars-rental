from fastapi import APIRouter, HTTPException, status, Depends, Header
from typing import Optional
from app.models.payment import Payment, PaymentCreate, PaymentIntentResponse, PaymentStatus
from app.models.booking import Booking, BookingStatus
from app.auth import get_current_user, require_role
from app.models.user import User, UserRole
from app.database import get_supabase
from config import settings
import stripe
from datetime import datetime
import uuid

router = APIRouter()
stripe.api_key = settings.STRIPE_SECRET_KEY


@router.post("/intent", response_model=PaymentIntentResponse)
async def create_payment_intent(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_user)
):
    """Create Stripe payment intent"""
    if not settings.STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Payment service is not configured. Please configure Stripe keys."
        )
    
    supabase = get_supabase()
    
    # Get booking
    booking_response = supabase.table("bookings").select("*").eq("id", payment_data.booking_id).execute()
    if not booking_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    booking = booking_response.data[0]
    
    # Verify booking belongs to user
    if booking["customer_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Calculate amount (subtract wallet and loyalty points if used)
    amount = payment_data.amount
    if payment_data.wallet_amount:
        amount -= payment_data.wallet_amount
    if payment_data.loyalty_points_used:
        # Convert points to currency (1 point = 0.01 AED)
        amount -= payment_data.loyalty_points_used * 0.01
    
    # Create Stripe payment intent
    try:
        intent = stripe.PaymentIntent.create(
            amount=int(amount * 100),  # Convert to cents
            currency="aed",
            metadata={
                "booking_id": payment_data.booking_id,
                "user_id": current_user.id,
            },
        )
        
        # Create payment record
        payment_id = str(uuid.uuid4())
        payment_dict = {
            "id": payment_id,
            "booking_id": payment_data.booking_id,
            "customer_id": current_user.id,
            "amount": payment_data.amount,
            "currency": "AED",
            "method": payment_data.method.value,
            "status": PaymentStatus.PENDING.value,
            "stripe_payment_intent_id": intent.id,
            "wallet_amount": payment_data.wallet_amount or 0.0,
            "loyalty_points_used": payment_data.loyalty_points_used or 0,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }
        
        supabase.table("payments").insert(payment_dict).execute()
        
        return PaymentIntentResponse(
            client_secret=intent.client_secret,
            payment_intent_id=intent.id,
            amount=amount,
            currency="AED"
        )
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Stripe error: {str(e)}"
        )


@router.post("/webhook")
async def stripe_webhook(
    payload: bytes = Header(...),
    stripe_signature: str = Header(...)
):
    """Handle Stripe webhook events"""
    try:
        event = stripe.Webhook.construct_event(
            payload, stripe_signature, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError:
        raise HTTPException(status_code=400, detail="Invalid signature")
    
    supabase = get_supabase()
    
    # Handle different event types
    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        booking_id = payment_intent["metadata"].get("booking_id")
        
        # Update payment status
        supabase.table("payments").update({
            "status": PaymentStatus.COMPLETED.value,
            "stripe_charge_id": payment_intent.get("charges", {}).get("data", [{}])[0].get("id"),
            "updated_at": datetime.utcnow().isoformat()
        }).eq("stripe_payment_intent_id", payment_intent["id"]).execute()
        
        # Update booking status
        if booking_id:
            supabase.table("bookings").update({
                "status": BookingStatus.CONFIRMED.value,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", booking_id).execute()
    
    elif event["type"] == "payment_intent.payment_failed":
        payment_intent = event["data"]["object"]
        
        # Update payment status
        supabase.table("payments").update({
            "status": PaymentStatus.FAILED.value,
            "failure_reason": payment_intent.get("last_payment_error", {}).get("message"),
            "updated_at": datetime.utcnow().isoformat()
        }).eq("stripe_payment_intent_id", payment_intent["id"]).execute()
    
    return {"status": "success"}


@router.get("/{payment_id}", response_model=Payment)
async def get_payment(
    payment_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get payment details"""
    supabase = get_supabase()
    
    response = supabase.table("payments").select("*").eq("id", payment_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    payment = response.data[0]
    
    # Check authorization
    if payment["customer_id"] != current_user.id and current_user.role not in [UserRole.ORG_ADMIN, UserRole.AGENCY_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    return Payment(**payment)


@router.get("/booking/{booking_id}", response_model=Payment)
async def get_booking_payment(
    booking_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get payment for a booking"""
    supabase = get_supabase()
    
    response = supabase.table("payments").select("*").eq("booking_id", booking_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    payment = response.data[0]
    
    # Check authorization
    if payment["customer_id"] != current_user.id and current_user.role not in [UserRole.ORG_ADMIN, UserRole.AGENCY_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    return Payment(**payment[0])


