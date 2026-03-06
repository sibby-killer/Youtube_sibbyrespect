import os
import glob
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.http import MediaFileUpload
from config import BASE_DIR

# Scope required for uploading videos
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]
TOKEN_FILE = os.path.join(BASE_DIR, "token.json")

def _find_client_secret():
    """Find the client_secret*.json file automatically."""
    matches = glob.glob(os.path.join(BASE_DIR, "client_secret*.json"))
    return matches[0] if matches else None

def get_authenticated_service():
    """
    Authenticates the user and returns the YouTube API service object.
    Supports both local token.json file and YOUTUBE_TOKEN_JSON environment variable (for GitHub Actions).
    """
    credentials = None
    client_secrets_file = _find_client_secret()
    
    # 1. Check for YOUTUBE_TOKEN_JSON environment variable (Highest priority for Cloud/CI)
    env_token = os.getenv("YOUTUBE_TOKEN_JSON")
    if env_token:
        # Debugging (safely)
        stripped_token = env_token.strip()
        print(f"YOUTUBE_TOKEN_JSON env var found (Length: {len(env_token)})")
        
        # Auto-fix: if the user pasted it with literal single/double quotes at start/end
        if (stripped_token.startswith("'") and stripped_token.endswith("'")) or \
           (stripped_token.startswith('"') and stripped_token.endswith('"')):
            print("Detected literal quotes surrounding the token. Stripping them...")
            stripped_token = stripped_token[1:-1].strip()

        if not stripped_token:
            print("WARNING: YOUTUBE_TOKEN_JSON is empty after stripping.")
        
        try:
            import json
            token_info = json.loads(stripped_token)
            credentials = Credentials.from_authorized_user_info(token_info, SCOPES)
            print("Authenticated using YOUTUBE_TOKEN_JSON environment variable.")
        except Exception as e:
            print(f"Error parsing YOUTUBE_TOKEN_JSON env var: {e}")
            # Show a tiny non-sensitive snippet to see what's actually in there (is it HTML? is it text?)
            snippet = stripped_token[:30].replace("\n", "\\n")
            print(f"RAW Snippet (first 30 chars): [{snippet}]")
    else:
        print("YOUTUBE_TOKEN_JSON is NOT set in environment variables.")

    # 2. Check for local token.json file (Fallback for local dev)
    if not credentials and os.path.exists(TOKEN_FILE):
        credentials = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
        print("Authenticated using local token.json file.")
        
    # If there are no (valid) credentials available, let the user log in.
    if not credentials or not credentials.valid:
        if credentials and credentials.expired and credentials.refresh_token:
            print("Refreshing YouTube access token...")
            try:
                credentials.refresh(Request())
            except Exception as e:
                print(f"Token refresh failed: {e}. Might need new client_secret or manual login.")
                credentials = None
        
        # If still no valid credentials, we need the client_secret to start new flow
        if not credentials:
            if not client_secrets_file:
                print("ERROR: Authentication failed. No valid token (env or file) and no client_secret*.json to start login flow.")
                return None
                
            print(f"Starting Google OAuth 2.0 flow using: {os.path.basename(client_secrets_file)}")
            print("Watch your browser window...")
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secrets_file, SCOPES)
            
            # Opens a local server on port 8080 to receive the OAuth callback
            credentials = flow.run_local_server(port=8080)
            
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'w') as token:
            token.write(credentials.to_json())

    return googleapiclient.discovery.build("youtube", "v3", credentials=credentials)


def sanitize_text(text):
    """
    Strips out characters strictly forbidden by the YouTube API in snippets.
    Specifically angles brackets < and > which cause 400 invalidDescription.
    """
    if not text:
        return ""
    # Remove angle brackets
    clean = text.replace("<", "").replace(">", "")
    # Trim to allowed lengths
    return clean

def upload_video(youtube, file_path, title, description, tags, privacy_status="private"):
    """
    Uploads a video to YouTube.
    For Shorts, if the title or description contains #shorts and it's under 60 seconds,
    YouTube automatically registers it as a Short.
    """
    print(f"Preparing to upload: {title}")
    
    # Sanitize inputs to prevent 400 Bad Request
    safe_title = sanitize_text(title)[:100]
    safe_description = sanitize_text(description)[:5000]
    safe_tags = [sanitize_text(t)[:500] for t in (tags or [])]

    body = {
        "snippet": {
            "title": safe_title,
            "description": safe_description,
            "tags": safe_tags,
            "categoryId": "22" # 22 = People & Blogs
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False
        }
    }

    # Use chunked resumable upload
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True, mimetype="video/mp4")

    # Creates the API request
    request = youtube.videos().insert(
        part=",".join(body.keys()),
        body=body,
        media_body=media
    )

    print("Uploading video... This might take a few minutes dependings on internet speed.")
    response = None
    
    try:
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"Uploaded {int(status.progress() * 100)}%")
                
        print("\nUPLOAD COMPLETE!")
        print(f"Video ID : {response.get('id')}")        
        print(f"Video URL: https://youtu.be/{response.get('id')}")
        return response.get("id")

    except googleapiclient.errors.HttpError as e:
        print(f"An HTTP error {e.resp.status} occurred:\n{e.content}")
        return None
    except Exception as e:
        print(f"Unexpected upload error: {e}")
        return None


if __name__ == "__main__":
    # Test block
    print("Testing YouTube API Authentication...")
    youtube_service = get_authenticated_service()
    if youtube_service:
        print("Successfully authenticated!")
    else:
        print("Authentication failed.")
