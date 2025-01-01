import requests
from pprint import pprint as pp
from include.common import PropertyDefaultDict, ErrorValidatingAccessToken

import include.config.init_config as init_config 
apc = init_config.apc

api= 'v20.0'


def check_page_token_validity():
    page_id= apc.page_id
    assert page_id in apc.pages, f'Page {page_id} not found in self.pages'
    assert apc.pages[page_id].page_token
    # Facebook Graph API endpoint for page information
    url = f"https://graph.facebook.com/{api}/me?access_token={apc.pages[page_id].page_token}"

    try:
        # Make a GET request to the API
        response = requests.get(url)
        
        # Check the response status code
        if response.status_code == 200:
            # Token is valid
            page_info = response.json()
            print(f"Token is valid. Page name: {page_info.get('name')}")
            return True
        else:
            # Token is invalid
            error_info = response.json().get('error', {})
            print(f"Token is invalid. Error: {error_info.get('message')}")
            return False
    
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        #return False




def set_page_access_tokens():
    p_id =  apc.page_id
    if not  apc.user_token:
        raise ErrorValidatingAccessToken(None, 'User token not set')
    # First, let's get the list of pages the user manages
    url = "https://graph.facebook.com/v20.0/me/accounts"
    
    params = {
        "access_token": apc.user_token
    }
    
    try:
        r = requests.get(url, params=params)
        json= r.json()
        r.raise_for_status()
        assert apc.user
        page_tokens= apc.page_tokens
        pages=page_tokens[apc.user]
        print(39393939,type(pages))
        data = r.json()
        if p_id in pages:
            del pages[p_id]
        
        if "data" in data and len(data["data"]) > 0:
            # Assuming the first page in the list is the one we want
            for page_data in data["data"]:
                #pp(page)
                page_id = page_data["id"]
                if page_id not in pages:
                    page= PropertyDefaultDict()
                else:
                    page= pages[page_id]
                print('Page ID:', page_id)
                page_access_token = page_data["access_token"]
                page_name = page_data["name"]
                print(f"Successfully obtained access token for page '{page_name}' (ID: {page_id})")
                pp(page)
                page.page_token =page_access_token
                page.page_name =page_name
                page.page_id =page_id
                print('Pages:', page)
                pages[page_id]=page
            
        else:
            print("No pages found for this user token")
            #raise Exception("No pages found for this user token")
        
    except requests.exceptions.RequestException as e:
        pp(json)
        err_code= json['error']['code'] 
        err_subcode= json['error']['error_subcode']
        if err_code == 190 and err_subcode == 463:
            # Token expired
            
            raise ErrorValidatingAccessToken(r, json['error'])
        
        #raise e   
    assert apc.pages 
    #pp(apc.pages)
    #e()

if __name__ == '__main__':
    apc.pages=PropertyDefaultDict()
    apc.user_token= 'EAAHbeMlmZCbYBO7cq2aPB8YhLDFjZCzhBN5UJTOfo4713aJlSvhzVXyytg8rPqKF9UWMfZC22MdByFWtBsmGInt6RRZCVNnxYKDKB7T09e0d7aFHv06ZB9RX1jE5T6EmWxmih6NFLGua6WYj45dtvrEdtRDLqlQ6mXgD6QAZBlr8RYFA5GwPOI2Gt8kktHLyAlgJbi89CJTXzR4ZCF1qZBihbG5yaVN9bBAZD'
    page_id= '105420925572228'
    set_page_access_token()
    

    if 1:
        is_valid = check_page_token_validity()  
        print('Valid:', is_valid)
