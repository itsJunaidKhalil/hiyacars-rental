from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class ContractStatus(str, Enum):
    DRAFT = "draft"
    PENDING_RTA = "pending_rta"
    SUBMITTED_TO_RTA = "submitted_to_rta"
    RTA_APPROVED = "rta_approved"
    RTA_REJECTED = "rta_rejected"
    SIGNED = "signed"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Contract(BaseModel):
    id: str
    booking_id: str
    customer_id: str
    vehicle_id: str
    organization_id: str
    
    # Contract details
    contract_number: str  # Auto-generated
    start_date: datetime
    end_date: datetime
    
    # RTA Integration
    rta_contract_id: Optional[str] = None
    rta_submission_status: Optional[str] = None
    rta_submission_date: Optional[datetime] = None
    rta_response: Optional[dict] = None
    
    # PDF
    pdf_url: Optional[str] = None
    
    # Status
    status: ContractStatus = ContractStatus.DRAFT
    
    # Signatures
    customer_signature_url: Optional[str] = None
    agency_signature_url: Optional[str] = None
    customer_signed_at: Optional[datetime] = None
    agency_signed_at: Optional[datetime] = None
    
    # Terms
    terms_and_conditions: Optional[str] = None
    special_conditions: Optional[str] = None
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ContractCreate(BaseModel):
    booking_id: str
    terms_and_conditions: Optional[str] = None
    special_conditions: Optional[str] = None


class ContractUpdate(BaseModel):
    status: Optional[ContractStatus] = None
    rta_contract_id: Optional[str] = None
    rta_submission_status: Optional[str] = None
    pdf_url: Optional[str] = None
    customer_signature_url: Optional[str] = None
    agency_signature_url: Optional[str] = None


class RTASubmissionRequest(BaseModel):
    contract_id: str
    environment: str = "sandbox"  # sandbox or production



