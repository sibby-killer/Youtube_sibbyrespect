import os
import requests
import random
from config import PEXELS_API_KEY, TEMP_DIR

def get_pexels_video(keyword: str, min_duration: int = 5):
    """
    Finds a vertical (portrait) video on Pexels matching the keyword.
    Returns the URL of the highest quality video file or None.
    """
    if not PEXELS_API_KEY:
        print("Error: PEXELS_API_KEY not found.")
        return None

    url = "https://api.pexels.com/videos/search"
    headers = {"Authorization": PEXELS_API_KEY}
    params = {
        "query": keyword,
        "orientation": "portrait", # For Shorts/TikTok
        "per_page": 15,
        "size": "medium"
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        videos = data.get("videos", [])
        if not videos:
            print(f"No videos found for keyword: {keyword}")
            return None
            
        # Pick a random video from top results to keep it fresh
        selected_video = random.choice(videos[:5])
        
        # Get the highest quality HD link
        video_files = selected_video.get("video_files", [])
        best_link = None
        for file in video_files:
            if file["quality"] == "hd" and file["width"] >= 720:
                best_link = file["link"]
                break
                
        # Fallback to any link if HD not found
        if not best_link and video_files:
            best_link = video_files[0]["link"]
            
        return best_link
        
    except Exception as e:
        print(f"Error fetching Pexels video for '{keyword}': {e}")
        return None


def download_b_roll(keywords: list):
    """
    Downloads B-roll videos for the given keywords.
    Returns a list of absolute paths to the downloaded videos.
    """
    downloaded_files = []
    
    for i, keyword in enumerate(keywords):
        print(f"Searching B-roll for: {keyword}...")
        video_url = get_pexels_video(keyword)
        
        if video_url:
            filename = os.path.join(TEMP_DIR, f"broll_{i}.mp4")
            try:
                print(f"Downloading {keyword} to {filename}...")
                response = requests.get(video_url, stream=True)
                response.raise_for_status()
                with open(filename, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                downloaded_files.append(filename)
                print(f"Successfully downloaded {keyword}")
            except Exception as e:
                print(f"Failed to download video: {e}")
                
    return downloaded_files

if __name__ == "__main__":
    test_keywords = ["stock market chart", "laptop typing"]
    download_b_roll(test_keywords)
