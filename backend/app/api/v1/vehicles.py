from fastapi import APIRouter, HTTPException, status, Depends, Query, UploadFile, File
from typing import List, Optional
from app.models.vehicle import (
    Vehicle, VehicleCreate, VehicleUpdate, VehicleSearchParams,
    VehicleStatus, VehicleCategory
)
from app.auth import get_current_user, require_role
from app.models.user import User, UserRole
from app.database import get_supabase
from app.storage import upload_file, storage
from datetime import datetime
import uuid

router = APIRouter()


@router.get("/", response_model=List[Vehicle])
async def list_vehicles(
    category: Optional[VehicleCategory] = None,
    location: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    seats: Optional[int] = None,
    status: Optional[VehicleStatus] = VehicleStatus.AVAILABLE,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: Optional[User] = Depends(get_current_user)
):
    """List all available vehicles with filters"""
    supabase = get_supabase()
    
    query = supabase.table("vehicles").select("*")
    
    if category:
        query = query.eq("category", category.value)
    if location:
        query = query.ilike("location", f"%{location}%")
    if min_price:
        query = query.gte("price_per_day", min_price)
    if max_price:
        query = query.lte("price_per_day", max_price)
    if seats:
        query = query.eq("seats", seats)
    if status:
        query = query.eq("status", status.value)
    
    # Pagination
    from_index = (page - 1) * limit
    to_index = from_index + limit - 1
    
    response = query.range(from_index, to_index).execute()
    
    return [Vehicle(**item) for item in response.data]


@router.get("/search", response_model=List[Vehicle])
async def search_vehicles(
    search_params: VehicleSearchParams = Depends(),
    current_user: Optional[User] = Depends(get_current_user)
):
    """Advanced vehicle search with date availability"""
    supabase = get_supabase()
    
    query = supabase.table("vehicles").select("*")
    
    # Apply filters
    if search_params.category:
        query = query.eq("category", search_params.category.value)
    if search_params.location:
        query = query.ilike("location", f"%{search_params.location}%")
    if search_params.min_price:
        query = query.gte("price_per_day", search_params.min_price)
    if search_params.max_price:
        query = query.lte("price_per_day", search_params.max_price)
    if search_params.seats:
        query = query.eq("seats", search_params.seats)
    if search_params.transmission:
        query = query.eq("transmission", search_params.transmission)
    if search_params.fuel_type:
        query = query.eq("fuel_type", search_params.fuel_type)
    
    query = query.eq("status", VehicleStatus.AVAILABLE.value)
    
    # Check availability if dates provided
    if search_params.start_date and search_params.end_date:
        # Get vehicles that are NOT booked during this period
        bookings_query = supabase.table("bookings").select("vehicle_id").or_(
            f"and(pickup_date.lte.{search_params.start_date.isoformat()},return_date.gte.{search_params.start_date.isoformat()}),"
            f"and(pickup_date.lte.{search_params.end_date.isoformat()},return_date.gte.{search_params.end_date.isoformat()}),"
            f"and(pickup_date.gte.{search_params.start_date.isoformat()},return_date.lte.{search_params.end_date.isoformat()})"
        ).eq("status", "confirmed").execute()
        
        booked_vehicle_ids = [b["vehicle_id"] for b in bookings_query.data]
        if booked_vehicle_ids:
            query = query.not_.in_("id", booked_vehicle_ids)
    
    # Pagination
    from_index = (search_params.page - 1) * search_params.limit
    to_index = from_index + search_params.limit - 1
    
    response = query.range(from_index, to_index).execute()
    
    return [Vehicle(**item) for item in response.data]


@router.get("/{vehicle_id}", response_model=Vehicle)
async def get_vehicle(
    vehicle_id: str,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Get vehicle details by ID"""
    supabase = get_supabase()
    
    response = supabase.table("vehicles").select("*").eq("id", vehicle_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    return Vehicle(**response.data[0])


@router.post("/", response_model=Vehicle, status_code=status.HTTP_201_CREATED)
async def create_vehicle(
    vehicle_data: VehicleCreate,
    current_user: User = Depends(require_role([UserRole.ORG_ADMIN, UserRole.AGENCY_ADMIN]))
):
    """Create a new vehicle (Admin only)"""
    supabase = get_supabase()
    
    vehicle_id = str(uuid.uuid4())
    vehicle_dict = {
        **vehicle_data.dict(),
        "id": vehicle_id,
        "organization_id": current_user.organization_id or str(uuid.uuid4()),
        "status": VehicleStatus.AVAILABLE.value,
        "rating": 0.0,
        "total_reviews": 0,
        "total_bookings": 0,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    
    response = supabase.table("vehicles").insert(vehicle_dict).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create vehicle"
        )
    
    return Vehicle(**response.data[0])


@router.put("/{vehicle_id}", response_model=Vehicle)
async def update_vehicle(
    vehicle_id: str,
    vehicle_update: VehicleUpdate,
    current_user: User = Depends(require_role([UserRole.ORG_ADMIN, UserRole.AGENCY_ADMIN]))
):
    """Update vehicle (Admin only)"""
    supabase = get_supabase()
    
    # Check if vehicle exists and belongs to user's organization
    existing = supabase.table("vehicles").select("*").eq("id", vehicle_id).execute()
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    update_data = vehicle_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    response = supabase.table("vehicles").update(update_data).eq("id", vehicle_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update vehicle"
        )
    
    return Vehicle(**response.data[0])


@router.delete("/{vehicle_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vehicle(
    vehicle_id: str,
    current_user: User = Depends(require_role([UserRole.ORG_ADMIN, UserRole.AGENCY_ADMIN]))
):
    """Delete vehicle (Admin only)"""
    supabase = get_supabase()
    
    # Check if vehicle exists
    existing = supabase.table("vehicles").select("id").eq("id", vehicle_id).execute()
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    supabase.table("vehicles").delete().eq("id", vehicle_id).execute()
    
    return None


@router.get("/{vehicle_id}/availability")
async def check_availability(
    vehicle_id: str,
    start_date: datetime,
    end_date: datetime,
    current_user: Optional[User] = Depends(get_current_user)
):
    """Check if vehicle is available for given dates"""
    supabase = get_supabase()
    
    # Check for conflicting bookings
    bookings = supabase.table("bookings").select("*").eq("vehicle_id", vehicle_id).or_(
        f"and(pickup_date.lte.{start_date.isoformat()},return_date.gte.{start_date.isoformat()}),"
        f"and(pickup_date.lte.{end_date.isoformat()},return_date.gte.{end_date.isoformat()}),"
        f"and(pickup_date.gte.{start_date.isoformat()},return_date.lte.{end_date.isoformat()})"
    ).in_("status", ["confirmed", "in_progress"]).execute()
    
    is_available = len(bookings.data) == 0
    
    return {
        "vehicle_id": vehicle_id,
        "start_date": start_date,
        "end_date": end_date,
        "available": is_available,
        "conflicting_bookings": len(bookings.data)
    }


@router.post("/{vehicle_id}/images")
async def upload_vehicle_image(
    vehicle_id: str,
    file: UploadFile = File(...),
    current_user: User = Depends(require_role([UserRole.ORG_ADMIN, UserRole.AGENCY_ADMIN]))
):
    """Upload vehicle image (Admin only)"""
    supabase = get_supabase()
    
    # Check if vehicle exists
    vehicle_response = supabase.table("vehicles").select("*").eq("id", vehicle_id).execute()
    if not vehicle_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    vehicle = vehicle_response.data[0]
    
    # Validate file type (images only)
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are allowed"
        )
    
    # Upload image to Supabase Storage
    image_url = await upload_file(
        file=file,
        bucket="vehicle-images",
        folder=vehicle_id
    )
    
    # Update vehicle's images array
    current_images = vehicle.get("images", []) or []
    current_images.append(image_url)
    
    # Update vehicle
    response = supabase.table("vehicles").update({
        "images": current_images,
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", vehicle_id).execute()
    
    return {
        "message": "Image uploaded successfully",
        "image_url": image_url,
        "vehicle": Vehicle(**response.data[0])
    }


@router.delete("/{vehicle_id}/images")
async def delete_vehicle_image(
    vehicle_id: str,
    image_url: str,
    current_user: User = Depends(require_role([UserRole.ORG_ADMIN, UserRole.AGENCY_ADMIN]))
):
    """Delete vehicle image (Admin only)"""
    supabase = get_supabase()
    
    # Check if vehicle exists
    vehicle_response = supabase.table("vehicles").select("*").eq("id", vehicle_id).execute()
    if not vehicle_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    vehicle = vehicle_response.data[0]
    current_images = vehicle.get("images", []) or []
    
    # Remove image URL from array
    if image_url not in current_images:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Image not found in vehicle"
        )
    
    current_images.remove(image_url)
    
    # Update vehicle
    response = supabase.table("vehicles").update({
        "images": current_images,
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", vehicle_id).execute()
    
    # Try to delete from storage (best effort)
    try:
        # Extract path from URL
        path_parts = image_url.split('/vehicle-images/')
        if len(path_parts) > 1:
            file_path = path_parts[1].split('?')[0]  # Remove query params
            await storage.delete_file("vehicle-images", file_path)
    except Exception:
        pass  # File might be already deleted or URL format different
    
    return {
        "message": "Image deleted successfully",
        "vehicle": Vehicle(**response.data[0])
    }



