# SibbyRespect — Brain-Rot YouTube Automation 🧠🔥

**The ultimate automated YouTube Shorts factory** for the SibbyRespect niche. This pipeline uses relatable Reddit stories, unhinged AI rants, and cinematic 4-layer audio mixing to create viral "Brain-Rot + Commentary" content.

Powered by Groq AI, Edge-TTS, Pixabay SFX, and Roblox gameplay from TikTok.

---

## 📁 Project Structure

```
AutoVidEmpire/
├── main.py                  # Master 20-step pipeline (Reddit -> AI -> Audio -> Video -> Upload)
├── reddit_source.py         # Relatable story scraper (Public JSON API)
├── tiktok_source.py         # Roblox gameplay downloader from @yellowrobloxreal
├── pixabay_audio.py         # SFX library + Validated Background music manager
├── sfx_manager.py           # Word-trigger based sound effects overlay (Format Matched)
├── audio_mixer.py           # 4-layer professional audio mixing (Voice+SFX+Music+Gameplay)
├── config.py                # Configuration and API keys
├── requirements.txt         # Project dependencies
├── .env                     # Local environment variables
│
├── core/
│   ├── ai_content.py        # Gen-Z "Brain-Rot" Persona engine (Llama-3) w/ Algorithm Optimization
│   ├── tts.py               # Edge-TTS voiceover + word-level timestamps
│   ├── video_editor.py      # Vertical 9:16 Vertical Engine (Zoom, Enhancements, Styled Captions)
│   ├── youtube_uploader.py  # YouTube Data API uploader (with AI Disclosure)
│   ├── auto_comment.py      # Comment-baiting strategy engine
│   └── supabase_db.py       # Progress and status logging
│
└── .github/
    └── workflows/
        └── schedule.yml     # Automated 4x daily posting schedule (CI/CD Optimized)
```

---

## ⚡ The New SibbyRespect (Phase 3 Optimization)

The pipeline has been completely upgraded for the **2026 YouTube Algorithm**:

1.  **Algorithm-Optimized 9:16 Engine**:
    - **115% Zoom & Center Crop**: Ensures full-screen mobile immersion and significantly alters content for "transformed" monetization status.
    - **Visual Enhancements**: Dark color grade, vignette, and sharpening applied to every video via FFmpeg.
    - **Styled Dynamic Captions**: High-contrast Impact font with black outlines for readability and engagement.
2.  **Chaotic AI Engine**:
    - **Loop-Friendly Scripts**: AI generates endings that flow back into the hook for infinite loop rewatches.
    - **Comment-Baiting**: Pinned comments use specific psychological triggers to maximize engagement.
    - **AI Disclosure**: Auto-adds synthetic media transparency tags.
3.  **Robust 4-Layer Audio Mix**:
    - Automatic format matching (sample rate, channels) for SFX and Music overlays to prevent processing errors.
    - Validation checks for corrupted or too-short audio files from external APIs.
4.  **20-Step Production Pipeline**: A structured workflow ensuring every video meets high-quality quality before being queued for upload.

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
The project runs **4 times per day** automatically.
The workflow is optimized to save state (used topics, music, scripts) back to the repo after every successful run.

---

## 📊 Analytics & Tracking
The pipeline tracks state to ensures zero duplicate content:
- `used_reddit_posts.json`: Prevents reuse of the same story.
- `used_tiktok_videos.json`: Tracks gameplay video usage.
- `used_music.json`: Prevents lo-fi background music repetition.
- `sfx_manifest.json`: Maps trigger words to sound effects.

---

## 🎮 The Modern Brain-Rot Pipeline
1. **Source**: Scrape relatable stories from Reddit.
2. **Transform**: AI rewrites the core idea into a chaotic 190-word rant.
3. **Voice**: Generate TTS and speed to 1.12x for dopamine-high pacing.
4. **Enhance**: Match SFX to script triggers and layer lo-fi music.
5. **Produce**: Zoom, Crop, Grade, and Burn styled captions onto the footage.
6. **Mux**: Ensure the final short is between 50-58 seconds for the Shorts Shelf.
7. **Post**: Upload with Gen-Z SEO and trigger a comment-baiting pinned thread.

---
*Created with chaotic energy for the SibbyRespect Empire.*
