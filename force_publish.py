import requests
import os, time
from pprint import pprint as pp



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

def publish_reel(video_id, title,  description):
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
    
    # Step 1: Initialize the video upload
    video_id = initialize_upload()
    if not video_id:
        return
    
    print("Video ID:", video_id)
    
    # Step 2: Upload the video
    upload_response = upload_video(video_id, video_file_path)
    print("Upload Response:", upload_response)
    
    publish_reel(video_id, title, reel_description)
    force_publish_reel(page_token, video_id)

    # Step 3: Wait for processing and publish
    #wait_for_processing_and_publish(video_id, Title, description)

if __name__ == "__main__":

    title = "#StandWithUkraine"

    page_id = "105420925572228"

    reel_description = '💙💛#StandWithUkraine💙💛'


    # Usage
    #access_token =  'EAACo9z7Sqe4BO5DVqlZBt02AHvd4dtE4QlqNywMUrRe3tpxxtAzhJMMoXVclfZB4L3k30VTvFS3WFvrp8i2MK5iNkBJX91EyzP7ZAuFchSH4F7VTFb1nmWyKWhz1DWedDmZBeSJMZBX5kieANgws4RfQNOJ7zYTGCPXhhT12vnb8UH4FZCHNZApJCiJwcZAOjr8nYG6hZBt1xbkyX1Mf2Hvjypxg0uyFm8KUqzZBtZA'
    page_token ='EAAHbeMlmZCbYBO6SZCrdMZCx2LPNZC83ZCWeS6WZBFcwxwIIgaR1Cp0QOssEiq28WDPAxSEH7Pa1dhejZAryU0naiKSZArcxemdlZAmeHCnSKSYZB80nPZBQGpZCqYyjMAIdii83cS24RgbcCXR4CzyjSp10bGl8DLToQwTz6pp6Eloox2trNFfdZBx9evByA9I56dx82K8w3MOvhrwTTlgXZB6k4v39fl5IZCv20d0pVZCvKwZDZD'
    video_file_path = mp4_path= r"C:\Users\alex_\myg\facebook_downloader\downloads\Any\latest\8d47017a-29a6-411d-92f6-3c9099f26025_Video.mp4"

    #main()
    video_id=reel_id='371622969315582'
    if 1:
        #publish_reel(video_id, title, reel_description)
        force_publish_reel(page_token, video_id)
    if 0:
        
        check_status(video_id)
        #publish_reel(video_id, '#StandWithUkraine', '#ArtForUkraine')
        #force_publish_reel(page_token, reel_id)
