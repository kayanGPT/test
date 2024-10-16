import os

def load_config():
    return {
        'DATABASE_URL': os.environ.get('DATABASE_URL', 'placeholder_database_url'),
        'YOUTUBE_API_KEY': os.environ.get('YOUTUBE_API_KEY', 'placeholder_youtube_api_key'),
        'KLAP_API_KEY': os.environ.get('KLAP_API_KEY', 'placeholder_klap_api_key'),
        'PLACID_API_KEY': os.environ.get('PLACID_API_KEY', 'placeholder_placid_api_key'),
        'OPENAI_API_KEY': os.environ.get('OPENAI_API_KEY', 'placeholder_openai_api_key'),
        'GOOGLE_SHEETS_CREDENTIALS': os.environ.get('GOOGLE_SHEETS_CREDENTIALS', 'placeholder_google_sheets_credentials'),
        'FACEBOOK_ACCESS_TOKEN': os.environ.get('FACEBOOK_ACCESS_TOKEN', 'placeholder_facebook_access_token'),
        'TWITTER_API_KEY': os.environ.get('TWITTER_API_KEY', 'placeholder_twitter_api_key'),
        'TWITTER_API_SECRET': os.environ.get('TWITTER_API_SECRET', 'placeholder_twitter_api_secret'),
        'TWITTER_ACCESS_TOKEN': os.environ.get('TWITTER_ACCESS_TOKEN', 'placeholder_twitter_access_token'),
        'TWITTER_ACCESS_TOKEN_SECRET': os.environ.get('TWITTER_ACCESS_TOKEN_SECRET', 'placeholder_twitter_access_token_secret'),
        'INSTAGRAM_ACCESS_TOKEN': os.environ.get('INSTAGRAM_ACCESS_TOKEN', 'placeholder_instagram_access_token'),
        'CHECK_INTERVAL': 300,  # 5 minutes
        'ERROR_RETRY_INTERVAL': 60,  # 1 minute
    }

def is_config_placeholder(config):
    return any('placeholder' in str(value) for value in config.values())
