import requests
import os
import time
from pprint import pprint as pp

# Replace with your actual page ID and access token
page_token = "EAACo9z7Sqe4BO7wbW7ZCsuu5nVpOflTaZArwphttkmAcodhpP2FhwctDKajtUuWHFvCTotcZA810No1ltNyOdHdfM4ZAtLaUk2u5kWpOdBMu5RlMdUyZAIQ4xSQPxuFZBE3TwW5KnMElrTc2Lw93C3vYlMoj8ZCttrMrXOuO2bQ8ZAcvZCCm3K024lNIh6ndIjVVj6zjZCuAZC5dGwDpelJKwGfOj0qZCxOPSziJ0VyZA"
page_id = "105420925572228"

def initialize_upload():
    url = f"https://graph.facebook.com/v20.0/{page_id}/video_reels?upload_phase=start"
    payload = {'access_token': page_token}
    r = requests.post(url, data=payload)
    pp(r.json())
    if r.status_code != 200:
        print("Error during initialization:", r.status_code, r.text)
        return None
    return r.json().get("video_id")

def upload_video(video_id, file_path):
    url = f"https://rupload.facebook.com/video-upload/v20.0/{video_id}"
    file_size = os.path.getsize(file_path)
    headers = {
        'Authorization': f'OAuth {page_token}',
        'offset': "0",
        'file_size': str(file_size),
    }
    with open(file_path, 'rb') as file:
        r = requests.post(url, data=file, headers=headers)
    return r.text

def check_status(video_id):
    url = f"https://graph.facebook.com/v20.0/{video_id}?fields=status&access_token={page_token}"
    r = requests.get(url)
    pp(r.json())
    if r.status_code == 200:
        return r.json()
    else:
        print("Failed to check status:", r.status_code, r.text)
        return None

def publish_reel(video_id):
    url = f"https://graph.facebook.com/v20.0/{video_id}"
    
    params = {
        "access_token": page_token,
        "fields": "status",
        "published": "true"
    }
    
    response = requests.post(url, params=params)
    pp(response.json())
    if response.status_code == 200:
        print("Reel published successfully!")
        return response.json()
    else:
        print(f"Error publishing reel: {response.text}")
        return None

def wait_for_processing_and_publish(video_id):
    max_attempts = 30  # Maximum number of attempts
    processing_started = False
    attempt = 0
    
    while attempt < max_attempts:
        status = check_status(video_id)
        
        # Get the current processing status
        processing_status = status.get('status', {}).get('processing_phase', {}).get('status')
        
        if processing_status == 'complete':
            print("Processing complete.")
            
            # Now check if the video is already published
            publishing_status = status.get('status', {}).get('publishing_phase', {}).get('status')
            if publishing_status == 'complete':
                print("Video is already published. Skipping publishing step.")
                break
            else:
                print("Now publishing...")
                time.sleep(5)  # Wait a bit before publishing
                publish_response = publish_reel(video_id)
                print("Publish Response:", publish_response)
                break
        elif processing_status == 'not_started':
            if processing_started:
                print("Processing not started, continuing to wait...")
            else:
                print("Processing not started, will check again.")
            
            # After a certain number of attempts, stop if processing doesn't start
            if attempt == max_attempts // 2:
                print("Processing did not start after waiting. Exiting.")
                break
        else:
            print("Processing in progress, waiting...")
            processing_started = True
        
        time.sleep(10)  # Wait for 10 seconds before checking again
        attempt += 1
    
    if attempt == max:
        print("Max attempts reached. Video processing took too long.")

def main():
    mp4_path = r"C:\Users\alex_\fb\downloads\Facebook.mp4"
    
    # Step 1: Initialize the video upload
    video_id = initialize_upload()
    if not video_id:
        return
    
    print("Video ID:", video_id)
    
    # Step 2: Upload the video
    upload_response = upload_video(video_id, mp4_path)
    print("Upload Response:", upload_response)
    
    # Step 3: Wait for processing and publish
    wait_for_processing_and_publish(video_id)

if __name__ == "__main__":
    main()
    if 0:
        video_id='1223714868873861'
        check_status(video_id)
        #publish_reel(video_id)