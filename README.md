# SibbyRespect — YouTube Automation Empire 🚀

**Automated YouTube Shorts factory** powered by Groq AI, Edge-TTS, yt-dlp, and the YouTube Data API.
Generates, uploads, and manages 4 viral Shorts per day targeting US/UK audiences — fully hands-free.

---

## 📁 Project Structure

```
AutoVidEmpire/
├── main.py                  # Master pipeline (run one video end-to-end)
├── scheduler.py             # Single-run entry point for GitHub Actions
├── config.py                # All API keys loaded from .env
├── requirements.txt
├── .env                     # ← YOUR SECRETS (never commit this)
├── client_secret_*.json     # ← Google OAuth client secret (never commit)
├── token.json               # ← Auto-generated OAuth token (add to GitHub Secrets)
│
├── core/
│   ├── ai_script.py         # Groq Llama-3 script + SEO description generator
│   ├── tts.py               # Edge-TTS voiceover + word-level SRT captions
│   ├── yt_scraper.py        # yt-dlp B-roll downloader (GTA/UK/US/China/Satisfying)
│   ├── video_editor.py      # MoviePy + FFmpeg assembler with Hormozi-style captions
│   ├── youtube_uploader.py  # YouTube Data API v3 OAuth uploader
│   ├── supabase_db.py       # Supabase video logging and status tracking
│   ├── topic_generator.py   # Reddit scraper + 100 fallback topics
│   ├── auto_comment.py      # Posts a pinned CTA comment after upload
│   └── cleanup.py           # Deletes local files for videos older than 3 days
│
├── dashboard/
│   ├── app.py               # Flask admin dashboard
│   └── templates/           # Dark-themed HTML pages
│
└── .github/
    └── workflows/
        └── schedule.yml     # GitHub Actions: 4 posts/day at US EST times
```

---

## ⚡ Quick Start (Local)

### 1. Clone & Setup

```bash
git clone https://github.com/sibby-killer/Youtube_sibbyrespect.git
cd Youtube_sibbyrespect
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

### 2. Create `.env`

```env
GROQ_API_KEY=your_groq_key
PEXELS_API_KEY=your_pexels_key
NEXT_PUBLIC_SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_supabase_service_role_key
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
FLASK_SECRET_KEY=any-random-string
```

### 3. Setup Supabase Table

Go to **Supabase Dashboard → SQL Editor** and run:

```sql
CREATE TABLE IF NOT EXISTS videos (
  id BIGSERIAL PRIMARY KEY,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  title TEXT,
  topic TEXT,
  script TEXT,
  local_path TEXT,
  description TEXT,
  tags TEXT[],
  status TEXT DEFAULT 'generated',
  youtube_id TEXT,
  youtube_url TEXT,
  views BIGINT DEFAULT 0,
  likes BIGINT DEFAULT 0,
  comments BIGINT DEFAULT 0
);
```

### 4. Add Google OAuth Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Enable **YouTube Data API v3**
3. Create OAuth 2.0 Credentials → **Desktop App**
4. Download JSON → place it in the project root as `client_secret_*.json`
5. Run once locally: `python main.py` → browser opens → log in → `token.json` is saved

### 5. Run One Video Locally

```bash
python main.py
# or with a specific topic:
python main.py --topic "Why the Dunning-Kruger effect is more dangerous than you think"
```

### 6. Run the Dashboard

```bash
cd dashboard
python app.py
# Open http://127.0.0.1:5000
```

---

## ⚡ Dual Automation Model

This project now supports **two independent ways** to automate your channel. You can use GitHub for hands-free 24/7 posting, or your Local PC for maximum control.

### Option A: GitHub Actions (Primary)
GitHub can post 4 viral videos per day automatically for free.
- **Workflow**: Automated via `.github/workflows/schedule.yml`.
- **Times**: 9:00 AM, 12:00 PM, 5:00 PM, and 9:00 PM (EST).
- **Setup**: Ensure you have added your `.env` keys to **GitHub Settings → Secrets and Variables → Actions**.

### Option B: Local Windows (Backup & Manual)
Use your own computer if GitHub fails or if you want to post a video right now.
1. **Manual Run**: Double-click `run_automation.bat`.
2. **Scheduled Run**: Follow the [local_setup_guide.md](local_setup_guide.md) to use Windows Task Scheduler.

---

## 📊 Local Dashboard
You can still use the beautiful Admin Dashboard to see view counts and analytics locally:
```bash
python dashboard/app.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

---

## 🔄 How It Works (TikTok B-Roll Edition)
We have migrated away from YouTube B-roll to avoid bot detection and CAPTCHAs.
1. **Groq AI**: Generates script and viral TikTok keywords.
2. **Edge-TTS**: Creates the voiceover.
3. **TikTok Scraper**: Direct HD download of unwatermarked clips via `tikwm` API.
4. **FFmpeg/MoviePy**: Stitches clips with Hormozi-style subtitles.
5. **YouTube API**: Uploads the final .mp4 as a public Short.
6. **Supabase**: Logs the view counts and upload status.

---

## 🔒 Security & Keys
- All keys live in `.env` (copy `.env.example` to start).
- `client_secret_*.json` and `token.json` are required for YouTube uploads.
- The `supabase_db.py` handles all the data tracking.

---

