"""
video_editor.py — CatTeaches Vertical Engine
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
ZOOM_FACTOR = 1.20  # 120% zoom — fills screen + alters content significantly

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
    Uses the new animated captions engine by default.
    """
    from core.animated_captions import burn_animated_captions
    return burn_animated_captions(video_path, srt_path, output_path)

def add_watermark_ffmpeg(video_path: str, watermark_text: str = "SibbyRespect") -> str:
    """
    Adds watermark using FFmpeg as a more robust alternative to ImageMagick.
    Uses drawtext filter at the bottom right.
    """
    output_path = video_path.replace(".mp4", "_watermarked.mp4")
    try:
        # drawtext filter: white, 25% opacity (0.25), bottom right
        # We use a standard path for Impact font on Windows
        filter_str = (
            f"drawtext=text='{watermark_text}':fontcolor=white@0.25:"
            f"fontsize=36:x=w-tw-60:y=h-th-100:fontfile='C\\:/Windows/Fonts/impact.ttf'"
        )
        
        # Fallback for fontfile if impact.ttf doesn't exist (simpler font)
        if not os.path.exists("C:/Windows/Fonts/impact.ttf"):
            filter_str = (
                f"drawtext=text='{watermark_text}':fontcolor=white@0.25:"
                f"fontsize=32:x=w-tw-40:y=h-th-80"
            )

        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", filter_str,
            "-c:a", "copy", "-c:v", "libx264",
            "-preset", "medium", "-crf", "23", "-y",
            output_path
        ]
        
        subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 100000:
            os.remove(video_path)
            os.rename(output_path, video_path)
            print(f"[Watermark] FFmpeg watermark applied")
            return video_path
        return video_path
    except Exception as e:
        print(f"[Watermark] FFmpeg error: {e}")
        return video_path

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
        
        # Render the video first, then apply watermark using FFmpeg for robustness
        print(f"[Assembly] Rendering primary vertical video...")
        final_video.write_videofile(
            output_path,
            codec="libx264", audio_codec="aac",
            preset="medium", threads=2, fps=TARGET_FPS, logger=None
        )
        
        # Always add watermark via FFmpeg after initial render
        add_watermark_ffmpeg(output_path, "CatTeaches")
        
        audio.close()
        bg.close()
        final_video.close()
        return True
    except Exception as e:
        print(f"[Assembly] CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False
