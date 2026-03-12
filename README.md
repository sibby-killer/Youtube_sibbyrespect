# SibbyRespect — Brain-Rot YouTube Automation 🧠🔥

**The ultimate automated YouTube Shorts factory** for the SibbyRespect niche. This pipeline uses relatable Reddit stories, unhinged AI rants, and cinematic 4-layer audio mixing to create viral "Brain-Rot + Commentary" content.

Powered by Groq AI, Edge-TTS, Pixabay SFX, and Roblox gameplay from TikTok.

---

## 📁 Project Structure

```
AutoVidEmpire/
├── main.py                  # Master pipeline (Reddit -> AI -> Audio -> Video -> Upload)
├── reddit_source.py         # Relatable story scraper (Public JSON API)
├── tiktok_source.py         # Roblox gameplay downloader from @yellowrobloxreal
├── pixabay_audio.py         # SFX library + Background music manager
├── sfx_manager.py           # Word-trigger based sound effects overlay
├── audio_mixer.py           # 4-layer professional audio mixing (Voice+SFX+Music+Gameplay)
├── config.py                # Configuration and API keys
├── requirements.txt         # Project dependencies
│
├── core/
│   ├── ai_content.py        # NEW: Gen-Z "Brain-Rot" Persona engine (Llama-3)
│   ├── tts.py               # Edge-TTS voiceover + word-level timestamps
│   ├── video_editor.py      # Vertical 9:16 assembler with Hormozi-style captions
│   ├── youtube_uploader.py  # YouTube Data API uploader
│   ├── auto_comment.py      # AI-generated unique pinned comments
│   └── supabase_db.py       # Progress and status logging
│
└── .github/
    └── workflows/
        └── schedule.yml     # Automated 4x daily posting schedule
```

---

## ⚡ The New SibbyRespect Overhaul

This project has been completely overhauled to dominate the "Brain-rot" niche:

1.  **Reddit Sourcing**: Automatically pulls the most relatable stories from `r/meirl`, `r/DoesAnybodyElse`, and `r/tifu`.
2.  **Chaotic AI Persona**: Scripts are rewritten by Llama-3 to sound like a dramatic 3am inner monologue (Gen-Z slang, chaotic rhythm).
3.  **4-Layer Audio Mix**:
    - **Layer 1**: 1.12x Sped-up voiceover for high energy.
    - **Layer 2**: Word-triggered sound effects (door creaks, heartbeats, oofs).
    - **Layer 3**: Chill lo-fi background music (via Pixabay API).
    - **Layer 4**: Atmospheric gameplay audio from the source video.
4.  **TikTok Backgrounds**: Uses high-quality, unwatermarked Roblox gameplay from `@yellowrobloxreal`.

---

## 🚀 Quick Start

### 1. Setup Environment
```bash
git clone https://github.com/sibby-killer/Youtube_sibbyrespect.git
cd Youtube_sibbyrespect
pip install -r requirements.txt
```

### 2. Configure Credentials
Create a `.env` file with the following:
```env
GROQ_API_KEY=your_key
PIXABAY_API_KEY=your_key
NEXT_PUBLIC_SUPABASE_URL=your_url
SUPABASE_SERVICE_ROLE_KEY=your_key
YOUTUBE_TOKEN_JSON=your_oauth_token_json
```

### 3. Run Locally
```bash
python main.py
```

### 4. GitHub Actions Automation
The project is configured to run **4 times per day** automatically on GitHub Actions.
Check `.github/workflows/schedule.yml` for times (standardized to US Eastern).

---

## 📊 Analytics & Tracking
The pipeline tracks state to ensure no duplicate content:
- `used_reddit_posts.json`: Prevents reuse of the same story.
- `used_tiktok_videos.json`: Tracks gameplay video usage.
- `used_music.json`: Prevents background music repetition.
- `sfx_manifest.json`: Maps trigger words to sound effects.

---

## 🎮 How It Works (The 3am Loop)
1. **Source**: Scrape a relatable story from Reddit.
2. **Brain-Rot**: AI transforms it into a chaotic, dramatic rant.
3. **Voice**: Generate TTS and speed it up to 1.12x.
4. **Mix**: Overlay SFX library based on script keywords + add music.
5. **Assemble**: Crop Roblox TikTok video to 9:16 and mux with audio.
6. **Upload**: Post to YouTube with custom Gen-Z SEO titles and descriptions.
7. **Engage**: Post an AI-generated unique pinned comment.

---
*Created with chaotic energy for the SibbyRespect Empire.*
