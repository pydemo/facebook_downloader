import requests
import json
from pprint import pprint as pp 

def upload_video(access_token, video_file_path):
    url = f"https://graph-video.facebook.com/v13.0/me/videos"
    
    with open(video_file_path, 'rb') as video_file:
        files = {'video_file': video_file}
        params = {
            'access_token': access_token,
            'description': 'My awesome Reel!',
        }
        
        response = requests.post(url, files=files, params=params)
        print('upload_video')
        pp(response.json())
    return json.loads(response.text)['id']

def create_reel(access_token, video_id):
    url = f"https://graph.facebook.com/v13.0/me/video_reels"
    
    params = {
        'access_token': access_token,
        'video_id': video_id,
        'description': 'Check out my new Reel!',
        'audio_source_id': 'ORIGINAL_SOUND'
    }
    
    response = requests.post(url, params=params)
    print('create_reel')
    pp(response.json())
    return json.loads(response.text)

# Usage
access_token =  'EAACo9z7Sqe4BOZBEj5jaX2uhLNPZBMtSKUfIHKO5X5npNRlFePdYZClj98SZCYBDo6WWg05y3BmKtCH2it7amlpbeZCuNaK2qBPhJrQ3TGMRFZAe72pfFrZAQNeWyGBGEaZCnlgC8FCCsIRw9LW90QELoHBRai67rERnZARrpSj2lAJ3h8ynRUu30viFxLnZCOpHauCbJMZCrxwMtup26tA6rSR0u57cc0YZBGZCyBjim'
video_file_path = r"C:\Users\alex_\fb\downloads\Facebook.mp4"

video_id = upload_video(access_token, video_file_path)
reel_response = create_reel(access_token, video_id)

print(f"Reel created successfully. Reel ID: {reel_response['id']}")