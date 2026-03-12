"""
Pixabay Audio Manager — SibbyRespect
Handles sound effects library + background music from Pixabay.
Requires PIXABAY_API_KEY in config/env.
"""

import os
import json
import random
import requests
import time
from config import PIXABAY_API_KEY

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
SFX_DIR = "sfx"
MUSIC_DIR = "bg_music"
SFX_MANIFEST_FILE = "sfx_manifest.json"
PIXABAY_API_BASE = "https://pixabay.com/api/"

# ─────────────────────────────────────────────────────────────────────────────
#  SFX LIBRARY — What we need to download on first run
# ─────────────────────────────────────────────────────────────────────────────
SFX_LIBRARY = {
    "door_creak": {"search": "door creak horror", "category": "sound-effects"},
    "heartbeat": {"search": "heartbeat slow", "category": "sound-effects"},
    "heartbeat_intense": {"search": "heartbeat fast intense", "category": "sound-effects"},
    "dramatic_bass_drop": {"search": "bass drop impact", "category": "sound-effects"},
    "angelic_choir": {"search": "angelic choir heavenly", "category": "sound-effects"},
    "roblox_oof": {"search": "oof impact funny", "category": "sound-effects"},
    "gta_wasted": {"search": "game over fail", "category": "sound-effects"},
    "sad_violin": {"search": "sad violin dramatic", "category": "sound-effects"},
    "thunder_crack": {"search": "thunder crack storm", "category": "sound-effects"},
    "glass_shatter": {"search": "glass breaking shatter", "category": "sound-effects"},
    "police_siren": {"search": "police siren distant", "category": "sound-effects"},
    "cricket_silence": {"search": "cricket silence awkward", "category": "sound-effects"},
    "record_scratch": {"search": "record scratch stop", "category": "sound-effects"},
    "emotional_piano": {"search": "emotional piano note", "category": "sound-effects"},
    "windows_error": {"search": "error notification computer", "category": "sound-effects"},
    "alarm_blaring": {"search": "alarm clock buzzing", "category": "sound-effects"},
    "anime_reveal": {"search": "dramatic reveal whoosh", "category": "sound-effects"},
    "dial_up_internet": {"search": "dial up modem internet", "category": "sound-effects"},
    "horror_sting": {"search": "horror sting scare", "category": "sound-effects"},
    "scream_sfx": {"search": "scream funny short", "category": "sound-effects"},
    "drum_roll": {"search": "drum roll suspense", "category": "sound-effects"},
    "whoosh": {"search": "whoosh fast transition", "category": "sound-effects"},
    "boing": {"search": "boing spring cartoon", "category": "sound-effects"},
    "fart_reverb": {"search": "fart funny cartoon", "category": "sound-effects"},
    "metal_gear_alert": {"search": "alert detection stealth", "category": "sound-effects"},
}

# Background music search terms
MUSIC_SEARCH_TERMS = [
    "lo-fi chill beat",
    "ambient background calm",
    "chill hip hop instrumental",
    "soft electronic beat",
    "minimal lo-fi",
    "relaxing beat",
    "chill study music",
    "mellow instrumental",
]

# ─────────────────────────────────────────────────────────────────────────────
#  VALIDATION
# ─────────────────────────────────────────────────────────────────────────────
def validate_audio_file(filepath: str, min_size_bytes: int = 5000, min_duration_ms: int = 100) -> bool:
    """Validates that a downloaded audio file is valid and usable."""
    try:
        if not os.path.exists(filepath):
            return False
        
        file_size = os.path.getsize(filepath)
        if file_size < min_size_bytes:
            print(f"[Validate] File too small ({file_size} bytes): {filepath}")
            return False
        
        from pydub import AudioSegment
        audio = AudioSegment.from_file(filepath)
        if len(audio) < min_duration_ms:
            print(f"[Validate] Audio too short ({len(audio)}ms): {filepath}")
            return False
        
        return True
    except Exception as e:
        print(f"[Validate] Invalid audio: {filepath} — {e}")
        return False

# ─────────────────────────────────────────────────────────────────────────────
#  PIXABAY API HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def search_pixabay_audio(query: str, audio_type: str = "sound-effects", per_page: int = 5) -> list:
    """
    Searches Pixabay for audio files.
    audio_type: "sound-effects" or "music"
    """
    if not PIXABAY_API_KEY:
        print("[Pixabay] API key not set")
        return []

    # Pixabay audio API endpoint
    # Note: Pixabay's specific audio endpoint might vary, but they often use specialized endpoints
    # for their music/SFX.
    url = f"https://pixabay.com/api/"
    params = {
        "key": PIXABAY_API_KEY,
        "q": query,
        "per_page": per_page,
    }

    try:
        response = requests.get(url, params=params, headers={
            "User-Agent": "SibbyRespect Audio Bot 1.0"
        }, timeout=15)

        if response.status_code == 200:
            data = response.json()
            return data.get("hits", [])
        else:
            print(f"[Pixabay] Error {response.status_code}: {response.text[:100]}")
            return []

    except Exception as e:
        print(f"[Pixabay] Search error: {e}")
        return []


def download_audio_file(url: str, output_path: str) -> bool:
    """Downloads an audio file from URL."""
    try:
        response = requests.get(url, timeout=30, stream=True)
        if response.status_code == 200:
            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            file_size = os.path.getsize(output_path)
            if file_size > 1000:  # At least 1KB
                print(f"[Pixabay] Downloaded ({file_size/1024:.0f}KB): {output_path}")
                return True
            else:
                os.remove(output_path)
                return False
        return False
    except Exception as e:
        print(f"[Pixabay] Download error: {e}")
        return False

# ─────────────────────────────────────────────────────────────────────────────
#  SFX LIBRARY SETUP — First run downloads all SFX
# ─────────────────────────────────────────────────────────────────────────────
def is_sfx_library_ready() -> bool:
    """Checks if the SFX library has been downloaded."""
    if not os.path.exists(SFX_DIR):
        return False
    if not os.path.exists(SFX_MANIFEST_FILE):
        return False
    
    # Check that we have at least 15 files
    sfx_files = [f for f in os.listdir(SFX_DIR) if f.endswith(('.mp3', '.wav', '.ogg'))]
    return len(sfx_files) >= 15


def setup_sfx_library():
    """
    Downloads the entire SFX library from Pixabay on first run.
    Stores all sound effects in sfx/ folder.
    Creates a manifest file mapping effect names to file paths.
    """
    os.makedirs(SFX_DIR, exist_ok=True)
    
    if is_sfx_library_ready():
        print("[SFX] Library already downloaded and ready")
        return True

    print("[SFX] First run — downloading sound effects library from Pixabay...")
    print(f"[SFX] Need to download {len(SFX_LIBRARY)} sound effects")

    manifest = {}
    downloaded = 0
    failed = 0

    for sfx_name, sfx_config in SFX_LIBRARY.items():
        output_path = os.path.join(SFX_DIR, f"{sfx_name}.mp3")
        
        # Skip if already exists
        if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
            print(f"[SFX] Already exists: {sfx_name}")
            manifest[sfx_name] = output_path
            downloaded += 1
            continue

        print(f"[SFX] Searching for: {sfx_name} ({sfx_config['search']})...")
        
        results = search_pixabay_audio(sfx_config["search"], sfx_config["category"])
        
        if results:
            # Try to download the first valid result
            success = False
            for result in results:
                # Get audio URL — structure depends on Pixabay API response
                audio_url = None
                
                # Try different possible URL fields
                for url_field in ["previewURL", "audio", "url", "largeImageURL", "webformatURL"]:
                    if url_field in result:
                        audio_url = result[url_field]
                        break
                
                if audio_url:
                    if download_audio_file(audio_url, output_path):
                        if validate_audio_file(output_path):
                            manifest[sfx_name] = output_path
                            downloaded += 1
                            success = True
                            break
                        else:
                            os.remove(output_path)

            if not success:
                print(f"[SFX] Failed to download: {sfx_name}")
                failed += 1
        else:
            print(f"[SFX] No results for: {sfx_name}")
            failed += 1

        # Rate limiting
        time.sleep(1)

    # Save manifest
    with open(SFX_MANIFEST_FILE, "w") as f:
        json.dump(manifest, f, indent=2)

    print(f"\n[SFX] Library setup complete!")
    print(f"[SFX] Downloaded: {downloaded}/{len(SFX_LIBRARY)}")
    print(f"[SFX] Failed: {failed}")

    return downloaded > 0


def get_sfx_path(sfx_name: str) -> str | None:
    """
    Gets the file path for a named sound effect.
    Returns None if not found.
    """
    # Check manifest first
    if os.path.exists(SFX_MANIFEST_FILE):
        with open(SFX_MANIFEST_FILE, "r") as f:
            manifest = json.load(f)
        if sfx_name in manifest and os.path.exists(manifest[sfx_name]):
            return manifest[sfx_name]

    # Direct file check
    for ext in [".mp3", ".wav", ".ogg"]:
        path = os.path.join(SFX_DIR, f"{sfx_name}{ext}")
        if os.path.exists(path):
            return path

    print(f"[SFX] Sound effect not found: {sfx_name}")
    return None


def get_available_sfx() -> list:
    """Returns list of all available sound effect names."""
    if not os.path.exists(SFX_DIR):
        return []
    
    sfx_names = []
    for f in os.listdir(SFX_DIR):
        if f.endswith(('.mp3', '.wav', '.ogg')):
            name = os.path.splitext(f)[0]
            sfx_names.append(name)
    return sfx_names

# ─────────────────────────────────────────────────────────────────────────────
#  BACKGROUND MUSIC — Fetched per video from Pixabay
# ─────────────────────────────────────────────────────────────────────────────
USED_MUSIC_FILE = "used_music.json"
MUSIC_MIN_SIZE = 100000  # 100KB minimum for music files
MUSIC_MIN_DURATION = 5000  # 5 seconds minimum

def load_used_music() -> list:
    if os.path.exists(USED_MUSIC_FILE):
        with open(USED_MUSIC_FILE, "r") as f:
            return json.load(f)
    return []

def save_used_music(music_id: str):
    used = load_used_music()
    used.append(music_id)
    with open(USED_MUSIC_FILE, "w") as f:
        json.dump(used, f, indent=2)


def get_background_music() -> str | None:
    """Downloads background music from Pixabay with proper validation."""
    os.makedirs(MUSIC_DIR, exist_ok=True)
    
    search_term = random.choice(MUSIC_SEARCH_TERMS)
    print(f"[Music] Searching Pixabay for: {search_term}")
    
    results = search_pixabay_audio(search_term, "music")
    used_music = load_used_music()
    
    for result in results:
        music_id = str(result.get("id", ""))
        if music_id in used_music:
            continue
        
        audio_url = None
        for url_field in ["previewURL", "audio", "url", "musicURL", "preview", "webformatURL"]:
            if url_field in result and result[url_field]:
                audio_url = result[url_field]
                break
        
        if not audio_url:
            continue
        
        output_path = os.path.join(MUSIC_DIR, f"bg_music_{music_id}.mp3")
        
        if download_audio_file(audio_url, output_path):
            file_size = os.path.getsize(output_path)
            
            if file_size < MUSIC_MIN_SIZE:
                print(f"[Music] File too small ({file_size/1024:.0f}KB), skipping...")
                os.remove(output_path)
                continue
            
            try:
                from pydub import AudioSegment
                test = AudioSegment.from_file(output_path)
                if len(test) < MUSIC_MIN_DURATION:
                    print(f"[Music] Too short ({len(test)/1000:.1f}s), skipping...")
                    os.remove(output_path)
                    continue
                print(f"[Music] Valid: {len(test)/1000:.1f}s, {file_size/1024:.0f}KB")
            except Exception as e:
                print(f"[Music] Invalid audio: {e}")
                os.remove(output_path)
                continue
            
            save_used_music(music_id)
            return output_path
    
    # Fallback: use any existing valid music file
    if os.path.exists(MUSIC_DIR):
        existing = [f for f in os.listdir(MUSIC_DIR) if f.endswith('.mp3')]
        for f in existing:
            fp = os.path.join(MUSIC_DIR, f)
            if os.path.getsize(fp) > MUSIC_MIN_SIZE:
                print(f"[Music] Using existing: {fp}")
                return fp
    
    print("[Music] No valid background music available")
    return None


# ─────────────────────────────────────────────────────────────────────────────
#  TEST
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("[Test] Setting up SFX library...")
    setup_sfx_library()
    
    print(f"\n[Test] Available SFX: {get_available_sfx()}")
    
    print("\n[Test] Getting background music...")
    music = get_background_music()
    print(f"[Test] Music: {music}")
