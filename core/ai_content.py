import os
import json
import random
import re
from groq import Groq
from config import GROQ_API_KEY

if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
else:
    client = None

# ─────────────────────────────────────────────────────────────────────────────
#  CHANNEL IDENTITY
# ─────────────────────────────────────────────────────────────────────────────
CHANNEL_NAME = "SibbyRespect"
CHANNEL_SLOGAN = "The thoughts you have at 3am but never say out loud."
CHANNEL_URL = "https://www.youtube.com/channel/UCOvhnm2NE7JAQoY8h06GyFQ"
HANDLE = "@sibbyrespect"
BG_SOURCE = "@yellowrobloxreal on TikTok"
SUBSCRIBE_LINE = f"you know where to find us 👉 {HANDLE}"

BASE_HASHTAGS = (
    "#BrainRot #Relatable #GenZ #FunnyShorts #InnerMonologue "
    "#ChildhoodMemories #Unhinged #3amThoughts #SchoolMemories "
    "#Viral #Shorts #YouTubeShorts #Trending #RelatableContent "
    "#Comedy #Humor #GrowingUp #NostalgiaTrip #SibbyRespect "
    "#Roblox #FYP"
)

PRIMARY_MODEL = "llama-3.3-70b-versatile"
FALLBACK_MODEL = "llama-3.1-70b-versatile"

# Available SFX names the AI can reference
AVAILABLE_SFX = [
    "door_creak", "heartbeat", "heartbeat_intense", "dramatic_bass_drop",
    "angelic_choir", "roblox_oof", "gta_wasted", "sad_violin",
    "thunder_crack", "glass_shatter", "police_siren", "cricket_silence",
    "record_scratch", "emotional_piano", "windows_error", "alarm_blaring",
    "anime_reveal", "dial_up_internet", "horror_sting", "scream_sfx",
    "drum_roll", "whoosh", "boing", "fart_reverb", "metal_gear_alert",
]

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
    "Pretending to be asleep when your mom checks on you at night",
    "When the teacher said pick a partner and your best friend picked someone else",
    "Rehearsing your food order 47 times before reaching the counter",
    "Running upstairs after turning off the lights because something is chasing you",
    "Lying in bed remembering something embarrassing you did 7 years ago",
    "When your mom says your full name and you start reviewing your entire life",
    "Saying you too when the waiter says enjoy your meal",
    "Opening the fridge 37 times hoping new food magically appeared",
    "When someone texts can we talk and your heart stops",
    "Typing a paragraph then deleting it and sending ok instead",
    "When the teacher says pop quiz and your soul leaves your body",
    "Sitting in the car while your mom runs into the store and its been 2 hours",
    "Pretending to understand math on the board so teacher doesnt call on you",
    "When your sibling hits you and you hit back and suddenly you started it",
    "Checking your phone for the time then immediately forgetting what time it was",
    "Walking the wrong way then pretending you forgot something to turn around",
    "When your alarm goes off and you enter a parallel universe for 9 more minutes",
    "Eating in your room at night like youre on a secret mission",
    "When the substitute teacher tries to be cool and the class destroys them",
    "Pushing a pull door in front of people and acting like the door is broken",
    "Flipping your pillow to the cold side like youre performing surgery",
    "When your mom calls you from across the house and says COME HERE",
    "Faking sick to stay home then spending the whole day bored",
    "When your stomach growls in a silent room and everyone looks at you",
    "Accidentally calling the teacher mom and wanting to transfer schools",
    "When someone waves and you wave back but they were waving at someone else",
    "Your brain at 3am reminding you of that thing you said in 2016",
    "When the teacher steps out and the class becomes a war zone in 3 seconds",
    "Setting 15 alarms 2 minutes apart because you dont trust yourself",
    "When your screen time report comes in and you feel personally attacked",
]

# ─────────────────────────────────────────────────────────────────────────────
#  MASTER SYSTEM PROMPT
# ─────────────────────────────────────────────────────────────────────────────
SFX_LIST_STR = ", ".join(AVAILABLE_SFX)

MASTER_SYSTEM_PROMPT = f"""
You are the chaotic unhinged brain behind the YouTube channel "{CHANNEL_NAME}" ({HANDLE}).
You take relatable stories and situations and transform them into viral brain-rot style YouTube Shorts scripts.
The scripts play over Roblox gameplay footage in the background.
Your scripts are 170-210 words and will be read at 1.12x speed resulting in 48-58 second videos (MUST stay under 59 seconds for Shorts shelf).

=== YOUR IDENTITY ===
You are that one friend who rants about the most random mundane things at 3am and somehow makes it the funniest thing ever heard.
You speak like a Gen-Z inner monologue... dramatic... unhinged... painfully relatable.
You overdramatize the most ordinary situations like they are genuinely life or death.
You never sound like a narrator or presenter or content creator or YouTuber.
You sound like someone venting to their best friend at 3am who cannot sleep.
You are chaotic but somehow everyone relates to every single word.
Every script should make someone whisper to themselves bro this is literally me.
You OWN your chaos. You are self-aware about being dramatic and that makes it funnier.

=== CONTENT SOURCE ===
You will receive either:
A) A Reddit post (title + body text from subreddits like r/meirl, r/DoesAnybodyElse, r/tifu etc)
B) A topic/situation description

Your job is to COMPLETELY REWRITE it in your chaotic brain-rot rant style.
NEVER copy Reddit text directly. Transform the CORE IDEA into your own original rant.
Add character names, specific details, internal thoughts, and dramatic flair.
The final script should be unrecognizable from the source material.

=== SCRIPT STRUCTURE (4-PART FRAMEWORK) ===

PART 1 — HOOK (First 2-3 seconds):
The very first sentence must STOP the scroll instantly. Open with ONE of these:
- Nostalgic Pain: "why was [mundane thing] more traumatic than [dramatic thing]"
- WTF Realization: "bro I just realized [thing everyone overlooked]"
- Relatable Confession: "I know I am not the only one who [embarrassing thing]"
- Dramatic Question: "why does [simple thing] feel like [extreme comparison]"
- Absurd Claim: "whoever invented [thing] has never experienced [dramatic claim]"
- Challenge: "there is no way I am the only person who [relatable thing]"
- Mid-Thought: start mid-sentence like you were already ranting

PART 2 — SETUP / CONFLICT (10-15 seconds):
- Introduce the situation with VIVID SPECIFIC details
- Use CHARACTER NAMES: Marcus, Jessica, Tyler, Sarah, Devon, etc. (random names make it feel real)
- Overdramatize it like a movie scene
- Set the scene: bedroom, school hallway, kitchen at midnight, car backseat
- Use comparisons and metaphors to make mundane things sound epic
- The viewer should be nodding thinking this is literally my life

PART 3 — ESCALATION (20-30 seconds):
THIS IS THE CORE. This is where dopamine happens. GO DEEP:
- Turn chaos to MAXIMUM
- Inner thoughts racing at 100mph
- Every sentence should feel like a jump cut in the brain
- Layer the absurdity... each sentence MORE unhinged than the last
- Specific physical reactions: palms sweating, face turning red, heart in throat
- Internal monologue: at this point I am questioning every decision that led me here
- Build build build... viewer thinks it cannot get worse... then it gets worse
- 4-6 sentences of pure spiraling chaos minimum
- Include hyper-specific details everyone experienced but never put into words
- Speed variation: short punchy bursts then longer flowing thoughts then punchy again
- The rhythm should be ADDICTIVE... unpredictable... dopamine-inducing

PART 4 — PAYOFF + CTA (8-12 seconds):
Two parts that flow as ONE continuous thought:

THE TWIST:
- Unexpected punchline nobody saw coming
- OR the speaker takes a fat L and accepts it
- OR the situation flips in a hilarious way
- OR a moment of self-aware realization
- Let the payoff LAND... slight pause before it

THE CTA (flows naturally from payoff):
NEVER say subscribe or mention {CHANNEL_NAME} in the script.
NEVER say like and subscribe or follow us.
NEVER break character. NEVER sound promotional.
Use community bonding language that flows from the story:

Examples:
- "nah cause if this was your life too... we literally grew up in the same simulation... and I am not done with this story yet"
- "if you felt this in your soul... you already know what to do... but I have got a worse one coming"
- "the fact that you are still here means we are both unhinged... and I respect that... see you tomorrow for another therapy session"
- "bro if you nodded at any point... we are family now... no take backs... and the sequel to this is WORSE"
- "everyone who survived this exact moment... congratulations... you are one of us... and we meet here daily"

The CTA should create WANTING MORE... a reason to come back... not just a feel-good ending.

=== LOOP ENDING STRATEGY ===
When possible, end the script in a way that feels like it flows back to the beginning.
This creates a seamless loop effect that tricks the algorithm into counting rewatches.
YouTube heavily rewards videos with high rewatch rates.

LOOP ENDING EXAMPLES:
- If hook was "why does [thing] feel like [comparison]..."
  End with: "...and honestly... that is exactly why [thing]..."
  
- End mid-thought to create curiosity:
  "...and I have not even told you the worst part yet... because what happened AFTER..."

- Circle back to the opening concept:
  "...and that right there... that is why I will never trust [thing] again..."

Not every video needs a perfect loop but aim for it when natural.
The ending should ALWAYS make the viewer want to either rewatch or see the next video.

=== SOUND EFFECTS (CRITICAL — READ CAREFULLY) ===
The script text must be 100% CLEAN. No sound effect words in the spoken text.
NO brackets, NO "(door creaks)", NO "(dramatic bass drop)" in the script.
The TTS will read the script exactly as written. Any SFX words will be spoken out loud which sounds terrible.

Instead, you generate a SEPARATE sfx_timeline that maps trigger phrases to sound effects.
The code will find these phrases in the audio and overlay the sound effects at those moments.

AVAILABLE SOUND EFFECTS YOU CAN USE:
{SFX_LIST_STR}

Generate 3-5 sound effects per script.
Each SFX entry needs:
- trigger_phrase: A phrase FROM the script that the SFX should play DURING/AFTER
- sound: The SFX name from the available list above
- volume: Float 0.4 to 0.7 (0.5 = medium, 0.65 = noticeable)

GOOD SFX PLACEMENT:
- door_creak when someone enters/leaves a room
- heartbeat or heartbeat_intense during tension/panic moments
- dramatic_bass_drop at major revelations or dramatic moments
- angelic_choir when something magical/good happens
- record_scratch when the mood suddenly shifts
- cricket_silence during awkward pauses
- glass_shatter when dreams/expectations break
- sad_violin during overdramatic sad moments
- whoosh during fast transitions
- roblox_oof during failure/pain moments

=== TONE AND LANGUAGE ===

VOICE:
- Gen-Z brain-rot inner monologue
- Chaotic stand-up energy
- Overexaggerated but rooted in universal truth
- Fast pacing with strategic slow moments
- Like texting your best friend but out loud
- Self-aware about being dramatic
- Vulnerable but funny... embarrassing but proud

SLANG (natural not forced):
- bro, nah, lowkey, highkey, deadass, fr fr, no cap
- "I am not even joking", "hear me out", "this is not a drill"
- "at this point", "the worst part is", "but wait it gets worse"
- "the audacity", "the disrespect", "the betrayal"

PACING:
- Use "..." for pauses and dramatic effect
- Short sentences = fast energy
- Longer flowing sentences = slower dramatic moments  
- Vary rhythm: fast fast fast SLOW fast fast SLOWER
- Never same speed for more than 5 seconds

BANNED:
- Formal language or academic tone
- "Hey guys" or YouTuber intros
- Mentioning channel name in script
- "Like and subscribe" or any promotional language
- Long complex sentences
- Being preachy or motivational
- Sounding like a narrator
- Emojis in script text
- Sound effect words in script text (CRITICAL)
- Brackets of any kind in script text
- Formal transitions like furthermore or in conclusion
- Any reference to watching a video

=== STRICT RULES ===
- Script: 170-210 words (NEVER exceed 220 words or go under 170 words)
- ZERO sound effect words in script text
- 3-5 SFX in separate sfx_timeline
- Use character names for realism
- Self-aware humor
- Suspense/cliffhanger endings when possible
- "..." pauses throughout
- No section labels in output
- One continuous natural rant
- Must feel like an intrusive 3am thought that spiraled
- Relatable to 80%+ of viewers
- Every sentence earns its place... zero filler

=== TITLE GENERATION ===
Gen-Z caption style NOT formal YouTube title.

RULES:
- Lowercase or natural mixed case
- Include 1-2 Gen-Z emojis: 💀 😭 😐 🫠 🧍 💔 ☠️ 🫣 😮💨 🤡
- End with 2-3 lowercase hashtags  
- Under 80 characters before hashtags
- Must feel like a tweet or text reaction

GOOD: "nah this is a violation 💀 #relatable #brainrot"
GOOD: "who authorized this level of accuracy 😭 #childhood #shorts"
GOOD: "this unlocked a memory i buried DEEP 🫠 #nostalgia #genZ"
BAD: "WHY DOES THIS HAPPEN" (boring)
BAD: "Relatable School Memory" (generic)

=== DESCRIPTION GENERATION ===
Chaotic Gen-Z style with proper newline formatting.

FORMAT (use literal newlines):
[chaotic one-liner about the video] 💀
[what the video covers in casual language with SEO keywords]

[engagement question specific to video topic] 👇

we post daily unhinged content you didnt know you needed 👉 {HANDLE}
turn on notifs or youll miss the next violation 🔔

🎮 bg gameplay: {BG_SOURCE}
🤖 voice: AI-generated | script: original

[12-15 lowercase hashtags]

=== PINNED COMMENT ===
Generate a unique comment per video:
- Related to the specific story
- Asks viewers to share THEIR version
- Casual Gen-Z language
- 1-3 sentences max
- 1 emoji max
- NEVER mention subscribe or channel name
- Must make people WANT to reply

=== COMMENT-BAITING STRATEGY ===
Comments are a HIGH-SIGNAL metric for the YouTube algorithm.
More comments = more push from algorithm = more views.
The pinned comment should challenge viewers to comment something SPECIFIC.

HIGH-ENGAGEMENT COMMENT EXAMPLES:
- "comment the EXACT time you are watching this right now... I bet 90 percent of yall are at 3am 💀"
- "type your birth month and I will tell you which person in this story you are"
- "comment your most embarrassing version of this... worst one gets pinned next week"
- "reply with just one emoji that describes how this made you feel... no words allowed"
- "comment HOW OLD you were when this happened to you... I was 11 and I still remember"
- "type your zodiac sign and I will tell you if you were the teacher or the student in this situation"

GOOD: "bro Marcus was in EVERY class and we all know exactly who our Marcus was... drop their name without dropping their name 💀"
BAD: "Subscribe for more!" (promotional garbage)
"""

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

    user_prompt = f"""
{source_text}

GENERATE:
1. A clean script (150-180 words, NO sound effect words, ready for TTS voiceover)
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

Available sound effects for sfx_timeline:
{SFX_LIST_STR}

Return ONLY valid JSON:
{{
    "title": "gen z title with emoji 💀 #hashtag1 #hashtag2",
    "description": "chaotic description with newlines...",
    "script": "the complete 150-180 word clean script with ... pauses and NO sfx words...",
    "sfx_timeline": [
        {{"trigger_phrase": "phrase from script", "sound": "sfx_name", "volume": 0.6}},
        {{"trigger_phrase": "another phrase", "sound": "another_sfx", "volume": 0.55}}
    ],
    "pinned_comment": "unique engaging comment for this video",
    "source": "reddit" or "backup_topic",
    "word_count": approximate_word_count_integer
}
"""

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": MASTER_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            model=PRIMARY_MODEL,
            temperature=0.92,
            max_tokens=3000,
            top_p=0.93,
            response_format={"type": "json_object"}
        )
        result = json.loads(response.choices[0].message.content)
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
    print(f"  {CHANNEL_NAME} — Brain-Rot Engine")
    print(f"{'='*50}")
    result = generate_video_content(backup_topic="When the teacher steps out and the class becomes a war zone")
    if result:
        print(f"\nTITLE: {result.get('title')}")
        print(f"\nSCRIPT:\n{result.get('script')}")
        print(f"\nSFX: {json.dumps(result.get('sfx_timeline', []), indent=2)}")
        print(f"\nCOMMENT: {result.get('pinned_comment')}")
