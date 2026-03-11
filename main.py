import os
import re
import argparse
from dotenv import load_dotenv

load_dotenv()

# --- MONKEY PATCH FOR MOVIEPY PIL DEPENDENCY (Pillow >= 10) ---
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.Resampling.LANCZOS
# --------------------------------------------------------------

from core.ai_content import (
    generate_video_content, fix_description_formatting,
    CHANNEL_NAME, get_next_topic
)
from core.tts import generate_voiceover
from core.video_editor import assemble_simple_video
from tiktok_source import get_background_video, cleanup_old_videos


def create_short(topic: str = None, progress_callback=None) -> bool:
    """
    Master function — generates a complete SibbyRespect YouTube Short.
    Pipeline:
      1. Generate script + metadata (ai_content)
      2. Generate voiceover (TTS)
      3. Download ONE Roblox background video from @yellowrobloxreal
      4. Assemble: single background + voiceover (loop/trim as needed)
      5. Log to Supabase
      6. Upload to YouTube + post pinned comment
    """
    def log(msg):
        print(msg)
        if progress_callback:
            progress_callback(msg)

    # ── Auto-pick topic if not supplied ─────────────────────────────────────
    if not topic:
        topic = get_next_topic()

    log(f"\n==========================================")
    log(f"  AUTO-VIDEO: {topic[:60]}")
    log(f"==========================================\n")

    # ── 1. Generate Script & Metadata ────────────────────────────────────────
    log("[1/5] Brainstorming with Groq...")
    content = generate_video_content(topic)
    if not content:
        log("[ERROR] Failed to generate content. Exiting.")
        return False

    log(f"  Title: {content.get('title')}")
    log(f"  Topic: {content.get('topic_used')}")
    word_count = len(content.get('script', '').split())
    log(f"  Script: {word_count} words")

    # ── 2. Generate Voiceover ────────────────────────────────────────────────
    log("\n[2/5] Recording Voiceover with Edge-TTS...")
    audio_path, srt_path = generate_voiceover(
        content.get('script'), filename="voiceover.mp3"
    )

    if not audio_path or not os.path.exists(audio_path):
        log("[ERROR] Voiceover generation failed. Exiting.")
        return False

    # ── 3. Download Roblox Background from @yellowrobloxreal ─────────────────
    log("\n[3/5] Downloading Roblox background from @yellowrobloxreal...")
    background_path = get_background_video()

    if not background_path:
        log("[ERROR] Failed to download background video. Exiting.")
        return False

    log(f"  Background: {background_path}")

    # ── 4. Assemble Video ────────────────────────────────────────────────────
    log("\n[4/5] Assembling final video...")
    safe_title = re.sub(r'[\\/*?:"<>|#]', "", content.get("title", "video")).strip().replace(" ", "_")
    output_filename = f"{safe_title[:40]}_final.mp4"

    final_video_path = assemble_simple_video(
        bg_video_path=background_path,
        voiceover_path=audio_path,
        output_filename=output_filename,
        srt_path=srt_path
    )

    if not final_video_path:
        log("\n[ERROR] Failed to assemble video. Exiting.")
        return False

    log(f"\nSUCCESS! Video ready: {final_video_path}")

    # ── Description Processing ───────────────────────────────────────────────
    # Fix formatting safety net (ensures proper newlines from AI)
    raw_desc   = content.get('description', '')
    final_desc = fix_description_formatting(raw_desc)

    # Save metadata backup
    meta_path = final_video_path.replace(".mp4", "_metadata.txt")
    with open(meta_path, "w", encoding="utf-8") as f:
        f.write(f"Title: {content.get('title')}\n\nDescription:\n{final_desc}\n")

    # ── 5. Supabase Logging ──────────────────────────────────────────────────
    log("\n[5/5] Logging to Supabase & Uploading to YouTube...")
    try:
        from core.supabase_db import log_video, update_video_upload
        db_record = log_video(
            title=content.get('title', ''),
            topic=topic,
            script=content.get('script', ''),
            local_path=final_video_path,
            description=final_desc,
            tags=[],           # no Pexels keywords needed
            status='generated'
        )
    except Exception as e:
        log(f"[Supabase] Logging failed (non-critical): {e}")
        db_record = None

    # ── 6. YouTube Upload ────────────────────────────────────────────────────
    from core.youtube_uploader import get_authenticated_service, upload_video, find_or_create_playlist, add_video_to_playlist

    youtube_service = get_authenticated_service()
    if youtube_service:
        yt_id = upload_video(
            youtube_service,
            final_video_path,
            content.get('title'),
            final_desc,
            ["SibbyRespect", "Shorts", "Relatable", "BrainRot", "GenZ", "Funny", "Viral"],
            privacy_status="public"
        )

        if yt_id:
            # Update Supabase record
            if db_record:
                try:
                    from core.supabase_db import update_video_upload
                    update_video_upload(db_record.get('id'), yt_id)
                except Exception:
                    pass

            # Playlist management
            from config import YOUTUBE_PLAYLIST_ID
            plist_id = YOUTUBE_PLAYLIST_ID
            if not plist_id:
                plist_title = f"{CHANNEL_NAME} — Brain-Rot Shorts"
                plist_desc  = f"Daily relatable brain-rot shorts from {CHANNEL_NAME}. #BrainRot #Relatable #Shorts"
                plist_id    = find_or_create_playlist(youtube_service, plist_title, plist_desc)

            if plist_id:
                add_video_to_playlist(youtube_service, yt_id, plist_id)

            # Post AI-generated pinned comment (falls back to pool if missing)
            from core.auto_comment import post_pinned_comment
            pinned_comment = content.get("pinned_comment", None)
            post_pinned_comment(youtube_service, yt_id, comment_text=pinned_comment)

            log(f"Successfully uploaded to YouTube! ID: {yt_id}")
    else:
        log("[Upload] YouTube auth not available — video saved locally only.")

    # ── Cleanup old background videos from disk ──────────────────────────────
    cleanup_old_videos(keep_latest=3)

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SibbyRespect Video Generator")
    parser.add_argument("--topic", type=str, default=None,
                        help="Override topic (auto-picked from topic list if omitted)")
    args = parser.parse_args()
    create_short(topic=args.topic)
