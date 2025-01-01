import requests
import os, time
from pprint import pprint as pp

# Replace with your actual page ID and access token
page_token = "EAACo9z7Sqe4BO7wbW7ZCsuu5nVpOflTaZArwphttkmAcodhpP2FhwctDKajtUuWHFvCTotcZA810No1ltNyOdHdfM4ZAtLaUk2u5kWpOdBMu5RlMdUyZAIQ4xSQPxuFZBE3TwW5KnMElrTc2Lw93C3vYlMoj8ZCttrMrXOuO2bQ8ZAcvZCCm3K024lNIh6ndIjVVj6zjZCuAZC5dGwDpelJKwGfOj0qZCxOPSziJ0VyZA"
user_token = "EAACo9z7Sqe4BO6jxv8G3ZB2tYLWWRKhcAgAOYutZAUPOTJjsJvpOLAZA0Up11PZAxO3Ww9bSRW3zdp7fZCBInmeLyI9pm6EUL8h4LveX1SPSRPfjQ05lrDzPshpAZC4ZCKARh0U8uXaVDhTnoL4J3EAHHLxaWYfHYNFMsY7djepwVZCZAn9itiGWPbaIE3s8aF0y6hEWfXfiHjHZBfJNfMXlNu7mbPPCnZAOaty33ptV125"

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

def _publish_reel(video_id, title, description):
    url = f"https://graph.facebook.com/v20.0/{page_id}/video_reels"
    payload = {
        'access_token': page_token,
        'upload_phase': 'finish',
        'video_id': video_id,
        'title': title,
        'description': description,
        'published': 'true',  # This should make the reel public
    }
    r = requests.post(url, data=payload)
    pp(r.json())
    if r.status_code == 200:
        print("Video published successfully!")
    else:
        print("Failed to publish video:", r.status_code, r.text)
    return r.text

def publish_reel(video_id, title, description):
    url = f"https://graph.facebook.com/v20.0/{page_id}/video_reels"
    payload = {
        'access_token': page_token,
        'upload_phase': 'finish',
        'video_id': video_id,
        'title': title,
        'description': description,
        'published': 'true',  # This should make the reel public
        'privacy': '{"value":"EVERYONE"}',  # This makes the reel visible to everyone
    }
    r = requests.post(url, data=payload)
    pp(r.json())
    if r.status_code == 200:
        print("Video published successfully!")
    else:
        print("Failed to publish video:", r.status_code, r.text)
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

def wait_for_processing_and_publish(video_id, title, description):
    while True:
        status = check_status(video_id)
        if status and status['status']['processing_phase']['status'] == 'complete':
            print("Processing complete. Now publishing...")
            publish_response = publish_reel(video_id, title, description)
            print("Publish Response:", publish_response)
            break
        else:
            print("Processing not started or in progress, waiting...")
        time.sleep(10)  # Wait for 10 seconds before checking again

def force_publish_reel(access_token, reel_id):
    url = f"https://graph.facebook.com/v20.0/{reel_id}"
    
    params = {
        "access_token": access_token,
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

def main():
    Title = "#StandWithUkraine"
    description = Title
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
    wait_for_processing_and_publish(video_id, Title, description)

if __name__ == "__main__":
    #main()
    if 1:
        video_id=reel_id='1911350766046943'
        check_status(video_id)
        #publish_reel(video_id, '#StandWithUkraine', '#ArtForUkraine')
        #force_publish_reel(page_token, reel_id)