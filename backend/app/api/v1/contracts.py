from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional, List
from app.models.contract import (
    Contract, ContractCreate, ContractUpdate, ContractStatus,
    RTASubmissionRequest
)
from app.models.booking import Booking, BookingStatus
from app.auth_supabase import get_current_user, require_role
from app.models.user import User, UserRole
from app.database import get_supabase
from config import settings
from datetime import datetime
import uuid
import httpx
import json

router = APIRouter()


async def generate_contract_pdf(contract: dict) -> str:
    """Generate PDF contract document"""
    # This is a placeholder - implement PDF generation using reportlab
    # Upload to S3 and return URL
    # For now, return a placeholder URL
    return f"https://example.com/contracts/{contract['id']}.pdf"


async def submit_to_rta(contract: dict, environment: str = "sandbox") -> dict:
    """Submit contract to RTA API"""
    rta_url = f"{settings.RTA_API_URL}/contracts" if environment == "sandbox" else f"{settings.RTA_API_URL}/contracts"
    
    # Prepare RTA payload (adjust based on actual RTA API requirements)
    rta_payload = {
        "contract_number": contract["contract_number"],
        "customer_id": contract["customer_id"],
        "vehicle_id": contract["vehicle_id"],
        "start_date": contract["start_date"],
        "end_date": contract["end_date"],
        # Add other required fields based on RTA API spec
    }
    
    headers = {
        "Authorization": f"Bearer {settings.RTA_API_KEY}",
        "Content-Type": "application/json"
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                rta_url,
                json=rta_payload,
                headers=headers,
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RTA API error: {str(e)}"
        )


@router.post("/", response_model=Contract, status_code=status.HTTP_201_CREATED)
async def create_contract(
    contract_data: ContractCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a contract for a booking"""
    supabase = get_supabase()
    
    # Get booking
    booking_response = supabase.table("bookings").select("*").eq("id", contract_data.booking_id).execute()
    if not booking_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )
    
    booking = booking_response.data[0]
    
    # Check authorization
    if booking["customer_id"] != current_user.id and current_user.role not in [UserRole.ORG_ADMIN, UserRole.AGENCY_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    # Check if booking is confirmed
    if booking["status"] != BookingStatus.CONFIRMED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Booking must be confirmed to create contract"
        )
    
    # Check if contract already exists
    existing = supabase.table("contracts").select("id").eq("booking_id", contract_data.booking_id).execute()
    if existing.data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract already exists for this booking"
        )
    
    # Generate contract number
    contract_number = f"CONTRACT-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
    
    contract_id = str(uuid.uuid4())
    contract_dict = {
        "id": contract_id,
        "booking_id": contract_data.booking_id,
        "customer_id": booking["customer_id"],
        "vehicle_id": booking["vehicle_id"],
        "organization_id": booking["organization_id"],
        "contract_number": contract_number,
        "start_date": booking["pickup_date"],
        "end_date": booking["return_date"],
        "status": ContractStatus.DRAFT.value,
        "terms_and_conditions": contract_data.terms_and_conditions,
        "special_conditions": contract_data.special_conditions,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }
    
    response = supabase.table("contracts").insert(contract_dict).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create contract"
        )
    
    # Generate PDF
    pdf_url = await generate_contract_pdf(response.data[0])
    
    # Update contract with PDF URL
    supabase.table("contracts").update({
        "pdf_url": pdf_url
    }).eq("id", contract_id).execute()
    
    contract = response.data[0]
    contract["pdf_url"] = pdf_url
    
    return Contract(**contract)


@router.get("/{contract_id}", response_model=Contract)
async def get_contract(
    contract_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get contract details"""
    supabase = get_supabase()
    
    response = supabase.table("contracts").select("*").eq("id", contract_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    contract = response.data[0]
    
    # Check authorization
    if contract["customer_id"] != current_user.id and current_user.role not in [UserRole.ORG_ADMIN, UserRole.AGENCY_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    return Contract(**contract)


@router.post("/{contract_id}/sign")
async def sign_contract(
    contract_id: str,
    signature_url: str,
    current_user: User = Depends(get_current_user)
):
    """Sign contract"""
    supabase = get_supabase()
    
    # Get contract
    contract_response = supabase.table("contracts").select("*").eq("id", contract_id).execute()
    if not contract_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    contract = contract_response.data[0]
    
    # Check authorization
    if contract["customer_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to sign this contract"
        )
    
    # Update contract with signature
    update_data = {
        "customer_signature_url": signature_url,
        "customer_signed_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat()
    }
    
    # If both parties signed, update status
    if contract.get("agency_signature_url"):
        update_data["status"] = ContractStatus.SIGNED.value
    
    response = supabase.table("contracts").update(update_data).eq("id", contract_id).execute()
    
    return Contract(**response.data[0])


@router.post("/{contract_id}/submit-rta")
async def submit_contract_to_rta(
    contract_id: str,
    rta_request: RTASubmissionRequest,
    current_user: User = Depends(require_role([UserRole.ORG_ADMIN, UserRole.AGENCY_ADMIN]))
):
    """Submit contract to RTA"""
    supabase = get_supabase()
    
    # Get contract
    contract_response = supabase.table("contracts").select("*").eq("id", contract_id).execute()
    if not contract_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    contract = contract_response.data[0]
    
    # Check if contract is signed
    if contract["status"] != ContractStatus.SIGNED.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contract must be signed before submitting to RTA"
        )
    
    # Submit to RTA
    rta_response = await submit_to_rta(contract, rta_request.environment)
    
    # Update contract
    update_data = {
        "rta_contract_id": rta_response.get("contract_id"),
        "rta_submission_status": "submitted",
        "rta_submission_date": datetime.utcnow().isoformat(),
        "rta_response": json.dumps(rta_response),
        "status": ContractStatus.SUBMITTED_TO_RTA.value,
        "updated_at": datetime.utcnow().isoformat()
    }
    
    response = supabase.table("contracts").update(update_data).eq("id", contract_id).execute()
    
    return Contract(**response.data[0])


@router.get("/booking/{booking_id}", response_model=Contract)
async def get_booking_contract(
    booking_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get contract for a booking"""
    supabase = get_supabase()
    
    response = supabase.table("contracts").select("*").eq("booking_id", booking_id).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found"
        )
    
    contract = response.data[0]
    
    # Check authorization
    if contract["customer_id"] != current_user.id and current_user.role not in [UserRole.ORG_ADMIN, UserRole.AGENCY_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized"
        )
    
    return Contract(**response.data[0])



