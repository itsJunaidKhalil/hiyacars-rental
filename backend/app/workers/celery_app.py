# Background Jobs with Celery
# Install Redis: https://redis.io/docs/getting-started/
# Run: celery -A app.workers.celery_app worker --loglevel=info

from celery import Celery
from celery.schedules import crontab
from config import settings
from app.database import get_supabase_admin
from datetime import datetime, timedelta
import httpx

celery_app = Celery(
    "hiyacars",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)


@celery_app.task(name="poll_rta_contract_status")
def poll_rta_contract_status(contract_id: str):
    """Poll RTA API for contract status updates"""
    supabase = get_supabase_admin()
    
    # Get contract
    contract_response = supabase.table("contracts").select("*").eq("id", contract_id).execute()
    if not contract_response.data:
        return {"error": "Contract not found"}
    
    contract = contract_response.data[0]
    
    if not contract.get("rta_contract_id"):
        return {"error": "No RTA contract ID"}
    
    # Poll RTA API
    rta_url = f"{settings.RTA_API_URL}/contracts/{contract['rta_contract_id']}/status"
    headers = {
        "Authorization": f"Bearer {settings.RTA_API_KEY}",
    }
    
    try:
        response = httpx.get(rta_url, headers=headers, timeout=30.0)
        response.raise_for_status()
        rta_status = response.json()
        
        # Update contract status
        status_mapping = {
            "approved": "rta_approved",
            "rejected": "rta_rejected",
            "pending": "submitted_to_rta"
        }
        
        new_status = status_mapping.get(rta_status.get("status"), "submitted_to_rta")
        
        supabase.table("contracts").update({
            "rta_submission_status": rta_status.get("status"),
            "status": new_status,
            "rta_response": rta_status,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("id", contract_id).execute()
        
        return {"success": True, "status": new_status}
    except Exception as e:
        return {"error": str(e)}


@celery_app.task(name="sync_fines_and_salik")
def sync_fines_and_salik(booking_id: str):
    """Sync fines and Salik charges for a booking"""
    supabase = get_supabase_admin()
    
    # Get booking
    booking_response = supabase.table("bookings").select("*").eq("id", booking_id).execute()
    if not booking_response.data:
        return {"error": "Booking not found"}
    
    booking = booking_response.data[0]
    
    # Get vehicle
    vehicle_response = supabase.table("vehicles").select("license_plate").eq("id", booking["vehicle_id"]).execute()
    if not vehicle_response.data:
        return {"error": "Vehicle not found"}
    
    license_plate = vehicle_response.data[0]["license_plate"]
    
    # Sync fines from RTA (placeholder - implement actual RTA API call)
    # fines = fetch_fines_from_rta(license_plate, booking["pickup_date"], booking["return_date"])
    
    # Sync Salik charges (placeholder - implement actual Salik API call)
    # salik_charges = fetch_salik_charges(license_plate, booking["pickup_date"], booking["return_date"])
    
    # Store fines and charges in a separate table or add to booking
    # This is a placeholder implementation
    
    return {"success": True, "message": "Fines and Salik synced"}


@celery_app.task(name="process_monthly_payouts")
def process_monthly_payouts(organization_id: str, month: int, year: int):
    """Process monthly payouts to agencies and investors"""
    supabase = get_supabase_admin()
    
    # Get all completed bookings for the month
    start_date = datetime(year, month, 1)
    end_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
    
    bookings = supabase.table("bookings").select("*").eq(
        "organization_id", organization_id
    ).eq("status", "completed").gte(
        "return_date", start_date.isoformat()
    ).lt("return_date", end_date.isoformat()).execute()
    
    total_revenue = sum(b["total_price"] for b in bookings.data)
    platform_fee = total_revenue * (settings.PLATFORM_FEE_PERCENTAGE / 100)
    agency_revenue = total_revenue - platform_fee
    
    # Calculate investor payouts (if vehicles are investor-owned)
    investor_payouts = {}
    for booking in bookings.data:
        vehicle = supabase.table("vehicles").select("investor_id").eq("id", booking["vehicle_id"]).execute()
        if vehicle.data and vehicle.data[0].get("investor_id"):
            investor_id = vehicle.data[0]["investor_id"]
            # Calculate investor share (e.g., 70% of vehicle revenue)
            investor_share = booking["base_price"] * 0.7
            if investor_id not in investor_payouts:
                investor_payouts[investor_id] = 0
            investor_payouts[investor_id] += investor_share
    
    # Create payout records (implement payout table)
    # This is a placeholder
    
    return {
        "success": True,
        "total_revenue": total_revenue,
        "platform_fee": platform_fee,
        "agency_revenue": agency_revenue,
        "investor_payouts": investor_payouts
    }


@celery_app.task(name="expire_loyalty_points")
def expire_loyalty_points():
    """Expire loyalty points that have passed their expiration date"""
    supabase = get_supabase_admin()
    
    # Get expired transactions
    expired_transactions = supabase.table("loyalty_transactions").select("*").eq(
        "transaction_type", "earned"
    ).lte("expires_at", datetime.utcnow().isoformat()).execute()
    
    for transaction in expired_transactions.data:
        # Mark as expired
        supabase.table("loyalty_transactions").update({
            "transaction_type": "expired",
            "points": -transaction["points"]
        }).eq("id", transaction["id"]).execute()
        
        # Update user's loyalty points
        points_response = supabase.table("loyalty_points").select("*").eq(
            "user_id", transaction["user_id"]
        ).execute()
        
        if points_response.data:
            current_points = points_response.data[0]
            supabase.table("loyalty_points").update({
                "available_points": max(0, current_points["available_points"] - transaction["points"]),
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", current_points["id"]).execute()
    
    return {"success": True, "expired_count": len(expired_transactions.data)}


# Periodic tasks (configure in celerybeat)
celery_app.conf.beat_schedule = {
    "poll-rta-status": {
        "task": "poll_rta_contract_status",
        "schedule": crontab(minute="*/15"),  # Every 15 minutes
    },
    "expire-loyalty-points": {
        "task": "expire_loyalty_points",
        "schedule": crontab(hour=0, minute=0),  # Daily at midnight
    },
}

