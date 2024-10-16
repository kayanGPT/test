import time
from api_utils import make_api_request, retry_api_call

class VideoProcessor:
    def __init__(self, klap_api_key, placid_api_key):
        self.klap_api_key = klap_api_key
        self.placid_api_key = placid_api_key
    
    @retry_api_call(max_retries=5, delay=10)
    def create_shorts(self, video_url):
        if 'placeholder' in self.klap_api_key:
            print("Warning: Using placeholder Klap API key. Returning mock data.")
            return ['https://example.com/mock_short1.mp4', 'https://example.com/mock_short2.mp4']
        
        klap_endpoint = "https://api.klap.ai/tasks/video-to-shorts"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.klap_api_key}"
        }
        data = {
            "source_video_url": video_url,
            "target_clip_count": 10,
            "max_clip_count": 10,
            "editing_options": {
                "captions": True,
                "reframe": True
            },
            "dimensions": {
                "width": 1080,
                "height": 1920
            }
        }
        
        response = make_api_request(klap_endpoint, method='POST', json=data, headers=headers)
        task_id = response.json()['task_id']
        
        # Poll for task completion
        while True:
            status_response = make_api_request(f"https://api.klap.ai/tasks/{task_id}", headers=headers)
            status = status_response.json()['status']
            if status == 'completed':
                return status_response.json()['output_urls']
            elif status == 'failed':
                raise Exception("Klap AI task failed")
            time.sleep(30)  # Wait 30 seconds before checking again
    
    @retry_api_call(max_retries=5, delay=10)
    def merge_with_sludge(self, shorts_urls, video_id):
        if 'placeholder' in self.placid_api_key:
            print("Warning: Using placeholder Placid API key. Returning mock data.")
            return {'url': 'https://example.com/mock_merged_video.mp4', 'id': 'mock_task_id'}
        
        sludge_url = self.get_sludge_content_url(video_id)
        
        placid_endpoint = "https://api.placid.app/v1/merge"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.placid_api_key}"
        }
        data = {
            "videos": [sludge_url] + shorts_urls,
            "output_format": "mp4"
        }
        
        response = make_api_request(placid_endpoint, method='POST', json=data, headers=headers)
        task_id = response.json()['task_id']
        
        # Poll for task completion
        while True:
            status_response = make_api_request(f"https://api.placid.app/v1/tasks/{task_id}", headers=headers)
            status = status_response.json()['status']
            if status == 'completed':
                return {
                    'url': status_response.json()['output_url'],
                    'id': task_id
                }
            elif status == 'failed':
                raise Exception("Placid AI task failed")
            time.sleep(30)  # Wait 30 seconds before checking again
    
    def get_sludge_content_url(self, video_id):
        # This method should be implemented to retrieve the corresponding sludge content URL
        # It could involve querying a database or another API
        # For now, we'll return a placeholder URL
        return f"https://example.com/sludge_content_{video_id}.mp4"
