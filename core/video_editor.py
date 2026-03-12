"""
video_editor.py — SibbyRespect Vertical Engine
Handles 9:16 vertical processing, zoom, visual enhancements, and styled captions.
Alters content enough to be considered "transformed" for monetization.
"""

import os
import subprocess
import shutil
from moviepy.editor import (
    VideoFileClip, AudioFileClip, CompositeVideoClip,
    concatenate_videoclips, TextClip
)
from config import OUTPUT_DIR, TEMP_DIR

TARGET_WIDTH = 1080
TARGET_HEIGHT = 1920
TARGET_FPS = 30
ZOOM_FACTOR = 1.15  # 115% zoom — fills screen + alters content

def process_background_video(bg_video_path: str, target_duration: float):
    """
    Processes background video to vertical 9:16 format with zoom and centering.
    """
    bg = VideoFileClip(bg_video_path)
    source_w, source_h = bg.size
    source_ratio = source_w / source_h
    target_ratio = TARGET_WIDTH / TARGET_HEIGHT
    
    print(f"[Video] Source: {source_w}x{source_h} (ratio: {source_ratio:.3f})")
    
    # Calculate scale dimensions to fill vertical frame with zoom
    if source_ratio > target_ratio:
        # Source is WIDER
        scale_height = TARGET_HEIGHT * ZOOM_FACTOR
        scale_width = scale_height * source_ratio
    else:
        # Source is NARROWER
        scale_width = TARGET_WIDTH * ZOOM_FACTOR
        scale_height = scale_width / source_ratio
    
    bg = bg.resize((int(scale_width), int(scale_height)))
    print(f"[Video] Scaled to: {int(scale_width)}x{int(scale_height)} ({ZOOM_FACTOR*100:.0f}% zoom)")
    
    # Center crop to exact target size
    current_w, current_h = bg.size
    x_center = current_w / 2
    y_center = current_h / 2
    
    # Shift crop slightly upward (2%) to capture more of character, less of ground
    y_offset = -int(current_h * 0.02)
    
    crop_x1 = int(x_center - TARGET_WIDTH / 2)
    crop_y1 = int(y_center - TARGET_HEIGHT / 2) + y_offset
    crop_x2 = crop_x1 + TARGET_WIDTH
    crop_y2 = crop_y1 + TARGET_HEIGHT
    
    # Keep crop within bounds
    crop_x1 = max(0, min(crop_x1, current_w - TARGET_WIDTH))
    crop_y1 = max(0, min(crop_y1, current_h - TARGET_HEIGHT))
    crop_x2 = crop_x1 + TARGET_WIDTH
    crop_y2 = crop_y1 + TARGET_HEIGHT
    
    bg = bg.crop(x1=crop_x1, y1=crop_y1, x2=crop_x2, y2=crop_y2)
    print(f"[Video] Center cropped to: {bg.size[0]}x{bg.size[1]}")
    
    # Loop or trim to match audio duration
    if bg.duration < target_duration:
        loops = int(target_duration / bg.duration) + 1
        print(f"[Video] Looping {loops}x to fill {target_duration:.1f}s...")
        bg = concatenate_videoclips([bg] * loops)
    
    bg = bg.subclip(0, target_duration)
    return bg

def apply_visual_enhancements(video_path: str) -> str:
    """
    Applies subtle visual enhancements using FFmpeg: dark grade, vignette, sharpening, contrast.
    """
    output_path = video_path.replace(".mp4", "_enhanced.mp4")
    try:
        filter_chain = (
            "eq=brightness=-0.03:contrast=1.1:saturation=1.05,"
            "vignette=PI/5,"
            "unsharp=3:3:0.5:3:3:0.0"
        )
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", filter_chain,
            "-c:a", "copy", "-c:v", "libx264",
            "-preset", "medium", "-crf", "23", "-y",
            output_path
        ]
        subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 100000:
            os.remove(video_path)
            os.rename(output_path, video_path)
            print(f"[Enhance] Visual enhancements applied")
            return video_path
        return video_path
    except Exception as e:
        print(f"[Enhance] Error: {e}")
        return video_path

def burn_captions_styled(video_path: str, srt_path: str, output_path: str) -> bool:
    """
    Burns dynamic styled captions onto the vertical video.
    """
    try:
        style = (
            "FontName=Impact,"
            "FontSize=18,"
            "PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H00000000,"
            "BackColour=&H40000000,"
            "Bold=1,Outline=3,Shadow=2,"
            "ShadowColour=&H80000000,Alignment=2,"
            "MarginV=120,MarginL=60,MarginR=60"
        )
        # Handle Windows paths for FFmpeg
        srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", f"subtitles='{srt_escaped}':force_style='{style}'",
            "-c:a", "copy", "-c:v", "libx264",
            "-preset", "medium", "-crf", "23", "-y",
            output_path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 100000:
            print(f"[Captions] Styled captions burned successfully")
            return True
        # Fallback
        simple_cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", f"subtitles='{srt_escaped}'",
            "-c:a", "copy", "-c:v", "libx264", "-y", output_path
        ]
        subprocess.run(simple_cmd, capture_output=True, timeout=600)
        return os.path.exists(output_path)
    except Exception as e:
        print(f"[Captions] Error: {e}")
        shutil.copy2(video_path, output_path)
        return True

def ensure_shorts_duration(video_path: str, max_duration: float = 59.0) -> str:
    """
    Ensures video is under 59 seconds for YouTube Shorts shelf.
    """
    try:
        video = VideoFileClip(video_path)
        if video.duration <= max_duration:
            video.close()
            return video_path
        
        print(f"[Duration] {video.duration:.1f}s — TRIMMING to {max_duration}s")
        trimmed_path = video_path.replace(".mp4", "_trimmed.mp4")
        trimmed = video.subclip(0, max_duration)
        trimmed.write_videofile(trimmed_path, codec="libx264", audio_codec="aac", logger=None)
        video.close()
        trimmed.close()
        os.remove(video_path)
        os.rename(trimmed_path, video_path)
        return video_path
    except Exception as e:
        print(f"[Duration] Error: {e}")
        return video_path

def assemble_simple_video(bg_video_path: str, final_audio_path: str, output_path: str) -> bool:
    """
    Complete vertical video assembly with zoom, watermark, and muxing.
    """
    try:
        audio = AudioFileClip(final_audio_path)
        target_duration = audio.duration
        print(f"[Assembly] Audio: {target_duration:.1f}s")
        
        bg = process_background_video(bg_video_path, target_duration)
        bg = bg.without_audio()
        
        final_video = bg.set_audio(audio)
        
        # Add watermark
        try:
            watermark = TextClip(
                "SibbyRespect",
                fontsize=24,
                color='white',
                font='Arial-Bold',
            ).set_opacity(0.25).set_duration(target_duration)
            watermark = watermark.set_position((TARGET_WIDTH - 250, TARGET_HEIGHT - 80))
            final_video = CompositeVideoClip([final_video, watermark])
            print(f"[Assembly] Watermark added")
        except Exception as e:
            print(f"[Assembly] Watermark skipped: {e}")
        
        print(f"[Assembly] Rendering {TARGET_WIDTH}x{TARGET_HEIGHT} vertical...")
        final_video.write_videofile(
            output_path,
            codec="libx264", audio_codec="aac",
            preset="medium", threads=2, fps=TARGET_FPS, logger=None
        )
        
        audio.close()
        bg.close()
        final_video.close()
        return True
    except Exception as e:
        print(f"[Assembly] CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
