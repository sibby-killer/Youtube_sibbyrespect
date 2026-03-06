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

from core.ai_script import generate_video_content, CHANNEL_NAME
from core.tts import generate_voiceover
from core.yt_scraper import download_viral_b_roll
from core.video_editor import stitch_video


def create_short(topic: str = None, progress_callback=None) -> bool:
    """
    Master function — generates a complete YouTube Short from a single topic.
    If topic is None, picks one automatically from Reddit or the fallback list.
    """
    def log(msg):
        print(msg)
        if progress_callback:
            progress_callback(msg)

    # Auto-pick topic if not supplied
    if not topic:
        from core.topic_generator import get_next_topic, get_used_topics_from_db
        used = get_used_topics_from_db()
        topic = get_next_topic(used_topics=used)

    log(f"\n===========================================")
    log(f"  AUTO-VIDEO: {topic[:60]}")
    log(f"===========================================\n")

    # ── 1. Generate Script & Metadata ──────────────────────────────────────
    log("[1/5] Brainstorming with Groq...")
    content = generate_video_content(topic)
    if not content:
        log("Failed to generate content. Exiting.")
        return False

    log(f"  Title   : {content.get('title')}")
    log(f"  Keywords: {content.get('b_roll_keywords')}")

    # ── 2. Generate Voiceover ───────────────────────────────────────────────
    log("\n[2/5] Recording Voiceover with Edge-TTS...")
    audio_path, srt_path = generate_voiceover(content.get('script'), filename="voiceover.mp3")

    # ---------------------------------------------------------
    # 3. Download B-Roll
    # ---------------------------------------------------------
    log("\n[3/5] Downloading Viral B-Roll with yt-dlp...")
    from core.yt_scraper import download_viral_b_roll
    keywords = content.get('b_roll_keywords', [])
    broll_paths, credits = download_viral_b_roll(keywords, clips_per_keyword=2, progress_callback=progress_callback)

    if not broll_paths:
        log("Failed to download B-roll. Exiting.")
        return False

    # ── 4. Assemble Video ──────────────────────────────────────────────────
    log("\n[4/5] Assembling Final MP4...")
    safe_title = re.sub(r'[\\/*?:"<>|#]', "", content.get("title", "video")).strip().replace(" ", "_")
    output_filename = f"{safe_title[:40]}_final.mp4"

    final_video_path = stitch_video(
        audio_path, broll_paths,
        output_filename=output_filename,
        srt_path=srt_path
    )

    if not final_video_path:
        log("\nFAILED to assemble video.")
        return False

    log(f"\nSUCCESS! Video ready: {final_video_path}")

    # Build full SEO description
    credits_text = "Background Video Credits:\n" + "\n".join([f"  {c}" for c in credits])
    final_desc = content.get('description', '')
    if "[CREDITS_HERE]" in final_desc:
        final_desc = final_desc.replace("[CREDITS_HERE]", credits_text)
    else:
        final_desc += f"\n\n{credits_text}"

    # Save metadata backup
    meta_path = final_video_path.replace(".mp4", "_metadata.txt")
    with open(meta_path, "w", encoding="utf-8") as f:
        f.write(f"Title: {content.get('title')}\n\nDescription:\n{final_desc}\n")

    # ── 5. Supabase Logging ────────────────────────────────────────────────
    log("\n[5/5] Logging to Supabase & Uploading to YouTube...")
    from core.supabase_db import log_video, update_video_upload
    db_record = log_video(
        title=content.get('title', ''),
        topic=topic,
        script=content.get('script', ''),
        local_path=final_video_path,
        description=final_desc,
        tags=keywords,
        status='generated'
    )

    # ── 6. YouTube Upload ──────────────────────────────────────────────────
    from core.youtube_uploader import get_authenticated_service, upload_video, find_or_create_playlist, add_video_to_playlist
    youtube_service = get_authenticated_service()
    if youtube_service:
        video_tags = keywords + ["SibbyRespect", "Shorts", "Facts", "USA", "UK"]
        yt_id = upload_video(
            youtube_service,
            final_video_path,
            content.get('title'),
            final_desc,
            video_tags,
            privacy_status="public"
        )
        if yt_id:
            if db_record:
                update_video_upload(db_record.get('id'), yt_id)
            
            # --- PLAYLIST INTEGRATION ---
            from config import YOUTUBE_PLAYLIST_ID
            plist_id = YOUTUBE_PLAYLIST_ID
            if not plist_id:
                # Automate playlist creation if not set
                plist_title = f"{CHANNEL_NAME} - Shocking Facts & Viral Stories"
                plist_desc  = (
                    f"The ultimate collection of mind-blowing facts and viral stories from {CHANNEL_NAME}. "
                    "New shorts uploaded 4 times every single day! #Facts #Shorts #Viral"
                )
                plist_id = find_or_create_playlist(youtube_service, plist_title, plist_desc)
            
            if plist_id:
                add_video_to_playlist(youtube_service, yt_id, plist_id)
            
            # Post pinned comment
            from core.auto_comment import post_pinned_comment
            post_pinned_comment(youtube_service, yt_id)
            log(f"Successfully uploaded to YouTube! ID: {yt_id}")
    else:
        log("[Upload] YouTube auth not available — video saved locally only.")

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SibbyRespect Video Generator")
    parser.add_argument("--topic", type=str, default=None,
                        help="Override topic (auto-picked from Reddit if omitted)")
    args = parser.parse_args()
    create_short(topic=args.topic)
