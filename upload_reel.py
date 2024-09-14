# token:
# https://developers.facebook.com/tools/explorer/
# 
from os.path import isfile
import requests
from pprint import pprint as pp 

# Replace with your actual page ID and access token
token = "EAACo9z7Sqe4BOZBEj5jaX2uhLNPZBMtSKUfIHKO5X5npNRlFePdYZClj98SZCYBDo6WWg05y3BmKtCH2it7amlpbeZCuNaK2qBPhJrQ3TGMRFZAe72pfFrZAQNeWyGBGEaZCnlgC8FCCsIRw9LW90QELoHBRai67rERnZARrpSj2lAJ3h8ynRUu30viFxLnZCOpHauCbJMZCrxwMtup26tA6rSR0u57cc0YZBGZCyBjim"
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
            'access_token': token,
        }
        r = requests.post(url, data=payload)
        pp(r.json())  # print the response in a pretty format
        if r.status_code != 200:
            print("Error during initialization:", r.status_code, r.text)
            return None
        return r.json().get("video_id")




    def Upload(vidid, size, filedata):
        url = f"https://rupload.facebook.com/video-upload/v13.0/{vidid}"
        payloadUp = {
            'Authorization': 'OAuth ' + token,
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


def Publish(vidid, title, description):
    url = f"https://graph.facebook.com/v20.0/{page_id}/video_reels"
    payload = {
        'access_token': token,
        'upload_phase': 'finish',
        'video_id': vidid,
        'title': title,
        'description': description,
        'published': True  # Ensure that the video is published, not saved as a draft
    }
    r = requests.post(url, data=payload)
    if r.status_code == 200:
        print("Video published successfully!")
    else:
        print("Failed to publish video:", r.status_code, r.text)
    return r.text


def check_status(video_id):
    url = f"https://graph.facebook.com/v20.0/{video_id}?fields=status&access_token={token}"
    
    r = requests.get(url)
    pp(r.json())
    if r.status_code == 200:
        status_info = r.json()
        #print("Video Status:", status_info)
        return status_info
    else:
        print("Failed to check status:", r.status_code, r.text)
        return None
def wait_for_processing_and_publish(video_id, title, description):
    while True:
        status = check_status(video_id)
        
        if status:
            # Check if the processing has started and completed
            if status['status']['processing_phase']['status'] == 'complete':
                print("Processing complete. Now publishing...")
                publish_response = Publish(video_id, title, description)
                print("Publish Response:", publish_response)
                break
            else:
                print("Processing not started or in progress, waiting...")
        
        # Wait before checking again
        time.sleep(10)  # Adjust the sleep duration as needed

def get_reels( since: str | int = None, until: str | int = None):
    url = f'https://graph.facebook.com/v20.0/{page_id}/video_reels'
    params = {
        'access_token': token,
        'since': since,
        'until': until
    }
    r = requests.get(url, params=params)
    pp(r.json())
    #reels = self._json_to_reels()
    #return reels
def get_reels_2( since: str | int = None, until: str | int = None):
        url = f'https://graph.facebook.com/v20.0/{page_id}/video_reels'
        params = {
            'access_token': token,
            'since': since,
            'until': until
        }

        reels = []
        pid=1
        while url:
            print(f"Fetching reels batch {pid}...")
            r = requests.get(url, params=params)
            json = r.json()

            # Append the current batch of reels to the main list
            reels.extend(_json_to_reels(json))

            # Check if there is a 'next' page
            paging = json.get('paging', {})
            url = paging.get('next')  # Update the URL to the 'next' page if available

            # Clear params after the first request since subsequent requests use the 'next' URL directly
            params = {}
            pid += 1

        return reels

def publish_draft_reel(reel_id, access_token):
    url = f'https://graph.facebook.com/v20.0/{reel_id}'
    payload = {
        'access_token': access_token,
        'is_published': True  # This flag changes the draft to a published post
    }
    r = requests.post(url, data=payload)
    pp(r.json())
    if r.status_code == 200:
        print("Draft reel published successfully!")
    else:
        print("Failed to publish draft reel:", r.status_code, r.text)


class Reel:
    def __init__(self, description: str, file_path: str = '', updated_time: str = None, id: str = None):
        self.id = id
        self.file_path = file_path
        self.description = description
        self.updated_time = updated_time

        if file_path:
            self.file_size = os.path.getsize(file_path)
            with open(file_path, 'rb') as file:
                self.file_data = file.read()
        else:
            self.file_size = None
            self.file_data = None

    def __str__(self):
        return f'Reel: {self.id} {self.description}'
    
def _json_to_reels(json):
    reels_data = json['data']
    #pp(json)
    reels = []
    for reel_data in reels_data:
        #pp(reel_data)
        reel = Reel(
            description=reel_data.get('description', 'not processed'),
            id=reel_data['id'],
            updated_time=reel_data['updated_time']
        )
        reels.append([reel_data.get('description', 'not processed'),
            reel_data['id'],
            reel_data['updated_time']])

    return reels




def publish_reel_immediately(reel_id, access_token):
    url = f'https://graph.facebook.com/v20.0/{reel_id}'
    
    payload = {
        'access_token': access_token,
        'is_published': True  # Immediately publish the reel
    }

    r = requests.post(url, data=payload)
    pp(r.json())
    if r.status_code == 200:
        print("Reel published immediately!")
    else:
        print("Failed to publish reel:", r.status_code, r.text)




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



def get_reel_data(access_token, reel_id):
    url = f"https://graph.facebook.com/v20.0/{reel_id}"
    
    params = {
        "access_token": access_token,
        "fields": "id,created_time,description,comments.limit(0).summary(true),likes.limit(0).summary(true),views"
    }
    
    response = requests.get(url, params=params)
    pp(response.json())
    if response.status_code == 200:
        reel_data = response.json()
        
        # Extract relevant information
        reel_info = {
            "id": reel_data.get("id"),
            "created_time": reel_data.get("created_time"),
            "description": reel_data.get("description"),
            "comment_count": reel_data.get("comments", {}).get("summary", {}).get("total_count", 0),
            "like_count": reel_data.get("likes", {}).get("summary", {}).get("total_count", 0),
            "view_count": reel_data.get("views", 0)
        }
        
        return reel_info
    else:
        print(f"Error getting reel info: {response.text}")
        return None




def get_reel_metadata_and_targeting(access_token, reel_id):
    url = f"https://graph.facebook.com/v20.0/{reel_id}"
    
    params = {
        "access_token": access_token,
        "fields": "id,created_time,description,comments.limit(0).summary(true),likes.limit(0).summary(true),views,privacy,status,permalink_url,from,place,is_crossposting_eligible"
    }
    
    response = requests.get(url, params=params)
    pp(response.json())
    if response.status_code == 200:
        reel_data = response.json()
        
        # Extract relevant information
        reel_info = {
            "Metadata": {
                "id": reel_data.get("id"),
                "created_time": reel_data.get("created_time"),
                "description": reel_data.get("description"),
                "comment_count": reel_data.get("comments", {}).get("summary", {}).get("total_count", 0),
                "like_count": reel_data.get("likes", {}).get("summary", {}).get("total_count", 0),
                "view_count": reel_data.get("views", 0),
                "status": reel_data.get("status", {}),
                "permalink_url": reel_data.get("permalink_url"),
                "from": reel_data.get("from", {}),
                "place": reel_data.get("place"),
                "is_crossposting_eligible": reel_data.get("is_crossposting_eligible"),
                "crossposting_status": reel_data.get("crossposting_status", {})
            },
            "Targeting": reel_data.get("targeting", {}),
            "Privacy": reel_data.get("privacy", {})
        }
        
        return reel_info
    else:
        print(f"Error getting reel info: {response.text}")
        return None



def get_reel_metadata_with_location(access_token, reel_id):
    url = f"https://graph.facebook.com/v20.0/{reel_id}"
    
    params = {
        "access_token": access_token,
        "fields": "id,created_time,description,comments.limit(0).summary(true),likes.limit(0).summary(true),views,permalink_url,from,place"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        pp(response.json())
        reel_data = response.json()
        
        # Extract relevant information
        reel_info = {
            "id": reel_data.get("id"),
            "created_time": reel_data.get("created_time"),
            "description": reel_data.get("description"),
            "comment_count": reel_data.get("comments", {}).get("summary", {}).get("total_count", 0),
            "like_count": reel_data.get("likes", {}).get("summary", {}).get("total_count", 0),
            "view_count": reel_data.get("views", 0),
            "permalink_url": reel_data.get("permalink_url"),
            "from": reel_data.get("from", {}),
            "location": {}
        }
        
        # Extract location information
        place = reel_data.get("place", {})
        if place:
            reel_info["location"] = {
                "name": place.get("name"),
                "id": place.get("id")
            }
            location = place.get("location", {})
            if location:
                reel_info["location"].update({
                    "city": location.get("city"),
                    "country": location.get("country"),
                    "latitude": location.get("latitude"),
                    "longitude": location.get("longitude"),
                    "street": location.get("street"),
                    "zip": location.get("zip")
                })
        
        return reel_info
    except requests.exceptions.RequestException as e:
        print(f"Error getting reel info: {str(e)}")
        if response.text:
            print(f"Response content: {response.text}")
        return None




def fetch_reel_tags(reel_id, access_token):
    """
    Fetches tags associated with a Facebook reel using the Graph API.

    Parameters:
    reel_id (str): The ID of the reel.
    access_token (str): The access token with necessary permissions.

    Returns:
    dict: A dictionary containing the tags or an error message.
    """
    url = f'https://graph.facebook.com/v20.0/{reel_id}?fields=tags&access_token={access_token}'

    response = requests.get(url)
    pp(response.json())
    if response.status_code == 200:
        data = response.json()
        return data.get('tags', [])
    else:
        return {"error": response.status_code, "message": response.text}


\
def update_reel_privacy(access_token, reel_id, privacy):
    url = f"https://graph.facebook.com/v20.0/{reel_id}"
    
    params = {
        "access_token": access_token,
        "privacy": privacy
    }
    
    try:
        response = requests.post(url, params=params)
        response.raise_for_status()
        
        result = response.json()
        if result.get("success"):
            print(f"Successfully updated privacy settings for Reel {reel_id}")
        else:
            print(f"Failed to update privacy settings for Reel {reel_id}")
        
        return result
    except requests.exceptions.RequestException as e:
        print(f"Error updating reel privacy: {str(e)}")
        if response.text:
            print(f"Response content: {response.text}")
        return None



def get_reel_info(reel_id, access_token):
    url = f'https://graph.facebook.com/v20.0/{reel_id}'
    params = {
        'access_token': access_token,
        'fields': 'id,title,description,length,created_time,updated_time,permalink_url,thumbnails,status'
    }
    
    r = requests.get(url, params=params)
    pp(r.json())
    if r.status_code == 200:
        reel_info = r.json()
        return reel_info
    else:
        print(f"Failed to retrieve reel info: {r.status_code} {r.text}")
        return None




def get_long_lived_token(app_id, app_secret, short_lived_token):
    url = "https://graph.facebook.com/oauth/access_token"
    
    params = {
        "grant_type": "fb_exchange_token",
        "client_id": app_id,
        "client_secret": app_secret,
        "fb_exchange_token": short_lived_token
    }
    
    try:
        response = requests.get(url, params=params)
        pp(response.json())
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        data = response.json()
        if "access_token" in data:
            print("Successfully obtained long-lived token")
            return data["access_token"]
        else:
            print("Failed to obtain long-lived token")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error getting long-lived token: {str(e)}")
        if response.text:
            print(f"Response content: {response.text}")
        return None



def get_page_access_token(user_access_token):
    # First, let's get the list of pages the user manages
    url = "https://graph.facebook.com/v20.0/me/accounts"
    
    params = {
        "access_token": user_access_token
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if "data" in data and len(data["data"]) > 0:
            # Assuming the first page in the list is the one we want
            page = data["data"][0]
            page_id = page["id"]
            page_access_token = page["access_token"]
            page_name = page["name"]
            print(f"Successfully obtained access token for page '{page_name}' (ID: {page_id})")
            return page_id, page_access_token
        else:
            print("No pages found for this user token")
            return None, None
    except requests.exceptions.RequestException as e:
        print(f"Error getting page access token: {str(e)}")
        if response.text:
            print(f"Response content: {response.text}")
        return None, None



def verify_page_access_token(page_access_token):
    url = "https://graph.facebook.com/v20.0/me"
    
    params = {
        "access_token": page_access_token,
        "fields": "id,name,access_token"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        if "id" in data and "name" in data:
            print(f"Successfully verified access token for page '{data['name']}' (ID: {data['id']})")
            return data['id'], data['access_token'], data['name']
        else:
            print("Failed to verify page access token")
            return None, None, None
    except requests.exceptions.RequestException as e:
        print(f"Error verifying page access token: {str(e)}")
        if response.text:
            print(f"Response content: {response.text}")
        return None, None, None



if 0:
    reel_id='1649236832528186'
    reel_info = get_reel_info(reel_id, token)

    if reel_info:
        print("Reel Information:")
        print(f"ID: {reel_info.get('id')}")
        print(f"Title: {reel_info.get('title')}")
        print(f"Description: {reel_info.get('description')}")
        print(f"Length: {reel_info.get('length')} seconds")
        print(f"Created Time: {reel_info.get('created_time')}")
        print(f"Updated Time: {reel_info.get('updated_time')}")
        print(f"Permalink URL: {reel_info.get('permalink_url')}")
        print(f"Thumbnails: {reel_info.get('thumbnails')}")
        print(f"Status: {reel_info.get('status')}")



if 0:
    rls=get_reels_2(since='2020-10-31', until='2024-11-31')
    pp(rls)


    
video_id = "1192178872027428" #523351983586573  1192178872027428

video_id = "1649236832528186" 
title='💙💛#StandWithUkraine'
description='💙💛 https://t.me/ArtForUkraine'
if 0:    
    if video_id:
        if 0:
            # Step 1: Initialize the video upload
            video_id = Initialize()
            print("Video ID:", video_id)

        if 0:
            # Step 2: Upload the video in chunks or as a single file
            with open(mp4_path, 'rb') as video_file:
                upload_response = Upload(video_id, file_size, video_file)
                print("Upload Response:", upload_response)
        if 0:
            # Step 3: Publish the uploaded video

            publish_response = Publish(video_id, title, description)
            print("Publish Response:", publish_response)
        if 0:
            # Step 4: Check the status of the video
            video_status = check_status(video_id)   
            #print(video_status)
        
        if 0:
            # Step 5: Wait for the video to finish processing and then publish it
            wait_for_processing_and_publish(video_id, title, description)



if 0:
    # Example usage:
    publish_draft_reel(video_id, token)

if 0:   

    # Example usage:

    publish_reel_immediately(video_id, token)

if 0:
    result = publish_reel(token, video_id)
    print(result)

if 0:


    video_id='390067760772239'
    
    reel_info = get_reel_data(token, video_id)
    if reel_info:
        print("Reel Information:")
        for key, value in reel_info.items():
            print(f"{key}: {value}")
    else:
        print("Failed to retrieve reel information.")

if 1:

    video_id='1187673318947825'
    reel_info = get_reel_metadata_and_targeting(token, video_id)
    if reel_info:
        print("Reel Metadata and Targeting Information:")
        pp(reel_info, width=120, compact=True)
    else:
        print("Failed to retrieve reel information.")    



if 0:


    reel_info = get_reel_metadata_with_location(token, video_id)
    if reel_info:
        print("Reel Metadata with Location Information:")
        pp(reel_info, width=120, compact=True)
    else:
        print("Failed to retrieve reel information.")

if 0:
    
    video_id='437299762789163'
    reel_info = get_reel_metadata_with_tags(token, video_id)
    if reel_info:
        print("Reel Metadata with Tags:")
        pp(reel_info, width=120, compact=True)
    else:
        print("Failed to retrieve reel information.")

if 0:
    fetch_reel_tags(video_id, token)

if 0:
    # Usage
    reel_id = "1649236832528186"  # The ID from your provided data

    privacy = '{"value":"EVERYONE"}'
    result = update_reel_privacy(token, reel_id, privacy)
    if result:
        print("Privacy update result:", result)        


if 0:
    # Usage
    
    reel_id = "437299762789163"  # The ID from your provided data

    reel_info = get_reel_metadata_with_privacy(token, reel_id)
    if reel_info:
        print("Reel Metadata with Privacy Information:")
        pp(reel_info, width=120, compact=True)
    else:
        print("Failed to retrieve reel information.")


if 0:

    # Usage
    app_id = "185779864381934"
    app_secret = "2dcc62d9792fd8a24f377fff13cb15d7"
    
    short_lived_token = token

    long_lived_token = get_long_lived_token(app_id, app_secret, short_lived_token)

    if long_lived_token:
        print("Long-lived token:", long_lived_token)
    else:
        print("Failed to retrieve long-lived token")

if 0:

    # Usage
    page_id = "185779864381934"
    user_access_token = "EAACo9z7Sqe4BO6jxv8G3ZB2tYLWWRKhcAgAOYutZAUPOTJjsJvpOLAZA0Up11PZAxO3Ww9bSRW3zdp7fZCBInmeLyI9pm6EUL8h4LveX1SPSRPfjQ05lrDzPshpAZC4ZCKARh0U8uXaVDhTnoL4J3EAHHLxaWYfHYNFMsY7djepwVZCZAn9itiGWPbaIE3s8aF0y6hEWfXfiHjHZBfJNfMXlNu7mbPPCnZAOaty33ptV125"

    page_id, page_access_token = get_page_access_token(user_access_token)

    if page_access_token:
        print("Page ID:", page_id)
        print("Page Access Token:", page_access_token)
    else:
        print("Failed to retrieve page access token")

if 0:

    # Usage
    page_access_token = "EAACo9z7Sqe4BO4zruDynUVXe3VnA32kXp3BZAKOseVhHjJ8ewTu3kAZBjWjNHcUwoZByKZABnlwIKI02Moh1bZAAeRvRy5ksO0G4dvGY0E4UxGCvczYcidO6GqNUrfxGIGITcXzPtGTsLmqZBxQanm1mDUEhqZBGnfb3CEktFgq6qvAvVma3QCZAsLzuZAz7QUzLImkAEN9UHeCff"

    page_id, verified_token, page_name = verify_page_access_token(page_access_token)

    if verified_token:
        print("Page ID:", page_id)
        print("Verified Page Access Token:", verified_token)
        print("Page Name:", page_name)
    else:
        print("Failed to verify page access token")



if 0:


    long_lived_token = "EAACo9z7Sqe4BO6jxv8G3ZB2tYLWWRKhcAgAOYutZAUPOTJjsJvpOLAZA0Up11PZAxO3Ww9bSRW3zdp7fZCBInmeLyI9pm6EUL8h4LveX1SPSRPfjQ05lrDzPshpAZC4ZCKARh0U8uXaVDhTnoL4J3EAHHLxaWYfHYNFMsY7djepwVZCZAn9itiGWPbaIE3s8aF0y6hEWfXfiHjHZBfJNfMXlNu7mbPPCnZAOaty33ptV125"

    url = f"https://graph.facebook.com/v16.0/me/accounts?access_token={long_lived_token}"


    response = requests.get(url)
    pp(response.json())
    pages = response.json().get('data')

    if pages:
        for page in pages:
            print(f"Page Name: {page['name']}")
            print(f"Page Access Token: {page['access_token']}")
    else:
        print("No pages found or token might be invalid.")

                