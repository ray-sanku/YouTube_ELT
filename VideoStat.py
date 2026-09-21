import requests
import os
from dotenv import load_dotenv
import json
from datetime import date

load_dotenv()
yt_key = os.getenv('YOUTUBE_API_KEY')
channel_handle = "MrBeast"

def getChannelPlaylistID(handle, key):
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

def getVideoIDs(playlistID, key):
    max_results = 50
    part = 'contentDetails'
    pageToken = None
    videoIDs = []

    base_url = f'https://youtube.googleapis.com/youtube/v3/playlistItems?part={part}&maxResults={max_results}&playlistId={playlistID}&key={key}'

    try:
        while True:
            url = base_url

            if pageToken:
                url = url + f"&pageToken={pageToken}"
            # Always specify a timeout to prevent your code from hanging indefinitely
            response = requests.get(url, timeout=5)
                
            # If the response was successful, no exception is raised.
            # If it's a 4xx or 5xx error, it triggers an HTTPError.
            response.raise_for_status()
            response_data = response.json()

            for item in response_data.get('items',[]):
                video_id = item['contentDetails']['videoId']
                videoIDs.append(video_id)

            #get the page token for getting next set of videos
            pageToken = response_data.get('nextPageToken')

            if not pageToken:
                break
        return videoIDs

    except requests.exceptions.RequestException as e:
        raise e

def getVideoBatches(videoList, size):
    return [videoList[i:i+size] for i in range(0, len(videoList), size)]

def extractVideoData(videoID_list, batch_size, key):
    extracted_data = []

    for batch in getVideoBatches(videoID_list, batch_size):
        videos_id_str = ','.join(batch)
        url = f'https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={videos_id_str}&key={key}'

        try:
            # Always specify a timeout to prevent your code from hanging indefinitely
            response = requests.get(url, timeout=5)
                
            # If the response was successful, no exception is raised.
            # If it's a 4xx or 5xx error, it triggers an HTTPError.
            response.raise_for_status()
            response_data = response.json()

            for item in response_data.get('items',[]):
                video_data = {"video_id" : item['id'],"title" : item['snippet']['title'], "description" : item['snippet']['description'],
                                  "published_at" : item['snippet']['publishedAt'], "duration" : item['contentDetails']['duration'], "viewCount" : item['statistics'].get('viewCount',None),
                                  "likeCount" : item['statistics'].get('likeCount',None), "commentCount" : item['statistics'].get('commentCount',None)
                                  }

                extracted_data.append(video_data)        

        except requests.exceptions.RequestException as e:
            raise e
    return extracted_data

def save_to_json(extracted_data):
    file_path = f'./data/YT_data_{channel_handle}_{date.today()}.json'

    with open(file=file_path, encoding="utf-8",mode='w') as json_output_file:
        json.dump(extracted_data, json_output_file, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    playlist_id = getChannelPlaylistID(channel_handle,yt_key)
    print(playlist_id)
    videos_ids = getVideoIDs(playlist_id, yt_key)
    batch_size = 50
    extracted_video_data = extractVideoData(videos_ids, batch_size, yt_key)

    ## Save in a file
    save_to_json(extracted_video_data)