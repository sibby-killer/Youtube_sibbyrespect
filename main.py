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
from core.video_editor import assemble_simple_video
from tiktok_source import get_background_video, cleanup_old_videos


def create_short(progress_callback=None) -> bool:
    """
    Master function — generates a complete SibbyRespect YouTube Short using the new Reddit + SFX pipeline.
    """
    def log(msg):
        print(msg)
        if progress_callback:
            progress_callback(msg)

    log(f"\n{'='*50}")
    log(f"  SIBBYSRESPECT OVERHAUL PIPELINE STARTING")
    log(f"{'='*50}\n")

    # ── 0. Setup SFX Library ────────────────────────────────────────────────
    log("[0/5] Ensuring SFX library is ready...")
    setup_sfx_library()

    # ── 1. Sourcing & AI ────────────────────────────────────────────────────
    log("[1/5] Sourcing content from Reddit...")
    reddit_post = get_reddit_story()
    
    if reddit_post:
        log(f"  Reddit Post: {reddit_post.get('title')[:60]}...")
    else:
        log("  No Reddit post found, falling back to backup topics.")

    log("  Brainstorming with Gen-Z AI engine...")
    content = generate_video_content(reddit_post=reddit_post)
    if not content:
        log("[ERROR] AI content generation failed.")
        return False

    log(f"  Title: {content.get('title')}")
    script = content.get('script', '')
    word_count = len(script.split())
    log(f"  Script: {word_count} words")

    # ── 2. Voiceover & Audio Enhancement ────────────────────────────────────
    log("\n[2/5] Generating voiceover & processing audio...")
    
    # Generate raw voiceover
    raw_voiceover, srt_path = generate_voiceover(script, filename="v_raw.mp3")
    if not raw_voiceover or not os.path.exists(raw_voiceover):
        log("[ERROR] Voiceover generation failed.")
        return False

    # Speed up (1.12x)
    fast_voiceover = speed_up_audio(raw_voiceover, speed=1.12, output_path="v_fast.mp3")
    
    # Calculate SFX timestamps based on script words
    # Note: We pass the raw script, the SFX manager handles the logic
    # We estimate duration from the sped-up audio
    from pydub import AudioSegment
    voice_audio = AudioSegment.from_file(fast_voiceover)
    duration_ms = len(voice_audio)
    
    sfx_timeline = content.get("sfx_timeline", [])
    sfx_ts = calculate_sfx_timestamps(script, sfx_timeline, duration_ms)
    
    # Overlay SFX
    voice_with_sfx = "v_sfx.mp3"
    overlay_sfx_on_audio(fast_voiceover, sfx_ts, voice_with_sfx)

    # Fetch Background Music
    bg_music = get_background_music()
    log(f"  Music selected: {bg_music}")

    # ── 3. Background Video ──────────────────────────────────────────────────
    log("\n[3/5] Downloading Roblox background from @yellowrobloxreal...")
    background_path = get_background_video()

    if not background_path:
        log("[ERROR] Failed to download background video.")
        return False

    log(f"  Background: {background_path}")

    # Extract gameplay audio from background video
    gameplay_audio = extract_audio_from_video(background_path, "v_gameplay.mp3")

    # ── 4. Final Audio Mix & Video Assembly ──────────────────────────────────
    log("\n[4/5] Mixing final audio layers & assembling video...")
    
    # Final 4-layer mix: Voiceover+SFX, Music, Gameplay
    final_audio = "v_final_mix.mp3"
    mix_final_audio(
        voiceover_path=voice_with_sfx,
        bg_music_path=bg_music,
        gameplay_audio_path=gameplay_audio,
        output_path=final_audio
    )

    # Assembly
    safe_title = re.sub(r'[\\/*?:"<>|#]', "", content.get("title", "video")).strip().replace(" ", "_")
    output_filename = f"{safe_title[:40]}_final.mp4"

    final_video_path = assemble_simple_video(
        bg_video_path=background_path,
        voiceover_path=final_audio,
        output_filename=output_filename,
        srt_path=srt_path
    )

    if not final_video_path:
        log("[ERROR] Video assembly failed.")
        return False

    log(f"\nSUCCESS! Video ready: {final_video_path}")

    # ── 5. Logging & Upload ──────────────────────────────────────────────────
    log("\n[5/5] Finalizing: Uploading and Pining Comment...")
    
    final_desc = fix_description_formatting(content.get('description', ''))
    
    # YouTube Upload
    from core.youtube_uploader import get_authenticated_service, upload_video, add_video_to_playlist, find_or_create_playlist
    youtube_service = get_authenticated_service()
    
    if youtube_service:
        yt_id = upload_video(
            youtube_service,
            final_video_path,
            content.get('title'),
            final_desc,
            ["SibbyRespect", "Shorts", "Relatable", "BrainRot", "Roblox"],
            privacy_status="public"
        )

        if yt_id:
            # Playlist
            from config import YOUTUBE_PLAYLIST_ID
            plist_id = YOUTUBE_PLAYLIST_ID
            if not plist_id:
                plist_id = find_or_create_playlist(youtube_service, f"{CHANNEL_NAME} Shorts", "Daily brain-rot.")
            
            if plist_id:
                add_video_to_playlist(youtube_service, yt_id, plist_id)

            # Pinned Comment
            from core.auto_comment import post_pinned_comment
            post_pinned_comment(youtube_service, yt_id, comment_text=content.get("pinned_comment"))
            
            log(f"Uploaded successfully! ID: {yt_id}")
            
            # Optional: Supabase logging if available
            try:
                from core.supabase_db import log_video, update_video_upload
                db_record = log_video(
                    title=content.get('title'),
                    topic=reddit_post.get('title') if reddit_post else "Daily Rant",
                    script=script,
                    local_path=final_video_path,
                    description=final_desc,
                    tags=[],
                    status='uploaded'
                )
                if db_record:
                    update_video_upload(db_record['id'], yt_id)
            except:
                pass

    # Cleanup
    cleanup_old_videos(keep=3)
    
    # Remove temp audio files
    temp_files = ["v_raw.mp3", "v_fast.mp3", "v_sfx.mp3", "v_gameplay.mp3", "v_final_mix.mp3", "voiceover.mp3"]
    for f in temp_files:
        if os.path.exists(f):
            try: os.remove(f)
            except: pass

    return True


if __name__ == "__main__":
    create_short()
