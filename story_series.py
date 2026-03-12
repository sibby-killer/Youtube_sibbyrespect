"""
Story Series Manager — SibbyRespect
Handles splitting long Reddit stories into Part 1, Part 2, Part 3...
Saves remaining parts for future uploads.
"""

import os
import json
import re

SERIES_FILE = "pending_series.json"
MIN_WORDS_FOR_SERIES = 300  # Stories over 300 words get split
WORDS_PER_PART = 180  # Each part covers ~180 words of the original story


def load_pending_series() -> list:
    """Loads pending story parts waiting to be uploaded."""
    if os.path.exists(SERIES_FILE):
        try:
            with open(SERIES_FILE, "r") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except:
            return []
    return []


def save_pending_series(series: list):
    """Saves pending series parts."""
    with open(SERIES_FILE, "w") as f:
        json.dump(series, f, indent=2)


def has_pending_parts() -> bool:
    """Checks if there are story parts waiting to be uploaded."""
    pending = load_pending_series()
    return len(pending) > 0


def get_next_pending_part() -> dict | None:
    """Gets the next pending story part and removes it from the queue."""
    pending = load_pending_series()
    if not pending:
        return None
    
    next_part = pending.pop(0)
    save_pending_series(pending)
    
    print(f"[Series] Loaded Part {next_part.get('part_number', '?')} of '{next_part.get('series_title', 'Unknown')}'")
    return next_part


def split_story_into_series(reddit_post: dict) -> list:
    """
    Splits a long Reddit story into multiple parts.
    Each part has enough content for one 45-60 second video.
    
    Returns list of part dicts, each containing:
    - series_title: The overall story title
    - part_number: 1, 2, 3, etc.
    - total_parts: Total number of parts
    - content: The story content for this part
    - reddit_source: Original Reddit info
    - is_series: True
    """
    title = reddit_post.get("title", "")
    selftext = reddit_post.get("selftext", "")
    full_content = f"{title} {selftext}".strip()
    
    word_count = len(full_content.split())
    
    # Not long enough for series — return as single part
    if word_count < MIN_WORDS_FOR_SERIES:
        return [{
            "series_title": title,
            "part_number": 1,
            "total_parts": 1,
            "content": full_content,
            "reddit_source": {
                "subreddit": reddit_post.get("subreddit", ""),
                "score": reddit_post.get("score", 0),
                "title": title,
            },
            "is_series": False,
        }]
    
    # Split into parts
    # Split by sentences first for natural breaks
    sentences = re.split(r'(?<=[.!?])\s+', full_content)
    
    parts_content = []
    current_part = []
    current_word_count = 0
    
    for sentence in sentences:
        sentence_words = len(sentence.split())
        
        if current_word_count + sentence_words > WORDS_PER_PART and current_part:
            # Save current part
            parts_content.append(" ".join(current_part))
            current_part = [sentence]
            current_word_count = sentence_words
        else:
            current_part.append(sentence)
            current_word_count += sentence_words
    
    # Add the last part
    if current_part:
        # If last part is too short, merge with previous if possible
        if len(parts_content) > 0 and current_word_count < 50:
            parts_content[-1] += " " + " ".join(current_part)
        else:
            parts_content.append(" ".join(current_part))
    
    total_parts = len(parts_content)
    series_title = title if title else "Untitled Story"
    
    print(f"[Series] Split '{series_title[:40]}...' into {total_parts} parts ({word_count} words)")
    
    result = []
    for i, content in enumerate(parts_content, 1):
        result.append({
            "series_title": series_title,
            "part_number": i,
            "total_parts": total_parts,
            "content": content,
            "reddit_source": {
                "subreddit": reddit_post.get("subreddit", ""),
                "score": reddit_post.get("score", 0),
                "title": title,
            },
            "is_series": True,
        })
    
    return result


def process_reddit_story(reddit_post: dict) -> dict:
    """
    Main function: Takes a Reddit post and returns the NEXT part to create.
    If the story is long, saves remaining parts for future uploads.
    """
    # First check if we have pending parts
    if has_pending_parts():
        return get_next_pending_part()
    
    # Split new story
    parts = split_story_into_series(reddit_post)
    
    # Return first part, save rest for later
    first_part = parts[0]
    
    if len(parts) > 1:
        remaining = parts[1:]
        save_pending_series(remaining)
        print(f"[Series] Saved {len(remaining)} remaining parts for future uploads")
    
    return first_part
