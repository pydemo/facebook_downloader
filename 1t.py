import requests
import json
from pprint import pprint as pp 
import requests
import json
import os
import requests
import json
import os
import time

def upload_video(access_token, video_file_path):
    url = "https://graph-video.facebook.com/v13.0/me/videos"
    
    with open(video_file_path, 'rb') as video_file:
        files = {'file': video_file}
        params = {
            'access_token': access_token,
            'description': 'My awesome Reel!'
        }
        
        print("Uploading video...")
        response = requests.post(url, files=files, params=params)
    
    response_json = response.json()
    print("Upload response:", json.dumps(response_json, indent=2))
    
    if 'error' in response_json:
        raise Exception(f"Error uploading video: {response_json['error']['message']}")
    
    return response_json.get('id')

def make_video_visible(access_token, video_id):
    url = f"https://graph.facebook.com/v13.0/{video_id}"
    
    params = {
        'access_token': access_token,
        'privacy': '{"value":"EVERYONE"}'  # This makes the video public
    }
    
    print("Making video visible...")
    response = requests.post(url, params=params)
    response_json = response.json()
    print("Make video visible response:", json.dumps(response_json, indent=2))
    
    if 'error' in response_json:
        raise Exception(f"Error making video visible: {response_json['error']['message']}")
    
    return response_json

def create_reel(access_token, video_id):
    url = f"https://graph.facebook.com/v13.0/{video_id}"
    
    params = {
        'access_token': access_token,
        'video_type': 'reels_video',  # Specify that this is a Reel
        'description': 'Check out my new Reel!'
    }
    
    print("Creating Reel...")
    response = requests.post(url, params=params)
    response_json = response.json()
    print("Reel creation response:", json.dumps(response_json, indent=2))
    
    if 'error' in response_json:
        raise Exception(f"Error creating Reel: {response_json['error']['message']}")
    
    return response_json

# Usage



# Usage
access_token =  'EAACo9z7Sqe4BO5DVqlZBt02AHvd4dtE4QlqNywMUrRe3tpxxtAzhJMMoXVclfZB4L3k30VTvFS3WFvrp8i2MK5iNkBJX91EyzP7ZAuFchSH4F7VTFb1nmWyKWhz1DWedDmZBeSJMZBX5kieANgws4RfQNOJ7zYTGCPXhhT12vnb8UH4FZCHNZApJCiJwcZAOjr8nYG6hZBt1xbkyX1Mf2Hvjypxg0uyFm8KUqzZBtZA'
access_token ='EAAHbeMlmZCbYBO1a9eXTdTxjGRogCW1M7ePpl0TqfeNmQUQZCIO4fKAoCc73uXRsvRHUWBOzMzDRWiWD8eZANTtlKJkP7LNsJeu1QT2whZCJZBnoJS3ZBsqJ3V4rGggePikMdfQDdN64TPCf1ZBKT9IkLEERCXCGaIUG1pwzDdvvQAB1VcPVRblvOX1Tn6QSuZCaIOhMhCPBkQPipSSoXcmETSDUfXLAYZAeZB46Np8AZDZD'
video_file_path = r"C:\Users\alex_\fb\downloads\Facebook.mp4"

video_id = upload_video(access_token, video_file_path)
make_visible_response = make_video_visible(access_token, video_id)
reel_response = create_reel(access_token, video_id)

pp(reel_response)