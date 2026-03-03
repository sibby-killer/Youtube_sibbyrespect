import os
import random
from yt_dlp import YoutubeDL
from config import TEMP_DIR

def download_viral_b_roll(keywords: list, clips_per_keyword: int = 2):
    """
    Downloads viral, highly-satisfying or intense clips from YouTube Shorts 
    instead of boring stock footage using yt-dlp.
    Returns:
       downloaded_files: A list of absolute paths to the downloaded videos.
       credits: A list of channel names or titles for the description.
    """
    downloaded_files = []
    credits = []
    
    for i, keyword in enumerate(keywords):
        print(f"Searching viral Shorts for: {keyword}...")
        # Search up to 40 results so we have a deep pool to randomly pick from
        search_query = f"ytsearch40:{keyword} tiktok short"
        
        def filter_shorts(info, *, incomplete):
            duration = info.get('duration')
            if duration and duration > 180:
                return 'Video is too long (not a short)'
            
            # 70% chance to skip a valid video. 
            # This forces yt-dlp to dig deep into the top 40 results 
            # instead of always grabbing the exact same top 2 videos every day.
            if random.random() < 0.70:
                return 'Randomly skipping to ensure fresh unique b-roll'
                
            return None
            
        import imageio_ffmpeg
        
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': os.path.join(TEMP_DIR, f'broll_viral_{i}_%(id)s.%(ext)s'),
            'quiet': False, # Let it print some progress natively
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'no_warnings': True,
            'match_filter': filter_shorts,
            'max_downloads': clips_per_keyword,
            'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
        }
        
        with YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(search_query, download=True)
                if 'entries' in info:
                    for entry in info['entries']:
                        if not entry:
                            continue
                        uploader = entry.get('uploader', 'Unknown Creator')
                        if uploader not in credits:
                            credits.append(uploader)
            except Exception as e:
                print(f"Failed to scrape yt-dlp for {keyword}: {e}")
                
        # Robustly discover downloaded files
        for f in os.listdir(TEMP_DIR):
            if f.startswith(f"broll_viral_{i}_") and (f.endswith(".mp4") or f.endswith(".mkv") or f.endswith(".webm")):
                full_path = os.path.join(TEMP_DIR, f)
                if full_path not in downloaded_files:
                    downloaded_files.append(full_path)
                    
    return downloaded_files, credits

if __name__ == "__main__":
    # Test
    files, creds = download_viral_b_roll(["satisfying kinetic sand", "extreme parkour trick"], clips_per_keyword=1)
    print("Files:", files)
    print("Credits:", creds)
