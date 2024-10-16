from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from api_utils import retry_api_call

class YouTubeHandler:
    def __init__(self, api_key):
        self.api_key = api_key
        self.youtube = None
        if 'placeholder' not in api_key:
            self.youtube = build('youtube', 'v3', developerKey=api_key)
    
    @retry_api_call(max_retries=3, delay=5)
    def check_new_uploads(self):
        if self.youtube is None:
            print("Warning: Using placeholder YouTube API key. Returning mock data.")
            return [{'id': 'mock_id', 'title': 'Mock Video', 'url': 'https://www.youtube.com/watch?v=mock_id'}]
        
        try:
            request = self.youtube.search().list(
                part="snippet",
                type="video",
                order="date",
                maxResults=5
            )
            response = request.execute()
            
            new_videos = []
            for item in response['items']:
                video = {
                    'id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'url': f"https://www.youtube.com/watch?v={item['id']['videoId']}"
                }
                new_videos.append(video)
            
            return new_videos
        except HttpError as e:
            print(f"An error occurred: {e}")
            raise
