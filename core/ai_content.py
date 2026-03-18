import os
import json
import random
import re
from groq import Groq
from config import GROQ_API_KEY
from sfx_cleaner import get_available_sfx_names

if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
else:
    client = None

# ─────────────────────────────────────────────────────────────────────────────
#  CHANNEL IDENTITY — CATTEACHES (2026 OVERHAUL)
# ─────────────────────────────────────────────────────────────────────────────
CHANNEL_NAME = "CatTeaches"
CHANNEL_SLOGAN = "Making learning interesting with... Cats! (Cat emoji)"
CHANNEL_URL = "https://www.youtube.com/@catteaches" # Placeholder
HANDLE = "@catteaches"
BG_SOURCE = "Satisfying ASMR (multi-source)"
SUBSCRIBE_LINE = f"follow the cat or stay a brokeboy 👉 {HANDLE}"

BASE_HASHTAGS = (
    "#CatTeaches #LifeHacks #MathTricks #Satire #HustleCulture "
    "#ASMR #Satisfying #LogicPuzzles #GenZ #Hacks #Viral #Shorts "
    "#SmartCat #Brainy #SuccessMindset #DailyHacks"
)

PRIMARY_MODEL = "llama-3.3-70b-versatile"
FALLBACK_MODEL = "llama-3.1-70b-versatile"

# SFX list is now dynamically fetched
def get_sfx_list_for_ai() -> str:
    """Gets formatted SFX list for the AI system prompt."""
    names = get_available_sfx_names()
    if names:
        return ", ".join(names)
    # Fallback if manifest not ready
    return "door_creak, heartbeat, dramatic_bass_drop, angelic_choir, record_scratch, sad_violin, thunder, glass_shatter, whoosh, cricket_silence"

# ─────────────────────────────────────────────────────────────────────────────
#  BACKUP TOPICS (used when Reddit fails)
# ─────────────────────────────────────────────────────────────────────────────
USED_TOPICS_FILE = "used_topics.json"

def load_used_topics() -> list:
    if os.path.exists(USED_TOPICS_FILE):
        with open(USED_TOPICS_FILE, "r") as f:
            return json.load(f)
    return []

def save_used_topic(topic: str):
    used = load_used_topics()
    used.append(topic)
    with open(USED_TOPICS_FILE, "w") as f:
        json.dump(used, f, indent=2)

BACKUP_TOPICS = [
    "Unethical ways to make money: reselling free samples as exclusive merch",
    "How to multiply any 2-digit number by 11 in 2 seconds",
    "The 'Missing Dollar' riddle that breaks 99% of brains",
    "Charging tourists to 'pet the local cat' (Spoiler: you're the cat)",
    "Using a hi-vis vest and a ladder to enter any building for free",
    "How to get a free hotel breakfast without being a guest",
    "The math trick to calculate percentages in your head instantly",
    "Why you should never trust a 'free' lost flash drive",
    "How to win any argument by agreeing with them until they look stupid",
    "The 'Premium Meow Alert' tax for your neighbors",
    "Selling 'Influencer Oxygen' in jars for 500% profit",
    "How to square any number ending in 5 instantly",
    "The secret to getting a free upgrade on any flight",
    "Why 0.999 repeating is actually equal to 1",
    "The 'Coat Rack' hack to never lose your seat at a bar",
    "How to know if someone is lying by watching their left ear",
    "Using 'Airplane Mode' to disconnect from a call without hanging up",
    "The 'Fake Wallet' strategy to avoid being mugged in style",
    "How to multiply 9s using only your fingers",
    "The logic puzzle of the three gods: Truth, False, and Chaos",
    "How to get free water at any vending machine",
    "The 'Student ID' hack that works even after you graduate",
    "Why you should always carry a clipboard to look busy",
    "How to solve the Monty Hall problem like a genius",
    "The 'Birthday Paradox': Why 23 people is enough for a match",
    "How to read a book in 20 minutes using the 'Z-pattern'",
    "The 'Psychology of Choice' hack to get what you want",
    "How to remember anyone's name using the 'Association' trick",
    "The 'Caffeine Nap' strategy for maximum productivity",
    "Why you should never buy the cheapest or most expensive wine",
    "How to tell if a diamond is real using only your breath",
    "The 'Empty Seat' hack for crowded trains",
    "How to turn a 1-dollar bill into a 'collectible' item",
    "The 'Mirroring' technique to make anyone trust you",
    "How to get a free dessert at any restaurant by acting like it's your birthday",
    "The 'Lost and Found' hack for phone chargers",
    "Simple trick to calculate tips in 1 second",
    "How to use a 'Ghost' wallet for crypto satire",
    "The 'Banana' self-checkout trick (Satire/Niche)",
    "Why you should always walk with purpose to avoid questions",
    "How to open a locked door with a credit card (Movie vs Reality)",
    "The 'Parking Cone' strategy for free city parking",
    "How to make 'Premium Dirt' and sell it as organic fertilizer",
    "Why the house always wins: Simple probability lesson",
    "The 'Handshake' hack to assert dominance instantly",
    "How to get out of a ticket by knowing one specific law",
    "The 'Wait 24 hours' rule to stop impulse buying",
    "How to spot a fake 'Limited Time Offer'",
    "The 'Social Proof' hack to get a table at a full restaurant",
    "How to calculate the day of the week for any date in your head",
] # More to be added programmatically or in a separate file

# ─────────────────────────────────────────────────────────────────────────────
#  MASTER SYSTEM PROMPT
# ─────────────────────────────────────────────────────────────────────────────
def get_system_prompt() -> str:
    """Builds the system prompt for CatTeaches (Satirical/Educational Persona)."""
    sfx_list = get_sfx_list_for_ai()
    
    prompt = f"""
You are the sharp, cynical, and highly intelligent mind behind the YouTube channel "{CHANNEL_NAME}" ({HANDLE}).
You take "life hacks," "math tricks," and "logic puzzles" and transform them into viral satirical/educational YouTube Shorts scripts.
The scripts play over satisfying ASMR footage (kinetic sand, soap cutting, factory loops) in the background.
Your scripts are 170-210 words and will be read at 1.12x speed resulting in 48-58 second videos.

=== YOUR IDENTITY ===
You are "CatTeaches" - a cat who has lived 9 lives and seen everything. 
You are smarter than the viewer, and you know it. You speak with a sense of "Street Smart Satire."
You aren't just teaching a hack; you're teaching a "violation."
You sound like a high-level hustler who just happened to be born a cat.
Your voice is confident, fast-paced, and uses Gen-Z slang naturally but intelligently.
You are slightly arrogant ("bro it's actually embarrassing that you didn't know this") but surprisingly helpful.

=== CONTENT TYPE: THE "DOGGIE" STYLE SATIRE ===
Follow the satirical "Doggieteaches" formula for all hacks:
1.  **The Hook**: Immediate, aggressive, and catchy. (e.g., "Unethical ways to make money part 12... stop being a brokeboy.")
2.  **The Setup**: "First, you'll need a loyal accomplice and zero morals."
3.  **The Steps**: Break it down into Step 1, Step 2, and maybe a "Bonus Move."
4.  **The Twist**: End with a cynical or absurd punchline that makes people comment.

=== SCRIPT STRUCTURE (4-PART FRAMEWORK) ===

PART 1 - THE HOOK (First 2-3 seconds):
- "Unethical ways to make money part [X]... listen up."
- "This math trick will make your teacher question their entire degree."
- "If you're still [doing something common], you're literally living in a simulation."
- "Pov: you just realized [thing] was a scam all along."

PART 2 - THE PREP / SETUP (10-15 seconds):
- Use character names like 'Sarah from accounting' or 'Devon from the block' to add realism.
- Set the scene: "So you're at the airport and some guy named Marcus is taking the last charger..."
- Explain the 'Requirement': "First, grab a hi-vis vest and a ladder, no cap."

PART 3 - THE EXECUTION (20-35 seconds):
- Step 1: [Aggressive Action]
- Step 2: [The Clever Part]
- Step 3: [The Payout]
- Use "..." for pauses and dramatic effect.
- Layer the "hustle" logic: "At this point, you're not just a student, you're the CEO of the hallway."

PART 4 - THE TWIST + CAT CTA (8-12 seconds):
- THE TWIST: A final cynical realization or a "cat" themed punchline. 
- THE CTA: Never say "subscribe." Instead:
    - "If you're still here, your cat is probably smarter than you. Follow for the next violation."
    - "Nah cause if you didn't know this... we're not even on the same level. See you tomorrow."
    - "Bro if you nodded once, you're officially one of the elite. Don't miss part 15."

=== SOUND EFFECTS ===
Use 3-5 SFX per script from this list: {sfx_list}
Common triggers: "Step 1", "The payout", "Bro", "Wait for it".

=== TONE AND LANGUAGE ===
- SLANG: bro, nah, deadass, brokeboy, hustle, valid, no cap.
- NO section labels in output.
- One continuous natural rant/lesson.
- WORD COUNT IS CRITICAL: 180-210 words exactly.
"""
    return prompt

# ─────────────────────────────────────────────────────────────────────────────
#  CONTENT GENERATION — From Reddit or Backup Topic
# ─────────────────────────────────────────────────────────────────────────────
def generate_video_content(reddit_post: dict = None, backup_topic: str = None) -> dict | None:
    """
    Generates complete video content from Reddit post or backup topic.
    Returns dict with script, sfx_timeline, title, description, comment.
    """
    if not client:
        print("Error: GROQ_API_KEY not set.")
        return None

    # Build the content source for the AI
    if reddit_post:
        if reddit_post.get("is_series"):
            part_num = reddit_post.get("part_number", 1)
            total = reddit_post.get("total_parts", 1)
            series_title = reddit_post.get("series_title", "")
            
            source_text = f"SERIES: Part {part_num} of {total}\n"
            source_text += f"Overall Story: {series_title}\n"
            source_text += f"This Part's Content: {reddit_post.get('content', '')}\n\n"
            
            if part_num == 1:
                source_text += "This is PART 1. Start the story with a strong hook. End with a cliffhanger for Part 2.\n"
            elif part_num < total:
                source_text += f"This is PART {part_num}. Start with a quick recap of what happened before. Continue the story. End with a cliffhanger for Part {part_num + 1}.\n"
            else:
                source_text += f"This is the FINAL PART ({part_num}). Start with a recap. Deliver the conclusion. End with a satisfying community CTA.\n"
        else:
            source_text = f"REDDIT SOURCE (r/{reddit_post.get('subreddit', 'unknown')}, {reddit_post.get('score', 0)} upvotes):\n"
            source_text += f"Title: {reddit_post.get('title', '')}\n"
            if reddit_post.get('selftext'):
                source_text += f"Body: {reddit_post['selftext'][:1000]}\n"
            source_text += "\nTransform this Reddit story into your brain-rot rant style. Do NOT copy it. Rewrite completely in your voice with added character names, specific details, and dramatic flair."
    elif backup_topic:
        source_text = f"TOPIC: {backup_topic}\nCreate a chaotic brain-rot rant about this relatable situation."
    else:
        # Use random backup topic
        used = load_used_topics()
        available = [t for t in BACKUP_TOPICS if t not in used]
        if not available:
            available = BACKUP_TOPICS
        backup_topic = random.choice(available)
        save_used_topic(backup_topic)
        source_text = f"TOPIC: {backup_topic}\nCreate a chaotic brain-rot rant about this relatable situation."

    system_prompt = get_system_prompt()
    sfx_list_str = get_sfx_list_for_ai()

    user_prompt = f"""
{source_text}

GENERATE:
1. A clean script (170-210 words, NO sound effect words, ready for TTS voiceover)
2. A separate sfx_timeline (3-5 sound effects with trigger phrases from the script)
3. A Gen-Z style title with emoji and hashtags
4. A chaotic SEO description with proper newlines
5. A unique pinned comment

CRITICAL REMINDERS:
- Script must be CLEAN TEXT ONLY — no brackets, no sfx words, no stage directions
- SFX go in the separate sfx_timeline only
- Use character names (Marcus, Jessica, Tyler, etc.)
- "..." for pauses throughout
- Suspense ending that makes them want to come back
- Community CTA woven naturally (never mention channel name)
- 170-210 words exactly. If the script is under 160 words, it is TOO SHORT. Aim for 190 words.

WORD COUNT IS CRITICAL:
- MINIMUM: 180 words
- TARGET: 190-200 words
- MAXIMUM: 220 words
- If your script is under 180 words, you MUST rewrite it longer
- Count your words. This is the #1 priority.

Available sound effects for sfx_timeline:
{sfx_list_str}

Return ONLY valid JSON:
{{
    "title": "gen z title with emoji 💀 #hashtag1 #hashtag2",
    "description": "chaotic description with newlines...",
    "script": "the complete 170-210 word clean script with ... pauses and NO sfx words...",
    "sfx_timeline": [
        {{"trigger_phrase": "phrase from script", "sound": "sfx_name", "volume": 0.6}},
        {{"trigger_phrase": "another phrase", "sound": "another_sfx", "volume": 0.55}}
    ],
    "pinned_comment": "unique engaging comment for this video",
    "source": "reddit" or "backup_topic",
    "word_count": approximate_word_count_integer
}}
"""

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=PRIMARY_MODEL,
            temperature=0.92,
            max_tokens=3000,
            top_p=0.93,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)

        # WORD COUNT RETRY LOGIC
        script = result.get("script", "")
        word_count = len(script.split())

        if word_count < 170:
            print(f"[AI] Script too short ({word_count} words). Requesting longer version...")
            retry_prompt = f"Your script was only {word_count} words. I need MINIMUM 180 words, ideally 190-200. Please rewrite the SAME topic but make it LONGER with more details, more escalation, more internal thoughts. Do NOT just add filler — add genuine funny relatable details."
            
            try:
                retry_response = client.chat.completions.create(
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                        {"role": "assistant", "content": response.choices[0].message.content},
                        {"role": "user", "content": retry_prompt}
                    ],
                    model=PRIMARY_MODEL,
                    temperature=0.92,
                    max_tokens=3000,
                    top_p=0.93,
                    response_format={"type": "json_object"}
                )
                retry_result = json.loads(retry_response.choices[0].message.content)
                retry_count = len(retry_result.get("script", "").split())
                
                if retry_count > word_count:
                    result = retry_result
                    print(f"[AI] Retry successful: {retry_count} words")
            except:
                print("[AI] Retry failed, using original")
        result["channel"] = CHANNEL_NAME
        result["bg_source"] = BG_SOURCE

        word_count = len(result.get("script", "").split())
        print(f"[AI] Script generated: {word_count} words")
        
        # Validate no SFX words leaked into script
        script = result.get("script", "")
        if "(" in script or ")" in script:
            # Strip any brackets that leaked
            script = re.sub(r'\([^)]*\)', '', script)
            script = re.sub(r'\s+', ' ', script).strip()
            result["script"] = script
            print("[AI] Cleaned leaked brackets from script")

        return result

    except Exception as e:
        print(f"[Groq] Error (primary): {e}")
        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": MASTER_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                model=FALLBACK_MODEL,
                temperature=0.92,
                max_tokens=3000,
                top_p=0.93,
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            result["channel"] = CHANNEL_NAME
            result["bg_source"] = BG_SOURCE
            return result
        except Exception as e2:
            print(f"[Groq] Fallback failed: {e2}")
            return None


def fix_description_formatting(description: str) -> str:
    """Fixes line breaks in description for YouTube."""
    if not description:
        return description
    markers = ["🔔", "👉", "🎮", "📌", "turn on notifs", "we post daily", "bg gameplay:"]
    for m in markers:
        if m in description:
            description = description.replace(m, f"\n\n{m}")
    description = re.sub(r'\n{4,}', '\n\n\n', description)
    lines = [l.strip() for l in description.split('\n')]
    return '\n'.join(lines).strip()


if __name__ == "__main__":
    print(f"{'='*50}")
    print(f"  {CHANNEL_NAME} — Educational Engine")
    print(f"{'='*50}")
    result = generate_video_content(backup_topic="When the teacher steps out and the class becomes a war zone")
    if result:
        print(f"\nTITLE: {result.get('title')}")
        print(f"\nSCRIPT:\n{result.get('script')}")
        print(f"\nSFX: {json.dumps(result.get('sfx_timeline', []), indent=2)}")
        print(f"\nCOMMENT: {result.get('pinned_comment')}")
