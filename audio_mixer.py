"""
Audio Mixer — SibbyRespect
Mixes 4 audio layers: Voiceover + SFX + Background Music + Gameplay Audio
"""

import os
from pydub import AudioSegment

# ─────────────────────────────────────────────────────────────────────────────
#  SPEED ADJUSTMENT
# ─────────────────────────────────────────────────────────────────────────────
def speed_up_audio(audio_path: str, speed: float = 1.12, output_path: str = None) -> str:
    """
    Speeds up audio by a factor (1.12 = 12% faster).
    Returns path to sped-up audio.
    """
    if output_path is None:
        base, ext = os.path.splitext(audio_path)
        output_path = f"{base}_fast{ext}"
    
    try:
        audio = AudioSegment.from_file(audio_path)
        
        # Speed up by changing frame rate then converting back
        faster_audio = audio._spawn(audio.raw_data, overrides={
            "frame_rate": int(audio.frame_rate * speed)
        }).set_frame_rate(audio.frame_rate)
        
        faster_audio.export(output_path, format="mp3", bitrate="192k")
        
        original_duration = len(audio) / 1000
        new_duration = len(faster_audio) / 1000
        print(f"[Audio] Speed {speed}x: {original_duration:.1f}s → {new_duration:.1f}s")
        
        return output_path
        
    except Exception as e:
        print(f"[Audio] Speed adjustment error: {e}")
        return audio_path


# ─────────────────────────────────────────────────────────────────────────────
#  4-LAYER AUDIO MIXING
# ─────────────────────────────────────────────────────────────────────────────
def mix_final_audio(
    voiceover_path: str,
    bg_music_path: str = None,
    gameplay_audio_path: str = None,
    output_path: str = "final_audio.mp3",
    voiceover_volume: float = 1.0,
    music_volume_db: float = -22,     # 6-8% perceived volume
    gameplay_volume_db: float = -26,  # 5% perceived volume
) -> str | None:
    """
    Mixes all audio layers into final audio.
    
    Layers:
    1. Voiceover (with SFX already mixed in) — 100% volume
    2. Background Music — 6-8% volume
    3. Gameplay Audio — 5% volume
    
    Args:
        voiceover_path: Path to voiceover (with SFX already overlaid)
        bg_music_path: Path to background music
        gameplay_audio_path: Path to gameplay audio extracted from video
        output_path: Output path for final mixed audio
        voiceover_volume: Voiceover volume multiplier
        music_volume_db: Background music volume in dB reduction
        gameplay_volume_db: Gameplay audio volume in dB reduction
    
    Returns:
        Path to final mixed audio, or None if failed
    """
    try:
        # Load voiceover (already has SFX)
        voiceover = AudioSegment.from_file(voiceover_path)
        target_duration = len(voiceover)
        print(f"[Mixer] Voiceover duration: {target_duration/1000:.1f}s")
        
        # Start with voiceover as base
        final_mix = voiceover
        
        # Layer 2: Background Music
        if bg_music_path and os.path.exists(bg_music_path):
            try:
                music = AudioSegment.from_file(bg_music_path)
                
                # Loop if shorter than voiceover
                if len(music) < target_duration:
                    loops = (target_duration // len(music)) + 1
                    music = music * loops
                
                # Trim to match voiceover
                music = music[:target_duration]
                
                # Reduce volume significantly
                music = music + music_volume_db
                
                # Fade in/out for smoothness
                music = music.fade_in(2000).fade_out(2000)
                
                # Overlay
                final_mix = final_mix.overlay(music)
                print(f"[Mixer] Background music added ({music_volume_db}dB)")
                
            except Exception as e:
                print(f"[Mixer] Background music error (skipping): {e}")
        
        # Layer 3: Gameplay Audio
        if gameplay_audio_path and os.path.exists(gameplay_audio_path):
            try:
                gameplay = AudioSegment.from_file(gameplay_audio_path)
                
                # Loop if needed
                if len(gameplay) < target_duration:
                    loops = (target_duration // len(gameplay)) + 1
                    gameplay = gameplay * loops
                
                # Trim
                gameplay = gameplay[:target_duration]
                
                # Very quiet
                gameplay = gameplay + gameplay_volume_db
                
                # Overlay
                final_mix = final_mix.overlay(gameplay)
                print(f"[Mixer] Gameplay audio added ({gameplay_volume_db}dB)")
                
            except Exception as e:
                print(f"[Mixer] Gameplay audio error (skipping): {e}")
        
        # Export final mix
        final_mix.export(output_path, format="mp3", bitrate="192k")
        print(f"[Mixer] Final audio exported: {output_path} ({len(final_mix)/1000:.1f}s)")
        
        return output_path
        
    except Exception as e:
        print(f"[Mixer] Critical error: {e}")
        return None


def extract_audio_from_video(video_path: str, output_path: str = "gameplay_audio.mp3") -> str | None:
    """
    Extracts audio track from video file (for gameplay audio layer).
    """
    try:
        from moviepy.editor import VideoFileClip
        video = VideoFileClip(video_path)
        
        if video.audio is None:
            print("[Mixer] Video has no audio track")
            video.close()
            return None
        
        video.audio.write_audiofile(output_path, logger=None)
        video.close()
        
        print(f"[Mixer] Extracted gameplay audio: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"[Mixer] Audio extraction error: {e}")
        return None


if __name__ == "__main__":
    print("[Test] Audio Mixer loaded successfully")
