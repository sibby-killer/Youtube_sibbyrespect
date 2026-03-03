"""
Cleanup Module — SibbyRespect
Deletes local MP4 files for videos that were uploaded more than 3 days ago.
Updates Supabase record status to 'cleaned'.
"""
import os
from datetime import datetime, timezone, timedelta


RETENTION_DAYS = 3  # delete local files this many days after upload


def run_cleanup() -> dict:
    """
    Main cleanup function. Call this daily.
    Returns a summary dict: {cleaned: int, errors: int, skipped: int}
    """
    summary = {"cleaned": 0, "errors": 0, "skipped": 0}

    try:
        from core.supabase_db import supabase
        if not supabase:
            print("[Cleanup] Supabase not configured, skipping cleanup.")
            return summary

        cutoff = (datetime.now(timezone.utc) - timedelta(days=RETENTION_DAYS)).isoformat()

        # Find uploaded videos older than cutoff
        result = supabase.table("videos") \
            .select("id, local_path, title") \
            .eq("status", "uploaded") \
            .lt("created_at", cutoff) \
            .execute()

        rows = result.data or []
        print(f"[Cleanup] Found {len(rows)} videos eligible for cleanup.")

        for row in rows:
            video_id  = row.get("id")
            local_path = row.get("local_path", "")
            title      = row.get("title", "Unknown")

            try:
                # Delete the local MP4
                if local_path and os.path.exists(local_path):
                    os.remove(local_path)
                    print(f"[Cleanup] Deleted: {local_path}")
                else:
                    print(f"[Cleanup] File not found (already gone?): {local_path}")

                # Also delete sidecar metadata txt if it exists
                meta_path = local_path.replace(".mp4", "_metadata.txt") if local_path else ""
                if meta_path and os.path.exists(meta_path):
                    os.remove(meta_path)

                # Update DB status
                supabase.table("videos").update({
                    "status": "cleaned",
                    "local_path": None
                }).eq("id", video_id).execute()

                summary["cleaned"] += 1

            except Exception as e:
                print(f"[Cleanup] Error cleaning video {video_id} ({title}): {e}")
                summary["errors"] += 1

    except Exception as e:
        print(f"[Cleanup] Fatal error: {e}")

    print(f"[Cleanup] Done. {summary}")
    return summary


if __name__ == "__main__":
    run_cleanup()
