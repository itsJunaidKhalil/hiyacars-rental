from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class DocumentType(str, Enum):
    EMIRATES_ID = "emirates_id"
    PASSPORT = "passport"
    DRIVING_LICENSE = "driving_license"
    VISA = "visa"


class KYCStatus(str, Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class KYC(BaseModel):
    id: str
    user_id: str
    
    # Documents
    emirates_id_front: Optional[str] = None
    emirates_id_back: Optional[str] = None
    passport_front: Optional[str] = None
    passport_back: Optional[str] = None
    driving_license_front: Optional[str] = None
    driving_license_back: Optional[str] = None
    visa: Optional[str] = None
    
    # Signature
    signature_image: Optional[str] = None
    
    # Personal Info
    full_name: str
    date_of_birth: Optional[datetime] = None
    nationality: Optional[str] = None
    emirates_id_number: Optional[str] = None
    passport_number: Optional[str] = None
    driving_license_number: Optional[str] = None
    
    # Status
    status: KYCStatus = KYCStatus.PENDING
    rejection_reason: Optional[str] = None
    reviewed_by: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class KYCCreate(BaseModel):
    full_name: str
    date_of_birth: Optional[datetime] = None
    nationality: Optional[str] = None
    emirates_id_number: Optional[str] = None
    passport_number: Optional[str] = None
    driving_license_number: Optional[str] = None


class KYCDocumentUpload(BaseModel):
    document_type: DocumentType
    side: str  # front, back
    file_url: str


class KYCSignatureUpload(BaseModel):
    signature_image_url: str


class KYCUpdate(BaseModel):
    status: Optional[KYCStatus] = None
    rejection_reason: Optional[str] = None



