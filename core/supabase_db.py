"""
Supabase Database Module
Tracks every generated video: metadata, upload status, and analytics.
Requires: pip install supabase
"""
import os
from config import SUPABASE_URL, SUPABASE_KEY

try:
    from supabase import create_client, Client
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY) if SUPABASE_URL and SUPABASE_KEY else None
except Exception as e:
    print(f"Warning: Supabase client could not be initialised: {e}")
    supabase = None


# ──────────────────────────────────────────
#  Table name expected in Supabase
# ──────────────────────────────────────────
VIDEOS_TABLE = "videos"


def log_video(title: str, topic: str, script: str, local_path: str,
              description: str = "", tags: list = None,
              status: str = "generated") -> dict | None:
    """
    Inserts a new video record into the Supabase 'videos' table.
    Call this immediately after a video is assembled.
    """
    if not supabase:
        print("Supabase not configured — skipping DB log.")
        return None

    record = {
        "title":       title,
        "topic":       topic,
        "script":      script,
        "local_path":  local_path,
        "description": description,
        "tags":        tags or [],
        "status":      status,   # generated | uploading | uploaded | failed
        "youtube_id":  None,
        "youtube_url": None,
    }

    try:
        result = supabase.table(VIDEOS_TABLE).insert(record).execute()
        if result.data:
            print(f"[DB] Video logged → ID: {result.data[0].get('id')}")
            return result.data[0]
    except Exception as e:
        print(f"[DB] Insert failed: {e}")
    return None


def update_video_upload(record_id: int, youtube_id: str) -> bool:
    """
    Marks a video as 'uploaded' and saves its YouTube video ID / URL.
    """
    if not supabase:
        return False

    try:
        supabase.table(VIDEOS_TABLE).update({
            "status":      "uploaded",
            "youtube_id":  youtube_id,
            "youtube_url": f"https://youtu.be/{youtube_id}",
        }).eq("id", record_id).execute()
        print(f"[DB] Video {record_id} marked as uploaded ({youtube_id})")
        return True
    except Exception as e:
        print(f"[DB] Update failed: {e}")
        return False


def get_recent_videos(limit: int = 10) -> list:
    """Returns the most recently generated videos."""
    if not supabase:
        return []
    try:
        result = supabase.table(VIDEOS_TABLE) \
            .select("*") \
            .order("created_at", desc=True) \
            .limit(limit) \
            .execute()
        return result.data or []
    except Exception as e:
        print(f"[DB] Query failed: {e}")
        return []


if __name__ == "__main__":
    print("Testing Supabase connection...")
    videos = get_recent_videos(5)
    print(f"Recent videos: {len(videos)} found")
    if supabase:
        print("Supabase connected successfully!")
    else:
        print("Supabase NOT connected. Check SUPABASE_URL and SUPABASE_KEY in .env")
