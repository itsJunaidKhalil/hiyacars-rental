from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from app.models.booking import (
    Booking, BookingCreate, BookingUpdate, BookingResponse,
    BookingStatus, RentalType
)
from app.models.vehicle import Vehicle
from app.auth_supabase import get_current_user, require_role
from app.models.user import User, UserRole
from app.database import get_supabase
from config import settings
from datetime import datetime, timedelta
import uuid
import math

router = APIRouter()


def calculate_booking_price(
    vehicle: dict,
    pickup_date: datetime,
    return_date: datetime,
    rental_type: RentalType,
    surge_multiplier: float = 1.0,
    with_driver: bool = False
) -> dict:
    """Calculate booking price based on rental type and duration"""
    duration = return_date - pickup_date
    
    if rental_type == RentalType.HOUR:
        hours = max(1, math.ceil(duration.total_seconds() / 3600))
        base_price = vehicle.get("price_per_hour", vehicle["price_per_day"] / 24) * hours
    elif rental_type == RentalType.DAY:
        days = max(1, math.ceil(duration.days))
        base_price = vehicle["price_per_day"] * days
    elif rental_type == RentalType.WEEKLY:
        weeks = max(1, math.ceil(duration.days / 7))
        base_price = vehicle["price_per_week"] * weeks
    else:  # MONTHLY
        months = max(1, math.ceil(duration.days / 30))
        base_price = vehicle["price_per_month"] * months
    
    # Apply surge pricing
    base_price *= surge_multiplier
    
    # Driver fee (if applicable)
    driver_fee = 0.0
    if with_driver:
        driver_fee = base_price * 0.15  # 15% of base price
    
    # Platform fee
    platform_fee = (base_price + driver_fee) * (settings.PLATFORM_FEE_PERCENTAGE / 100)
    
    total_price = base_price + driver_fee + platform_fee
    
    return {
        "base_price": round(base_price, 2),
        "surge_multiplier": surge_multiplier,
        "driver_fee": round(driver_fee, 2),
        "platform_fee": round(platform_fee, 2),
        "total_price": round(total_price, 2)
    }


def calculate_surge_multiplier(
    vehicle_id: str,
    pickup_date: datetime,
    return_date: datetime
) -> float:
    """Calculate surge pricing multiplier based on demand"""
    supabase = get_supabase()
    
    # Check bookings in similar time period
    # This is a simplified version - implement actual surge logic
    bookings = supabase.table("bookings").select("id").eq("vehicle_id", vehicle_id).or_(
        f"and(pickup_date.lte.{pickup_date.isoformat()},return_date.gte.{pickup_date.isoformat()}),"
        f"and(pickup_date.lte.{return_date.isoformat()},return_date.gte.{return_date.isoformat()})"
    ).in_("status", ["confirmed", "in_progress"]).execute()
    
    # Simple surge: 1.0x base, 1.2x if 50%+ booked, 1.5x if 80%+ booked
    # In production, implement more sophisticated surge pricing
    return 1.0


@router.post("/", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def create_booking(
    booking_data: BookingCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new booking"""
    supabase = get_supabase()
    
    # Check KYC verification
    if not current_user.is_kyc_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="KYC verification required to make bookings"
        )
    
    # Get vehicle
    vehicle_response = supabase.table("vehicles").select("*").eq("id", booking_data.vehicle_id).execute()
    if not vehicle_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    vehicle = vehicle_response.data[0]
    
    # Check availability
    availability = await check_availability(
        booking_data.vehicle_id,
        booking_data.pickup_date,
        booking_data.return_date,
        current_user
    )
    
    if not availability["available"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Vehicle not available for selected dates"
        )
    
    # Calculate surge multiplier
    surge_multiplier = calculate_surge_multiplier(
        booking_data.vehicle_id,
        booking_data.pickup_date,
        booking_data.return_date
    )
    
    # Calculate pricing
    pricing = calculate_booking_price(
        vehicle,
        booking_data.pickup_date,
        booking_data.return_date,
        booking_data.rental_type,
        surge_multiplier,
        booking_data.with_driver
    )
    
    # Create booking
    booking_id = str(uuid.uuid4())
    booking_dict = {
        "id": booking_id,
        "customer_id": current_user.id,
        "vehicle_id": booking_data.vehicle_id,
        "organization_id": vehicle["organization_id"],
        "pickup_date": booking_data.pickup_date.isoformat(),
        "return_date": booking_data.return_date.isoformat(),
        "rental_type": booking_data.rental_type.value,
        "pickup_location": booking_data.pickup_location,
        "return_location": booking_data.return_location,
        "base_price": pricing["base_price"],
        "surge_multiplier": pricing["surge_multiplier"],
        "driver_fee": pricing["driver_fee"],
        "platform_fee": pricing["platform_fee"],
        "total_price": pricing["total_price"],
        "status": BookingStatus.PENDING.value,
        "with_driver": booking_data.with_driver,
        "customer_gender": booking_data.customer_gender,
        "special_requests": booking_data.special_requests,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    
    response = supabase.table("bookings").insert(booking_dict).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create booking"
        )
    
    booking = response.data[0]
    booking["vehicle"] = vehicle
    
    return BookingResponse(**booking)


@router.get("/", response_model=List[BookingResponse])
async def list_bookings(
    status_filter: Optional[BookingStatus] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user)
):
    """List bookings for current user"""
    supabase = get_supabase()
    
    query = supabase.table("bookings").select("*, vehicles(*)").eq("customer_id", current_user.id)
    
    if status_filter:
        query = query.eq("status", status_filter.value)
    
    # Pagination
    from_index = (page - 1) * limit
    to_index = from_index + limit - 1
    
    response = query.order("created_at", desc=True).range(from_index, to_index).execute()
    
    bookings = []
    for item in response.data:
        booking_dict = item.copy()
        booking_dict["vehicle"] = item.get("vehicles", {})
        bookings.append(BookingResponse(**booking_dict))
    
    return bookings


@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get booking details"""
    supabase = get_supabase()
    
    response = supabase.table("bookings").select("*, vehicles(*)").eq("id", booking_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    booking = response.data[0]
    
    # Check authorization
    if booking["customer_id"] != current_user.id and current_user.role not in [UserRole.ORG_ADMIN, UserRole.AGENCY_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this booking"
        )
    
    booking_dict = booking.copy()
    booking_dict["vehicle"] = booking.get("vehicles", {})
    
    return BookingResponse(**booking_dict)


@router.put("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: str,
    booking_update: BookingUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update booking"""
    supabase = get_supabase()
    
    # Get existing booking
    existing = supabase.table("bookings").select("*").eq("id", booking_id).execute()
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    booking = existing.data[0]
    
    # Check authorization
    if booking["customer_id"] != current_user.id and current_user.role not in [UserRole.ORG_ADMIN, UserRole.AGENCY_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this booking"
        )
    
    # Only allow updates if booking is pending or confirmed
    if booking["status"] not in [BookingStatus.PENDING.value, BookingStatus.CONFIRMED.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot update booking in current status"
        )
    
    update_data = booking_update.dict(exclude_unset=True)
    if "pickup_date" in update_data:
        update_data["pickup_date"] = update_data["pickup_date"].isoformat()
    if "return_date" in update_data:
        update_data["return_date"] = update_data["return_date"].isoformat()
    if "status" in update_data:
        update_data["status"] = update_data["status"].value
    
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    response = supabase.table("bookings").update(update_data).eq("id", booking_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update booking"
        )
    
    booking = response.data[0]
    vehicle_response = supabase.table("vehicles").select("*").eq("id", booking["vehicle_id"]).execute()
    booking["vehicle"] = vehicle_response.data[0] if vehicle_response.data else {}
    
    return BookingResponse(**booking)


@router.post("/{booking_id}/cancel", response_model=BookingResponse)
async def cancel_booking(
    booking_id: str,
    current_user: User = Depends(get_current_user)
):
    """Cancel a booking"""
    supabase = get_supabase()
    
    # Get existing booking
    existing = supabase.table("bookings").select("*").eq("id", booking_id).execute()
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    booking = existing.data[0]
    
    # Check authorization
    if booking["customer_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to cancel this booking"
        )
    
    # Only allow cancellation if booking is pending or confirmed
    if booking["status"] not in [BookingStatus.PENDING.value, BookingStatus.CONFIRMED.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel booking in current status"
        )
    
    # Update status
    response = supabase.table("bookings").update({
        "status": BookingStatus.CANCELLED.value,
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", booking_id).execute()
    
    booking = response.data[0]
    vehicle_response = supabase.table("vehicles").select("*").eq("id", booking["vehicle_id"]).execute()
    booking["vehicle"] = vehicle_response.data[0] if vehicle_response.data else {}
    
    return BookingResponse(**booking)


async def check_availability(
    vehicle_id: str,
    start_date: datetime,
    end_date: datetime,
    current_user: User
):
    """Check vehicle availability"""
    supabase = get_supabase()
    
    bookings = supabase.table("bookings").select("*").eq("vehicle_id", vehicle_id).or_(
        f"and(pickup_date.lte.{start_date.isoformat()},return_date.gte.{start_date.isoformat()}),"
        f"and(pickup_date.lte.{end_date.isoformat()},return_date.gte.{end_date.isoformat()}),"
        f"and(pickup_date.gte.{start_date.isoformat()},return_date.lte.{end_date.isoformat()})"
    ).in_("status", ["confirmed", "in_progress"]).execute()
    
    return {
        "available": len(bookings.data) == 0,
        "conflicting_bookings": len(bookings.data)
    }



