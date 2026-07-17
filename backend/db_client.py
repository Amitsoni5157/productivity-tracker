from supabase import create_client, Client
from config import settings

# Initialize Supabase client
# Hum settings se URL aur KEY le rahe hain (Loosely Coupled)
supabase_client: Client = None

# Check for credentials and initialize
if settings.SUPABASE_URL and settings.SUPABASE_KEY:
    supabase_client = create_client(
        settings.SUPABASE_URL,
        settings.SUPABASE_KEY
    )
else:
    print("[WARNING] Supabase credentials missing. DB operations will fail.")

# Dependency injection function to get DB connection 
def get_db():
      """Returns the supabase client instance."""
      if not supabase_client:
        raise ValueError("Database client not initialized. Check your credentials or env file.")
      return supabase_client
