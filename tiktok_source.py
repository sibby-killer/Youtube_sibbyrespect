"""
tiktok_source.py — SibbyRespect
Downloads Roblox gameplay from @yellowrobloxreal on TikTok for use as background video.
One video per short — no mixing or concatenation needed.
"""

import os
import json
import random
import subprocess

TIKTOK_SOURCE_ACCOUNT = "yellowrobloxreal"
TIKTOK_SOURCE_URL     = "https://www.tiktok.com/@yellowrobloxreal"
DOWNLOADED_VIDEOS_DIR = "tiktok_bg_videos"
USED_VIDEOS_FILE      = "used_tiktok_videos.json"


# ─────────────────────────────────────────────────────────────────────────────
#  USAGE TRACKING
# ─────────────────────────────────────────────────────────────────────────────
def load_used_videos() -> list:
    """Loads list of already-used TikTok video URLs to prevent reuse."""
    if os.path.exists(USED_VIDEOS_FILE):
        try:
            with open(USED_VIDEOS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_used_video(video_url: str):
    """Marks a TikTok video URL as used."""
    used = load_used_videos()
    used.append(video_url)
    with open(USED_VIDEOS_FILE, "w") as f:
        json.dump(used, f, indent=2)


def reset_used_videos():
    """Resets the used videos tracker — called when all videos have been cycled."""
    with open(USED_VIDEOS_FILE, "w") as f:
        json.dump([], f)


# ─────────────────────────────────────────────────────────────────────────────
#  VIDEO LISTING
# ─────────────────────────────────────────────────────────────────────────────
def get_tiktok_videos_list(max_videos: int = 50) -> list:
    """
    Gets list of recent video URLs from @yellowrobloxreal using yt-dlp.
    Returns list of video URLs, or empty list on failure.
    """
    try:
        cmd = [
            "yt-dlp",
            "--flat-playlist",
            "--print", "url",
            "--playlist-items", f"1-{max_videos}",
            f"https://www.tiktok.com/@{TIKTOK_SOURCE_ACCOUNT}",
        ]
        print(f"[TikTok] Listing videos from @{TIKTOK_SOURCE_ACCOUNT}...")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

        if result.returncode == 0 and result.stdout.strip():
            urls = [url.strip() for url in result.stdout.strip().split('\n') if url.strip()]
            print(f"[TikTok] Found {len(urls)} videos from @{TIKTOK_SOURCE_ACCOUNT}")
            return urls
        else:
            err = result.stderr[:300] if result.stderr else "No output"
            print(f"[TikTok] Error listing videos: {err}")
            return []

    except subprocess.TimeoutExpired:
        print("[TikTok] Timeout while getting video list")
        return []
    except Exception as e:
        print(f"[TikTok] Error getting video list: {e}")
        return []


# ─────────────────────────────────────────────────────────────────────────────
#  VIDEO DOWNLOAD
# ─────────────────────────────────────────────────────────────────────────────
def download_single_video(video_url: str, output_path: str) -> bool:
    """
    Downloads a single TikTok video using yt-dlp.
    Returns True if successful and file is valid, False otherwise.
    """
    try:
        # Remove stale file if any
        if os.path.exists(output_path):
            os.remove(output_path)

        cmd = [
            "yt-dlp",
            "-o", output_path,
            "--format", "best[ext=mp4]/best",
            "--no-check-certificates",
            "--no-warnings",
            "--quiet",
            video_url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        # Check exact output path first
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            if file_size > 50_000:   # At least 50 KB
                print(f"[TikTok] Downloaded successfully ({file_size / 1024:.0f} KB): {output_path}")
                return True
            else:
                print(f"[TikTok] File too small ({file_size} bytes) — likely incomplete")
                os.remove(output_path)
                return False

        # yt-dlp may append extension — check alternatives
        for ext in ['.mp4', '.webm', '.mkv']:
            alt = os.path.splitext(output_path)[0] + ext
            if os.path.exists(alt) and os.path.getsize(alt) > 50_000:
                if alt != output_path:
                    os.rename(alt, output_path)
                print(f"[TikTok] Downloaded as {ext}: {output_path}")
                return True

        print(f"[TikTok] Download failed — no valid file found for: {video_url[:60]}")
        return False

    except subprocess.TimeoutExpired:
        print(f"[TikTok] Download timeout: {video_url[:60]}")
        return False
    except Exception as e:
        print(f"[TikTok] Download error: {e}")
        return False


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN — GET BACKGROUND VIDEO
# ─────────────────────────────────────────────────────────────────────────────
def get_background_video() -> str | None:
    """
    Main function: Gets ONE unused Roblox gameplay video from @yellowrobloxreal.
    Tracks usage so the same video is not reused across runs.

    Returns:
        Filepath of the downloaded MP4, or None if all attempts fail.
    """
    os.makedirs(DOWNLOADED_VIDEOS_DIR, exist_ok=True)

    print(f"\n[TikTok] Fetching background video from @{TIKTOK_SOURCE_ACCOUNT}...")

    all_videos = get_tiktok_videos_list()
    if not all_videos:
        print("[TikTok] Could not retrieve video list — TikTok may be blocking the request")
        return None

    used_videos = load_used_videos()
    available   = [v for v in all_videos if v not in used_videos]

    if not available:
        print("[TikTok] All videos from this account have been used. Resetting tracker...")
        reset_used_videos()
        available = all_videos

    # Shuffle so we get different random ordering each run
    random.shuffle(available)

    # Try up to 3 different videos in case some fail to download
    for attempt, video_url in enumerate(available[:3], start=1):
        print(f"[TikTok] Download attempt {attempt}/3: {video_url[:70]}...")

        # Build a unique filename based on a hash of the URL
        video_hash  = str(abs(hash(video_url)))[:8]
        output_path = os.path.join(DOWNLOADED_VIDEOS_DIR, f"roblox_bg_{video_hash}.mp4")

        if download_single_video(video_url, output_path):
            save_used_video(video_url)
            print(f"[TikTok] ✓ Background video ready: {output_path}")
            return output_path

        print(f"[TikTok] Attempt {attempt} failed — trying next...")

    print("[TikTok] All 3 download attempts failed")
    return None


# ─────────────────────────────────────────────────────────────────────────────
#  CLEANUP — save disk space between runs
# ─────────────────────────────────────────────────────────────────────────────
def cleanup_old_videos(keep_latest: int = 5):
    """
    Removes old downloaded background videos to save disk space.
    Keeps only the `keep_latest` most recently modified files.
    """
    if not os.path.exists(DOWNLOADED_VIDEOS_DIR):
        return

    files = []
    for fname in os.listdir(DOWNLOADED_VIDEOS_DIR):
        fpath = os.path.join(DOWNLOADED_VIDEOS_DIR, fname)
        if os.path.isfile(fpath):
            files.append((fpath, os.path.getmtime(fpath)))

    # Sort newest-first
    files.sort(key=lambda x: x[1], reverse=True)

    for fpath, _ in files[keep_latest:]:
        try:
            os.remove(fpath)
            print(f"[Cleanup] Removed old background video: {fpath}")
        except OSError:
            pass


# ─────────────────────────────────────────────────────────────────────────────
#  CLI TEST
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"[Test] Getting background video from @{TIKTOK_SOURCE_ACCOUNT}...")
    path = get_background_video()
    if path:
        print(f"[Test] ✓ Success: {path}")
    else:
        print("[Test] ✗ Failed to get background video")
