"""
Reddit Content Source — SibbyRespect
Scrapes relatable stories from Reddit using public JSON endpoint.
No API key required. No authentication needed.
"""

import os
import json
import random
import time
import requests

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
USED_REDDIT_POSTS_FILE = "used_reddit_posts.json"
MIN_SCORE = 500  # Minimum upvotes — only proven relatable content
MAX_POST_LENGTH = 2000  # Skip essays
MIN_POST_LENGTH = 30  # Skip empty posts
REQUEST_DELAY = 2  # Seconds between subreddit requests (rate limiting)

# User agent is REQUIRED by Reddit — they block requests without one
# Using a modern browser profile to bypass bot detection (403 errors)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Cache-Control": "max-age=0",
}

# ─────────────────────────────────────────────────────────────────────────────
#  SUBREDDIT SOURCES — EDUCATIONAL & HACKS (CATTEACHES ERA)
# ─────────────────────────────────────────────────────────────────────────────
SUBREDDIT_SOURCES = {
    "hacks": [
        {"sub": "lifehacks", "sort": "top", "time": "week"},
        {"sub": "QuickTips", "sort": "top", "time": "week"},
        {"sub": "learnuselesstalents", "sort": "top", "time": "month"},
        {"sub": "todayilearned", "sort": "top", "time": "week"},
        {"sub": "PsychologyInRealLife", "sort": "top", "time": "month"},
    ],
    "math_logic": [
        {"sub": "math", "sort": "top", "time": "month"},
        {"sub": "puzzles", "sort": "top", "time": "week"},
        {"sub": "riddles", "sort": "top", "time": "week"},
        {"sub": "LogicPuzzles", "sort": "top", "time": "month"},
    ],
    "unethical": [
        {"sub": "UnethicalLifeProTips", "sort": "top", "time": "week"},
    ],
}

# ─────────────────────────────────────────────────────────────────────────────
#  TRACKING — Prevent reusing same Reddit posts
# ─────────────────────────────────────────────────────────────────────────────
def load_used_reddit_posts() -> list:
    """Loads list of already-used Reddit post IDs."""
    if os.path.exists(USED_REDDIT_POSTS_FILE):
        with open(USED_REDDIT_POSTS_FILE, "r") as f:
            return json.load(f)
    return []

def save_used_reddit_post(post_data: dict):
    """Marks a Reddit post as used."""
    used = load_used_reddit_posts()
    used.append({
        "id": post_data.get("id", ""),
        "subreddit": post_data.get("subreddit", ""),
        "title": post_data.get("title", "")[:100],
        "score": post_data.get("score", 0),
        "used_date": time.strftime("%Y-%m-%d"),
    })
    with open(USED_REDDIT_POSTS_FILE, "w") as f:
        json.dump(used, f, indent=2)

def reset_used_reddit_posts():
    """Resets the used posts tracker."""
    with open(USED_REDDIT_POSTS_FILE, "w") as f:
        json.dump([], f)

# ─────────────────────────────────────────────────────────────────────────────
#  REDDIT FETCHER — Public JSON endpoint
# ─────────────────────────────────────────────────────────────────────────────
def fetch_subreddit_posts(subreddit: str, sort: str = "top", time_filter: str = "week", limit: int = 25) -> list:
    """
    Fetches posts from a subreddit using Reddit's public JSON endpoint.
    No API key needed. No authentication needed.
    """
    url = f"https://www.reddit.com/r/{subreddit}/{sort}.json"
    params = {
        "t": time_filter,
        "limit": limit,
    }

    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=15)

        if response.status_code == 200:
            data = response.json()
            posts = []

            for child in data.get("data", {}).get("children", []):
                post = child.get("data", {})
                posts.append({
                    "id": post.get("id", ""),
                    "title": post.get("title", ""),
                    "selftext": post.get("selftext", ""),
                    "score": post.get("score", 0),
                    "num_comments": post.get("num_comments", 0),
                    "subreddit": post.get("subreddit", ""),
                    "permalink": post.get("permalink", ""),
                    "url": f"https://reddit.com{post.get('permalink', '')}",
                    "over_18": post.get("over_18", False),
                    "is_self": post.get("is_self", True),
                })

            return posts

        elif response.status_code == 429:
            print(f"[Reddit] Rate limited on r/{subreddit}. Waiting 10 seconds...")
            time.sleep(10)
            return fetch_subreddit_posts(subreddit, sort, time_filter, limit)

        else:
            print(f"[Reddit] Error {response.status_code} on r/{subreddit}")
            return []

    except requests.exceptions.Timeout:
        print(f"[Reddit] Timeout on r/{subreddit}")
        return []
    except Exception as e:
        print(f"[Reddit] Error fetching r/{subreddit}: {e}")
        return []

# ─────────────────────────────────────────────────────────────────────────────
#  CONTENT FILTER — Only quality relatable content
# ─────────────────────────────────────────────────────────────────────────────
# Words that indicate content we should SKIP
SKIP_KEYWORDS = [
    "politics", "election", "trump", "biden", "democrat", "republican",
    "suicide", "self-harm", "abuse", "assault", "rape",
    "racist", "racism", "homophobic",
    "nsfw", "porn", "sex",
    "death", "died", "funeral", "cancer",
    "gun", "shooting", "murder",
    "divorce", "custody",
    "religion", "church", "god", "bible",
    "crypto", "bitcoin", "stock",
    "sponsor", "advertisement", "promotion",
]

def is_safe_content(post: dict) -> bool:
    """Checks if a Reddit post is safe and appropriate for our channel."""
    if post.get("over_18", False):
        return False

    content = (post.get("title", "") + " " + post.get("selftext", "")).lower()

    for keyword in SKIP_KEYWORDS:
        if keyword in content:
            return False

    return True

def is_good_content(post: dict) -> bool:
    """Checks if a Reddit post meets our quality criteria."""
    # Must have minimum upvotes
    if post.get("score", 0) < MIN_SCORE:
        return False

    # Combine title and body
    content = post.get("title", "")
    if post.get("selftext"):
        content += " " + post["selftext"]

    # Must not be too long (hard to condense)
    if len(content) > MAX_POST_LENGTH:
        return False

    # Must not be too short (not enough material)
    if len(content) < MIN_POST_LENGTH:
        return False

    # Must be safe
    if not is_safe_content(post):
        return False

    # Must not be just a link post (we need text content)
    if not post.get("is_self", True) and not post.get("selftext"):
        # Check if title alone is enough
        if len(post.get("title", "")) < 50:
            return False

    return True

# ─────────────────────────────────────────────────────────────────────────────
#  MAIN FUNCTION — Get a relatable story from Reddit
# ─────────────────────────────────────────────────────────────────────────────
def get_reddit_story(content_type: str = None) -> dict | None:
    """
    Gets ONE relatable story from Reddit.
    Checks multiple subreddits, filters for quality, avoids already-used posts.

    Args:
        content_type: "brain_rot", "commentary", "stories", or None (random)

    Returns:
        Dict with post data, or None if nothing found
    """
    used_posts = load_used_reddit_posts()
    used_ids = [p.get("id", "") for p in used_posts]

    # Decide which subreddits to check
    if content_type and content_type in SUBREDDIT_SOURCES:
        sources = SUBREDDIT_SOURCES[content_type]
    else:
        # Random mix — weighted toward hacks (60%), math_logic (25%), unethical (15%)
        all_sources = []
        all_sources.extend(SUBREDDIT_SOURCES["hacks"] * 3)  # 3x weight
        all_sources.extend(SUBREDDIT_SOURCES["math_logic"] * 2)  # 2x weight
        all_sources.extend(SUBREDDIT_SOURCES["unethical"])  # 1x weight
        random.shuffle(all_sources)
        sources = all_sources[:6]  # Check up to 6 subreddits

    all_candidates = []

    for source in sources:
        sub = source["sub"]
        print(f"[Reddit] Checking r/{sub}...")

        posts = fetch_subreddit_posts(sub, source["sort"], source["time"])

        for post in posts:
            if post["id"] in used_ids:
                continue
            if not is_good_content(post):
                continue

            all_candidates.append(post)

        # Rate limiting between requests
        time.sleep(REQUEST_DELAY)

    if all_candidates:
        # Sort by score descending
        all_candidates.sort(key=lambda x: x.get("score", 0), reverse=True)

        # Pick randomly from top 10 (variety)
        top_picks = all_candidates[:min(10, len(all_candidates))]
        chosen = random.choice(top_picks)

        # Prepare the content
        content = chosen.get("title", "")
        if chosen.get("selftext"):
            content += "\n\n" + chosen["selftext"]

        chosen["full_content"] = content

        # Mark as used
        save_used_reddit_post(chosen)

        print(f"[Reddit] Selected: '{chosen['title'][:60]}...' "
              f"(r/{chosen['subreddit']}, {chosen['score']} upvotes)")

        return chosen

    print("[Reddit] No suitable posts found across all subreddits")
    return None

def get_reddit_status() -> dict:
    """Returns stats about Reddit content sourcing."""
    used = load_used_reddit_posts()
    return {
        "total_used": len(used),
        "subreddits_configured": sum(len(v) for v in SUBREDDIT_SOURCES.values()),
    }

# ─────────────────────────────────────────────────────────────────────────────
#  TEST
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("[Test] Fetching relatable story from Reddit...")
    story = get_reddit_story()
    if story:
        print(f"\nTitle: {story['title']}")
        print(f"Subreddit: r/{story['subreddit']}")
        print(f"Score: {story['score']}")
        print(f"Content: {story['full_content'][:200]}...")
    else:
        print("[Test] No stories found")
