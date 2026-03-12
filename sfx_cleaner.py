"""
SFX Library Cleaner — SibbyRespect
Scans sfx/ folder, trims long files, removes unusable ones,
creates manifest that AI references.
"""

import os
import json
from pydub import AudioSegment

SFX_DIR = "sfx"
SFX_MANIFEST_FILE = "sfx_manifest.json"
MAX_SFX_DURATION_MS = 3000  # 3 seconds max
MIN_SFX_DURATION_MS = 100   # 100ms minimum
MIN_SFX_SIZE_BYTES = 3000   # 3KB minimum


def clean_sfx_library():
    """
    Processes ALL files in sfx/ folder:
    1. Removes files that are not audio
    2. Removes files under 100ms or under 3KB
    3. TRIMS files over 3 seconds to 3 seconds (keeps first 3 sec)
    4. Normalizes all to mp3 format
    5. Builds clean manifest mapping name → filepath
    """
    if not os.path.exists(SFX_DIR):
        os.makedirs(SFX_DIR, exist_ok=True)
        print("[SFX Clean] Created sfx/ folder")
        return {}
    
    print(f"[SFX Clean] Scanning {SFX_DIR}/...")
    
    manifest = {}
    kept = 0
    trimmed = 0
    removed = 0
    
    all_files = sorted(os.listdir(SFX_DIR))
    print(f"[SFX Clean] Found {len(all_files)} files")
    
    for filename in all_files:
        filepath = os.path.join(SFX_DIR, filename)
        
        if not os.path.isfile(filepath):
            continue
        
        # Skip non-audio files
        ext = os.path.splitext(filename)[1].lower()
        if ext not in ['.mp3', '.wav', '.ogg', '.m4a', '.flac', '.aac', '.wma']:
            # If it's the manifest itself, skip
            if filename == SFX_MANIFEST_FILE:
                continue
            print(f"[SFX Clean] Skipping non-audio: {filename}")
            removed += 1
            continue
        
        try:
            # Check file size
            file_size = os.path.getsize(filepath)
            if file_size < MIN_SFX_SIZE_BYTES:
                print(f"[SFX Clean] Too small ({file_size}B), removing: {filename}")
                os.remove(filepath)
                removed += 1
                continue
            
            # Load audio
            audio = AudioSegment.from_file(filepath)
            duration_ms = len(audio)
            
            # Too short
            if duration_ms < MIN_SFX_DURATION_MS:
                print(f"[SFX Clean] Too short ({duration_ms}ms), removing: {filename}")
                os.remove(filepath)
                removed += 1
                continue
            
            # Too long — TRIM to 3 seconds
            if duration_ms > MAX_SFX_DURATION_MS:
                print(f"[SFX Clean] Trimming {duration_ms/1000:.1f}s → 3.0s: {filename}")
                audio = audio[:MAX_SFX_DURATION_MS]
                
                # Fade out the last 200ms for smooth ending
                audio = audio.fade_out(200)
                
                # Save back as mp3
                mp3_path = os.path.join(SFX_DIR, os.path.splitext(filename)[0] + ".mp3")
                audio.export(mp3_path, format="mp3", bitrate="192k")
                
                # Remove original if different filename
                if filepath != mp3_path and os.path.exists(filepath):
                    os.remove(filepath)
                
                filepath = mp3_path
                trimmed += 1
            
            # Convert to mp3 if not already
            if ext != '.mp3':
                mp3_path = os.path.join(SFX_DIR, os.path.splitext(filename)[0] + ".mp3")
                if not os.path.exists(mp3_path):
                    audio.export(mp3_path, format="mp3", bitrate="192k")
                if os.path.exists(filepath) and filepath != mp3_path:
                    os.remove(filepath)
                filepath = mp3_path
            
            # Add to manifest
            clean_name = os.path.splitext(os.path.basename(filepath))[0]
            # Normalize name: lowercase, replace spaces with underscores
            clean_name = clean_name.lower().replace(" ", "_").replace("-", "_")
            
            manifest[clean_name] = {
                "path": filepath,
                "duration_ms": min(duration_ms, MAX_SFX_DURATION_MS),
                "size_bytes": os.path.getsize(filepath),
            }
            kept += 1
            
        except Exception as e:
            print(f"[SFX Clean] Error processing {filename}: {e}")
            removed += 1
            continue
    
    # Save manifest
    with open(SFX_MANIFEST_FILE, "w") as f:
        json.dump(manifest, f, indent=2)
    
    print(f"\n[SFX Clean] Results:")
    print(f"  Kept: {kept}")
    print(f"  Trimmed: {trimmed}")
    print(f"  Removed: {removed}")
    print(f"  Manifest saved: {SFX_MANIFEST_FILE}")
    
    return manifest


def get_available_sfx_names() -> list:
    """Returns list of all available SFX names from manifest."""
    if os.path.exists(SFX_MANIFEST_FILE):
        try:
            with open(SFX_MANIFEST_FILE, "r") as f:
                manifest = json.load(f)
            return sorted(manifest.keys())
        except:
            pass
    
    # Fallback: scan folder directly
    if os.path.exists(SFX_DIR):
        names = []
        for f in os.listdir(SFX_DIR):
            if f.endswith(('.mp3', '.wav', '.ogg')):
                name = os.path.splitext(f)[0].lower().replace(" ", "_").replace("-", "_")
                names.append(name)
        return sorted(names)
    
    return []


def get_sfx_path(sfx_name: str) -> str | None:
    """Gets filepath for a named SFX from manifest."""
    # Clean the name
    clean_name = sfx_name.lower().strip().replace(" ", "_").replace("-", "_")
    
    # Check manifest
    if os.path.exists(SFX_MANIFEST_FILE):
        try:
            with open(SFX_MANIFEST_FILE, "r") as f:
                manifest = json.load(f)
            
            # Exact match
            if clean_name in manifest:
                path = manifest[clean_name]["path"]
                if os.path.exists(path):
                    return path
            
            # Partial match (if AI says "door_creak" but file is "door_creak_horror")
            for name, data in manifest.items():
                if clean_name in name or name in clean_name:
                    path = data["path"]
                    if os.path.exists(path):
                        print(f"[SFX] Partial match: '{sfx_name}' → '{name}'")
                        return path
        except:
            pass
    
    # Direct file check
    for ext in [".mp3", ".wav", ".ogg"]:
        path = os.path.join(SFX_DIR, f"{clean_name}{ext}")
        if os.path.exists(path):
            return path
    
    print(f"[SFX] Not found: {sfx_name}")
    return None


if __name__ == "__main__":
    clean_sfx_library()
    names = get_available_sfx_names()
    print(f"\nAvailable SFX ({len(names)}):")
    for n in names:
        print(f"  - {n}")
