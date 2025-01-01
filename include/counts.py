
import requests
from datetime import datetime, timedelta


def get_photo_count_in_last_24_hours(page_id, access_token):
    """
    Fetches the count of video posts from the Facebook page feed in the last 24 hours.

    Args:
        page_id (str): The ID of the Facebook page.
        access_token (str): The access token for authenticating with the Graph API.

    Returns:
        int: The count of video posts uploaded in the last 24 hours.
    """
    # Calculate the timestamp for 24 hours ago, ensure it's in UTC
    since_time = datetime.utcnow() - timedelta(hours=24)
    since_timestamp = int(since_time.timestamp())
    
    url = f'https://graph.facebook.com/v17.0/{page_id}/feed'
    params = {
        'access_token': access_token,
        'fields': 'id,created_time,message,attachments{media_type,media,description},permalink_url',
        'since': since_timestamp
    }
    
    video_count = 0
    
    while url:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            posts = data.get('data', [])
            
            # Count only video posts
            for post in posts:
                attachments = post.get('attachments', {}).get('data', [])
                for attachment in attachments:
                    #print(attachment.get('media_type'))
                    if attachment.get('media_type') == 'photo' :
                        print(attachment) 
                        video_count += 1
            
            # Handle pagination
            url = data.get('paging', {}).get('next')
            params = {}  # Clear params for next page request
        else:
            print(f"Error: {response.status_code}, {response.text}")
            break
    
    return video_count
if 0:
    # Usage example:
    access_token = apc.get_access_token()
    page_id = apc.page_id
    video_count = get_photo_count_in_last_24_hours(page_id, access_token)

    print(f"Number of video posts uploaded in the last 24 hours: {video_count}")


    e()

def get_video_count_in_last_24_hours(page_id, access_token):
    """
    Fetches the count of video posts from the Facebook page feed in the last 24 hours.

    Args:
        page_id (str): The ID of the Facebook page.
        access_token (str): The access token for authenticating with the Graph API.

    Returns:
        int: The count of video posts uploaded in the last 24 hours.
    """
    # Calculate the timestamp for 24 hours ago, ensure it's in UTC
    since_time = datetime.utcnow() - timedelta(hours=24)
    since_timestamp = int(since_time.timestamp())
    
    url = f'https://graph.facebook.com/v17.0/{page_id}/feed'
    params = {
        'access_token': access_token,
        'fields': 'id,created_time,message,attachments{media_type,media,description},permalink_url',
        'since': since_timestamp
    }
    
    video_count = 0
    
    while url:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            posts = data.get('data', [])
            
            # Count only video posts
            for post in posts:
                attachments = post.get('attachments', {}).get('data', [])
                for attachment in attachments:
                    if attachment.get('media_type') == 'video' and 'reel' not in post.get('permalink_url', '').lower():
                        print( post.get('permalink_url')) 
                        video_count += 1
            
            # Handle pagination
            url = data.get('paging', {}).get('next')
            params = {}  # Clear params for next page request
        else:
            print(f"Error: {response.status_code}, {response.text}")
            break
    
    return video_count
if 0:
    # Usage example:
    access_token = apc.get_access_token()
    page_id = apc.page_id
    video_count = get_video_count_in_last_24_hours(page_id, access_token)

    print(f"Number of video posts uploaded in the last 24 hours: {video_count}")


    e()

def get_recent_videos_from_feed(page_id, access_token):
    """
    Fetches a list of video posts from the Facebook page feed in the last 24 hours.

    Args:
        page_id (str): The ID of the Facebook page.
        access_token (str): The access token for authenticating with the Graph API.

    Returns:
        list: A list of dictionaries containing video post details uploaded in the last 24 hours.
    """
    # Calculate the timestamp for 24 hours ago, ensure it's in UTC
    since_time = datetime.utcnow() - timedelta(hours=24)
    since_timestamp = int(since_time.timestamp())
    
    url = f'https://graph.facebook.com/v17.0/{page_id}/feed'
    params = {
        'access_token': access_token,
        'fields': 'id,created_time,message,attachments{media_type,media,description},permalink_url',
        'since': since_timestamp
    }
    
    recent_videos = []
    
    while url:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            posts = data.get('data', [])
            
            # Filter out only video posts
            for post in posts:
                attachments = post.get('attachments', {}).get('data', [])
                for attachment in attachments:
                    print(attachment.get('media_type'), post.get('permalink_url', 'No permalink available'))
                    if attachment.get('media_type') == 'video':
                        recent_videos.append({
                            'id': post['id'],
                            'created_time': post['created_time'],
                            'message': post.get('message', 'No description available'),
                            'permalink_url': post.get('permalink_url', 'No permalink available'),
                            'video': attachment.get('media', {})
                        })
            
            # Handle pagination
            url = data.get('paging', {}).get('next')
            params = {}  # Clear params for next page request
        else:
            print(f"Error: {response.status_code}, {response.text}")
            break
    
    return recent_videos
if 0:
    # Usage example:
    access_token = apc.get_access_token()
    page_id = apc.page_id
    videos_in_last_24_hours = get_recent_videos_from_feed(page_id, access_token)

    if videos_in_last_24_hours:
        for video in videos_in_last_24_hours:
            print(f"Video Post ID: {video['id']}")
            print(f"Created Time: {video['created_time']}")
            print(f"Description: {video['message']}")
            print(f"Permalink: {video['permalink_url']}")
            print(f"Video Details: {video['video']}")
            print('---')
    else:
        print("No video posts uploaded in the last 24 hours.")


    e()

def get_videos_in_last_24_hours(page_id, access_token):
    """
    Fetches a list of videos uploaded to a Facebook page in the last 24 hours.

    Args:
        page_id (str): The ID of the Facebook page.
        access_token (str): The access token for authenticating with the Graph API.

    Returns:
        list: A list of dictionaries containing video details uploaded in the last 24 hours.
    """
    # Calculate the timestamp for 24 hours ago, ensure it's in UTC
    since_time = datetime.utcnow() - timedelta(hours=24)
    print(f"Checking for videos uploaded since: {since_time.isoformat()} UTC")
    
    url = f'https://graph.facebook.com/v17.0/{page_id}/videos'
    params = {
        'access_token': access_token,
        'fields': 'id,title,description,created_time,length,permalink_url,thumbnails,status'
    }
    
    recent_videos = []
    
    while url:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            videos = data.get('data', [])
            
            # Debug: Print all fetched video timestamps
            for video in videos:
                print(f"Video created_time: {video['created_time']}")

            # Filter videos based on created_time being within the last 24 hours
            for video in videos:
                created_time = datetime.strptime(video['created_time'], '%Y-%m-%dT%H:%M:%S%z')
                if created_time >= since_time.replace(tzinfo=created_time.tzinfo):
                    recent_videos.append(video)
            
            # Handle pagination
            url = data.get('paging', {}).get('next')
            params = {}  # Clear params for next page request
        else:
            print(f"Error: {response.status_code}, {response.text}")
            break
    
    return recent_videos
if 0:
    # Usage example:
    access_token = apc.get_access_token()
    page_id = apc.page_id
    videos_in_last_24_hours = get_videos_in_last_24_hours(page_id, access_token)

    if videos_in_last_24_hours:
        for video in videos_in_last_24_hours:
            print(f"Video ID: {video['id']}")
            print(f"Title: {video.get('title', 'No title available')}")
            print(f"Description: {video.get('description', 'No description available')}")
            print(f"Created Time: {video['created_time']}")
            print(f"Length: {video.get('length', 'N/A')} seconds")
            print(f"Permalink: {video.get('permalink_url', 'No permalink available')}")
            print(f"Thumbnails: {video.get('thumbnails', 'No thumbnails available')}")
            print(f"Status: {video.get('status', 'No status available')}")
            print('---')
    else:
        print("No videos uploaded in the last 24 hours.")



    e()

import requests

def get_video_info(video_id, access_token):
    """
    Fetches detailed information about a specific Facebook video using its ID.

    Args:
        video_id (str): The ID of the video.
        access_token (str): The access token for authenticating with the Graph API.

    Returns:
        dict: A dictionary containing detailed video information.
    """
    url = f'https://graph.facebook.com/v17.0/{video_id}'
    params = {
        'access_token': access_token,
        'fields': 'id,title,description,created_time,length,permalink_url,thumbnails,status'
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None
if 0:   
    # Usage example:
    access_token = apc.get_access_token()   
    video_id = '1050180129787415'  # Replace with the actual video ID
    video_info = get_video_info(video_id, access_token)

    if video_info:
        print(f"Video ID: {video_info['id']}")
        print(f"Title: {video_info.get('title', 'No title available')}")
        print(f"Description: {video_info.get('description', 'No description available')}")
        print(f"Created Time: {video_info['created_time']}")
        print(f"Length: {video_info.get('length', 'N/A')} seconds")
        print(f"Permalink: {video_info.get('permalink_url', 'No permalink available')}")
        print(f"Thumbnails: {video_info.get('thumbnails', 'No thumbnails available')}")
        print(f"Status: {video_info.get('status', 'No status available')}")

    e()

import requests

def get_page_video_info(page_id, video_id, access_token):
    """
    Fetches detailed information about a specific video posted on a Facebook page.

    Args:
        page_id (str): The ID of the Facebook page.
        video_id (str): The ID of the video.
        access_token (str): The access token for authenticating with the Graph API.

    Returns:
        dict: A dictionary containing detailed video information.
    """
    url = f'https://graph.facebook.com/v17.0/{page_id}/videos/{video_id}'
    params = {
        'access_token': access_token,
        'fields': 'id,title,description,created_time,length,permalink_url,thumbnails,status'
    }
    
    response = requests.get(url, params=params)
    pp(response.json())
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None
if 0:
    # Usage example:
    access_token =apc.get_access_token()
    page_id = apc.page_id  # Replace with the actual page ID
    video_id = '1050180129787415'  # Replace with the actual video ID
    video_info = get_page_video_info(page_id, video_id, access_token)

    if video_info:
        print(f"Video ID: {video_info['id']}")
        print(f"Title: {video_info.get('title', 'No title available')}")
        print(f"Description: {video_info.get('description', 'No description available')}")
        print(f"Created Time: {video_info['created_time']}")
        print(f"Length: {video_info.get('length', 'N/A')} seconds")
        print(f"Permalink: {video_info.get('permalink_url', 'No permalink available')}")
        print(f"Thumbnails: {video_info.get('thumbnails', 'No thumbnails available')}")
        print(f"Status: {video_info.get('status', 'No status available')}")


    e()


import requests
from datetime import datetime

def get_page_videos(page_id, access_token):
    """
    Fetches the list of videos uploaded to a Facebook page, sorted by created_time in descending order.

    Args:
        page_id (str): The ID of the Facebook page.
        access_token (str): The access token for authenticating with the Graph API.

    Returns:
        list: A list of dictionaries containing video details (id, title, description, created_time, permalink_url) sorted by created_time in descending order.
    """
    url = f'https://graph.facebook.com/v17.0/{page_id}/videos'
    params = {
        'access_token': access_token,
        'fields': 'id,title,description,created_time,permalink_url'
    }
    
    videos = []
    while url:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            videos.extend(data.get('data', []))
            url = data.get('paging', {}).get('next')
            params = {}  # Clear params for the next page request
        else:
            print(f"Error: {response.status_code}, {response.text}")
            break

    # Sort the videos by created_time in descending order
    videos.sort(key=lambda x: datetime.strptime(x['created_time'], '%Y-%m-%dT%H:%M:%S%z'), reverse=True)
    
    return videos
if 0:
    # Your access token
    access_token = apc.get_access_token()

    # Your page ID
    page_id = apc.page_id
    videos = get_page_videos(page_id, access_token)

    for video in videos:
        print(f"Video ID: {video['id']}")
        #print(f"Title: {video['title']}")
        print(f"Description: {video['description']}")
        print(f"Created Time: {video['created_time']}")
        print(f"Permalink: {video['permalink_url']}")
        print('---')

    e()

def check_facebook_page_videos(page_id, page_access_token):
    try:
        # Set the date range for the last 24 hours
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        # Common parameters for the requests
        common_params = {
            "access_token": page_access_token,
            "fields": "id,created_time,title,description,updated_time",
            "since": int(start_time.timestamp()),
            "until": int(end_time.timestamp()),
            "limit": 100  # Adjust if necessary
        }

        # Check regular videos
        videos_url = f"https://graph.facebook.com/v20.0/{page_id}/videos"
        videos_response = requests.get(videos_url, params=common_params)

        if videos_response.status_code == 200:
            videos_data = videos_response.json()
            videos = videos_data.get('data', [])
            
            print(f"Total videos retrieved: {len(videos)}")
            print("\nDetailed video information:")
            
            for video in videos:
                print(f"Video ID: {video.get('id')}")
                print(f"Title: {video.get('title', 'No title')}")
                print(f"Created time: {video.get('created_time')}")
                print(f"Updated time: {video.get('updated_time')}")
                print(f"Description: {video.get('description', 'No description')[:100]}...")  # Truncate long descriptions
                print("---")

            if not videos:
                print("No videos found in the last 24 hours.")
                print("Note: There might be a delay in the API updating with recently uploaded videos.")

            return len(videos)
        else:
            print(f"Error in Videos response: {videos_response.status_code}")
            print(videos_response.text)
            return None

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None
if 0:
    # Example usage
    page_id = apc.page_id
    page_access_token = apc.get_access_token()

    video_count = check_facebook_page_videos(page_id, page_access_token)

    if video_count is not None:
        print(f"\nTotal video count in the last 24 hours: {video_count}")
    else:
        print("Unable to retrieve video information.")
    e()


def check_facebook_page_video_limits(page_id, page_access_token):
    try:
        # Set the date range for the last 24 hours
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        # Common parameters for the requests
        common_params = {
            "access_token": page_access_token,
            "fields": "created_time",
            "since": int(start_time.timestamp()),
            "until": int(end_time.timestamp()),
            "limit": 100  # Adjust if necessary
        }

        # Check Reels
        reels_url = f"https://graph.facebook.com/v20.0/{page_id}/video_reels"
        reels_response = requests.get(reels_url, params=common_params)

        # Check regular videos
        videos_url = f"https://graph.facebook.com/v20.0/{page_id}/videos"
        videos_response = requests.get(videos_url, params=common_params)

        if reels_response.status_code == 200 and videos_response.status_code == 200:
            reels_data = reels_response.json()
            videos_data = videos_response.json()
            pp(videos_data)
            reels_count = len(reels_data.get('data', []))
            videos_count = len(videos_data.get('data', []))

            # Limits (these may vary, please confirm with Facebook's latest documentation)
            reels_daily_limit = 30
            videos_daily_limit = 100  # This is an assumed limit, please verify

            reels_remaining = reels_daily_limit - reels_count
            videos_remaining = videos_daily_limit - videos_count

            print(f"Published Reels in the last 24 hours: {reels_count}")
            print(f"Reels API daily limit: {reels_daily_limit}")
            print(f"Remaining Reel uploads: {reels_remaining}")
            print("\n")
            print(f"Published regular videos in the last 24 hours: {videos_count}")
            print(f"Assumed regular video daily limit: {videos_daily_limit}")
            print(f"Remaining regular video uploads: {videos_remaining}")
            print("\nNote: These counts include published content only. Unpublished or draft content is not included.")

            return {
                "can_upload_reels": reels_remaining > 0,
                "can_upload_videos": videos_remaining > 0,
                "reels_remaining": reels_remaining,
                "videos_remaining": videos_remaining
            }
        else:
            print(f"Error in Reels response: {reels_response.status_code}")
            print(reels_response.text)
            print(f"Error in Videos response: {videos_response.status_code}")
            print(videos_response.text)
            return None

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None
if 0:
    # Example usage
    page_id = apc.page_id
    page_access_token = apc.get_access_token()

    result = check_facebook_page_video_limits(page_id, page_access_token)

    if result:
        if result["can_upload_reels"]:
            print("You can still upload Reels.")
        else:
            print("You have reached your Reels upload limit for the 24-hour period.")

        if result["can_upload_videos"]:
            print("You can still upload regular videos.")
        else:
            print("You have reached your regular video upload limit for the 24-hour period.")
    else:
        print("Unable to determine video upload limit status.")
    e()

def check_facebook_video_api_limit_me(user_access_token):
    try:
        # API endpoint for videos of the authenticated user
        url = "https://graph.facebook.com/v20.0/me/videos"
        
        # Set the date range for the last 24 hours
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=24)
        
        # Parameters for the request
        params = {
            "access_token": user_access_token,
            "fields": "created_time,description",
            "since": int(start_time.timestamp()),
            "until": int(end_time.timestamp()),
            "limit": 100  # Adjust if necessary
        }
        
        # Make the GET request
        response = requests.get(url, params=params)
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            
            # Count videos that might be Reels (you may need to adjust this filtering)
            video_count = sum(1 for video in data.get('data', []) if 'Reel' in video.get('description', ''))
            
            # API limit (this is an assumption, actual limit may vary)
            daily_limit = 30
            remaining = daily_limit - video_count
            
            print(f"Videos/Reels uploaded in the last 24 hours: {video_count}")
            print(f"Assumed daily limit: {daily_limit}")
            print(f"Estimated remaining uploads: {remaining}")
            print("Note: This count includes all videos that might be Reels. The actual Reel count may vary.")
            
            return remaining > 0  # Returns True if uploads are still available
        else:
            print(f"Error: {response.status_code}")
            print(response.text)
            return None

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return None
    

if 0:
    user_access_token = apc.user_token

    can_upload = check_facebook_video_api_limit_me(user_access_token)

    if can_upload is True:
        print("Based on published reels, you can likely still upload reels via the API.")
    elif can_upload is False:
        print("Based on published reels, you may have reached your Reels API upload limit for the 24-hour period.")
    else:
        print("Unable to determine Reels API upload limit status.")

    e()
import requests
from datetime import datetime, timedelta

def check_facebook_reel_api_limit(page_id, page_access_token):
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
if 0:
    # Example usage
    page_id = apc.page_id
    page_access_token = apc.get_access_token()

    can_upload = check_facebook_reel_api_limit(page_id, page_access_token)

    if can_upload is True:
        print("You can still upload reels.")
    elif can_upload is False:
        print("You have reached your reel upload limit for today.")
    else:
        print("Unable to determine reel upload limit status.")

    e()