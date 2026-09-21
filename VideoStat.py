import requests
import os
from dotenv import load_dotenv
import json

load_dotenv()
yt_key = os.getenv('YOUTUBE_API_KEY')
channel_handle = "MrBeast"

def getChannelPlaylistID(key, handle):
    url = f'https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle=%40{handle}&key={key}'

    try:
        # Always specify a timeout to prevent your code from hanging indefinitely
        response = requests.get(url, timeout=5)
    
        # If the response was successful, no exception is raised.
        # If it's a 4xx or 5xx error, it triggers an HTTPError.
        response.raise_for_status()

        response_data = response.json()
        channel_items = response_data['items'][0]
        channel_playlistID = channel_items['contentDetails']['relatedPlaylists']['uploads']

        return channel_playlistID
    except requests.exceptions.HTTPError as errh:
    # e.g., 404 Not Found, 500 Server Error
        print(f"HTTP Error: {errh}")

    except requests.exceptions.ConnectionError as errc:
    # e.g., DNS failure, refused connection, bad domain
        print(f"Error Connecting: {errc}")

    except requests.exceptions.Timeout as errt:
    # e.g., The server took too long to send data or connect
        print(f"Timeout Error: {errt}")

if __name__ == "__main__":
    playlist_id = getChannelPlaylistID(yt_key, channel_handle)
    print(playlist_id)