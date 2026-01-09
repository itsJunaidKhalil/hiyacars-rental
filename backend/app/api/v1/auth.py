from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user import User, UserCreate, UserResponse, UserUpdate
from app.auth_supabase import get_current_user, create_access_token
from app.database import get_supabase
from app.storage import upload_file
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
   """Register a new user using Supabase Admin API"""
   from app.database import get_supabase_admin
  
   supabase_admin = get_supabase_admin()
  
   try:
       # Create user in Supabase Auth first using admin API
       # According to Supabase docs, create_user takes a dict with these keys
       auth_user_data = {
           "email": user_data.email,
           "password": user_data.password,
           "email_confirm": False,  # keep unconfirmed; we'll send invite email
           "user_metadata": {
               "full_name": user_data.full_name,
               "phone": user_data.phone,
               "language": user_data.language,
           }
       }
      
       auth_response = supabase_admin.auth.admin.create_user(auth_user_data)
       user_id = auth_response.user.id

       # Send invite/confirmation email with redirect
       try:
           supabase_admin.auth.admin.invite_user_by_email(
               email=user_data.email,
               options={
                   "email_redirect_to": "https://example.com/welcome"
               }
           )
       except Exception:
           # If invite fails, continue; user can request resend
           pass
      
   except Exception as e:
       error_msg = str(e).lower()
       if "already" in error_msg or "exists" in error_msg:
           raise HTTPException(
               status_code=status.HTTP_400_BAD_REQUEST,
               detail="Email already registered"
           )
       raise HTTPException(
           status_code=status.HTTP_400_BAD_REQUEST,
           detail=f"Failed to create user: {str(e)}"
       )
  
   # The database trigger should automatically create the user record
   # Wait a moment and check if it exists
   supabase = get_supabase()
  
   try:
       # Check if trigger created the user
       response = supabase.table("users").select("*").eq("id", user_id).execute()
      
       if response.data:
           return UserResponse(**response.data[0])
      
       # If trigger didn't create it, create manually as fallback
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
      
       response = supabase.table("users").insert(user_dict).execute()
      
       if not response.data:
           raise HTTPException(
               status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
               detail="Failed to create user record"
           )
      
       return UserResponse(**response.data[0])
      
   except Exception as e:
       # If user creation in table fails, clean up auth user
       try:
           supabase_admin.auth.admin.delete_user(user_id)
       except:
           pass
      
       raise HTTPException(
           status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
           detail=f"Failed to create user record: {str(e)}"
       )


@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
   """Login with email and password via Supabase Auth"""
   supabase = get_supabase()

   try:
       auth_res = supabase.auth.sign_in_with_password({
           "email": form_data.username,
           "password": form_data.password,
       })
   except Exception as e:
       raise HTTPException(
           status_code=status.HTTP_401_UNAUTHORIZED,
           detail=f"Authentication failed: {str(e)}",
       )

   session = getattr(auth_res, "session", None)
   user_obj = getattr(auth_res, "user", None)
   if not session or not user_obj:
       raise HTTPException(
           status_code=status.HTTP_401_UNAUTHORIZED,
           detail="Invalid credentials",
       )

   user_id = user_obj.id

   # Fetch profile from users table
   db_res = supabase.table("users").select("*").eq("id", user_id).execute()
   if not db_res.data:
       raise HTTPException(
           status_code=status.HTTP_404_NOT_FOUND,
           detail="User profile not found",
       )
   user = db_res.data[0]

   # Update last login
   supabase.table("users").update({
       "last_login": datetime.utcnow().isoformat()
   }).eq("id", user_id).execute()

   return {
       "access_token": session.access_token,
       "refresh_token": session.refresh_token,
       "token_type": "bearer",
       "user": UserResponse(**user),
   }


@router.post("/resend-confirmation")
async def resend_confirmation(email: str, redirect_to: str | None = None):
   """Resend email confirmation for a user"""
   from app.database import get_supabase_admin
   supabase_admin = get_supabase_admin()

   opts = {"email_redirect_to": redirect_to or "https://example.com/welcome"}
   try:
       supabase_admin.auth.admin.resend({
           "type": "signup",
           "email": email,
           "options": opts,
       })
       return {"message": "Confirmation email resent"}
   except Exception as e:
       raise HTTPException(
           status_code=status.HTTP_400_BAD_REQUEST,
           detail=f"Failed to resend confirmation: {str(e)}",
       )


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


@router.post("/me/avatar")
async def upload_avatar(
   file: UploadFile = File(...),
   current_user: User = Depends(get_current_user)
):
   """Upload user profile picture"""
   supabase = get_supabase()
   
   # Validate file type (images only)
   if not file.content_type or not file.content_type.startswith('image/'):
       raise HTTPException(
           status_code=status.HTTP_400_BAD_REQUEST,
           detail="Only image files are allowed"
       )
   
   # Upload avatar to Supabase Storage
   avatar_url = await upload_file(
       file=file,
       bucket="avatars",
       folder=current_user.id,
       file_name="avatar.jpg"  # Always overwrite the same file
   )
   
   # Update user profile
   response = supabase.table("users").update({
       "profile_picture": avatar_url,
       "updated_at": datetime.utcnow().isoformat()
   }).eq("id", current_user.id).execute()
   
   if not response.data:
       raise HTTPException(
           status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
           detail="Failed to update profile"
       )
   
   return {
       "message": "Avatar uploaded successfully",
       "avatar_url": avatar_url,
       "user": UserResponse(**response.data[0])
   }



