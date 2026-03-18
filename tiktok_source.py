"""
TikTok Background Video Source — SibbyRespect
Downloads ONE Roblox gameplay video from @yellowrobloxreal per short.
No mixing or concatenation — single video used as background.
"""

import os
import json
import random
import subprocess

# ─────────────────────────────────────────────────────────────────────────────
#  SATISFYING BACKGROUND SOURCES
# ─────────────────────────────────────────────────────────────────────────────
SATISFYING_ACCOUNTS = [
    "kirkmaxson",
    "watchlike87",
    "hasnain._0009",
    "soapsoul.asmr",
    "oddlysatisfying",
    "kinetic.graphics",
    "factoryzone1"
]
DOWNLOADED_VIDEOS_DIR = "satisfying_bg_videos"
USED_VIDEOS_FILE = "used_satisfying_videos.json"


def load_used_videos() -> list:
    if os.path.exists(USED_VIDEOS_FILE):
        with open(USED_VIDEOS_FILE, "r") as f:
            return json.load(f)
    return []

def save_used_video(video_url: str):
    used = load_used_videos()
    used.append(video_url)
    with open(USED_VIDEOS_FILE, "w") as f:
        json.dump(used, f, indent=2)

def reset_used_videos():
    with open(USED_VIDEOS_FILE, "w") as f:
        json.dump([], f)


def get_tiktok_videos_list(account: str, max_videos: int = 30) -> list:
    """Gets list of video URLs from a specific account using yt-dlp."""
    try:
        print(f"[TikTok] Fetching videos from @{account}...")
        cmd = [
            "yt-dlp",
            "--flat-playlist",
            "--print", "url",
            "--playlist-items", f"1-{max_videos}",
            f"https://www.tiktok.com/@{account}",
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)

        if result.returncode == 0 and result.stdout.strip():
            urls = [u.strip() for u in result.stdout.strip().split('\n') if u.strip()]
            print(f"[TikTok] Found {len(urls)} videos from @{account}")
            return urls
        else:
            print(f"[TikTok] Error: {result.stderr[:200] if result.stderr else 'No output'}")
            return []
    except subprocess.TimeoutExpired:
        print("[TikTok] Timeout getting video list")
        return []
    except Exception as e:
        print(f"[TikTok] Error: {e}")
        return []


def download_single_video(video_url: str, output_path: str) -> bool:
    """Downloads a single TikTok video using yt-dlp."""
    try:
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
        subprocess.run(cmd, capture_output=True, text=True, timeout=120)

        if os.path.exists(output_path) and os.path.getsize(output_path) > 50000:
            print(f"[TikTok] Downloaded: {output_path}")
            return True

        # Check for alt extensions
        for ext in ['.mp4', '.webm', '.mkv']:
            alt = output_path.rsplit('.', 1)[0] + ext
            if os.path.exists(alt) and os.path.getsize(alt) > 50000:
                if alt != output_path:
                    os.rename(alt, output_path)
                return True

        return False

    except Exception as e:
        print(f"[TikTok] Download error: {e}")
        return False


def get_background_video() -> str | None:
    """
    Gets ONE unused satisfying background video. 
    Picks a random account from the whitelist.
    """
    os.makedirs(DOWNLOADED_VIDEOS_DIR, exist_ok=True)

    # Pick a random account to sample from
    account = random.choice(SATISFYING_ACCOUNTS)
    all_videos = get_tiktok_videos_list(account)
    
    if not all_videos:
        # Try another if first fails
        alt_account = random.choice([a for a in SATISFYING_ACCOUNTS if a != account])
        all_videos = get_tiktok_videos_list(alt_account)
        if not all_videos: return None

    used = load_used_videos()
    available = [v for v in all_videos if v not in used]

    if not available:
        print(f"[TikTok] All videos from current batch used or seen. Picking any...")
        available = all_videos

    random.shuffle(available)

    for attempt, url in enumerate(available[:3], 1):
        print(f"[TikTok] Download Attempt {attempt}/3...")
        video_hash = str(abs(hash(url)))[:8]
        output = os.path.join(DOWNLOADED_VIDEOS_DIR, f"bg_{video_hash}.mp4")

        if download_single_video(url, output):
            save_used_video(url)
            return output

    return None


def cleanup_old_videos(keep: int = 3):
    """Removes old downloads to save space."""
    if not os.path.exists(DOWNLOADED_VIDEOS_DIR):
        return
    files = []
    for f in os.listdir(DOWNLOADED_VIDEOS_DIR):
        fp = os.path.join(DOWNLOADED_VIDEOS_DIR, f)
        if os.path.isfile(fp):
            files.append((fp, os.path.getmtime(fp)))
    files.sort(key=lambda x: x[1], reverse=True)
    for fp, _ in files[keep:]:
        try:
            os.remove(fp)
        except:
            pass
