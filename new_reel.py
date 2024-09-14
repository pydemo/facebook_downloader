import os
import requests
from os.path import isfile
from pprint import pprint as pp
from include.page_utils import set_page_access_tokens


import include.config.init_config as init_config 
apc = init_config.apc
api_version= 'v20.0'    

class CustomError(Exception):
    """Base class for custom exceptions in this module."""
    pass

class TokenExpiredError(CustomError):
    """Raised when page token is expired."""
    def __init__(self, r, json):
        self.value = r.status_code
        self.message = r.text
        self.json   = json
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}: {self.value}'

class VideoUploadIsMissingError(CustomError):
    """Raised when Video upload is missing ."""
    def __init__(self, r, json):
        self.value = r.status_code
        self.message = r.text
        self.json   = json
        super().__init__(self.message)

    def __str__(self):
        return f'{self.message}: {self.value}'
    

def init_upload():
    page_id= apc.page_id
    page_token=apc.pages[page_id].page_token
    assert page_id in apc.pages, f'Page {page_id} not found in apc.pages'
    assert page_token, f'"page_token" is not set for  {page_id}'
    url = f"https://graph.facebook.com/{api_version}/{page_id}/video_reels"
    payload = {
        'upload_phase': 'start',
        'access_token': page_token
    }

    r = requests.post(url, data=payload)
    
    
    json = r.json()
    if r.status_code == 200:
        video_id = r.json()['video_id']
    else:
        print('ERROR: initialize_upload')
        pp(json)
        
        print('Error during initialization:', r.status_code, r.text)    
        err_code= json['error']['code'] 
        err_subcode= json['error']['error_subcode']
        if err_code == 190 and err_subcode == 463:
            # Token expired
            raise TokenExpiredError(r, json['error'])
        
        raise Exception(json)
    return video_id
    


def process_upload(  file_size, file_data):
    page_id =apc.page_id    
    reel_id = apc.reel_id
    assert page_id 
    assert reel_id 
    assert file_size   
    assert file_data 
    page_token= apc.pages[page_id].page_token
    assert page_token   
    print('process_upload', page_id, reel_id, file_size)
    url = f'https://rupload.facebook.com/video-upload/{api_version}/{reel_id}'
    payload = {
        'Authorization': 'OAuth ' + page_token,
        'offset': '0',
        'file_size': str(file_size),
        'Content-Type': 'application/octet-stream'
    }
    r = requests.post(url, data=file_data, headers=payload)
    print('process_upload')
    pp(r.json())
    json = r.json()
    if r.status_code != 200:
        raise Exception(json)



    

def publish(description, publish_time=None):
    page_id, reel_id, page_token = apc.page_id, apc.reel_id, apc.get_access_token()
    assert page_id  
    assert reel_id
    assert page_token
    url = f"https://graph.facebook.com/{api_version}/{page_id}/video_reels"

    payload = {
        'access_token': page_token,
        'video_id': reel_id,
        'upload_phase': 'finish',
        'description': description,
        'privacy': '{"value":"EVERYONE"}',
        'allow_public_reshares': 'true',
    }
    if publish_time:
        payload['video_state'] = 'SCHEDULED'
        payload['scheduled_publish_time'] = publish_time
    else:
        payload['video_state'] = 'PUBLISHED'

    r = requests.post(url, data=payload)
    print('publish')
    pp(r.json())
    json = r.json()
    if r.status_code != 200:
        
        err_code= json['error']['code'] 
        err_subcode= json['error']['error_subcode']
        if err_code == 6000 and err_subcode == 1363130:
            # Token expired
            raise VideoUploadIsMissingError(r, json['error'])

        raise Exception(json)  






def main(file_path, page_id):
    video_id = init_upload(page_id)
    print(video_id)
    if 0:
            
        if isfile(file_path):
            file_size = os.path.getsize(file_path)
            file_data= open(file_path, 'rb')
            process_upload(page_id, video_id, file_size, file_data)
            publish(page_id, video_id,  '💙💛#StandWithUkraine💙💛')
        else:
            print('File not found')
        print(f'https://www.facebook.com/reel/{video_id}')    

if __name__ == '__main__':



    page_id= '105420925572228'
    api_version= 'v20.0'
    user_token= 'EAAHbeMlmZCbYBO7cq2aPB8YhLDFjZCzhBN5UJTOfo4713aJlSvhzVXyytg8rPqKF9UWMfZC22MdByFWtBsmGInt6RRZCVNnxYKDKB7T09e0d7aFHv06ZB9RX1jE5T6EmWxmih6NFLGua6WYj45dtvrEdtRDLqlQ6mXgD6QAZBlr8RYFA5GwPOI2Gt8kktHLyAlgJbi89CJTXzR4ZCF1qZBihbG5yaVN9bBAZD'


    mp4_path= r"C:\Users\alex_\myg\facebook_downloader\downloads\ArtForUkraine\backup\bbb6ef9a-9ed3-4b7b-8b5b-27281f1cc53b_Технологічна революція в Сеньківці 😎 – Серіал Будиночок на щастя.mp4"

    main(mp4_path, page_id)  