import os
import requests
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ['https://www.googleapis.com/auth/photospicker.mediaitems.readonly']

def authenticate():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def create_picker_session(creds):
    url = "https://photospicker.googleapis.com/v1/sessions"
    headers = {
        "Authorization": f"Bearer {creds.token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, headers=headers, json={})

    if response.status_code == 200:
        data = response.json()
        session_id = data.get("id")
        picker_uri = data.get("pickerUri")
        
        print(f"Session Created! ID: {session_id}")
        return session_id, picker_uri
    else:
        print(f"Error creating session: {response.status_code}")
        print(response.text)
        return None, None

def download_selected_photos(creds, session_id, save_folder):
    headers = {"Authorization": f"Bearer {creds.token}"}
    session_url = f"https://photospicker.googleapis.com/v1/sessions/{session_id}"
    media_items_url = "https://photospicker.googleapis.com/v1/mediaItems"
    
    max_retries = 20
    retries = 0
    media_items_ready = False

    print("Waiting for user to select photos...")
    while retries < max_retries:
        print(f"Waiting for selection... ({retries + 1}/{max_retries})")
        response = requests.get(session_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data.get("mediaItemsSet") is True:
                media_items_ready = True
                break
        
        retries += 1
        time.sleep(3)
    
    if not media_items_ready:
        print("Polling timed out or user cancelled.")
        return []

    print("User finished picking. Fetching photo list...")
    params = {"sessionId": session_id}
    list_response = requests.get(media_items_url, headers=headers, params=params)
    
    saved_paths = []
    if list_response.status_code == 200:
        media_items = list_response.json().get("mediaItems", [])
        
        if not os.path.exists(save_folder):
            os.makedirs(save_folder)

        for item in media_items:
            media_file = item.get('mediaFile', {})
            
            mime_type = media_file.get('mimeType', '')
            base_url = media_file.get('baseUrl')
            filename = item.get('filename', f"{item.get('id')}.jpg")

            print(f"Checking: {filename} | MIME: {mime_type}")

            if not base_url:
                print(f"Skipping {filename} - No baseUrl found.")
                continue

            if 'image' not in mime_type:
                print(f"Skipping {filename} - Not an image file (MIME: {mime_type}).")
                continue

            download_url = f"{base_url}=d"
            file_path = os.path.join(save_folder, filename)
            
            try:
                img_response = requests.get(download_url, headers=headers)
                if img_response.status_code == 200:
                    with open(file_path, 'wb') as f:
                        f.write(img_response.content)
                    saved_paths.append(file_path)
                    print(f"Successfully Downloaded: {filename}")
            except Exception as e:
                print(f"Error saving {filename}: {e}")

    return saved_paths