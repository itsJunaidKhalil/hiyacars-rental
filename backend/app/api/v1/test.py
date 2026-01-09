from datetime import datetime
from typing import Dict, Any
from pathlib import Path
import sys
import os
import argparse

# Ensure project root (backend/) is on sys.path and set as CWD so .env loads
CURRENT_FILE = Path(__file__).resolve()
BACKEND_DIR = CURRENT_FILE.parents[3]  # .../backend
if str(BACKEND_DIR) not in sys.path:
   sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

from app.database import get_supabase, get_supabase_admin


def delete_user_and_profile(
   user_id: str,
   *,
   soft_delete_auth: bool = True,
   hard_delete_profile: bool = False,
) -> Dict[str, Any]:
   """
   Delete a user from Supabase Auth and remove (or anonymize) their profile row in `users`.

   - Deletes the auth user using service role via Admin API.
   - Attempts to delete the profile row from `public.users`.
     Falls back to anonymizing if foreign key constraints prevent deletion.

   Args:
       user_id: The Supabase Auth user id (UUID string).
       soft_delete_auth: If True, soft-deletes in Auth (recommended). If False, hard-deletes.
       hard_delete_profile: If True, attempts to hard delete profile row. Otherwise anonymizes on FK conflict.

   Returns:
       Dict with deletion/anonymization results.
   """

   supabase_admin = get_supabase_admin()
   supabase = get_supabase()

   result: Dict[str, Any] = {
       "auth_deleted": False,
       "profile_deleted": False,
       "profile_anonymized": False,
   }

   # 1) Delete user in Supabase Auth (soft delete recommended)
   try:
       supabase_admin.auth.admin.delete_user(user_id, should_soft_delete=soft_delete_auth)
       result["auth_deleted"] = True
   except Exception as e:
       # If hard delete failed, retry with soft delete once
       if not soft_delete_auth:
           try:
               supabase_admin.auth.admin.delete_user(user_id, should_soft_delete=True)
               result["auth_deleted"] = True
           except Exception as e2:
               return {**result, "error": f"Auth delete failed (hard + soft): {e}; {e2}"}
       else:
           return {**result, "error": f"Auth delete failed: {e}"}

   # 2) Remove or anonymize profile record in our `users` table
   try:
       if hard_delete_profile:
           # Try hard delete; may fail due to FK constraints
           supabase.table("users").delete().eq("id", user_id).execute()
           result["profile_deleted"] = True
       else:
           # Prefer anonymization to preserve referential integrity
           supabase.table("users").update(
               {
                   "email": f"deleted+{user_id}@example.com",
                   "full_name": "Deleted User",
                   "phone": None,
                   "avatar_url": None,
                   "status": "inactive",
                   "updated_at": datetime.utcnow().isoformat(),
               }
           ).eq("id", user_id).execute()
           result["profile_anonymized"] = True

   except Exception as e:
       # If hard delete failed, anonymize as fallback
       try:
           supabase.table("users").update(
               {
                   "email": f"deleted+{user_id}@example.com",
                   "full_name": "Deleted User",
                   "phone": None,
                   "avatar_url": None,
                   "status": "inactive",
                   "updated_at": datetime.utcnow().isoformat(),
               }
           ).eq("id", user_id).execute()
           result["profile_anonymized"] = True
       except Exception as e2:
           result["error"] = f"Profile removal failed: {e}; Fallback anonymize failed: {e2}"

   return result


if __name__ == "__main__":
   parser = argparse.ArgumentParser(
       description="Delete a Supabase Auth user and their profile row."
   )
   parser.add_argument(
       "--user-id",
       required=True,
       help="Supabase Auth user UUID to delete",
   )
   parser.add_argument(
       "--hard-delete-auth",
       action="store_true",
       help="Hard delete auth user (default soft delete)",
   )
   parser.add_argument(
       "--hard-delete-profile",
       action="store_true",
       help="Hard delete profile row (default anonymize on FK conflicts)",
   )

   args = parser.parse_args()

   res = delete_user_and_profile(
       user_id=args.user_id,
       soft_delete_auth=not args.hard_delete_auth,
       hard_delete_profile=args.hard_delete_profile,
   )
   print(res)


result = delete_user_and_profile(
   user_id="28bdda17-0904-4055-b551-6b73e8e50d1f",
   soft_delete_auth=True,       # recommended
   hard_delete_profile=True    # recommended (avoids FK constraint issues)
)
print(result)
