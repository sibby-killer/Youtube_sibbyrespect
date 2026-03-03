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

## ☁️ Automated 4x/Day Posting (via Render)

The automation schedule has been moved completely off of GitHub Actions and natively inside the Flask Dashboard using `APScheduler`. This prevents YouTube from blocking the bot due to public GitHub IP addresses.

### Posting Schedule (US Eastern Time)
The `dashboard/app.py` script automatically runs the video generation in the background at these times:

| Time | Action |
|---|---|
| 9:00 AM EST | Generate Video |
| 9:15 AM EST | Local File Cleanup |
| 12:00 PM EST | Generate Video |
| 5:00 PM EST | Generate Video |
| 9:00 PM EST | Generate Video |

*(You can also trigger it manually at any time by clicking "Generate" in the dashboard).*

---

## 🎨 Channel Branding

Edit the top of `core/ai_script.py`:

```python
CHANNEL_NAME   = "SibbyRespect"
CHANNEL_SLOGAN = "Shocking facts that change how you see the world."
HANDLE         = "@sibbyrespect"
Channel_URL    = "https://www.youtube.com/channel/UCOvhnm2NE7JAQoY8h06GyFQ"
```

---

## 🔄 How It Works

```
Reddit / Topic List
      ↓
  Groq Llama-3      → Script + Title + SEO Description + B-roll keywords
      ↓
  Edge-TTS          → MP3 voiceover + SRT word-level captions
      ↓
  yt-dlp            → Download viral B-roll (GTA / UK / US / China / Satisfying)
      ↓
  MoviePy + FFmpeg  → Stitch video + burn centered Hormozi-style captions
      ↓
  YouTube API       → Upload as public Short
      ↓
  Comment Bot       → Post + pin CTA comment
      ↓
  Supabase          → Log title, script, status, YouTube ID
      ↓
  3-Day Cleanup     → Delete local MP4, free disk space
```

---

## 📊 Admin Dashboard

Run locally at `http://127.0.0.1:5000`:

- **Overview** — stats cards + recent videos table
- **Videos** — full CRUD (edit title/status, delete)
- **Generate** — trigger a new video with live status
- **Analytics** — Chart.js views/likes/comments from Supabase

### 🌐 Hosting the Dashboard Live (For Free)

We recommend **Render.com** to host the dashboard because it supports the background threads needed for the `Generate` button. (Vercel kills background processes).

1. Push your repo to GitHub.
2. Go to [Render.com](https://render.com) and sign in with GitHub.
3. Click **New +** → **Web Service**.
4. Select your `Youtube_sibbyrespect` repository.
5. Setup the service:
   - **Name**: `sibbyrespect-admin` (or whatever you like)
   - **Language**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
6. Scroll down to **Environment Variables** and add:
   - `NEXT_PUBLIC_SUPABASE_URL` = (your Supabase URL)
   - `SUPABASE_SERVICE_ROLE_KEY` = (your Supabase key)
   - `GROQ_API_KEY` = (your Groq key)
   - `PEXELS_API_KEY` = (your Pexels key)
   - `FLASK_SECRET_KEY` = (any random secure password)
   - `YOUTUBE_TOKEN_JSON` = (paste the entire contents of your local token.json)
   - `PYTHON_VERSION` = `3.11.0`
7. Click **Create Web Service**.

Once it builds, you will have a live URL (e.g., `https://sibbyrespect-admin.onrender.com`) where you can access your dashboard from anywhere!

---

## 🔒 Security Notes

- There are **ZERO** hardcoded API keys in the Python code. Everything loads from `.env` or system variables.
- `.env`, `client_secret*.json`, and `token.json` are in `.gitignore` — they will never be pushed to GitHub.
- All production secrets live securely in **GitHub Repository Secrets** or **Render Environment Variables**.
- The Supabase service role key has full DB access — do not expose it publicly.
