# token:
# https://developers.facebook.com/tools/explorer/
# 
from os.path import isfile
import requests
from pprint import pprint as pp 

# Replace with your actual page ID and access token
user_token = "EAACo9z7Sqe4BO6jxv8G3ZB2tYLWWRKhcAgAOYutZAUPOTJjsJvpOLAZA0Up11PZAxO3Ww9bSRW3zdp7fZCBInmeLyI9pm6EUL8h4LveX1SPSRPfjQ05lrDzPshpAZC4ZCKARh0U8uXaVDhTnoL4J3EAHHLxaWYfHYNFMsY7djepwVZCZAn9itiGWPbaIE3s8aF0y6hEWfXfiHjHZBfJNfMXlNu7mbPPCnZAOaty33ptV125"
page_token = "EAACo9z7Sqe4BO7wbW7ZCsuu5nVpOflTaZArwphttkmAcodhpP2FhwctDKajtUuWHFvCTotcZA810No1ltNyOdHdfM4ZAtLaUk2u5kWpOdBMu5RlMdUyZAIQ4xSQPxuFZBE3TwW5KnMElrTc2Lw93C3vYlMoj8ZCttrMrXOuO2bQ8ZAcvZCCm3K024lNIh6ndIjVVj6zjZCuAZC5dGwDpelJKwGfOj0qZCxOPSziJ0VyZA"

user_id = "100083627761445"


page_id = "105420925572228"

import requests
import os, time
import json

Title ="Title of the video"
title = Title
description = title

source =mp4_path= r"C:\Users\alex_\fb\downloads\Facebook.mp4"
assert isfile(source), "File not found"
files = {'source': open(source, 'rb')}
file_size = os.path.getsize(source)
print("File Size is :", file_size, "bytes")
if 1:
    def Initialize():
        
        url = f"https://graph.facebook.com/v20.0/{page_id}/video_reels?upload_phase=start"
        payload = {
            'access_token': page_token,
        }
        r = requests.post(url, data=payload)
        pp(r.json())  # print the response in a pretty format
        if r.status_code != 200:
            print("Error during initialization:", r.status_code, r.text)
            return None
        return r.json().get("video_id")




    def Upload(vidid, size, filedata):
        url = f"https://rupload.facebook.com/video-upload/v20.0/{vidid}"
        payloadUp = {
            'Authorization': 'OAuth ' + page_token,
            'offset': "0",
            'file_size': str(size),
        }

        print(payloadUp)
        r = requests.post(url, data=filedata, headers=payloadUp)
        return r.text




def _Publish(vidid, title, description):
    url = f"https://graph.facebook.com/v20.0/{page_id}/video_reels"
    payload = {
        'access_token': token,
        'upload_phase': 'finish',
        'video_id': vidid,
        'title': title,
        'description': description,
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
        status_info = r.json()
        #print("Video Status:", status_info)
        return status_info
    else:
        print("Failed to check status:", r.status_code, r.text)
        return None


def publish_reel(access_token, reel_id):
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
    
def wait_for_processing_and_publish(video_id, title, description):
    while True:
        status = check_status(video_id)
        
        if status:
            # Check if the processing has started and completed
            if status['status']['processing_phase']['status'] == 'complete':
                print("Processing complete. Now publishing...")
                publish_response =publish_reel(page_token, video_id)
                print("Publish Response:", publish_response)
                break
            else:
                print("Processing not started or in progress, waiting...")
        
        # Wait before checking again
        time.sleep(10)  # Adjust the sleep duration as needed



    
if 1:
    # Step 1: Initialize the video upload
    video_id = Initialize()
    print("Video ID:", video_id)        
#video_id="1538527150203682"
if 1:

    with open(mp4_path, 'rb') as video_file:
        upload_response = Upload(video_id, file_size, video_file)
        print("Upload Response:", upload_response)



    
if 1:
    publish_reel( page_token, video_id)     

if 1:
    # Step 4: Check the status of the video
    video_status = check_status(video_id)   
