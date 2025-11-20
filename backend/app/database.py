from supabase import create_client, Client
from config import settings
from typing import Optional

# Initialize Supabase client
supabase: Optional[Client] = None
supabase_admin: Optional[Client] = None


def get_supabase() -> Client:
    """Get Supabase client instance"""
    global supabase
    if supabase is None:
        supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    return supabase


def get_supabase_admin() -> Client:
    """Get Supabase admin client with service role key"""
    global supabase_admin
    if supabase_admin is None:
        supabase_admin = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
    return supabase_admin


async def init_db():
    """Initialize database connections and run migrations if needed"""
    # This can be used to run migrations or setup tasks
    # Supabase handles schema via SQL migrations
    pass

