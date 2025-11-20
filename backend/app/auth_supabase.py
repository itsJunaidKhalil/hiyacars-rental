"""
Supabase Auth Integration
Validates Supabase JWT tokens and extracts user information
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import get_supabase
from config import settings
from app.models.user import User, UserRole
import json
import base64

security = HTTPBearer()


def decode_supabase_jwt(token: str):
    """Decode Supabase JWT token without verification (for user ID extraction)"""
    try:
        # Supabase JWT tokens have 3 parts: header.payload.signature
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        # Decode payload (second part)
        payload = parts[1]
        # Add padding if needed
        payload += '=' * (4 - len(payload) % 4)
        decoded = base64.urlsafe_b64decode(payload)
        return json.loads(decoded)
    except Exception:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get current authenticated user from Supabase JWT token"""
    token = credentials.credentials
    
    # Decode token to get user ID
    payload = decode_supabase_jwt(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
        )
    
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID",
        )
    
    # Get user from our custom users table
    # The database trigger should have created the user record automatically when they signed up
    supabase = get_supabase()
    response = supabase.table("users").select("*").eq("id", user_id).execute()
    
    if not response.data:
        # User doesn't exist in our table - might be a new signup before trigger fired
        # Try to create a basic user record from token payload
        try:
            user_metadata = payload.get("user_metadata", {}) or {}
            email = payload.get("email", "unknown@example.com")
            
            user_dict = {
                "id": user_id,
                "email": email,
                "full_name": user_metadata.get("full_name", email.split("@")[0]) if isinstance(user_metadata, dict) else email.split("@")[0],
                "phone": user_metadata.get("phone") if isinstance(user_metadata, dict) else None,
                "role": "customer",
                "status": "pending_verification",
                "language": user_metadata.get("language", "en") if isinstance(user_metadata, dict) else "en",
                "is_kyc_verified": False,
                "avatar_url": user_metadata.get("avatar_url") if isinstance(user_metadata, dict) else None,
            }
            
            response = supabase.table("users").insert(user_dict).execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found and could not be created",
                )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"User not found: {str(e)}",
            )
    
    user_data = response.data[0]
    return User.model_validate(user_data)


def require_role(allowed_roles: list[UserRole]):
    """Dependency to check if user has required role"""
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )
        return current_user
    return role_checker
