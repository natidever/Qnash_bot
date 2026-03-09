import os

from dotenv import load_dotenv
from supabase import Client, create_client


def get_supabase_client() -> Client:
    load_dotenv()
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    if not supabase_url or not supabase_key:
        raise RuntimeError("SUPABASE_URL or SUPABASE_ANON_KEY is missing in .env")
    return create_client(supabase_url, supabase_key)
