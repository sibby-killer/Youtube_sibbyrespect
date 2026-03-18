"""
Topic Generator for CatTeaches
Primary: Scrapes Reddit (r/lifehacks, r/UnethicalLifeProTips) for trending posts.
Fallback: 100-topic curated list when Reddit is unreachable.
"""
import os
import random
import logging

log = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
#  REDDIT CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────
REDDIT_SUBREDDITS = [
    "todayilearned",
    "Damnthatsinteresting",
    "MindBlowing",
    "interestingasfuck",
    "science",
    "psychology",
]

# ─────────────────────────────────────────────────────────────────────────────
#  FALLBACK TOPIC LIST  (100 viral psychology / science / facts topics)
# ─────────────────────────────────────────────────────────────────────────────
FALLBACK_TOPICS = [
    # Psychology
    "The Benjamin Franklin Effect: why asking for favors makes people like you",
    "The Dunning-Kruger effect and why dumb people think they're smart",
    "How the anchoring bias controls every price you pay",
    "Why your brain confuses memory and imagination",
    "The bystander effect: why crowds do nothing in emergencies",
    "How mirror neurons make you feel other people's pain",
    "The Zeigarnik effect: why unfinished tasks haunt your mind",
    "The halo effect: why attractive people get treated better",
    "How confirmation bias makes you blind to the truth",
    "The sunk cost fallacy: why you keep watching bad movies",
    "Why humans have a negativity bias and how to fight it",
    "The placebo effect: how belief literally heals your body",
    "How the peak-end rule distorts all your memories",
    "Why loneliness is as deadly as smoking 15 cigarettes a day",
    "How social proof manipulates every decision you make",
    "The Pygmalion effect: how expectations change reality",
    "Why sleep deprivation makes you feel drunk",
    "How dopamine really works and why social media is designed around it",
    "The spotlight effect: why nobody is watching you as much as you think",
    "Why the human brain cannot multitask",
    # Science / Nature
    "How a tardigrade can survive in outer space",
    "Why mantis shrimp can punch with the force of a bullet",
    "The truth about how trees communicate underground",
    "Why octopuses have three hearts and blue blood",
    "How crows hold grudges and recognize human faces",
    "The science behind why music gives you chills",
    "Why your body replaces itself completely every 7 years",
    "How ants build cities more complex than New York",
    "The real reason humans need to dream to survive",
    "Why yawning is contagious even thinking about it",
    "How sharks can detect one drop of blood in a million parts water",
    "Why the deep ocean is more unexplored than outer space",
    "How a single bolt of lightning contains enough energy to power a house for a month",
    "Why honey found in Egyptian tombs is still edible after 3000 years",
    "The science of déjà vu and what your brain is actually doing",
    "How the human nose can detect 1 trillion different smells",
    "Why cold water is actually dangerous after intense exercise",
    "The bizarre truth about how viruses might control human behavior",
    "How some animals can regrow entire limbs",
    "Why cats always land on their feet — the physics explained",
    # History / Society
    "The shocking truth about how little sleep historical humans got",
    "Why ancient Romans used urine as mouthwash",
    "How Napoleon was actually average height for his time",
    "The real reason Cleopatra was more powerful than any pharaoh",
    "How Einstein failed his university entrance exam",
    "Why the Great Wall of China cannot be seen from space",
    "How the Vikings discovered America 500 years before Columbus",
    "The brutal truth about what happens during solitary confinement",
    "Why the Sahara Desert was once a lush green jungle",
    "How medieval peasants actually ate better than people think",
    # Technology / Future
    "How AI can now write better code than most programmers",
    "Why Elon Musk is betting everything on brain-computer interfaces",
    "The truth about how social media algorithms are designed to addict you",
    "How quantum computers will break all encryption in 10 years",
    "Why scientists think we may already be living in a simulation",
    "The dark truth about what companies do with your deleted data",
    "How deepfake technology is already being used to steal identities",
    "Why self-driving cars may be illegal within 5 years",
    "The shocking amount of energy Bitcoin uses every day",
    "How your phone knows you're pregnant before you do",
    # Money / Business
    "The psychological trick casinos use to make you lose more money",
    "Why lottery winners usually go broke within 5 years",
    "How insurance companies use math to always win",
    "The dark reason airlines seat you next to strangers",
    "Why fast food meals are engineered to make you addicted",
    "How credit card companies make money when you pay on time",
    "The truth about how influencer marketing really works",
    "Why most startups fail within the first year and how to avoid it",
    "How Amazon decides what price to show you specifically",
    "The shocking truth about planned obsolescence in electronics",
    # Body / Health
    "Why your appendix is not useless — the truth revealed",
    "How your gut bacteria control your mood and anxiety",
    "The science behind why cold showers are insanely good for you",
    "Why intermittent fasting changes gene expression",
    "How stress physically shrinks your brain over time",
    "The real reason you get a second wind when exhausted",
    "Why humans are the only animals that cry emotional tears",
    "How laughing burns calories and fights disease",
    "The truth about why you get 'beer goggles'",
    "Why spicy food is actually a survival mechanism",
    # Weird / Viral
    "The country where it is illegal to be overweight by law",
    "Why the inventor of the AK-47 regretted creating it",
    "How pigeons were once the fastest way to send messages across oceans",
    "The bizarre reason Finland has the happiest people on Earth",
    "Why Japan has a special word for dying from overwork",
    "How Iceland has virtually eliminated Down syndrome through testing",
    "The US city that is technically in two states at once",
    "Why Dubai bans and arrests people for traffic violations mid-air",
    "How North Korea accidentally created the world's most creative economy",
    "The country where people live the longest and what they eat",
    "Why plants scream in ultrasonic frequencies when under stress",
    "How a single man planted an entire forest by himself over 40 years",
    "The truth behind why GTA V made more money than any Hollywood film",
    "How the Chinese government built an entire city in 3 months",
    "Why UK speed cameras have caught over 10 million drivers in 2024",
]


def _scrape_reddit(limit: int = 20) -> list[str]:
    """
    Fetch hot post titles from the configured subreddits using PRAW.
    Returns a list of topic strings or [] if Reddit creds are unavailable.
    """
    try:
        import praw
        from config import (
            REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
        )
        if not REDDIT_CLIENT_ID:
            return []

        reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT or "CatTeaches/1.0",
            read_only=True,
        )

        topics = []
        per_sub = max(1, limit // len(REDDIT_SUBREDDITS))
        for sub_name in REDDIT_SUBREDDITS:
            try:
                subreddit = reddit.subreddit(sub_name)
                for post in subreddit.hot(limit=per_sub * 3):
                    title = post.title.strip()
                    # Skip TIL prefix, keep the fact
                    if title.startswith("TIL ") or title.startswith("TIL that "):
                        title = title.replace("TIL that ", "").replace("TIL ", "")
                    if len(title) > 20:
                        topics.append(title)
                        if len(topics) >= per_sub:
                            break
            except Exception:
                pass

        return topics[:limit]

    except (ImportError, Exception) as e:
        log.warning(f"Reddit scrape failed ({e}), using fallback topics.")
        return []


def get_next_topic(used_topics: list[str] | None = None) -> str:
    """
    Returns the next topic to use for video generation.
    Priority: Reddit hot posts → fallback list (avoiding already-used topics).
    """
    used = set(t.lower() for t in (used_topics or []))

    # 1. Try Reddit first
    reddit_topics = _scrape_reddit(limit=30)
    fresh = [t for t in reddit_topics if t.lower() not in used]
    if fresh:
        chosen = random.choice(fresh[:10])  # pick from top 10
        print(f"[Topics] Reddit topic selected: {chosen[:60]}...")
        return chosen

    # 2. Fall back to curated list
    available = [t for t in FALLBACK_TOPICS if t.lower() not in used]
    if not available:
        available = FALLBACK_TOPICS  # reset cycle
    chosen = random.choice(available)
    print(f"[Topics] Fallback topic selected: {chosen[:60]}...")
    return chosen


def get_used_topics_from_db() -> list[str]:
    """Fetch topics already logged in Supabase to avoid repeats."""
    try:
        from core.supabase_db import supabase
        if not supabase:
            return []
        result = supabase.table("videos").select("topic").execute()
        return [row["topic"] for row in (result.data or []) if row.get("topic")]
    except Exception as e:
        log.warning(f"Could not fetch used topics from DB: {e}")
        return []


if __name__ == "__main__":
    used = get_used_topics_from_db()
    topic = get_next_topic(used_topics=used)
    print(f"\nNext topic:\n{topic}")
