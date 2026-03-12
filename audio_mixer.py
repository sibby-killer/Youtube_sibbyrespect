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
def mix_final_audio(voiceover_path, bg_music_path=None, gameplay_audio_path=None,
                    output_path="final_audio.mp3",
                    music_volume_db=-22, gameplay_volume_db=-26):
    """
    Mixes all audio layers with proper format matching and error handling.
    
    Audio levels optimized for YouTube Shorts:
    - Voiceover: 0dB (crystal clear, always dominant)
    - SFX: already mixed into voiceover
    - Music: -22dB (6-8% perceived — subtle atmosphere)
    - Gameplay: -26dB (5% perceived — subtle immersion)
    """
    try:
        from pydub import AudioSegment
        
        voiceover = AudioSegment.from_file(voiceover_path)
        target_duration = len(voiceover)
        print(f"[Mixer] Voiceover: {target_duration/1000:.1f}s, {voiceover.channels}ch, {voiceover.frame_rate}Hz")
        
        final_mix = voiceover
        
        # Background Music
        if bg_music_path and os.path.exists(bg_music_path):
            try:
                music_size = os.path.getsize(bg_music_path)
                if music_size < 100000:
                    print(f"[Mixer] Music file too small ({music_size/1024:.0f}KB), skipping")
                else:
                    music = AudioSegment.from_file(bg_music_path)
                    
                    if len(music) < 3000:
                        print(f"[Mixer] Music too short, skipping")
                    else:
                        # CRITICAL: Match format to voiceover
                        music = music.set_frame_rate(voiceover.frame_rate)
                        music = music.set_channels(voiceover.channels)
                        music = music.set_sample_width(voiceover.sample_width)
                        
                        if len(music) < target_duration:
                            loops = (target_duration // len(music)) + 1
                            music = music * int(loops)
                        music = music[:target_duration]
                        music = music + music_volume_db
                        music = music.fade_in(2000).fade_out(2000)
                        
                        final_mix = final_mix.overlay(music)
                        print(f"[Mixer] Music added ({music_volume_db}dB)")
            except Exception as e:
                print(f"[Mixer] Music error (skipping): {e}")
        
        # Gameplay Audio
        if gameplay_audio_path and os.path.exists(gameplay_audio_path):
            try:
                gameplay_size = os.path.getsize(gameplay_audio_path)
                if gameplay_size < 10000:
                    print(f"[Mixer] Gameplay audio too small, skipping")
                else:
                    gameplay = AudioSegment.from_file(gameplay_audio_path)
                    
                    # Match format
                    gameplay = gameplay.set_frame_rate(voiceover.frame_rate)
                    gameplay = gameplay.set_channels(voiceover.channels)
                    gameplay = gameplay.set_sample_width(voiceover.sample_width)
                    
                    if len(gameplay) < target_duration:
                        loops = (target_duration // len(gameplay)) + 1
                        gameplay = gameplay * int(loops)
                    gameplay = gameplay[:target_duration]
                    gameplay = gameplay + gameplay_volume_db
                    
                    final_mix = final_mix.overlay(gameplay)
                    print(f"[Mixer] Gameplay audio added ({gameplay_volume_db}dB)")
            except Exception as e:
                print(f"[Mixer] Gameplay error (skipping): {e}")
        
        final_mix.export(output_path, format="mp3", bitrate="192k")
        print(f"[Mixer] Final audio: {output_path} ({len(final_mix)/1000:.1f}s)")
        return output_path
        
    except Exception as e:
        print(f"[Mixer] Critical error: {e}")
        import traceback
        traceback.print_exc()
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
