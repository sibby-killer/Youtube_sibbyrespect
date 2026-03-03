"""
scheduler.py — SibbyRespect
Single-run orchestrator called by GitHub Actions 4× per day at US EST times.
Also runs cleanup once daily (on the 9AM run).
"""
import os
import sys
import datetime

# Make sure the project root is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import create_short
from core.cleanup import run_cleanup

# GitHub Actions sets this via environment on the 09:00 UTC run
RUN_CLEANUP_ON_THIS_RUN = os.getenv("RUN_CLEANUP", "false").lower() == "true"


def main():
    run_time = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    print(f"\n{'='*50}")
    print(f"  SibbyRespect Scheduler — {run_time}")
    print(f"{'='*50}\n")

    # Run cleanup pass first (only on the wake marked for cleanup)
    if RUN_CLEANUP_ON_THIS_RUN:
        print("Running 3-day cleanup pass...")
        run_cleanup()

    # Generate and upload one Short
    success = create_short()

    if success:
        print("\nScheduler run COMPLETE — video generated and uploaded.")
        sys.exit(0)
    else:
        print("\nScheduler run FAILED.")
        sys.exit(1)


if __name__ == "__main__":
    main()
