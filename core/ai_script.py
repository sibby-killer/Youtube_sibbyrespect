import os
import json
from groq import Groq
from config import GROQ_API_KEY

if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
else:
    client = None

# ─────────────────────────────────────────────────────────────────────────────
#  CHANNEL BRAND IDENTITY  (edit these to rebrand the channel)
# ─────────────────────────────────────────────────────────────────────────────
CHANNEL_NAME   = "SibbyRespect"
CHANNEL_SLOGAN = "Shocking facts that change how you see the world."
Channel_URL = "https://www.youtube.com/channel/UCOvhnm2NE7JAQoY8h06GyFQ"
HANDLE = "@sibbyrespect"
SUBSCRIBE_LINE = f"Subscribe to {CHANNEL_NAME} for daily mind-blowing content: {HANDLE} -> {Channel_URL}"
# Primary US/UK-focused hashtag pool injected into every description
BASE_HASHTAGS = (
    "#USA #UK #UnitedStates #UnitedKingdom #America #Britain "
    "#Facts #MindBlast #Psychology #DidYouKnow #TikTokFacts "
    "#Viral #Shorts #YouTubeShorts #Trending #MindBlowing "
    "#Satisfying #InterestingFacts #FunFacts #GTA #China"
)


def generate_video_content(topic: str = "a psychology trick to win negotiations") -> dict | None:
    """
    Uses Groq Llama-3 to generate the full video package:
    title, SEO description, spoken script, and B-roll search keywords.
    """
    if not client:
        print("Error: GROQ_API_KEY not set.")
        return None

    prompt = f"""
You are the head content strategist for the YouTube channel "{CHANNEL_NAME}".
Channel slogan: "{CHANNEL_SLOGAN}"
Target audience: English-speaking viewers aged 18-35 in the USA and United Kingdom.
Your style mirrors the YouTube channel "FitFix" — fast-paced, dopamine-boosting, fact-driven.

Create a viral 45-60 second YouTube Shorts script about: {topic}

=== THE FITFIX FORMULA ===
1. HOOK (0-3s): Start with a jaw-dropping claim or question about what appears on screen.
2. STORY (4-45s): Deliver the facts at high speed. Short sentences. Simple words. Urgent tone.
3. DOPAMINE SPIKE (45-55s): Ask a polarising question to push viewers to the comments.
   Example: "Would YOU do this? Tell me below."
4. CTA (55-60s): End with "Follow {CHANNEL_NAME} for more shocking facts every day."

=== SEO TITLE RULES ===
- Under 70 characters total
- Curiosity-driven, power words
- End with EXACTLY 3 trending hashtags relevant to the topic and one of: #USA #UK #America #Britain
- Example format: "The Secret Banks Don't Want You to Know #Finance #USA #Money"

=== DESCRIPTION RULES ===
Write a 300-400 word SEO description with this EXACT structure:

{CHANNEL_SLOGAN}

[2-3 engaging, curiosity-driven sentences that expand on the video topic without
 giving away everything — make the viewer want to watch AND comment]

KEY FACTS covered in this video:
• [Key fact 1]
• [Key fact 2]
• [Key fact 3]

What do YOU think? Drop your answer in the comments below!

{SUBSCRIBE_LINE}

WATCH MORE mind-blowing content:
• [Related topic 1 title]
• [Related topic 2 title]
• [Related topic 3 title]

{BASE_HASHTAGS}

[CREDITS_HERE]

=== B-ROLL KEYWORDS ===
Provide EXACTLY 4 keywords for Pexels API search. IMPORTANT: Keep them extremely simple and generic (1-2 words max). E.g., 'city timelapse', 'sand', 'waterfall', 'abstract', 'space', 'driving'. Do NOT use specific phrases like 'gta 5', 'satisfying kinetic sand', or long sentences.

=== OUTPUT ===
Return ONLY valid JSON matching this schema — no markdown, no commentary:
{{
    "title": "string",
    "description": "string",
    "script": "string (spoken words only — no stage directions, no brackets, no speaker labels)",
    "b_roll_keywords": ["string", "string", "string", "string"]
}}
"""

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.3-70b-versatile",
            temperature=0.75,
            max_tokens=2048,
            response_format={"type": "json_object"}
        )
        content_str = response.choices[0].message.content
        return json.loads(content_str)

    except Exception as e:
        print(f"Error generating script: {e}")
        return None


if __name__ == "__main__":
    print("Testing branded MindBlast script generation...")
    result = generate_video_content("How the Benjamin Franklin effect makes people like you")
    if result:
        print(json.dumps(result, indent=2))
