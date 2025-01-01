import requests
import json
from pprint import pprint as pp 
import requests
import json
import os
import time

def check_token_permissions(access_token):
    url = f"https://graph.facebook.com/v13.0/debug_token"
    params = {
        'input_token': access_token,
        'access_token': access_token
    }
    response = requests.get(url, params=params)
    response_json = response.json()
    print("Token info:", json.dumps(response_json, indent=2))
    return response_json

def upload_reel(access_token, video_file_path, description):
    url = "https://graph-video.facebook.com/v13.0/me/video_reels"
    
    with open(video_file_path, 'rb') as video_file:
        files = {'video_file': video_file}
        params = {
            'access_token': access_token,
            'description': description
        }
        
        print("Uploading Reel...")
        response = requests.post(url, files=files, params=params)
    
    response_json = response.json()
    print("Upload response:", json.dumps(response_json, indent=2))
    
    if 'error' in response_json:
        raise Exception(f"Error uploading Reel: {response_json['error']['message']}")
    
    return response_json.get('id')  # Facebook returns 'id' for the video_id

def check_reel_status(access_token, video_id):
    url = f"https://graph.facebook.com/v13.0/{video_id}"
    
    params = {
        'access_token': access_token,
        'fields': 'id,description,permalink_url,status'
    }
    
    print("Checking Reel status...")
    response = requests.get(url, params=params)
    response_json = response.json()
    print("Reel status response:", json.dumps(response_json, indent=2))
    
    if 'error' in response_json:
        raise Exception(f"Error checking Reel status: {response_json['error']['message']}")
    
    return response_json

def wait_for_reel_publishing(access_token, video_id, max_attempts=20, delay=10):
    for attempt in range(max_attempts):
        reel_status = check_reel_status(access_token, video_id)
        status = reel_status.get('status', {})
        
        if status.get('publishing_phase', {}).get('status') == 'complete':
            print("Reel has been successfully published!")
            return reel_status
        
        print(f"Attempt {attempt + 1}/{max_attempts}: Reel is still being processed. Waiting {delay} seconds...")
        time.sleep(delay)
    
    print("Maximum attempts reached. The Reel may still be processing.")
    return reel_status




reel_description = '💙💛#StandWithUkraine💙💛'


# Usage

access_token ='EAAHbeMlmZCbYBO6SZCrdMZCx2LPNZC83ZCWeS6WZBFcwxwIIgaR1Cp0QOssEiq28WDPAxSEH7Pa1dhejZAryU0naiKSZArcxemdlZAmeHCnSKSYZB80nPZBQGpZCqYyjMAIdii83cS24RgbcCXR4CzyjSp10bGl8DLToQwTz6pp6Eloox2trNFfdZBx9evByA9I56dx82K8w3MOvhrwTTlgXZB6k4v39fl5IZCv20d0pVZCvKwZDZD'
video_file_path = r"C:\Users\alex_\fb\downloads\Video.mp4"
if 0:
    
    print("Checking token permissions...")
    token_info = check_token_permissions(access_token)
    
    if 'data' in token_info and 'scopes' in token_info['data']:
        print("Token has the following permissions:", ', '.join(token_info['data']['scopes']))
    else:
        print("Unable to retrieve token permissions.")
    if 0:
        video_id = upload_reel(access_token, video_file_path, reel_description)
        print(f"Reel uploaded successfully. Video ID: {video_id}")
        
        final_status = wait_for_reel_publishing(access_token, video_id)
        
        if 'permalink_url' in final_status:
            print(f"Reel URL: {final_status['permalink_url']}")
        else:
            print("Reel URL not available yet.")
        
        print("Final Reel status:", json.dumps(final_status.get('status', {}), indent=2))
if 1:    
    video_id='371622969315582'
    reel_status = check_reel_status(access_token, video_id)

    if 'status' in reel_status:
        print(f"Reel status: {reel_status['status']}")
        if 'permalink_url' in reel_status:
            print(f"Reel URL: {reel_status['permalink_url']}")
    else:
        print("Unable to determine Reel status.")
    
