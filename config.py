import os
from dotenv import load_dotenv

load_dotenv()

# Base directory (root of this project)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# API Keys
GROQ_API_KEY      = os.getenv("GROQ_API_KEY")
PEXELS_API_KEY    = os.getenv("PEXELS_API_KEY")
YOUTUBE_COOKIES   = os.getenv("YOUTUBE_COOKIES")
YOUTUBE_PLAYLIST_ID = os.getenv("YOUTUBE_PLAYLIST_ID")
PIXABAY_API_KEY   = os.getenv("PIXABAY_API_KEY", "")

# Supabase (Database & Dashboard)
SUPABASE_URL      = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
SUPABASE_KEY      = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Reddit API (for auto-topic scraping)
REDDIT_CLIENT_ID     = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT    = "SibbyRespect/1.0"

# Flask dashboard secret
FLASK_SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "sibbyrespect-super-secret-2026")

# Output Configuration
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TEMP_DIR   = os.path.join(BASE_DIR, "temp")

# Create directories if they don't exist
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
