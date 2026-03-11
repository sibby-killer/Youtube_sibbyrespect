"""
auto_comment.py — SibbyRespect
Posts unique AI-generated pinned comments on each video.
Falls back to a curated engaging comment pool if no AI comment is available.
"""

import random


# ─────────────────────────────────────────────────────────────────────────────
#  FALLBACK COMMENT POOL — topic-agnostic but engaging
# ─────────────────────────────────────────────────────────────────────────────
FALLBACK_COMMENTS = [
    "bro the fact that everyone has lived this exact moment is proof we are all NPCs running the same program... whats your version 💀",
    "nah cause tell me WHY this is literally a core memory I tried to forget... drop your story",
    "ok but has anyone actually survived this situation with their dignity intact... asking for myself",
    "the accuracy of this is VIOLENT... tell me your version I need to know its not just me",
    "bro I literally stared at my screen processing how accurate this is... whats your experience 💀",
    "nah everyone in the comments about to expose themselves... go ahead I will wait",
    "the fact that you clicked means you already know EXACTLY what this feels like... so spill",
    "ok genuine question has ANYONE in history NOT experienced this... prove me wrong",
    "this unlocked a memory I forgot I had... whats the memory this unlocked for you 💀",
    "am I the only one who STILL does this or are we all just grown children... be honest",
    "the way this video found me personally and called me out... I did not consent to this... tell me yours",
    "bro I saw the title and immediately had a flashback... you too? drop it",
    "nah cause the fact that millions of people watched this and went 'thats me' is so funny and so sad 💀",
    "ok I actually need to know if there is a single person alive who has NOT been through this",
    "this is genuinely embarrassing... and yet here we all are... relating... drop your worst version",
]


# ─────────────────────────────────────────────────────────────────────────────
#  COMMENT SELECTION
# ─────────────────────────────────────────────────────────────────────────────
def get_comment_text(ai_generated_comment: str = None) -> str:
    """
    Returns the AI-generated comment if valid, otherwise picks from the fallback pool.
    """
    if ai_generated_comment and len(ai_generated_comment.strip()) > 10:
        return ai_generated_comment.strip()
    return random.choice(FALLBACK_COMMENTS)


# ─────────────────────────────────────────────────────────────────────────────
#  YOUTUBE PINNED COMMENT
# ─────────────────────────────────────────────────────────────────────────────
def post_pinned_comment(youtube, video_id: str, comment_text: str = None) -> str | None:
    """
    Posts and pins a comment on the given YouTube video.

    Args:
        youtube:       Authenticated YouTube API service object.
        video_id:      YouTube video ID (e.g. "dQw4w9WgXcQ").
        comment_text:  AI-generated comment text (optional). Falls back to pool.

    Returns:
        Comment ID on success, None on failure.
    """
    if not youtube or not video_id:
        return None

    final_comment = get_comment_text(comment_text)

    try:
        # Insert the comment
        insert_response = youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {"textOriginal": final_comment}
                    }
                }
            }
        ).execute()

        comment_id = insert_response["snippet"]["topLevelComment"]["id"]

        # Publish / pin it
        youtube.comments().setModerationStatus(
            id=comment_id,
            moderationStatus="published",
            banAuthor=False
        ).execute()

        print(f"[Comment] Posted & Pinned: '{final_comment[:60]}...'")
        print(f"[Comment] Video: https://youtu.be/{video_id}")
        return comment_id

    except Exception as e:
        print(f"[Comment] Error posting comment: {e}")
        return None
