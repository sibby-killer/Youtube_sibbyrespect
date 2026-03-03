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
        # Search up to 20 results to build a pool to pick from
        search_query = f"ytsearch20:{keyword} tiktok short"
        
        # Step 1: Extract info WITHOUT downloading to get the list of videos
        import imageio_ffmpeg
        
        extract_opts = {
            'quiet': True,
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'no_warnings': True,
            'extract_flat': True, # Only extract metadata, don't download yet
        }
        
        video_urls = []
        with YoutubeDL(extract_opts) as ydl:
            try:
                info = ydl.extract_info(search_query, download=False)
                if info and 'entries' in info:
                    for entry in info['entries']:
                        if entry and entry.get('url'):
                            # Ensure it's a short (heuristic: duration < 180s if available)
                            # extract_flat might not have duration, so we just grab URLs
                            video_urls.append(entry.get('url'))
                            
                            uploader = entry.get('uploader', 'Unknown Creator')
                            if uploader not in credits:
                                credits.append(uploader)
            except Exception as e:
                print(f"Failed to extract info for {keyword}: {e}")
                
        if not video_urls:
            print(f"No videos found for {keyword}")
            continue
            
        # Step 2: Randomize the pool! This prevents repeating the exact same top clips.
        random.shuffle(video_urls)
        selected_urls = video_urls[:clips_per_keyword]
        
        # Step 3: Download ONLY the randomly selected URLs
        for j, url in enumerate(selected_urls):
            print(f"Downloading randomized pick {j+1}/{clips_per_keyword} for '{keyword}'...")
            
            # Use original rigorous filter to ensure it's actually a short
            def filter_shorts(info, *, incomplete):
                duration = info.get('duration')
                if duration and duration > 180:
                    return 'Video is too long (not a short)'
                return None
            
            download_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
                'outtmpl': os.path.join(TEMP_DIR, f'broll_viral_{i}_{j}_%(id)s.%(ext)s'),
                'quiet': False,
                'nocheckcertificate': True,
                'ignoreerrors': True,
                'no_warnings': True,
                'match_filter': filter_shorts,
                'ffmpeg_location': imageio_ffmpeg.get_ffmpeg_exe(),
            }
            
            with YoutubeDL(download_opts) as ydl:
                try:
                    ydl.download([url])
                except Exception as e:
                    print(f"Failed to download URL {url}: {e}")
                
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
