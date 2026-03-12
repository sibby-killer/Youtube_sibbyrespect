"""
Animated Captions — SibbyRespect
Converts SRT subtitles to ASS format with dopamine-inducing animations.
Uses FFmpeg ASS renderer — no external tools needed.
"""

import os
import re
import random


# Animation styles that rotate for variety
ANIMATION_STYLES = {
    "pop_in": r"{\fad(100,50)\fscx50\fscy50\t(0,100,\fscx100\fscy100)}",
    "fade_up": r"{\fad(150,100)\move(540,1050,540,980)}",
    "slide_left": r"{\fad(100,50)\move(1200,980,540,980)}",
    "slide_right": r"{\fad(100,50)\move(-100,980,540,980)}",
    "bounce": r"{\fad(100,50)\fscx120\fscy120\t(0,80,\fscx100\fscy100)\t(80,150,\fscx105\fscy105)\t(150,200,\fscx100\fscy100)}",
    "zoom_shake": r"{\fad(80,50)\fscx80\fscy80\t(0,100,\fscx105\fscy105)\t(100,150,\fscx100\fscy100)}",
}

# Color schemes that rotate (primary color for keywords)
HIGHLIGHT_COLORS = [
    "&H0000FFFF",  # Yellow
    "&H0000FF00",  # Green
    "&H005EFFE8",  # Orange-Gold
    "&H00FF69B4",  # Pink
    "&H0000D4FF",  # Gold
]


def srt_to_ass(srt_path: str, ass_path: str) -> bool:
    """
    Converts SRT to ASS with animated, dopamine-inducing captions.
    """
    try:
        # Read SRT
        if not os.path.exists(srt_path):
            print(f"[Captions] SRT not found: {srt_path}")
            return False

        with open(srt_path, "r", encoding="utf-8") as f:
            srt_content = f.read()
        
        # Parse SRT entries
        entries = parse_srt(srt_content)
        
        if not entries:
            print("[Captions] No SRT entries found")
            return False
        
        # Build ASS header
        ass_header = """[Script Info]
Title: SibbyRespect Captions
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginV, MarginR, Encoding
Style: Default,Impact,28,&H00FFFFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,2,60,150,60,1
Style: Highlight,Impact,32,&H0000FFFF,&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,2,60,150,60,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        
        # Build ASS events with animations
        ass_events = []
        animation_keys = list(ANIMATION_STYLES.keys())
        
        for i, entry in enumerate(entries):
            start_time = format_ass_time(entry["start"])
            end_time = format_ass_time(entry["end"])
            text = entry["text"].replace("\n", "\\N")
            
            # Pick animation style (rotate through them)
            anim_key = animation_keys[i % len(animation_keys)]
            anim_code = ANIMATION_STYLES[anim_key]
            
            # Highlight random keywords (make 1-2 words colored per subtitle)
            text = highlight_keywords(text, HIGHLIGHT_COLORS[i % len(HIGHLIGHT_COLORS)])
            
            # Build the ASS dialogue line
            line = f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{anim_code}{text}"
            ass_events.append(line)
        
        # Write ASS file
        ass_content = ass_header + "\n".join(ass_events) + "\n"
        
        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(ass_content)
        
        print(f"[Captions] ASS file created: {ass_path} ({len(entries)} entries)")
        return True
        
    except Exception as e:
        print(f"[Captions] SRT to ASS error: {e}")
        return False


def parse_srt(srt_text: str) -> list:
    """Parses SRT text into list of entries with start, end, text."""
    entries = []
    # Handle both \n\n and \r\n\r\n
    blocks = re.split(r'\n\s*\n', srt_text.strip())
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            # Parse timestamp line
            time_match = re.search(
                r'(\d{2}:\d{2}:\d{2}[,\.]\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2}[,\.]\d{3})',
                lines[1]
            )
            if time_match:
                start = time_match.group(1).replace(',', '.')
                end = time_match.group(2).replace(',', '.')
                text = ' '.join(lines[2:])
                entries.append({"start": start, "end": end, "text": text})
    
    return entries


def format_ass_time(srt_time: str) -> str:
    """Converts SRT timestamp to ASS format (H:MM:SS.CC)."""
    # Input: 00:00:01.500
    # Output: 0:00:01.50
    parts = srt_time.replace(',', '.').split(':')
    h = int(parts[0])
    m = parts[1]
    s_ms = parts[2]
    
    if '.' in s_ms:
        s, ms = s_ms.split('.')
        cs = ms[:2]  # ASS uses centiseconds (2 digits)
    else:
        s = s_ms
        cs = "00"
    
    return f"{h}:{m}:{s}.{cs}"


def highlight_keywords(text: str, color: str) -> str:
    """
    Highlights 1-2 important words in the subtitle with a different color.
    Makes captions more dynamic and attention-grabbing.
    """
    words = text.split()
    
    if len(words) <= 2:
        return text  # Too short to highlight
    
    # Find words to highlight (longer words are usually more important)
    important_indices = []
    for i, word in enumerate(words):
        clean_word = re.sub(r'[^a-zA-Z]', '', word)
        if len(clean_word) >= 4:  # Highlight words with 4+ letters
            important_indices.append(i)
    
    if not important_indices:
        return text
    
    # Pick 1-2 words to highlight
    highlight_count = min(2, len(important_indices))
    chosen = random.sample(important_indices, highlight_count)
    
    for idx in chosen:
        original = words[idx]
        # ASS color override: {\c&HCOLOR&}word{\c&H00FFFFFF&}
        words[idx] = r"{\c" + color + r"}" + original.upper() + r"{\c&H00FFFFFF&}"
    
    return " ".join(words)


def burn_animated_captions(video_path: str, srt_path: str, output_path: str) -> bool:
    """
    Burns animated ASS captions onto the video.
    Steps:
    1. Convert SRT to ASS with animations
    2. Burn ASS onto video using FFmpeg
    """
    import subprocess
    import shutil
    
    ass_path = srt_path.replace(".srt", ".ass")
    
    # Step 1: Convert SRT to animated ASS
    if not srt_to_ass(srt_path, ass_path):
        print("[Captions] ASS conversion failed, trying basic SRT burn...")
        # Fallback to basic SRT
        return burn_basic_captions(video_path, srt_path, output_path)
    
    # Step 2: Burn ASS onto video
    try:
        # Escape path for FFmpeg filter
        # On Windows, we need to handle backslashes and colons
        ass_escaped = ass_path.replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
        
        cmd = [
            "ffmpeg",
            "-i", video_path,
            "-vf", f"ass='{ass_escaped}'",
            "-c:a", "copy",
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "23",
            "-y",
            output_path
        ]
        
        print(f"[Captions] Burning ASS captions: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 100000:
            print(f"[Captions] Animated captions burned successfully")
            return True
        else:
            print(f"[Captions] ASS burn failed: {result.stderr[:300] if result.stderr else ''}")
            # Fallback
            return burn_basic_captions(video_path, srt_path, output_path)
            
    except Exception as e:
        print(f"[Captions] Error: {e}")
        return burn_basic_captions(video_path, srt_path, output_path)


def burn_basic_captions(video_path: str, srt_path: str, output_path: str) -> bool:
    """Fallback: burns basic styled captions without animation."""
    import subprocess
    import shutil
    
    try:
        style = (
            "FontName=Impact,"
            "FontSize=16,"
            "PrimaryColour=&H00FFFFFF,"
            "OutlineColour=&H00000000,"
            "Bold=1,"
            "Outline=3,"
            "Shadow=2,"
            "Alignment=2,"
            "MarginV=120,"
            "MarginL=60,"
            "MarginR=60"
        )
        
        # Escape string for subtitles filter
        srt_escaped = srt_path.replace("\\", "/").replace(":", "\\:")
        
        cmd = [
            "ffmpeg", "-i", video_path,
            "-vf", f"subtitles='{srt_escaped}':force_style='{style}'",
            "-c:a", "copy", "-c:v", "libx264",
            "-preset", "medium", "-crf", "23",
            "-y", output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        if os.path.exists(output_path) and os.path.getsize(output_path) > 100000:
            print("[Captions] Basic styled captions applied")
            return True
        
        # Last resort: copy without captions
        if video_path != output_path:
            shutil.copy2(video_path, output_path)
        print("[Captions] Using video without captions")
        return True
        
    except Exception as e:
        print(f"[Captions] Basic burn error: {e}")
        if video_path != output_path:
            shutil.copy2(video_path, output_path)
        return True
