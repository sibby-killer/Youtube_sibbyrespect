"""
Auto-Comment Bot — SibbyRespect
Unique AI-generated pinned comments per video.
"""

import random

FALLBACK_COMMENTS = [
    "bro the fact that everyone has lived this exact moment is proof we are all the same person 💀 whats your version",
    "nah cause tell me WHY this is a core memory I tried to forget... drop your story",
    "ok has anyone survived this with their dignity intact... asking for myself",
    "the accuracy is VIOLENT... tell me your version I need to know its not just me 💀",
    "this unlocked a memory I forgot I had... whats the memory this unlocked for you",
    "nah everyone in the comments about to expose themselves... go ahead",
    "ok genuine question has ANYONE not experienced this... prove me wrong",
    "I need to know am I the only one who STILL does this as an adult... be honest 💀",
    "bro we really all grew up in the same simulation huh... drop your proof",
    "the fact that you clicked means you already know EXACTLY what this feels like... spill",
]

def get_comment_text(ai_comment: str = None) -> str:
    if ai_comment and len(ai_comment.strip()) > 10:
        return ai_comment.strip()
    return random.choice(FALLBACK_COMMENTS)

def post_pinned_comment(youtube, video_id: str, comment_text: str = None) -> str | None:
    if not youtube or not video_id:
        return None
    final = get_comment_text(comment_text)
    try:
        resp = youtube.commentThreads().insert(
            part="snippet",
            body={"snippet": {"videoId": video_id, "topLevelComment": {"snippet": {"textOriginal": final}}}}
        ).execute()
        cid = resp["snippet"]["topLevelComment"]["id"]
        youtube.comments().setModerationStatus(id=cid, moderationStatus="published", banAuthor=False).execute()
        print(f"[Comment] Pinned: '{final[:60]}...'")
        return cid
    except Exception as e:
        print(f"[Comment] Error: {e}")
        return None
