import requests
from pprint import pprint as pp

user_access_token = "EAACo9z7Sqe4BO6jxv8G3ZB2tYLWWRKhcAgAOYutZAUPOTJjsJvpOLAZA0Up11PZAxO3Ww9bSRW3zdp7fZCBInmeLyI9pm6EUL8h4LveX1SPSRPfjQ05lrDzPshpAZC4ZCKARh0U8uXaVDhTnoL4J3EAHHLxaWYfHYNFMsY7djepwVZCZAn9itiGWPbaIE3s8aF0y6hEWfXfiHjHZBfJNfMXlNu7mbPPCnZAOaty33ptV125"

# Get the page access token
url = "https://graph.facebook.com/v20.0/me/accounts"
params = {
    'access_token': user_access_token
}

page_id = "100083627761445"

response = requests.get(url, params=params)
page_data = response.json()
pp(page_data)

# Extract the page access token for the specific page
for page in page_data['data']:
    print(page['id'], page['name']) 
    if page['id'] == page_id:
        page_access_token = page['access_token']
        break
else:
    raise Exception("Page ID not found or token missing permissions")
