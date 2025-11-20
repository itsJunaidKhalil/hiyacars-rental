from fastapi import APIRouter, HTTPException, status, Depends
from typing import List, Optional
from app.models.review import Review, ReviewCreate, ReviewUpdate
from app.models.booking import Booking, BookingStatus
from app.auth import get_current_user
from app.models.user import User
from app.database import get_supabase
from datetime import datetime
import uuid

router = APIRouter()


@router.post("/", response_model=Review, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a review for a completed booking"""
    supabase = get_supabase()
    
    # Get booking
    booking_response = supabase.table("bookings").select("*").eq("id", review_data.booking_id).execute()
    if not booking_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    booking = booking_response.data[0]
    
    # Check authorization
    if booking["customer_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Check if booking is completed
    if booking["status"] != BookingStatus.COMPLETED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only review completed bookings"
        )
    
    # Check if review already exists
    existing = supabase.table("reviews").select("id").eq("booking_id", review_data.booking_id).execute()
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Review already exists for this booking"
        )
    
    # Validate rating
    if not 1.0 <= review_data.rating <= 5.0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rating must be between 1.0 and 5.0"
        )
    
    # Create review
    review_id = str(uuid.uuid4())
    review_dict = {
        "id": review_id,
        "booking_id": review_data.booking_id,
        "customer_id": current_user.id,
        "vehicle_id": booking["vehicle_id"],
        "rating": review_data.rating,
        "comment": review_data.comment,
        "cleanliness_rating": review_data.cleanliness_rating,
        "comfort_rating": review_data.comfort_rating,
        "value_rating": review_data.value_rating,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    
    response = supabase.table("reviews").insert(review_dict).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create review"
        )
    
    # Update vehicle rating
    vehicle_reviews = supabase.table("reviews").select("rating").eq(
        "vehicle_id", booking["vehicle_id"]
    ).execute()
    
    if vehicle_reviews.data:
        avg_rating = sum(r["rating"] for r in vehicle_reviews.data) / len(vehicle_reviews.data)
        supabase.table("vehicles").update({
            "rating": round(avg_rating, 2),
            "total_reviews": len(vehicle_reviews.data),
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("id", booking["vehicle_id"]).execute()
    
    return Review(**response.data[0])


@router.get("/vehicle/{vehicle_id}", response_model=List[Review])
async def get_vehicle_reviews(
    vehicle_id: str,
    page: int = 1,
    limit: int = 20,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get reviews for a vehicle"""
    supabase = get_supabase()
    
    from_index = (page - 1) * limit
    to_index = from_index + limit - 1
    
    response = supabase.table("reviews").select("*").eq(
        "vehicle_id", vehicle_id
    ).order("created_at", desc=True).range(from_index, to_index).execute()
    
    return [Review(**item) for item in response.data]


@router.get("/{review_id}", response_model=Review)
async def get_review(
    review_id: str,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get review details"""
    supabase = get_supabase()
    
    response = supabase.table("reviews").select("*").eq("id", review_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    return Review(**response.data[0])


@router.put("/{review_id}", response_model=Review)
async def update_review(
    review_id: str,
    review_update: ReviewUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update review"""
    supabase = get_supabase()
    
    # Get existing review
    existing = supabase.table("reviews").select("*").eq("id", review_id).execute()
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    review = existing.data[0]
    
    # Check authorization
    if review["customer_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    update_data = review_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    response = supabase.table("reviews").update(update_data).eq("id", review_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update review"
        )
    
    # Update vehicle rating if rating changed
    if "rating" in update_data:
        vehicle_reviews = supabase.table("reviews").select("rating").eq(
            "vehicle_id", review["vehicle_id"]
        ).execute()
        
        if vehicle_reviews.data:
            avg_rating = sum(r["rating"] for r in vehicle_reviews.data) / len(vehicle_reviews.data)
            supabase.table("vehicles").update({
                "rating": round(avg_rating, 2),
                "updated_at": datetime.utcnow().isoformat(),
            }).eq("id", review["vehicle_id"]).execute()
    
    return Review(**response.data[0])


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete review"""
    supabase = get_supabase()
    
    # Get existing review
    existing = supabase.table("reviews").select("*").eq("id", review_id).execute()
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    review = existing.data[0]
    
    # Check authorization
    if review["customer_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    supabase.table("reviews").delete().eq("id", review_id).execute()
    
    # Update vehicle rating
    vehicle_reviews = supabase.table("reviews").select("rating").eq(
        "vehicle_id", review["vehicle_id"]
    ).execute()
    
    if vehicle_reviews.data:
        avg_rating = sum(r["rating"] for r in vehicle_reviews.data) / len(vehicle_reviews.data)
        supabase.table("vehicles").update({
            "rating": round(avg_rating, 2),
            "total_reviews": len(vehicle_reviews.data),
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("id", review["vehicle_id"]).execute()
    else:
        supabase.table("vehicles").update({
            "rating": 0.0,
            "total_reviews": 0,
            "updated_at": datetime.utcnow().isoformat(),
        }).eq("id", review["vehicle_id"]).execute()
    
    return None



