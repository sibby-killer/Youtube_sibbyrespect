import os
from core.youtube_uploader import get_authenticated_service

if __name__ == "__main__":
    print("="*50)
    print("   REFRESHING YOUTUBE TOKEN (WITH COMMENT SCOPES)")
    print("="*50)
    print("\nStarting OAuth flow...")
    
    # Force removal of old token if it exists to ensure new scopes are requested
    if os.path.exists("token.json"):
        os.remove("token.json")
        print("Removed old token.json to request new permissions.")

    service = get_authenticated_service()
    
    if service:
        print("\n" + "="*50)
        print("   SUCCESS! New token.json created.")
        print("="*50)
        print("\nACTION REQUIRED:")
        print("1. Open 'token.json' in your project folder.")
        print("2. Copy the ENTIRE content of that file.")
        print("3. Go to your GitHub repository -> Settings -> Secrets -> Actions.")
        print("4. Update 'YOUTUBE_TOKEN_JSON' with the new content.")
    else:
        print("\nFailed to generate a new token.")
