from db_client import get_db

# 1. User Profile Create karna 
def create_profile(name: str, profession:str) -> dict:
    """creates a new user profile and returns the profile details."""
    supabase = get_db()
    response = supabase.table("profiles").insert({
        "name":name,
        "profession":profession
    }).execute()

    # Supabase execute() ke baad data attribute me list of inserted rows deta hai
    if response.data:
        return response.data[0]
    raise Exception("Failed to create profile.")

# 2. User Profile Fetch karna

def get_profile(profile_id: str) -> dict:
    """Fetch user profile details by ID."""
    supabase = get_db()
    response = supabase.table("profiles").select('*').eq("id",profile_id).execute()
    if response.data:
        return response.data[0]
    return None

# 3. Daily Activity Log aur AI Report insert karna (with Embeddings)
def insert_daily_log(
    profile_id: str,
    raw_log: str,
    productive_hours: float,
    wasted_hours: float,
    score: float,
    report_content: str,
    embedding: list[float]
) ->dict:
    """Inserts a new daily productivity log including the AI vector embedding."""
    supabase = get_db()
    response = supabase.table("productivity_logs").insert({
        "profile_id":profile_id,
        "raw_log":raw_log,
        "productive_hours":productive_hours,
        "wasted_hours":wasted_hours,
        "score":score,
        "report_content":report_content,
        "embedding":embedding
    }).execute()

    if response.data:
        return response.data[0]
    raise Exception("Failed to insert daily log.")

# 4. Semantic Search (pgvector RPC function call)
# ector similarity search use karke database se purani matching reports ko search/read karega.
def search_past_logs(profile_id: str, query_embedding: list[float], limit: int =3) -> list[dict]:
    """Uses Supabase RPC to call our match_logs PostgreSQL function for semantic search."""
    supabase = get_db()
    response = supabase.rpc(
        "match_logs",
        {
          "query_embedding": query_embedding,
          "match_threshold": 0.1,  # Similar matches above 10% similarity
          "match_count": limit,
          "p_profile_id": profile_id
        }
    ).execute()

    return response.data or []