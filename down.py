import yt_dlp
import sys

def download_facebook_video(video_url, output_path, cookie_file):
    ydl_opts = {
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
        'verbose': True,
        'cookiefile': cookie_file,  # Use the cookie file
        'format': 'best',
        'no_warnings': False,
        'ignoreerrors': False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(video_url, download=False)
            
            if info:
                print(f"Video title: {info.get('title', 'Unknown')}")
                print(f"Available formats: {len(info.get('formats', []))}")
                
                if info.get('formats'):
                    ydl.download([video_url])
                else:
                    print("No formats found. The video might be private or restricted.")
            else:
                print("Failed to extract video information.")
                
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Please check the video URL, your cookie file, and your internet connection.")
            print("If the problem persists, consider reporting this issue to the yt-dlp GitHub repository.")

def main():
    if len(sys.argv) < 3:
        print("Usage: python script.py <facebook_video_url> <path_to_cookie_file>")
        sys.exit(1)
    
    facebook_video_url = sys.argv[1]
    cookie_file = sys.argv[2]
    output_path = './downloads'  # Ensure this path exists
    download_facebook_video(facebook_video_url, output_path, cookie_file)

if __name__ == "__main__":
    main()