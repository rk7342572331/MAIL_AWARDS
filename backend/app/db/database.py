from supabase import create_client
from dotenv import load_dotenv

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent.parent

env_path = BASE_DIR / ".env"

load_dotenv(dotenv_path=env_path)


SUPABASE_URL = os.getenv("SUPABASE_URL")

SUPABASE_KEY = os.getenv("SUPABASE_KEY")


print("SUPABASE_URL:", SUPABASE_URL)
print("SUPABASE_KEY EXISTS:", bool(SUPABASE_KEY))


supabase = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)