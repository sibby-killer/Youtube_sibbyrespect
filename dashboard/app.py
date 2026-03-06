"""
SibbyRespect Admin Dashboard — Flask App
Routes: overview, video CRUD, analytics, generate trigger
"""
import os
import sys
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, redirect, url_for, request, jsonify, flash
from config import FLASK_SECRET_KEY, SUPABASE_URL, SUPABASE_KEY
import atexit
import threading
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

# ─────────────────────────────────────────────────────────────────────────────
# Scheduler Setup (Runs natively on Render to replace GitHub Actions)
# ─────────────────────────────────────────────────────────────────────────────
def run_scheduled_generation():
    print("[SCHEDULER] Triggering automatic video generation...")
    try:
        from main import create_short
        create_short()
    except Exception as e:
        print(f"[SCHEDULER ERORR] Daily run failed: {e}")

# Only start the scheduler if we are running in the main Render thread
# (This prevents starting double schedulers in debug mode)
scheduler = None
_scheduler_started = False

def _boot_scheduler():
    import time
    time.sleep(3) # Wait for Gunicorn fork and request pipeline to warm up
    global scheduler, _scheduler_started
    if _scheduler_started:
        return
        
    try:
        scheduler = BackgroundScheduler(timezone=pytz.timezone('US/Eastern'))
        
        # 9:00 AM EST 
        scheduler.add_job(func=run_scheduled_generation, trigger=CronTrigger(hour=9, minute=0))
        # 12:00 PM EST
        scheduler.add_job(func=run_scheduled_generation, trigger=CronTrigger(hour=12, minute=0))
        # 5:00 PM EST
        scheduler.add_job(func=run_scheduled_generation, trigger=CronTrigger(hour=17, minute=0))
        # 9:00 PM EST
        scheduler.add_job(func=run_scheduled_generation, trigger=CronTrigger(hour=21, minute=0))
        
        def run_scheduled_cleanup():
            print("[SCHEDULER] Triggering daily video cleanup...")
            try:
                from core.cleanup import run_cleanup
                run_cleanup()
            except Exception as e:
                print(f"[SCHEDULER ERROR] Cleanup failed: {e}")
                
        scheduler.add_job(func=run_scheduled_cleanup, trigger=CronTrigger(hour=9, minute=15))
        
        scheduler.start()
        _scheduler_started = True
        print("[SCHEDULER] Started securely in background thread.")
    except Exception as e:
        print(f"[SCHEDULER CRITICAL] Failed to boot up: {e}")

# Boot the scheduler asynchronously so it doesn't block the first web request.
threading.Thread(target=_boot_scheduler, daemon=True).start()

# ─────────────────────────────────────────────────────────────────────────────

def get_db():
    from core.supabase_db import supabase
    return supabase

# ── Overview / Home ───────────────────────────────────────────────────────────

@app.route("/")
def index():
    db = get_db()
    stats = {"total": 0, "uploaded": 0, "generated": 0, "cleaned": 0}
    recent = []
    if db:
        try:
            all_rows = db.table("videos").select("id, status").execute().data or []
            stats["total"] = len(all_rows)
            for r in all_rows:
                s = r.get("status", "")
                if s in stats:
                    stats[s] += 1

            recent = db.table("videos") \
                .select("*") \
                .order("created_at", desc=True).limit(5).execute().data or []
        except Exception as e:
            flash(f"DB error: {e}", "danger")

    return render_template("index.html", stats=stats, recent=recent)

# ── Videos CRUD ───────────────────────────────────────────────────────────────

@app.route("/videos")
def videos():
    db = get_db()
    rows = []
    if db:
        try:
            rows = db.table("videos") \
                .select("*") \
                .order("created_at", desc=True) \
                .execute().data or []
        except Exception as e:
            flash(f"DB error: {e}", "danger")
    return render_template("videos.html", videos=rows)


@app.route("/videos/delete/<int:vid_id>", methods=["POST"])
def delete_video(vid_id):
    db = get_db()
    if db:
        try:
            row = db.table("videos").select("local_path").eq("id", vid_id).single().execute()
            path = row.data.get("local_path") if row.data else None
            if path and os.path.exists(path):
                os.remove(path)
            db.table("videos").delete().eq("id", vid_id).execute()
            flash(f"Video {vid_id} deleted.", "success")
        except Exception as e:
            flash(f"Delete error: {e}", "danger")
    return redirect(url_for("videos"))


@app.route("/videos/update/<int:vid_id>", methods=["POST"])
def update_video(vid_id):
    db = get_db()
    if db:
        new_title = request.form.get("title", "").strip()
        new_status = request.form.get("status", "").strip()
        if new_title or new_status:
            update = {}
            if new_title:  update["title"]  = new_title
            if new_status: update["status"] = new_status
            try:
                db.table("videos").update(update).eq("id", vid_id).execute()
                flash("Video updated.", "success")
            except Exception as e:
                flash(f"Update error: {e}", "danger")
    return redirect(url_for("videos"))

# ── Automation & Generation (async, non-blocking) ────────────────────────────

_generation_status = {"running": False, "message": "Idle", "logs": []}

def _progress_callback(msg):
    global _generation_status
    _generation_status["message"] = msg
    _generation_status["logs"].append(msg)
    # Keep logs from growing infinitely
    if len(_generation_status["logs"]) > 100:
        _generation_status["logs"] = _generation_status["logs"][-100:]

def _run_generation(topic=None):
    global _generation_status
    _generation_status = {"running": True, "message": "Generating video...", "logs": ["Started manual format..."]}
    try:
        from main import create_short
        ok = create_short(topic=topic or None, progress_callback=_progress_callback)
        _generation_status["running"] = False
        _generation_status["message"] = "Done! Video uploaded." if ok else "Generation failed."
        _generation_status["logs"].append(_generation_status["message"])
    except Exception as e:
        _generation_status["running"] = False
        _generation_status["message"] = f"CRITICAL ERROR: {e}"
        _generation_status["logs"].append(f"Error: {e}")


@app.route("/automation", methods=["GET", "POST"])
def automation():
    global _generation_status
    if request.method == "POST":
        if _generation_status["running"]:
            flash("A generation is already in progress!", "warning")
        else:
            topic = request.form.get("topic", "").strip() or None
            thread = threading.Thread(target=_run_generation, args=(topic,), daemon=True)
            thread.start()
            flash("Video generation started in the background!", "info")
    return render_template("automation.html", status=_generation_status)


@app.route("/api/generation-status")
def generation_status():
    return jsonify(_generation_status)


@app.route("/api/scheduler/status")
def scheduler_status():
    try:
        state = "running" if scheduler and scheduler.state == 1 else "paused"
        jobs = []
        if scheduler:
            for job in scheduler.get_jobs():
                jobs.append({
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None
                })
        return jsonify({"state": state, "jobs": jobs, "server_time": datetime.now(pytz.timezone('US/Eastern')).isoformat()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/scheduler/toggle", methods=["POST"])
def scheduler_toggle():
    try:
        action = request.json.get("action")
        if not scheduler:
            return jsonify({"error": "Scheduler not initialized"}), 500
            
        if action == "pause":
            scheduler.pause()
            return jsonify({"status": "paused"})
        elif action == "resume":
            scheduler.resume()
            return jsonify({"status": "running"})
        return jsonify({"error": "Invalid action"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── Analytics ─────────────────────────────────────────────────────────────────

@app.route("/analytics")
def analytics():
    db = get_db()
    chart_data = {"labels": [], "views": [], "likes": [], "comments": []}
    if db:
        try:
            rows = db.table("videos") \
                .select("*") \
                .eq("status", "uploaded") \
                .order("created_at", desc=True).limit(10).execute().data or []
            for r in rows:
                label = (r.get("title") or "")[:30]
                chart_data["labels"].append(label)
                chart_data["views"].append(r.get("views") or 0)
                chart_data["likes"].append(r.get("likes") or 0)
                chart_data["comments"].append(r.get("comments") or 0)
        except Exception as e:
            flash(f"Analytics error: {e}", "danger")

    return render_template("analytics.html", chart_data=chart_data)


# ── JSON API ──────────────────────────────────────────────────────────────────

@app.route("/api/videos")
def api_videos():
    db = get_db()
    if not db:
        return jsonify([])
    try:
        rows = db.table("videos").select("*").order("created_at", desc=True).limit(50).execute().data or []
        return jsonify(rows)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
