"""
Supabase Auth Integration Endpoints
These endpoints work with Supabase Auth and sync user data
"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.models.user import User, UserResponse, UserUpdate
from app.auth_supabase import get_current_user
from app.database import get_supabase
from datetime import datetime

router = APIRouter()


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile from Supabase Auth"""
    return UserResponse(**current_user.dict())


@router.put("/me", response_model=UserResponse)
async def update_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update current user profile"""
    supabase = get_supabase()
    
    update_data = user_update.dict(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    response = supabase.table("users").update(update_data).eq("id", current_user.id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Note: Updating Supabase Auth metadata requires admin API
    # This is optional - the database trigger will handle sync
    # Uncomment if you want to update Supabase Auth metadata directly:
    # supabase_admin = get_supabase_admin()
    # try:
    #     supabase_admin.auth.admin.update_user_by_id(
    #         current_user.id,
    #         {
    #             "user_metadata": {
    #                 "full_name": update_data.get("full_name", current_user.full_name),
    #                 "phone": update_data.get("phone", current_user.phone),
    #                 "language": update_data.get("language", current_user.language),
    #             }
    #         }
    #     )
    # except Exception as e:
    #     print(f"Error updating Supabase Auth metadata: {e}")
    
    return UserResponse(**response.data[0])


@router.post("/refresh")
async def refresh_token(current_user: User = Depends(get_current_user)):
    """Refresh token - handled by Supabase Auth client"""
    # Supabase handles token refresh automatically
    # This endpoint is kept for compatibility
    return {
        "message": "Token refresh is handled automatically by Supabase Auth client"
    }

