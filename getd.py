import yt_dlp
from typing import Optional, Dict, Any

def get_reel_description_yt_dlp(reel_url: str) -> Optional[str]:
    """
    Fetch the description of a Facebook Reel using yt-dlp.

    Args:
    reel_url (str): The URL of the Facebook Reel.

    Returns:
    Optional[str]: The Reel description if available, None if not found or on error.
    """
    ydl_opts = {
        'skip_download': True,  # We don't want to download the video, just fetch info
        'no_warnings': True,    # Suppress warnings
        'quiet': True           # Don't print progress
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info: Dict[str, Any] = ydl.extract_info(reel_url, download=False)
            return info.get('description')
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# Example usage
if __name__ == "__main__":
    reel_url = "https://www.facebook.com/reel/1153864419250467"  # Replace with actual Reel URL
    description = get_reel_description_yt_dlp(reel_url)
    if description:
        print(f"Reel Description: {description}")
    else:
        print("No description available or an error occurred.")