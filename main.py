import os
import re
import argparse
import time
from dotenv import load_dotenv

load_dotenv()

# --- MONKEY PATCH FOR MOVIEPY PIL DEPENDENCY (Pillow >= 10) ---
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS
# --------------------------------------------------------------

from core.ai_content import (
    generate_video_content, fix_description_formatting,
    CHANNEL_NAME
)
from reddit_source import get_reddit_story
from pixabay_audio import setup_sfx_library, get_background_music
from sfx_manager import calculate_sfx_timestamps, overlay_sfx_on_audio
from audio_mixer import speed_up_audio, mix_final_audio, extract_audio_from_video
from core.tts import generate_voiceover
from core.video_editor import (
    assemble_simple_video, apply_visual_enhancements,
    burn_captions_styled, ensure_shorts_duration
)
from tiktok_source import get_background_video, cleanup_old_videos


def ensure_tracking_files():
    """Creates empty tracking JSON files if they dont exist."""
    import json
    tracking_files = [
        "used_topics.json",
        "used_reddit_posts.json",
        "used_tiktok_videos.json",
        "used_music.json",
    ]
    for f in tracking_files:
        if not os.path.exists(f):
            with open(f, "w") as fp:
                json.dump([], fp)
            print(f"[Init] Created {f}")


def create_short(progress_callback=None) -> bool:
    """
    Master function — SibbyRespect Pipeline (2026 Algorithm Optimized).
    Follows 20-step high-quality production order.
    """
    def log(msg):
        print(msg)
        if progress_callback:
            progress_callback(msg)

    log(f"\n{'='*50}")
    log(f"  SIBBYSRESPECT OVERHAUL PIPELINE (PHASE 3)")
    log(f"{'='*50}\n")

    # STEP 0: Init Tracking
    ensure_tracking_files()

    # STEP 1: SFX Library
    log("[STEP 1] Ensuring SFX library is ready...")
    setup_sfx_library()

    # STEP 2: Content Sourcing
    log("[STEP 2] Sourcing content from Reddit...")
    reddit_post = get_reddit_story()
    
    # STEP 3: AI Content Generation
    log("[STEP 3] Generating chaotic AI content...")
    content = generate_video_content(reddit_post=reddit_post)
    if not content:
        log("[ERROR] AI content generation failed.")
        return False

    script = content.get('script', '')
    title = content.get('title', 'Video')
    log(f"  Title: {title}")

    # STEP 4: TTS Generation
    log("[STEP 4] Generating TTS voiceover...")
    raw_voiceover, srt_path = generate_voiceover(script, filename="v_raw.mp3")
    if not raw_voiceover or not os.path.exists(raw_voiceover):
        log("[ERROR] TTS failed.")
        return False

    # STEP 5: Speed up Audio
    log("[STEP 5] Speding up audio (1.12x)...")
    fast_voiceover = speed_up_audio(raw_voiceover, speed=1.12, output_path="v_fast.mp3")

    # STEP 6: Calculate SFX Timestamps
    from pydub import AudioSegment
    voice_audio = AudioSegment.from_file(fast_voiceover)
    duration_ms = len(voice_audio)
    sfx_timeline = content.get("sfx_timeline", [])
    sfx_ts = calculate_sfx_timestamps(script, sfx_timeline, duration_ms)

    # STEP 7: Overlay SFX
    log("[STEP 7] Overlaying SFX on voiceover...")
    voice_with_sfx = "v_sfx.mp3"
    overlay_sfx_on_audio(fast_voiceover, sfx_ts, voice_with_sfx)

    # STEP 8: Get Background Music
    log("[STEP 8] Fetching validated background music...")
    bg_music = get_background_music()

    # STEP 9: Get Background Video
    log("[STEP 9] Fetching Roblox background...")
    background_path = get_background_video()
    if not background_path:
        log("[ERROR] Background video failed.")
        return False

    # STEP 10: Extract Gameplay Audio
    log("[STEP 10] Extracting gameplay audio...")
    gameplay_audio = extract_audio_from_video(background_path, "v_gameplay.mp3")

    # STEP 11: Final 4-Layer Mix
    log("[STEP 11] Mixing 4-layer audio (Match formats)...")
    final_audio = "v_final_mix.mp3"
    mix_final_audio(
        voiceover_path=voice_with_sfx,
        bg_music_path=bg_music,
        gameplay_audio_path=gameplay_audio,
        output_path=final_audio
    )

    # STEP 12: Assemble Simple Video (Vertical 9:16)
    log("[STEP 12] Assembling vertical video (Zoom + Center)...")
    intermediate_video = "v_intermediate.mp4"
    if not assemble_simple_video(background_path, final_audio, intermediate_video):
        log("[ERROR] Assembly failed.")
        return False

    # STEP 13: Apply Visual Enhancements
    log("[STEP 13] Applying dark grade, vignette, and sharpening...")
    enhanced_video = apply_visual_enhancements(intermediate_video)

    # STEP 14: Burn Styled Captions
    log("[STEP 14] Burning styled captions (Impact font)...")
    final_video_path = "final_output.mp4"
    if not burn_captions_styled(enhanced_video, srt_path, final_video_path):
        log("[ERROR] Captioning failed.")
        return False

    # STEP 15: Ensure Shorts Duration
    log("[STEP 15] Verifying duration (Max 59s)...")
    final_video_path = ensure_shorts_duration(final_video_path)

    # STEP 16: Upload to YouTube
    log("[STEP 16] Uploading to YouTube with AI disclosure...")
    from core.youtube_uploader import get_authenticated_service, upload_video, add_video_to_playlist, find_or_create_playlist
    youtube_service = get_authenticated_service()
    
    if youtube_service:
        final_desc = fix_description_formatting(content.get('description', ''))
        yt_id = upload_video(
            youtube_service,
            final_video_path,
            title,
            final_desc,
            ["SibbyRespect", "Shorts", "Relatable", "BrainRot", "Roblox"],
            privacy_status="public"
        )

        if yt_id:
            # STEP 17: Post Pinned Comment
            log("[STEP 17] Posting comment-baiting pinned comment...")
            from core.auto_comment import post_pinned_comment
            post_pinned_comment(youtube_service, yt_id, comment_text=content.get("pinned_comment"))
            
            # Logging
            try:
                from core.supabase_db import log_video, update_video_upload
                db_record = log_video(
                    title=title,
                    topic=reddit_post.get('title') if reddit_post else "Daily Rant",
                    script=script,
                    local_path=final_video_path,
                    description=final_desc,
                    tags=[],
                    status='uploaded'
                )
                if db_record: update_video_upload(db_record['id'], yt_id)
            except: pass

    # STEP 18: Cleanup Temp Files
    log("[STEP 18] Cleaning up workspace...")
    cleanup_old_videos(keep=3)
    temp_files = [
        "v_raw.mp3", "v_fast.mp3", "v_sfx.mp3", "v_gameplay.mp3", 
        "v_final_mix.mp3", "v_intermediate.mp4", "final_output.mp4",
        srt_path
    ]
    for f in temp_files:
        if os.path.exists(f): 
            try: os.remove(f)
            except: pass

    log(f"\nSUCCESS! Short created for {CHANNEL_NAME}")
    return True


if __name__ == "__main__":
    create_short()
