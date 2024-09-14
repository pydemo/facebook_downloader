import yt_dlp
import os, sys
import uuid
from os.path import isfile, isdir, join 
e=sys.exit
def download_facebook_video(video_url, output_path, cookie_file):
    out_fn = f'{output_path}/%(title)s.%(ext)s'
    ydl_opts = {
        'outtmpl': out_fn,
        'verbose': True,
        'cookiefile': cookie_file,
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
                    # Prepare the filename before download
                    filename = ydl.prepare_filename(info)
                    
                    # Attempt to download
                    download_result = ydl.download([video_url])
                    
                    if download_result == 0:  # 0 indicates success
                        print(f"Download successful. Result code: {download_result}")
                        return filename
                    else:
                        print(f"Download failed. Result code: {download_result}")
                else:
                    print("No formats found. The video might be private or restricted.")
            else:
                print("Failed to extract video information.")
                
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Please check the video URL, your cookie file, and your internet connection.")
            print("If the problem persists, consider reporting this issue to the yt-dlp GitHub repository.")
    
    return None 

def main():
    if len(sys.argv) < 3:
        print("Usage: python script.py <facebook_video_url> <path_to_cookie_file>")
        sys.exit(1)
    
    facebook_video_url = sys.argv[1]
    cookie_file = sys.argv[2]
    output_path = 'downloads'  # Ensure this path exists
    downloaded_file = download_facebook_video(facebook_video_url, output_path, cookie_file)
    assert downloaded_file, downloaded_file
    assert isfile(downloaded_file), downloaded_file
    if downloaded_file:
        print(f"Downloaded video: {downloaded_file}")

        
        random_prefix = str(uuid.uuid4())
        new_downloaded_file = join(output_path, f"{random_prefix}_{os.path.basename(downloaded_file)}")
        print(f"Renaming {downloaded_file} to {new_downloaded_file}")
        os.rename(downloaded_file, new_downloaded_file)

        

        latest_output_path=join('downloads','latest')  
        #move it to downloaded\latest
        if not isdir(latest_output_path):
            os.mkdir(latest_output_path)
        else:
            #if there's a file in latest move it to downloads\backup
            backup_path=join('downloads','backup')
            if not isdir(backup_path):
                os.mkdir(backup_path)
            #get list of files from  folder downloads\latest
            files = [f for f in os.listdir(latest_output_path) if isfile(join(latest_output_path, f))]    
            assert len(files) == 1, 'Latest folder should have only one file'
            latest_file=join(latest_output_path,files[0])

            
            os.rename(latest_file, join(backup_path,os.path.basename(latest_file)))
        #rename the downloaded file to have random suffix

        os.rename(new_downloaded_file, join(latest_output_path,os.path.basename(new_downloaded_file)))
    else:
        print("Failed to download the video.")

if __name__ == "__main__":
    main()