import requests


# Usage example
access_token = "EAACo9z7Sqe4BOZCANT82ax3d9Yj8ZASvTpLGnZCOSx0TrOfnreqywAyZCOH9rBE4REC6uFFAs6lAce9k5oB8x7XMtAgL4jbsY3WVGodcZC2L08V3yvefIXNsMSC34rw4WgG2hsOFJlABDU1YWhEQahF3ZBZCKdRWaaHBXOOeNK5CgZAKIQUKwGiwJG7atLq1VU5WpTlfQ0nWarUbRd9Nuu0QiWSIk6ab4DdKdXmsYZBUx"
user_id = "100083627761445"


page_id = "185779864381934"

url = f"https://graph.facebook.com/v20.0/{user_id}/videos?access_token={access_token}"

response = requests.get(url)
data = response.json()
print(data)
if 0:
    for video in data['data']:
        print(f"Video ID: {video['id']}, Video Title: {video.get('title', 'No title')}")
