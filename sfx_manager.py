"""
SFX Manager — SibbyRespect
Handles word-trigger based sound effect overlay on voiceover audio.
Uses proportional text position matching for timestamp calculation.
"""

import os
import re
from pydub import AudioSegment

# ─────────────────────────────────────────────────────────────────────────────
#  WORD-TRIGGER TIMESTAMP CALCULATION
# ─────────────────────────────────────────────────────────────────────────────
def calculate_sfx_timestamps(script: str, sfx_timeline: list, audio_duration_ms: int) -> list:
    """
    Calculates exact timestamps for each SFX based on word position in script.
    
    Uses proportional matching:
    - Find which word position the trigger phrase starts at
    - Calculate percentage through script
    - Apply percentage to audio duration
    
    Args:
        script: The full clean script text
        sfx_timeline: List of dicts with trigger_phrase, sound, volume
        audio_duration_ms: Total voiceover duration in milliseconds
    
    Returns:
        List of dicts with timestamp_ms, sound, volume
    """
    words = script.lower().split()
    total_words = len(words)
    
    if total_words == 0:
        return []
    
    timestamped_sfx = []
    
    for sfx in sfx_timeline:
        trigger = sfx.get("trigger_phrase", "").lower().strip()
        sound = sfx.get("sound", "")
        volume = sfx.get("volume", 0.6)
        
        if not trigger or not sound:
            continue
        
        # Find the trigger phrase in the script
        trigger_words = trigger.split()
        trigger_start_pos = -1
        
        # Search for the phrase in the word list
        for i in range(len(words) - len(trigger_words) + 1):
            match = True
            for j, tw in enumerate(trigger_words):
                # Clean both words for comparison
                script_word = re.sub(r'[^a-z]', '', words[i + j])
                trigger_word = re.sub(r'[^a-z]', '', tw)
                if script_word != trigger_word:
                    match = False
                    break
            if match:
                trigger_start_pos = i
                break
        
        if trigger_start_pos == -1:
            # Phrase not found — try partial match (first 2 words)
            if len(trigger_words) >= 2:
                for i in range(len(words) - 1):
                    w1 = re.sub(r'[^a-z]', '', words[i])
                    w2 = re.sub(r'[^a-z]', '', words[i + 1])
                    t1 = re.sub(r'[^a-z]', '', trigger_words[0])
                    t2 = re.sub(r'[^a-z]', '', trigger_words[1])
                    if w1 == t1 and w2 == t2:
                        trigger_start_pos = i
                        break
        
        if trigger_start_pos >= 0:
            # Calculate position as percentage
            position_pct = trigger_start_pos / total_words
            timestamp_ms = int(audio_duration_ms * position_pct)
            
            # Small offset — play SFX slightly after the word (more natural)
            timestamp_ms = max(0, timestamp_ms + 200)
            
            timestamped_sfx.append({
                "timestamp_ms": timestamp_ms,
                "sound": sound,
                "volume": volume,
                "trigger": trigger,
            })
            print(f"[SFX] '{trigger}' → {timestamp_ms/1000:.1f}s ({sound})")
        else:
            print(f"[SFX] Trigger phrase not found in script: '{trigger}' — skipping")
    
    # Sort by timestamp
    timestamped_sfx.sort(key=lambda x: x["timestamp_ms"])
    
    return timestamped_sfx


# ─────────────────────────────────────────────────────────────────────────────
#  SFX OVERLAY — Mix sound effects into voiceover
# ─────────────────────────────────────────────────────────────────────────────
def overlay_sfx_on_audio(voiceover_path: str, sfx_timestamps: list, output_path: str) -> bool:
    """
    Overlays sound effects onto the voiceover audio at calculated timestamps.
    
    Args:
        voiceover_path: Path to the voiceover audio file
        sfx_timestamps: List of dicts with timestamp_ms, sound, volume
        output_path: Path for the output audio with SFX
    
    Returns:
        True if successful
    """
    from pixabay_audio import get_sfx_path
    
    try:
        # Load voiceover
        voiceover = AudioSegment.from_file(voiceover_path)
        print(f"[SFX] Voiceover loaded: {len(voiceover)/1000:.1f}s")
        
        # Overlay each SFX
        sfx_applied = 0
        for sfx_data in sfx_timestamps:
            sound_name = sfx_data["sound"]
            timestamp = sfx_data["timestamp_ms"]
            volume = sfx_data.get("volume", 0.6)
            
            # Get SFX file path
            sfx_path = get_sfx_path(sound_name)
            if not sfx_path:
                continue
            
            try:
                # Load SFX
                sfx_audio = AudioSegment.from_file(sfx_path)
                
                # Trim SFX if too long (max 2 seconds)
                if len(sfx_audio) > 2000:
                    sfx_audio = sfx_audio[:2000]
                
                # Adjust volume
                # volume 0.6 = reduce by ~4dB, 0.5 = ~6dB, etc
                volume_reduction = -int((1 - volume) * 15)
                sfx_audio = sfx_audio + volume_reduction
                
                # Make sure timestamp is within bounds
                if timestamp < len(voiceover):
                    voiceover = voiceover.overlay(sfx_audio, position=timestamp)
                    sfx_applied += 1
                    print(f"[SFX] Applied {sound_name} at {timestamp/1000:.1f}s")
                
            except Exception as e:
                print(f"[SFX] Error applying {sound_name}: {e}")
                continue
        
        # Export
        voiceover.export(output_path, format="mp3", bitrate="192k")
        print(f"[SFX] Output saved: {output_path} ({sfx_applied} effects applied)")
        return True
        
    except Exception as e:
        print(f"[SFX] Overlay error: {e}")
        return False


if __name__ == "__main__":
    print("[Test] SFX Manager loaded successfully")
    print(f"[Test] Available functions: calculate_sfx_timestamps, overlay_sfx_on_audio")
