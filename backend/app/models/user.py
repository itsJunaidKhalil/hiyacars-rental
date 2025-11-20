from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    CUSTOMER = "customer"
    ORG_ADMIN = "org_admin"
    AGENCY_ADMIN = "agency_admin"
    STAFF = "staff"
    INVESTOR = "investor"
    SUPPORT = "support"


class UserStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"
    PENDING_VERIFICATION = "pending_verification"


class User(BaseModel):
    id: str
    email: EmailStr
    phone: Optional[str] = None
    full_name: str
    role: UserRole = UserRole.CUSTOMER
    status: UserStatus = UserStatus.PENDING_VERIFICATION
    avatar_url: Optional[str] = None
    language: str = "en"  # en or ar
    is_kyc_verified: bool = False
    organization_id: Optional[str] = None  # For multi-tenant
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: EmailStr
    password: Optional[str] = None  # None for OAuth
    phone: Optional[str] = None
    full_name: str
    provider: str = "email"  # email, google, facebook, phone
    provider_id: Optional[str] = None  # OAuth provider user ID
    language: str = "en"


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    avatar_url: Optional[str] = None
    language: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    phone: Optional[str] = None
    full_name: str
    role: UserRole
    status: UserStatus
    avatar_url: Optional[str] = None
    language: str
    is_kyc_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True



