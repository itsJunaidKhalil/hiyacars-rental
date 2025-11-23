from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user import User, UserCreate, UserResponse, UserUpdate
from app.auth import get_current_user, create_access_token
from app.database import get_supabase
from passlib.context import CryptContext
from datetime import datetime
import uuid

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    """Register a new user"""
    supabase = get_supabase()
    
    # Check if user exists
    existing = supabase.table("users").select("id").eq("email", user_data.email).execute()
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user in Supabase Auth (if using email/password)
    user_id = str(uuid.uuid4())
    user_dict = {
        "id": user_id,
        "email": user_data.email,
        "phone": user_data.phone,
        "full_name": user_data.full_name,
        "role": "customer",
        "status": "pending_verification",
        "language": user_data.language,
        "is_kyc_verified": False,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    
    # If password provided, hash it
    if user_data.password:
        hashed_password = get_password_hash(user_data.password)
        # Note: In production, use Supabase Auth API for user creation
        # This is a simplified version
    
    # Insert user
    response = supabase.table("users").insert(user_dict).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user"
        )
    
    return UserResponse(**response.data[0])


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login with email and password"""
    supabase = get_supabase()
    
    # Get user
    response = supabase.table("users").select("*").eq("email", form_data.username).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    user = response.data[0]
    
    # Verify password (in production, use Supabase Auth)
    # For now, this is a placeholder
    # if not verify_password(form_data.password, user.get("password_hash")):
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Incorrect email or password"
    #     )
    
    # Create access token
    access_token = create_access_token(data={"sub": user["id"]})
    
    # Update last login
    supabase.table("users").update({
        "last_login": datetime.utcnow().isoformat()
    }).eq("id", user["id"]).execute()
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(**user)
    }


@router.post("/google")
async def google_auth(token: str):
    """Authenticate with Google OAuth token"""
    # Verify Google token and create/get user
    # This is a placeholder - implement Google token verification
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Google OAuth not yet implemented"
    )


@router.post("/facebook")
async def facebook_auth(token: str):
    """Authenticate with Facebook OAuth token"""
    # Verify Facebook token and create/get user
    # This is a placeholder - implement Facebook token verification
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Facebook OAuth not yet implemented"
    )


@router.post("/phone/otp/send")
async def send_otp(phone: str):
    """Send OTP to phone number"""
    # Integrate with SMS service (Twilio, AWS SNS, etc.)
    # This is a placeholder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Phone OTP not yet implemented"
    )


@router.post("/phone/otp/verify")
async def verify_otp(phone: str, otp: str):
    """Verify OTP and login/register"""
    # Verify OTP and create/get user
    # This is a placeholder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Phone OTP verification not yet implemented"
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
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
    
    return UserResponse(**response.data[0])


@router.post("/refresh")
async def refresh_token(current_user: User = Depends(get_current_user)):
    """Refresh access token"""
    access_token = create_access_token(data={"sub": current_user.id})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


