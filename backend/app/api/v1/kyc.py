from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from typing import Optional
from app.models.kyc import (
    KYC, KYCCreate, KYCDocumentUpload, KYCSignatureUpload,
    KYCUpdate, KYCStatus, DocumentType
)
from app.auth_supabase import get_current_user, require_role
from app.models.user import User, UserRole
from app.database import get_supabase
from app.storage import upload_file
from datetime import datetime
import uuid

router = APIRouter()


@router.post("/", response_model=KYC, status_code=status.HTTP_201_CREATED)
async def create_kyc(
    kyc_data: KYCCreate,
    current_user: User = Depends(get_current_user)
):
    """Create KYC application"""
    supabase = get_supabase()
    
    # Check if KYC already exists
    existing = supabase.table("kyc").select("id").eq("user_id", current_user.id).execute()
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="KYC application already exists"
        )
    
    kyc_id = str(uuid.uuid4())
    kyc_dict = {
        "id": kyc_id,
        "user_id": current_user.id,
        "full_name": kyc_data.full_name,
        "date_of_birth": kyc_data.date_of_birth.isoformat() if kyc_data.date_of_birth else None,
        "nationality": kyc_data.nationality,
        "emirates_id_number": kyc_data.emirates_id_number,
        "passport_number": kyc_data.passport_number,
        "driving_license_number": kyc_data.driving_license_number,
        "status": KYCStatus.PENDING.value,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    
    response = supabase.table("kyc").insert(kyc_dict).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create KYC application"
        )
    
    return KYC(**response.data[0])


@router.get("/", response_model=KYC)
async def get_kyc(
    current_user: User = Depends(get_current_user)
):
    """Get current user's KYC"""
    supabase = get_supabase()
    
    response = supabase.table("kyc").select("*").eq("user_id", current_user.id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC not found"
        )
    
    return KYC(**response.data[0])


@router.post("/documents/{document_type}")
async def upload_document(
    document_type: DocumentType,
    side: str,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload KYC document"""
    supabase = get_supabase()
    
    # Get KYC
    kyc_response = supabase.table("kyc").select("*").eq("user_id", current_user.id).execute()
    if not kyc_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC application not found. Please create KYC first."
        )
    
    kyc = kyc_response.data[0]
    
    # Upload file to Supabase Storage
    file_url = await upload_file(
        file=file,
        bucket="kyc-documents",
        folder=f"{current_user.id}/{document_type.value}"
    )
    
    # Update KYC with document URL
    update_field = None
    if document_type == DocumentType.EMIRATES_ID:
        update_field = f"emirates_id_{side}"
    elif document_type == DocumentType.PASSPORT:
        update_field = f"passport_{side}"
    elif document_type == DocumentType.DRIVING_LICENSE:
        update_field = f"driving_license_{side}"
    elif document_type == DocumentType.VISA:
        update_field = "visa"
    
    if not update_field:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document type"
        )
    
    update_data = {
        update_field: file_url,
        "updated_at": datetime.utcnow().isoformat()
    }
    
    # If all required documents uploaded, change status to under_review
    # (This is simplified - implement proper validation)
    if kyc["status"] == KYCStatus.PENDING.value:
        update_data["status"] = KYCStatus.UNDER_REVIEW.value
    
    response = supabase.table("kyc").update(update_data).eq("id", kyc["id"]).execute()
    
    return {
        "message": "Document uploaded successfully",
        "file_url": file_url,
        "kyc": KYC(**response.data[0])
    }


@router.post("/signature")
async def upload_signature(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """Upload signature"""
    supabase = get_supabase()
    
    # Get KYC
    kyc_response = supabase.table("kyc").select("*").eq("user_id", current_user.id).execute()
    if not kyc_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC application not found"
        )
    
    kyc = kyc_response.data[0]
    
    # Upload signature to Supabase Storage
    signature_url = await upload_file(
        file=file,
        bucket="kyc-documents",
        folder=f"{current_user.id}/signatures"
    )
    
    # Update KYC
    response = supabase.table("kyc").update({
        "signature_image": signature_url,
        "updated_at": datetime.utcnow().isoformat()
    }).eq("id", kyc["id"]).execute()
    
    return {
        "message": "Signature uploaded successfully",
        "signature_url": signature_url,
        "kyc": KYC(**response.data[0])
    }


@router.put("/{kyc_id}", response_model=KYC)
async def update_kyc(
    kyc_id: str,
    kyc_update: KYCUpdate,
    current_user: User = Depends(require_role([UserRole.ORG_ADMIN, UserRole.SUPPORT]))
):
    """Update KYC status (Admin only)"""
    supabase = get_supabase()
    
    # Get existing KYC
    existing = supabase.table("kyc").select("*").eq("id", kyc_id).execute()
    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="KYC not found"
        )
    
    update_data = kyc_update.dict(exclude_unset=True)
    if "status" in update_data:
        update_data["status"] = update_data["status"].value
    
    update_data["reviewed_by"] = current_user.id
    update_data["reviewed_at"] = datetime.utcnow().isoformat()
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    # If approved, update user's KYC status
    if update_data.get("status") == KYCStatus.APPROVED.value:
        kyc = existing.data[0]
        supabase.table("users").update({
            "is_kyc_verified": True,
            "status": "active"
        }).eq("id", kyc["user_id"]).execute()
    
    response = supabase.table("kyc").update(update_data).eq("id", kyc_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update KYC"
        )
    
    return KYC(**response.data[0])


