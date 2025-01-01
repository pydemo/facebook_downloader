import os, time
import json as JS
import requests
from os.path import isfile
from pprint import pprint as pp
from pprint import pformat
from os.path import join   , isdir 
from datetime import datetime, timedelta
from include.common import VideoUploadIsMissingError
from include.common import TokenExpiredError
import include.config.init_config as init_config 
apc = init_config.apc

api_version='v20.0'


def init_upload(user_id, page_id):
    page_token=apc.get_page_access_token(user_id, page_id) 
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


def check_status(user_id, page_id, reel_id):
    

    page_token=apc.get_page_access_token(user_id, page_id) 
    assert page_token, page_token
    url = f"https://graph.facebook.com/v20.0/{reel_id}?fields=id,description,permalink_url,status&access_token={page_token}"
    r = requests.get(url)
    json= r.json()  
    print("Reel status")
    #pp(r.json())
    if r.status_code == 200:
        return json
    #pformat(r.json(), indent=2, width=80) 
    else:
        print("Failed to check status:", r.status_code, r.text)
        raise Exception(json    )
    


def check_reel_status(user_id, page_id, reel_id):
    #reel_id=apc.reel_id
    page_token=apc.get_page_access_token(user_id, page_id)    
    url = f"https://graph.facebook.com/v13.0/{reel_id}"
    
    params = {
        'access_token': page_token,
        'fields': 'id,description,permalink_url,status'
    }
    
    print("Checking Reel status...")
    response = requests.get(url, params=params)
    response_json = response.json()
    #print("Reel status response:", JS.dumps(response_json, indent=2))
    
    if 'error' in response_json:
        raise Exception(f"Error checking Reel status: {response_json['error']['message']}")
    
    return response_json
def wait_for_reel_publishing(user_id, page_id, reel_id, max_attempts=20, delay=5):

    for attempt in range(max_attempts):
        reel_status = check_reel_status(user_id, page_id,reel_id)
        status = reel_status.get('status', {})
        pp(status)
        if status.get('publishing_phase', {}).get('status') == 'complete':
            print("Reel has been successfully published!")
            return reel_status
        
        print(f"Attempt {attempt + 1}/{max_attempts}: Reel is still being processed. Waiting {delay} seconds...")
        time.sleep(delay)
    
    print("Maximum attempts reached. The Reel may still be processing.")
    return reel_status

def publish(user_id, page_id, reel_id, description, publish_time=None):
    page_token=apc.get_page_access_token(user_id, page_id) 
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



from typing import Optional, Dict, Any

def get_reel_description() -> Optional[str]:
    """
    Fetch the description of a Facebook Reel using the Graph API.

    Args:
    reel_id (str): The ID of the Reel to fetch.
    access_token (str): Facebook Graph API access token.

    Returns:
    Optional[str]: The Reel description if available, None if not found or on error.

    Raises:
    requests.RequestException: If there's an error with the HTTP request.
    """
    assert apc.reel_id, apc.reel_id
    access_token= apc.get_access_token()  
    assert access_token, access_token     
    url = f"https://graph.facebook.com/v20.0/{apc.reel_id}"
    params = {
        'fields': 'description',
        'access_token': access_token
    }

    try:
        r = requests.get(url, params=params)
        
        json= r.json()   
        r.raise_for_status()
        reel_data: Dict[str, Any] = r.json()
        return reel_data.get('description')
    except requests.RequestException as e:
        
        
        err_code= json['error']['code'] 
        err_subcode= json['error']['error_subcode']
        if err_code == 190 and err_subcode == 463:
            # Token expired
            raise TokenExpiredError(r, json['error'])
        pp(json)
        print(f"An error occurred: {e}")

        raise e


def check_api_limits():
    access_token = apc.get_access_token()

    graph_url = "https://graph.facebook.com/v20.0/me"
    
    params = {
        'access_token': access_token
    }

    try:
        response = requests.get(graph_url, params=params)
        pp(response.json())
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        print(f"Response: {response.json()}")
        
        # Check if limit information is available in the response headers
        if 'x-app-usage' in response.headers:
            app_usage = JS.loads(response.headers['x-app-usage'])
            print("Current API usage:")
            for key, value in app_usage.items():
                print(f"  {key}: {value}%")
        else:
            print("App usage information not available in response headers")
        
        if 'x-ad-account-usage' in response.headers:
            ad_account_usage = JS.loads(response.headers['x-ad-account-usage'])
            print("\nAd Account usage:")
            for key, value in ad_account_usage.items():
                print(f"  {key}: {value}%")
        else:
            print("Ad Account usage information not available")
        
        if 'x-business-use-case-usage' in response.headers:
            business_usage = JS.loads(response.headers['x-business-use-case-usage'])
            print("\nBusiness use case usage:")
            for business_id, usage_list in business_usage.items():
                print(f"Business ID: {business_id}")
                for usage_item in usage_list:
                    for key, value in usage_item.items():
                        print(f"  {key}: {value}")
        else:
            print("Business use case usage information not available")
            
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    except JS.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Response content: {response.text}")


    
def get_page_metrics():
    page_id, access_token= apc.page_id, apc.get_access_token()  
    graph_url = f"https://graph.facebook.com/v20.0/{page_id}"
    
    params = {
        'fields': 'followers_count,fan_count',
        'access_token': access_token
    }

    try:
        response = requests.get(graph_url, params=params)
        pp(response.json())
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        data = response.json()
        
        followers_count = data.get('followers_count', 'N/A')
        fan_count = data.get('fan_count', 'N/A')
        
        print(f"Page ID: {page_id}")
        print(f"Followers count: {followers_count}")
        print(f"Fan count (Page likes): {fan_count}")
        
        apc.update_stats(data)


        return data
        
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
        return None


def process_upload(  file_size, file_data, page_id, reel_id):

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



def check_facebook_reel_api_limit(user_id, page_id):
    page_access_token=apc.get_page_access_token(user_id, page_id)
    try:
        # API endpoint for published video reels
        url = f"https://graph.facebook.com/v20.0/{page_id}/video_reels"
        
        # Set the date range for the last 24 hours
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        # Parameters for the request
        params = {
            "access_token": page_access_token,
            "fields": "created_time",
            "since": int(start_time.timestamp()),
            "until": int(end_time.timestamp()),
            "limit": 100  # Adjust if necessary
        }
        
        # Make the GET request
        response = requests.get(url, params=params)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            
            # Count published reels uploaded in the last 24 hours
            reels_count = len(data.get('data', []))
            
            # Reels API limit
            daily_limit = 30
            remaining = daily_limit - reels_count
            
            print(f"Published Reels in the last 24 hours: {reels_count}")
            print( f"Reels API daily limit: {daily_limit}")
            print(f"Estimated remaining uploads: {remaining}")
            print("Note: This count only includes published reels. Unpublished or draft reels are not included in this count.")
            
            return remaining > 0  # Returns True if uploads are still available
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None



if __name__ == '__main__':

    #mp4_path=r'C:\Users\alex_\myg\facebook_downloader\downloads\ArtForUkraine\backup\done\bbb6ef9a-9ed3-4b7b-8b5b-27281f1cc53b_Технологічна революція в Сеньківці 😎 – Серіал Будиночок на щастя_shortened.mp4'
    mp4_path= r"C:\Users\alex_\myg\facebook_downloader\downloads\ArtForUkraine\backup\done\bbb6ef9a-9ed3-4b7b-8b5b-27281f1cc53b_Технологічна революція в Сеньківці 😎 – Серіал Будиночок на щастя.mp4"
    length=90
    file_path = validate_reel_length(mp4_path)  
    print(file_path)