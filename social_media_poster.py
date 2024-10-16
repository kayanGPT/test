import facebook
import tweepy
from instagram_private_api import Client, ClientCompatPatch
from api_utils import retry_api_call

class SocialMediaPoster:
    def __init__(self, config):
        self.fb_access_token = config['FACEBOOK_ACCESS_TOKEN']
        self.tw_api_key = config['TWITTER_API_KEY']
        self.tw_api_secret = config['TWITTER_API_SECRET']
        self.tw_access_token = config['TWITTER_ACCESS_TOKEN']
        self.tw_access_token_secret = config['TWITTER_ACCESS_TOKEN_SECRET']
        self.ig_username = config['INSTAGRAM_USERNAME']
        self.ig_password = config['INSTAGRAM_PASSWORD']
    
    def schedule_posts(self, video_url, caption, hashtags):
        statuses = {}
        
        # Facebook
        try:
            fb_status = self.post_to_facebook(video_url, caption, hashtags)
            statuses['facebook'] = fb_status
        except Exception as e:
            statuses['facebook'] = f"Error: {str(e)}"
        
        # Twitter
        try:
            tw_status = self.post_to_twitter(video_url, caption, hashtags)
            statuses['twitter'] = tw_status
        except Exception as e:
            statuses['twitter'] = f"Error: {str(e)}"
        
        # Instagram
        try:
            ig_status = self.post_to_instagram(video_url, caption, hashtags)
            statuses['instagram'] = ig_status
        except Exception as e:
            statuses['instagram'] = f"Error: {str(e)}"
        
        return statuses
    
    @retry_api_call(max_retries=3, delay=5)
    def post_to_facebook(self, video_url, caption, hashtags):
        graph = facebook.GraphAPI(access_token=self.fb_access_token, version="3.0")
        post_message = f"{caption}\n\n{hashtags}"
        response = graph.put_video(video_url, title=caption[:100], description=post_message)
        return "Posted" if response.get('id') else "Failed"
    
    @retry_api_call(max_retries=3, delay=5)
    def post_to_twitter(self, video_url, caption, hashtags):
        auth = tweepy.OAuthHandler(self.tw_api_key, self.tw_api_secret)
        auth.set_access_token(self.tw_access_token, self.tw_access_token_secret)
        api = tweepy.API(auth)
        
        tweet_text = f"{caption[:200]}... {hashtags}"  # Twitter has a 280 character limit
        media = api.media_upload(video_url)
        response = api.update_status(status=tweet_text, media_ids=[media.media_id])
        return "Posted" if response.id else "Failed"
    
    @retry_api_call(max_retries=3, delay=5)
    def post_to_instagram(self, video_url, caption, hashtags):
        api = Client(self.ig_username, self.ig_password)
        post_message = f"{caption}\n\n{hashtags}"
        response = api.post_video(video_url, caption=post_message)
        return "Posted" if response.get('status') == 'ok' else "Failed"
