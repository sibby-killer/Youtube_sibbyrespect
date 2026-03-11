"""
video_editor.py — SibbyRespect
Simplified video assembly: ONE background video (Roblox TikTok footage) + voiceover.
Loops background if shorter than audio, trims if longer. Burns subtitles via FFmpeg.
"""

import os
import gc
import subprocess
from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeAudioClip,
    concatenate_videoclips, concatenate_audioclips
)
from config import OUTPUT_DIR, TEMP_DIR


def assemble_simple_video(
    bg_video_path: str,
    voiceover_path: str,
    output_filename: str = "final_short.mp4",
    srt_path: str = None
) -> str | None:
    """
    Simple assembly: ONE background video + voiceover overlay.
    - Loops background if it is shorter than the voiceover duration.
    - Trims background if it is longer.
    - Burns subtitles with FFmpeg if an SRT file is provided.
    - Removes original audio from the Roblox TikTok video.

    Args:
        bg_video_path:   Path to the single Roblox gameplay TikTok video.
        voiceover_path:  Path to the TTS voiceover MP3.
        output_filename: Output filename (placed in OUTPUT_DIR).
        srt_path:        Optional path to .srt subtitle file.

    Returns:
        Full path to the assembled MP4, or None on failure.
    """
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    print("\n[Assembly] Starting video assembly (SibbyRespect simple mode)...")

    if not os.path.exists(bg_video_path):
        print(f"[Assembly] ERROR: Background video not found: {bg_video_path}")
        return None

    if not os.path.exists(voiceover_path):
        print(f"[Assembly] ERROR: Voiceover not found: {voiceover_path}")
        return None

    voiceover = None
    bg_video  = None
    final_video = None

    try:
        # ── Load voiceover ────────────────────────────────────────────────
        voiceover       = AudioFileClip(voiceover_path)
        target_duration = voiceover.duration
        print(f"[Assembly] Voiceover duration: {target_duration:.1f}s")

        # ── Load background video ─────────────────────────────────────────
        bg_video = VideoFileClip(bg_video_path)
        print(f"[Assembly] Background duration: {bg_video.duration:.1f}s")

        # ── Crop to 9:16 vertical (1080×1920) for Shorts ─────────────────
        w, h = bg_video.size
        target_ratio = 1080 / 1920.0
        clip_ratio   = w / float(h)

        if clip_ratio > target_ratio:
            # Too wide — crop width
            new_w   = int(h * target_ratio)
            bg_video = bg_video.crop(x_center=w // 2, width=new_w)
        elif clip_ratio < target_ratio:
            # Too tall — crop height
            new_h   = int(w / target_ratio)
            bg_video = bg_video.crop(y_center=h // 2, height=new_h)

        bg_video = bg_video.resize(newsize=(1080, 1920))

        # ── Loop if shorter than voiceover ────────────────────────────────
        if bg_video.duration < target_duration:
            loops    = int(target_duration / bg_video.duration) + 1
            print(f"[Assembly] Background shorter than audio — looping {loops}x...")
            bg_video = concatenate_videoclips([bg_video] * loops)

        # ── Trim to exact voiceover duration ──────────────────────────────
        bg_video = bg_video.subclip(0, target_duration)

        # ── Strip original Roblox audio (TikTok background sound) ─────────
        bg_video = bg_video.without_audio()

        # ── Set voiceover as the only audio track ─────────────────────────
        final_video = bg_video.set_audio(voiceover)

        # ── Render ────────────────────────────────────────────────────────
        if srt_path and os.path.exists(srt_path):
            # Render silent + voiceover first, then burn subs via FFmpeg
            temp_output = os.path.join(TEMP_DIR, "temp_no_subs.mp4")
            print(f"[Assembly] Rendering intermediate (no subs)...")
            final_video.write_videofile(
                temp_output,
                fps=30,
                codec="libx264",
                audio_codec="aac",
                preset="medium",
                threads=2,
                logger=None
            )

            # Cleanup moviepy objects before FFmpeg pass
            voiceover.close()
            bg_video.close()
            final_video.close()
            gc.collect()

            print("[Assembly] Burning subtitles with FFmpeg...")
            _burn_subtitles(temp_output, srt_path, output_path)

            if os.path.exists(temp_output):
                try:
                    os.remove(temp_output)
                except OSError:
                    pass

        else:
            # No subtitles — render directly
            print(f"[Assembly] Rendering final video...")
            final_video.write_videofile(
                output_path,
                fps=30,
                codec="libx264",
                audio_codec="aac",
                preset="medium",
                threads=2,
                logger=None
            )
            voiceover.close()
            bg_video.close()
            final_video.close()
            gc.collect()

        if os.path.exists(output_path):
            size_mb = os.path.getsize(output_path) / (1024 * 1024)
            print(f"[Assembly] ✓ Video ready ({size_mb:.1f} MB): {output_path}")
            return output_path
        else:
            print("[Assembly] ERROR: Output file was not created")
            return None

    except Exception as e:
        print(f"[Assembly] CRITICAL ERROR: {e}")
        # Best-effort cleanup
        for clip in [voiceover, bg_video, final_video]:
            try:
                if clip:
                    clip.close()
            except Exception:
                pass
        gc.collect()
        return None


# ─────────────────────────────────────────────────────────────────────────────
#  SUBTITLE BURNING — FFmpeg helper
# ─────────────────────────────────────────────────────────────────────────────
def _burn_subtitles(input_path: str, srt_path: str, output_path: str):
    """Burns SRT subtitles into the video using FFmpeg. Hormozi-style captions."""
    try:
        import imageio_ffmpeg
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        ffmpeg_exe = "ffmpeg"

    srt_abs = os.path.abspath(srt_path)

    # Platform-specific path escaping for FFmpeg subtitles filter
    if len(srt_abs) >= 2 and srt_abs[1] == ':':
        drive          = srt_abs[0]
        rest           = srt_abs[2:].replace('\\', '/')
        ffmpeg_srt_path = f"{drive}\\\\:{rest}"
    else:
        ffmpeg_srt_path = srt_abs.replace('\\', '/')

    # Hormozi bold yellow captions, centre-screen
    style = (
        "FontName=Arial,FontSize=26,"
        "PrimaryColour=&H00FFFF&,OutlineColour=&H000000&,"
        "Outline=2,Alignment=10,Bold=1"
    )

    cmd = [
        ffmpeg_exe, "-y",
        "-i", input_path,
        "-vf", f"subtitles={ffmpeg_srt_path}:force_style='{style}'",
        "-c:a", "copy",
        output_path
    ]
    subprocess.run(cmd, check=True)
    print("[Assembly] Subtitles burned successfully.")


# ─────────────────────────────────────────────────────────────────────────────
#  LEGACY ALIAS — kept so old code that imports stitch_video doesn't crash
# ─────────────────────────────────────────────────────────────────────────────
def stitch_video(audio_path: str, broll_paths: list,
                  output_filename: str = "final_short.mp4",
                  srt_path: str = None):
    """
    LEGACY — this project now uses assemble_simple_video().
    If called, uses the first clip in broll_paths as the single background.
    """
    print("[Assembly] Warning: stitch_video() is deprecated for SibbyRespect.")
    print("[Assembly] Use assemble_simple_video() with a TikTok background instead.")
    if not broll_paths:
        return None
    return assemble_simple_video(
        bg_video_path=broll_paths[0],
        voiceover_path=audio_path,
        output_filename=output_filename,
        srt_path=srt_path
    )
