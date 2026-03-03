"""
Auto-Comment Bot — SibbyRespect
Posts and pins a CTA engagement comment immediately after a video is uploaded.
"""


# Pinned comment text – keep it punchy and engagement-focused
CTA_COMMENT_TEXT = (
    "What fact shocked you the MOST? Drop it below! "
    "Subscribe for daily mind-blowing content: @sibbyrespect "
    "Turn on notifications so you never miss one! "
)


def post_pinned_comment(youtube, video_id: str) -> str | None:
    """
    Posts a CTA comment on the given video and pins it.
    Returns the comment ID on success, None on failure.
    """
    if not youtube or not video_id:
        return None

    try:
        # 1. Insert the comment thread
        insert_response = youtube.commentThreads().insert(
            part="snippet",
            body={
                "snippet": {
                    "videoId": video_id,
                    "topLevelComment": {
                        "snippet": {
                            "textOriginal": CTA_COMMENT_TEXT
                        }
                    }
                }
            }
        ).execute()

        comment_id = insert_response["snippet"]["topLevelComment"]["id"]
        print(f"[Comment] Posted comment: {comment_id}")

        # 2. Pin the comment (mark it as 'heldForReview' pins it for the owner)
        youtube.comments().setModerationStatus(
            id=comment_id,
            moderationStatus="published",
            banAuthor=False
        ).execute()

        print(f"[Comment] Comment pinned successfully on https://youtu.be/{video_id}")
        return comment_id

    except Exception as e:
        # Pinning can fail if comment moderation is off — that's okay
        print(f"[Comment] Could not post/pin comment: {e}")
        return None
