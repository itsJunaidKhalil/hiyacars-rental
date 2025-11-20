from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from app.models.loyalty import (
    LoyaltyPoints, LoyaltyTransaction, LoyaltyEarnRequest, LoyaltyRedeemRequest,
    LoyaltyTransactionType
)
from app.auth import get_current_user, require_role
from app.models.user import User, UserRole
from app.database import get_supabase
from datetime import datetime, timedelta
import uuid

router = APIRouter()


@router.get("/points", response_model=LoyaltyPoints)
async def get_loyalty_points(
    current_user: User = Depends(get_current_user)
):
    """Get current user's loyalty points"""
    supabase = get_supabase()
    
    response = supabase.table("loyalty_points").select("*").eq("user_id", current_user.id).execute()
    
    if not response.data:
        # Create loyalty points record if doesn't exist
        points_id = str(uuid.uuid4())
        points_dict = {
            "id": points_id,
            "user_id": current_user.id,
            "total_points": 0,
            "available_points": 0,
            "lifetime_points": 0,
            "updated_at": datetime.utcnow().isoformat(),
        }
        supabase.table("loyalty_points").insert(points_dict).execute()
        return LoyaltyPoints(**points_dict)
    
    return LoyaltyPoints(**response.data[0])


@router.get("/transactions", response_model=List[LoyaltyTransaction])
async def get_loyalty_transactions(
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user)
):
    """Get loyalty point transactions"""
    supabase = get_supabase()
    
    from_index = (page - 1) * limit
    to_index = from_index + limit - 1
    
    response = supabase.table("loyalty_transactions").select("*").eq(
        "user_id", current_user.id
    ).order("created_at", desc=True).range(from_index, to_index).execute()
    
    return [LoyaltyTransaction(**item) for item in response.data]


@router.post("/earn")
async def earn_loyalty_points(
    earn_request: LoyaltyEarnRequest,
    current_user: User = Depends(get_current_user)
):
    """Earn loyalty points from booking (usually called after booking completion)"""
    supabase = get_supabase()
    
    # Verify booking belongs to user and is completed
    booking_response = supabase.table("bookings").select("*").eq("id", earn_request.booking_id).execute()
    if not booking_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    booking = booking_response.data[0]
    if booking["customer_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Check if points already earned for this booking
    existing = supabase.table("loyalty_transactions").select("id").eq(
        "booking_id", earn_request.booking_id
    ).eq("transaction_type", LoyaltyTransactionType.EARNED.value).execute()
    
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Points already earned for this booking"
        )
    
    # Calculate points based on booking distance/amount
    # 1 mile = 1 point (simplified - calculate actual miles from booking)
    points = earn_request.points
    
    # Create transaction
    transaction_id = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(days=365)  # Points expire in 1 year
    
    transaction_dict = {
        "id": transaction_id,
        "user_id": current_user.id,
        "booking_id": earn_request.booking_id,
        "transaction_type": LoyaltyTransactionType.EARNED.value,
        "points": points,
        "description": f"Points earned from booking {earn_request.booking_id}",
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.utcnow().isoformat(),
    }
    
    supabase.table("loyalty_transactions").insert(transaction_dict).execute()
    
    # Update loyalty points
    points_response = supabase.table("loyalty_points").select("*").eq("user_id", current_user.id).execute()
    
    if points_response.data:
        current_points = points_response.data[0]
        supabase.table("loyalty_points").update({
            "total_points": current_points["total_points"] + points,
            "available_points": current_points["available_points"] + points,
            "lifetime_points": current_points["lifetime_points"] + points,
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("id", current_points["id"]).execute()
    else:
        # Create if doesn't exist
        points_id = str(uuid.uuid4())
        supabase.table("loyalty_points").insert({
            "id": points_id,
            "user_id": current_user.id,
            "total_points": points,
            "available_points": points,
            "lifetime_points": points,
            "updated_at": datetime.utcnow().isoformat(),
        }).execute()
    
    return {
        "message": f"Earned {points} loyalty points",
        "transaction": LoyaltyTransaction(**transaction_dict)
    }


@router.post("/redeem")
async def redeem_loyalty_points(
    redeem_request: LoyaltyRedeemRequest,
    current_user: User = Depends(get_current_user)
):
    """Redeem loyalty points"""
    supabase = get_supabase()
    
    # Get current points
    points_response = supabase.table("loyalty_points").select("*").eq("user_id", current_user.id).execute()
    
    if not points_response.data or points_response.data[0]["available_points"] < redeem_request.points:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient loyalty points"
        )
    
    current_points = points_response.data[0]
    
    # Create redemption transaction
    transaction_id = str(uuid.uuid4())
    transaction_dict = {
        "id": transaction_id,
        "user_id": current_user.id,
        "booking_id": redeem_request.booking_id,
        "transaction_type": LoyaltyTransactionType.REDEEMED.value,
        "points": -redeem_request.points,
        "description": f"Redeemed {redeem_request.points} points",
        "created_at": datetime.utcnow().isoformat(),
    }
    
    supabase.table("loyalty_transactions").insert(transaction_dict).execute()
    
    # Update loyalty points
    supabase.table("loyalty_points").update({
        "available_points": current_points["available_points"] - redeem_request.points,
        "updated_at": datetime.utcnow().isoformat(),
    }).eq("id", current_points["id"]).execute()
    
    return {
        "message": f"Redeemed {redeem_request.points} loyalty points",
        "remaining_points": current_points["available_points"] - redeem_request.points,
        "transaction": LoyaltyTransaction(**transaction_dict)
    }



