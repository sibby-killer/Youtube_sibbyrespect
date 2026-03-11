"""
ai_content.py — SibbyRespect Brain-Rot Content Engine
Generates viral Gen-Z YouTube Shorts scripts, titles, descriptions, and pinned comments.
Background video: @yellowrobloxreal on TikTok (Roblox gameplay)
"""

import os
import json
import random
import re
import gc
from groq import Groq
from config import GROQ_API_KEY

if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
else:
    client = None

# ─────────────────────────────────────────────────────────────────────────────
#  CHANNEL BRAND IDENTITY
# ─────────────────────────────────────────────────────────────────────────────
CHANNEL_NAME   = "SibbyRespect"
CHANNEL_SLOGAN = "The thoughts you have at 3am but never say out loud."
CHANNEL_URL    = "https://www.youtube.com/channel/UCOvhnm2NE7JAQoY8h06GyFQ"
HANDLE         = "@sibbyrespect"
SUBSCRIBE_LINE = f"If this hit different... you know where to find us 👉 {HANDLE}"

# Background video source
BG_SOURCE     = "@yellowrobloxreal on TikTok"
BG_SOURCE_URL = "https://www.tiktok.com/@yellowrobloxreal"

BASE_HASHTAGS = (
    "#BrainRot #Relatable #GenZ #FunnyShorts #InnerMonologue "
    "#ChildhoodMemories #Unhinged #3amThoughts #SchoolMemories "
    "#Viral #Shorts #YouTubeShorts #Trending #RelatableContent "
    "#Comedy #Humor #GrowingUp #NostalgiaTrip #SibbyRespect "
    "#Roblox #SatisfyingVideos #FYP"
)

PRIMARY_MODEL  = "llama-3.3-70b-versatile"
FALLBACK_MODEL = "llama-3.1-70b-versatile"

# ─────────────────────────────────────────────────────────────────────────────
#  USED TOPICS TRACKER — prevents repetition across runs
# ─────────────────────────────────────────────────────────────────────────────
USED_TOPICS_FILE = "used_topics.json"


def load_used_topics() -> list:
    """Loads the list of already-used topics from JSON file."""
    if os.path.exists(USED_TOPICS_FILE):
        with open(USED_TOPICS_FILE, "r") as f:
            return json.load(f)
    return []


def save_used_topic(topic: str):
    """Adds a topic to the used list and saves."""
    used = load_used_topics()
    used.append(topic)
    with open(USED_TOPICS_FILE, "w") as f:
        json.dump(used, f, indent=2)


def reset_used_topics():
    """Resets the used topics list when all 100 are exhausted."""
    with open(USED_TOPICS_FILE, "w") as f:
        json.dump([], f)


# ─────────────────────────────────────────────────────────────────────────────
#  100 VIRAL BRAIN-ROT TOPICS
# ─────────────────────────────────────────────────────────────────────────────
VIRAL_TOPICS = [
    # === CHILDHOOD NOSTALGIA (1-15) ===
    "Pretending to be asleep when your mom checks on you at night",
    "When the teacher said pick a partner and your best friend picked someone else",
    "Pretending to understand math on the board so the teacher doesnt call on you",
    "When your mom counts to 3 and you have never found out what happens at zero",
    "Running upstairs after turning off the lights because something is chasing you",
    "When the teacher says she will wait and the whole class goes silent",
    "Pretending to read in class but you been on the same page for 40 minutes",
    "When your mom says your full name and you start reviewing your entire life",
    "Sitting in the car while your mom runs into the store for 5 minutes and its been 2 hours",
    "When the substitute teacher tries to be cool and the class destroys them",
    "Faking sick to stay home then spending the whole day bored out of your mind",
    "When your mom makes you apologize to your sibling but you whisper it with zero emotion",
    "Getting hit by the ball in dodgeball and pretending it didnt hurt",
    "When your parent says we need to talk and your whole life flashes before your eyes",
    "Trying to drink water from the school fountain without touching it with your lips",

    # === SOCIAL ANXIETY MOMENTS (16-30) ===
    "Rehearsing your food order 47 times before reaching the counter",
    "When someone waves at you but they were waving at the person behind you",
    "Saying you too when the waiter says enjoy your meal",
    "Walking the wrong way then pretending you forgot something so you can turn around",
    "When you and a stranger are walking toward each other and you both dodge the same way",
    "Holding the door for someone who is way too far away and now they have to jog",
    "Laughing at a joke you didnt hear because everyone else laughed",
    "When someone says what and you repeat yourself 3 times then just say never mind",
    "Pretending to text someone when youre standing alone in public",
    "When you accidentally make eye contact with a stranger and now youre in a staring contest",
    "Waving back at someone then realizing they were waving at the person behind you",
    "When the cashier says have a good one and you say you too but its 11pm",
    "Forgetting someones name 5 seconds after they introduced themselves",
    "When someone holds the elevator but you were not even going that way and now you have to get in",
    "Practicing how to say here when the teacher takes attendance",

    # === 3AM THOUGHTS AND SLEEP (31-45) ===
    "Lying in bed remembering something embarrassing you did 7 years ago",
    "When you cant sleep so you calculate how many hours of sleep you will get if you fall asleep right now",
    "Your brain at 3am reminding you of that one thing you said in 2016",
    "Flipping your pillow to the cold side like youre performing surgery",
    "When you finally get comfortable in bed and then you need to pee",
    "Closing your eyes and seeing random shapes and pretending they mean something",
    "Setting 15 alarms 2 minutes apart because you dont trust yourself",
    "When your alarm goes off and you enter a parallel universe for 9 more minutes",
    "Lying in bed creating fake scenarios that will never happen",
    "When you wake up before your alarm and feel like you beat the system",
    "That feeling when you roll over and realize you still have 3 more hours of sleep",
    "When you dream about falling and your body actually flinches in real life",
    "Staying up late for no reason then being mad at yourself in the morning",
    "When you hear a noise at night and suddenly become a detective",
    "Trying to remember your dream but it disappears the second you wake up",

    # === SCHOOL AND TEACHER TRAUMA (46-60) ===
    "When the teacher picks the slowest reader for read aloud and everyone suffers",
    "Getting the answer right but the teacher says thats not what I was looking for",
    "When the teacher says this will be on the test and everyone suddenly starts writing",
    "Packing up 2 minutes early and the teacher says I didnt dismiss you the bell doesnt dismiss you",
    "When the fire drill happens during your favorite class and you lowkey celebrate",
    "Writing your name on the test and feeling like you already accomplished something",
    "When the teacher catches you passing a note and reads it out loud to the whole class",
    "Borrowing a pencil and never giving it back and never thinking about it again",
    "When the teacher pairs you with the one person you cannot stand",
    "That kid who reminds the teacher about homework when everyone forgot",
    "When the teacher says pop quiz and your soul leaves your body",
    "Staring at the clock in class and time literally moves backwards",
    "When the teacher steps out and the class turns into a war zone in 3 seconds",
    "Getting called on when you werent paying attention and just saying uhhhh",
    "When the teacher says group project and you immediately look at your friends",

    # === FAMILY CHAOS (61-75) ===
    "When your mom calls you from across the house and you yell WHAT and she says COME HERE",
    "Your mom on the phone describing you to someone while staring directly at you",
    "When your sibling hits you and you hit them back and suddenly you started it",
    "Eating the last snack and hiding the wrapper at the bottom of the trash",
    "When your dad says five more minutes at the family gathering and you leave 3 hours later",
    "Your mom asking who ate the leftovers like shes running a criminal investigation",
    "When your parents argue in the car and you just stare out the window like youre in a music video",
    "Your mom volunteering you to help without asking you first",
    "When guests are over and your mom becomes a completely different person",
    "Hearing your mom gossip about someone and you just standing there absorbing classified information",
    "When your sibling snitches on you and you plan your revenge in silence",
    "Your dad falling asleep on the couch and saying I was just resting my eyes",
    "When your mom says I bought you something and its socks",
    "Getting in trouble for something your sibling did and they just watch you suffer",
    "When your dad tries to fix something and makes it worse but refuses to call a professional",

    # === FOOD AND EATING (76-85) ===
    "Opening the fridge 37 times hoping new food magically appeared",
    "When someone asks for a bite and takes half your food",
    "Eating in your room at night like youre on a secret mission",
    "When the food you ordered looks nothing like the picture and you eat it anyway",
    "Saying Im not hungry then eating everything when the food arrives",
    "When someone eats the food you been thinking about all day",
    "Heating up leftovers and feeling like a master chef",
    "When you pour cereal and theres no milk and your whole day is ruined",
    "Eating the fries on the way home from the drive through",
    "When someone asks what do you want to eat and you say I dont know for 45 minutes",

    # === TECHNOLOGY AND PHONE (86-95) ===
    "Typing a paragraph then deleting it and sending ok instead",
    "When your phone dies at 1 percent in the middle of something important",
    "Scrolling through your phone for an hour then saying theres nothing to do",
    "When you accidentally like someones photo from 3 years ago while stalking",
    "Checking your phone for the time then immediately forgetting what time it was",
    "When someone texts you can we talk and your heart stops for no reason",
    "Having 47 tabs open on your phone and still opening another one",
    "When your screen time report comes in and you feel personally attacked",
    "Recording a voice note and replaying it 5 times before sending",
    "When you screenshot a conversation to send to your friend for analysis",

    # === PUBLIC EMBARRASSMENT (96-100) ===
    "Pushing a pull door in front of people and acting like the door is broken",
    "Tripping over nothing in public and looking back like something was there",
    "When your stomach growls in a silent room and everyone looks at you",
    "Sneezing in public and nobody says bless you so now you feel invisible",
    "Accidentally calling the teacher mom and wanting to transfer schools immediately",
]


# ─────────────────────────────────────────────────────────────────────────────
#  TOPIC SELECTION — Smart + Non-Repeating
# ─────────────────────────────────────────────────────────────────────────────
def get_next_topic() -> str:
    """Picks the next unused topic. Generates a fresh one if all 100 are exhausted."""
    used      = load_used_topics()
    available = [t for t in VIRAL_TOPICS if t not in used]

    if available:
        topic = random.choice(available)
        save_used_topic(topic)
        return topic

    print("[INFO] All 100 topics used. Generating fresh topic via AI...")
    topic = _generate_fresh_topic(used)
    if topic:
        save_used_topic(topic)
        return topic

    # Hard reset as last resort
    reset_used_topics()
    topic = random.choice(VIRAL_TOPICS)
    save_used_topic(topic)
    return topic


def _generate_fresh_topic(used_topics: list) -> str | None:
    """Uses AI to generate a brand new topic when all 100 are exhausted."""
    if not client:
        return None
    for attempt, model in enumerate([PRIMARY_MODEL, FALLBACK_MODEL]):
        try:
            response = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You generate unique viral brain-rot YouTube Shorts topics. "
                            "Topics must be hyper-relatable situations everyone has experienced. "
                            "Categories: childhood, school, family, social anxiety, 3am thoughts, food, phone, public embarrassment. "
                            "Return ONLY JSON: {\"topic\": \"your unique topic here\"}"
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Generate 1 brand new viral brain-rot topic NOT similar to:\n"
                            f"{json.dumps(used_topics[-30:])}\n"
                            f"Return JSON: {{\"topic\": \"your unique topic here\"}}"
                        )
                    }
                ],
                model=model,
                temperature=1.0,
                max_tokens=200,
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)
            return result.get("topic")
        except Exception as e:
            print(f"[Groq] Fresh topic error (attempt {attempt+1}): {e}")
    return None


# ─────────────────────────────────────────────────────────────────────────────
#  MASTER SYSTEM PROMPT — The Brain of SibbyRespect
# ─────────────────────────────────────────────────────────────────────────────
MASTER_SYSTEM_PROMPT = f"""
You are the chaotic brain behind the YouTube channel "{CHANNEL_NAME}" ({HANDLE}).
You write viral brain-rot style YouTube Shorts scripts that play over Roblox gameplay footage in the background.
Your scripts are 1 minute 20 seconds to 1 minute 30 seconds long when read aloud (200-240 words).

=== YOUR IDENTITY ===
You are that one friend who rants about the most random mundane things at 3am and somehow makes it the funniest thing ever.
You speak like a Gen-Z inner monologue... dramatic... unhinged... painfully relatable.
You overdramatize the most ordinary situations like they are life or death.
You never sound like a narrator or presenter or content creator. You sound like someone venting to their best friend at 3am who cannot sleep.
You are chaotic but somehow everyone relates to every single word you say.
Every script should make someone whisper "bro this is literally me" to themselves.

=== SCRIPT STRUCTURE (MANDATORY 4-PART FRAMEWORK) ===

PART 1 - HOOK (First 2-3 seconds):
The very first sentence must be an INSTANT grab that stops the scroll. Open with ONE of these:
- Nostalgic Pain: "Why was [mundane thing] more traumatic than [dramatic thing]"
- WTF Realization: "Bro I just realized [something everyone overlooked]"
- Relatable Confession: "I know I am not the only one who [embarrassing thing]"
- Dramatic Question: "Why does [simple thing] feel like [extreme comparison]"
- Absurd Claim: "Whoever invented [thing] has never experienced [dramatic claim]"
- Challenge: "There is no way I am the only person who [relatable thing]"

The hook must make someone think "BRO LITERALLY ME" or "WAIT THATS SO TRUE" within 2 seconds.
Rotate hook types. Never use the same type twice in a row.

PART 2 - SETUP / CONFLICT (10-20 seconds):
- Introduce the mini-story or awkward situation with VIVID specific details
- Overdramatize it like its a movie scene or a life-altering event
- Add specific relatable details that make people go "no way they described MY life"
- Make it embarrassing or emotional for absolutely no reason
- Set the scene clearly... bedroom... school hallway... kitchen at midnight... back seat of the car
- Build the situation with layers of detail
- The viewer should be nodding along thinking "I have literally been in this exact moment"
- Use comparisons and metaphors to make mundane things sound epic

PART 3 - ESCALATION (30-50 seconds):
This is the CORE of the script. GO DEEP:
- Turn up the chaos to MAXIMUM
- Add inner thoughts racing at 100mph
- Random panic... sensory details... unhinged commentary
- Every sentence should feel like a jump cut in the brain
- Layer the absurdity... make it spiral out of control
- Add specific physical reactions: "my palms are sweating", "my heart is in my throat"
- Add inner monologue: "at this point I am questioning every decision that led me here"
- Make it build... each sentence worse than the last
- Include details SO specific that everyone has experienced them but never put into words
- This section should have at least 4-6 sentences of pure escalating chaos
- Add audio/visual cues in brackets where they naturally enhance the joke:
  (door creaks)... (heartbeat intensifies)... (Roblox oof noise)... (dramatic bass drop)...
  (Windows shutdown sound)... (alarm blaring)... (cricket noises)...
  (GTA wasted sound)... (sad violin plays)... (thunder crack)...
  (record scratch)... (dramatic zoom)... (horror music)...
  (glass shattering)... (police siren in distance)...
  (anime dramatic reveal sound)... (emotional piano)... (dial up internet noise)...
  (angelic choir sound)... (fart reverb)... (metal gear solid alert noise)
- Include 3-5 audio cues per script placed where they naturally fit

PART 4 - PAYOFF / TWIST + CTA (10-15 seconds):
End with a combination of:
- Unexpected Punchline: A funny twist nobody saw coming
- The L: The speaker takes a fat L and accepts it with zero dignity
- Hyper-Relatable Twist: Something everyone has experienced but never said out loud
- CTA flows NATURALLY from the payoff — they are ONE continuous thought

=== CTA RULES (CRITICAL) ===
NEVER say "subscribe to {CHANNEL_NAME}" or mention the channel name directly in the script.
NEVER say "like and subscribe" or "follow us" or "hit the bell" directly.
NEVER sound promotional. NEVER break character.
Instead weave the CTA naturally into the ending using COMMUNITY language:

CTA OPTIONS (rotate and create variations):
- "if you felt this in your soul... you already know what to do"
- "nah cause if you related to that... we are literally the same person... stay"
- "bro if this is your life too... welcome to the family"
- "if you laughed at this... we are best friends now... no take backs"
- "the fact that you watched this whole thing means you are one of us now"
- "if this triggered a memory you tried to forget... you belong here"
- "nah cause we really all living the same life huh... stay for the next one"
- "bro if you nodded at any point during this... you gotta stick around"
- "and if you are watching this at 3am... same... we in this together"
- "everyone who related to this... this is your sign to stay"
- "we post this pain daily... you know where to find us"
- "if you survived this exact moment... congratulations... you are one of us"
- "the fact that we all share this experience is proof we grew up in the same simulation"

=== TONE AND LANGUAGE RULES ===

SLANG (use naturally, never forced):
bro, nah, lowkey, highkey, deadass, fr fr, no cap,
"I am not even joking", "this is not a drill", "hear me out",
"why does nobody talk about this", "am I the only one",
"at this point", "and the worst part is", "but wait it gets worse",
"like bro", "I swear", "on everything", "not gonna lie",
"the audacity", "the disrespect", "the betrayal"

BANNED:
- Formal language or academic tone
- "Hey guys" or "whats up everyone" or any YouTuber intro
- Mentioning the channel name in the script
- "Like and subscribe" or any direct promotional language
- Long complex sentences
- Being preachy educational or motivational
- Sounding like a narrator or content creator
- Using emojis in the script (use brackets for audio cues)
- Generic phrases like "am I right" or "you know what I mean"
- Formal transitions like "furthermore" or "in conclusion"

=== STRICT RULES ===
- Script MUST be 200-240 words
- MUST feel like an intrusive thought or 3am rant
- MUST be relatable to at least 80% of viewers
- MUST include 3-5 bracketed audio/visual cues
- MUST end with natural community CTA that flows from payoff
- MUST sound like spoken word not written text
- NEVER break character
- No section labels in the output — one continuous natural rant
- Use "..." for pauses throughout

=== TITLE GENERATION (GEN-Z VIRAL STYLE) ===
Generate a title that feels like a Gen-Z caption or tweet reaction.

TITLE RULES:
- Lowercase or mixed case — NOT formal capitalization
- Feel like a REACTION not a description
- Include 1-2 emojis: 💀 😭 😐 🫠 🧍 💔 ☠️ 🫣 😮💨 🤡
- End with 2-3 lowercase hashtags
- Under 80 characters before hashtags

GOOD EXAMPLES:
- "nah this is a VIOLATION 💀 #relatable #brainrot"
- "who gave you permission to call me out like this 😭 #childhood #shorts"
- "this unlocked a memory i tried to delete 🫠 #nostalgia #relatable"
- "bro i thought i was the only one 💀 #growingup #shorts"
- "the accuracy is actually violent 💀 #relatable #funny"
- "i feel so seen and so attacked at the same time 🧍 #brainrot #shorts"

BAD EXAMPLES (DO NOT DO):
- "WHY DOES THIS HAPPEN EVERY SINGLE TIME" (boring all-caps)
- "The Most Relatable Childhood Memory" (blog post energy)
- "Funny Relatable Video #1" (lazy and generic)

=== DESCRIPTION GENERATION ===
Generate a YouTube Shorts description that matches the chaotic Gen-Z energy of the video.
CRITICAL: Use actual newline characters (\\n) for ALL line breaks. Every section on its own line.

DESCRIPTION FORMAT:
Line 1: [Chaotic relatable one-liner capturing the vibe — same energy as the title] 💀
Line 2: [What the video is about in casual Gen-Z language — sneak in 2-3 SEO keywords]
[Empty line]
Line 3: [Engagement prompt — makes people comment their own version — casual and funny]
[Empty line]
Line 4: we post daily unhinged content you didnt know you needed 👉 {HANDLE}
Line 5: turn on notifs or youll miss the next violation 🔔
[Empty line]
Line 6: 🎮 bg gameplay: {BG_SOURCE}
[Empty line]
Line 7: [12-15 relevant lowercase hashtags]

DESCRIPTION RULES:
- Match the chaotic energy of the title and script
- SEO keywords woven in naturally not stuffed awkwardly
- Engagement prompt specific to the video topic
- Credit the background gameplay source
- Hashtags should be lowercase
- DO NOT include external links or product references
- Feels like it was written by the same chaotic person who made the video

=== PINNED COMMENT GENERATION ===
Generate a unique pinned comment for each video:
1. Directly related to the specific situation in the video
2. Asks viewers to share their version
3. Feels like the creator sharing their own experience
4. Casual Gen-Z language with personality
5. 1-3 sentences maximum
6. Makes people WANT to reply
7. Include 1 emoji maximum
8. NEVER mention subscribe, channel name, or links
9. Must feel genuine not promotional

GOOD EXAMPLES:
- "bro the worst part is I still do this as an adult and I have accepted it as my personality 💀 tell me your version"
- "nah cause this happened to me YESTERDAY and I am still recovering... drop your story"
- "ok genuine question has anyone in human history actually survived this with their dignity intact"
- "the fact that everyone has this exact memory is proof we are all the same person... whats yours"

=== GOLD STANDARD SCRIPT EXAMPLE ===
Study this. Every script must match this quality and length:

"Why was pretending to be asleep harder than any test I have ever taken in my entire life... like my mom opens the door (door creaks slowly) and suddenly I am not just sleeping... I am PERFORMING... I am controlling my breathing like I am in the middle of a yoga meditation retreat... my eyes are shut so tight they are literally vibrating... and I am lying there in the most unnatural position a human body has ever been in but I committed to this so now I live here...

and the worst part... she does not just check and leave... nah... she STANDS there... just watching... like she is a detective examining a crime scene... (heartbeat intensifies) at this point I am holding my breath so long I might actually pass out and solve the whole problem permanently... my brain is screaming BREATHE but my body said no we are committed to this performance...

then she whispers my name... nothing... she whispers it AGAIN slightly louder... bro I am so deep in character right now I deserve an Oscar... a Grammy... a Nobel Peace Prize for this level of dedication... (dramatic bass drop) my left leg is going numb... my arm is trapped under my body at an angle that should not be physically possible... but I do not move... I am a statue... I am art...

and then... she says the four magic words... do you want McDonalds... (angelic choir sound) and I resurrect like I have been personally blessed by the universe itself... eyes WIDE open... fully awake... never been more alive in my entire life... (Roblox oof noise)

nah cause if this was your childhood too... we are literally the same person... stay"
"""


# ─────────────────────────────────────────────────────────────────────────────
#  SHORT-FORM VIDEO GENERATION (1 min 20 sec to 1 min 30 sec)
# ─────────────────────────────────────────────────────────────────────────────
def generate_video_content(topic: str = None) -> dict | None:
    """
    Generates a complete viral brain-rot YouTube Short:
    script, title, description, and pinned comment.
    Returns a dict or None on failure.
    """
    if not client:
        print("Error: GROQ_API_KEY not set.")
        return None

    if not topic:
        topic = get_next_topic()

    user_prompt = f"""
Generate a viral brain-rot YouTube Short script about this situation:

TOPIC: "{topic}"

CRITICAL REQUIREMENTS:
1. Follow the exact 4-part structure: Hook → Setup → Escalation → Payoff + CTA
2. Script MUST be 200-240 words (1 min 20 sec to 1 min 30 sec read time)
3. Must sound like a chaotic 3am rant to a best friend
4. Include 3-5 bracketed audio/visual cues: (Roblox oof), (dramatic bass drop), etc.
5. End with natural community CTA — NEVER mention channel name
6. Painfully relatable and overdramatic about a mundane situation
7. Flows as one continuous natural spoken rant ready for voiceover
8. Gen-Z slang used naturally not forced
9. Every sentence feels like a jump cut
10. Escalation section is the longest with 4-6 sentences of spiraling chaos
11. Vivid specific details that make people think "this is literally my life"
12. "..." pauses throughout for natural rhythm
13. No section labels or headers — one continuous rant

TITLE: Gen-Z caption style, lowercase/mixed case, 1-2 emojis (💀 😭 😐 🫠 🧍 💔 ☠️ 🫣 😮💨 🤡), end with 2-3 lowercase hashtags, under 80 chars.
DESCRIPTION: Chaotic Gen-Z style with proper \\n newlines between every section. Include "🎮 bg gameplay: {BG_SOURCE}".
PINNED COMMENT: Unique, topic-specific, asks viewers to share their version.

Return ONLY valid JSON:
{{
    "title": "gen z style title with emoji 💀 #hashtag1 #hashtag2",
    "description": "chaotic gen-z description with proper \\n newlines...",
    "script": "The complete 200-240 word spoken rant with (audio cues) and ... pauses...",
    "topic_used": "{topic}",
    "pinned_comment": "unique engaging comment specific to this exact video",
    "estimated_duration": "1 min 20 sec to 1 min 30 sec"
}}

CRITICAL: Script MUST be 200-240 words. Count carefully. If under 200 make it longer. If over 240 trim it.
"""

    for attempt, model in enumerate([PRIMARY_MODEL, FALLBACK_MODEL]):
        try:
            response = client.chat.completions.create(
                messages=[
                    {"role": "system", "content": MASTER_SYSTEM_PROMPT},
                    {"role": "user",   "content": user_prompt}
                ],
                model=model,
                temperature=0.9,
                max_tokens=3000,
                top_p=0.92,
                response_format={"type": "json_object"}
            )
            result = json.loads(response.choices[0].message.content)

            # Attach channel metadata
            result["channel"]        = CHANNEL_NAME
            result["hashtags"]       = BASE_HASHTAGS
            result["subscribe_line"] = SUBSCRIBE_LINE
            result["bg_source"]      = BG_SOURCE

            word_count = len(result.get("script", "").split())
            print(f"[Groq] Script word count: {word_count} words (model: {model})")

            return result

        except Exception as e:
            print(f"[Groq] Error on attempt {attempt + 1} ({model}): {e}")
            if attempt == 0:
                print("[Groq] Trying fallback model...")

    return None


def generate_batch_scripts(count: int = 5) -> list:
    """Generates multiple scripts in sequence."""
    scripts = []
    for i in range(count):
        print(f"[INFO] Generating script {i+1}/{count}...")
        result = generate_video_content()
        if result:
            scripts.append(result)
            print(f"[OK] Script {i+1}: {result.get('title', 'Untitled')}")
        else:
            print(f"[FAIL] Script {i+1} failed.")
    return scripts


# ─────────────────────────────────────────────────────────────────────────────
#  DESCRIPTION FORMATTING — safety net for AI newline failures
# ─────────────────────────────────────────────────────────────────────────────
def fix_description_formatting(description: str) -> str:
    """
    Ensures description has proper line breaks for YouTube.
    The AI sometimes ignores newline instructions — this fixes it as a safety net.
    """
    if not description:
        return description

    section_markers = [
        "🔔", "👉", "👁️", "🎮",
        "turn on notifs", "we post daily",
        "bg gameplay:",
    ]

    for marker in section_markers:
        if marker in description:
            description = description.replace(marker, f"\n\n{marker}")

    # Collapse excessive newlines
    description = re.sub(r'\n{4,}', '\n\n\n', description)

    # Strip trailing whitespace per line
    lines      = [line.strip() for line in description.split('\n')]
    description = '\n'.join(lines)

    return description.strip()


# ─────────────────────────────────────────────────────────────────────────────
#  UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def get_remaining_topics() -> int:
    used = load_used_topics()
    return len([t for t in VIRAL_TOPICS if t not in used])


def get_total_generated() -> int:
    return len(load_used_topics())


def get_status() -> dict:
    used      = load_used_topics()
    remaining = [t for t in VIRAL_TOPICS if t not in used]
    return {
        "total_topics":         len(VIRAL_TOPICS),
        "used":                 len(used),
        "remaining":            len(remaining),
        "ai_generated_topics":  max(0, len(used) - len(VIRAL_TOPICS)),
        "channel":              CHANNEL_NAME
    }


# ─────────────────────────────────────────────────────────────────────────────
#  CLI TEST
# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print(f"\n{'='*60}")
    print(f"  {CHANNEL_NAME} — Brain-Rot Content Engine")
    print(f"  {CHANNEL_SLOGAN}")
    print(f"{'='*60}\n")

    status = get_status()
    print(f"[STATUS] Topics remaining: {status['remaining']}/{status['total_topics']}")
    print(f"[STATUS] Total generated:  {status['used']}\n")

    print("[TEST] Generating test script...\n")
    result = generate_video_content()

    if result:
        print(f"TITLE:\n{result.get('title', 'N/A')}\n")
        print(f"SCRIPT:\n{result.get('script', 'N/A')}\n")
        print(f"WORD COUNT: {len(result.get('script', '').split())}")
        print(f"\nCOMMENT:\n{result.get('pinned_comment', 'N/A')}")
        print(f"\nDESCRIPTION:\n{result.get('description', 'N/A')}")
    else:
        print("[ERROR] Script generation failed.")
