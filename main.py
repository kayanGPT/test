import time
from config import load_config, is_config_placeholder
from youtube_handler import YouTubeHandler
from video_processor import VideoProcessor
from transcription_handler import TranscriptionHandler
from content_generator import ContentGenerator
from social_media_poster import SocialMediaPoster
from database_manager import DatabaseManager
from google_sheets_handler import GoogleSheetsHandler
from utils import setup_logging

def main():
    config = load_config()
    logger = setup_logging()

    if is_config_placeholder(config):
        logger.warning("Using placeholder values for some configuration items. The system may not function correctly until all required secrets are provided.")

    try:
        db = DatabaseManager(config['DATABASE_URL'])
        sheets = GoogleSheetsHandler(config['GOOGLE_SHEETS_CREDENTIALS'])
        youtube = YouTubeHandler(config['YOUTUBE_API_KEY'])
        video_processor = VideoProcessor(config['KLAP_API_KEY'], config['PLACID_API_KEY'])
        transcription = TranscriptionHandler(config['OPENAI_API_KEY'])
        content_gen = ContentGenerator(config['OPENAI_API_KEY'])
        social_poster = SocialMediaPoster(config)

        logger.info("Starting automated video processing and posting system")

        while True:
            try:
                # Get all users
                users = db.get_all_users()
                
                for user in users:
                    # Check for new YouTube uploads
                    new_videos = youtube.check_new_uploads()
                    
                    for video in new_videos:
                        # Get user's Google Sheet URL
                        sheet_url = user['google_sheet_url']
                        if not sheet_url:
                            logger.warning(f"User {user['username']} has no Google Sheet URL set. Skipping.")
                            continue
                        
                        spreadsheet_id = sheets.get_spreadsheet_id_from_url(sheet_url)
                        
                        # Log video details in Google Sheets
                        sheets.log_video(spreadsheet_id, video)
                        
                        # Process video with Klap AI
                        shorts = video_processor.create_shorts(video['url'])
                        sheets.update_shorts_status(spreadsheet_id, video['id'], "Shorts Created")
                        
                        # Merge shorts with sludge content
                        merged_video = video_processor.merge_with_sludge(shorts, video['id'])
                        sheets.update_merge_status(spreadsheet_id, video['id'], "Merged")
                        
                        # Transcribe merged video
                        transcription_text = transcription.transcribe_video(merged_video['url'])
                        sheets.update_transcription(spreadsheet_id, video['id'], transcription_text)
                        
                        # Generate captions and hashtags
                        caption, hashtags = content_gen.generate_content(transcription_text)
                        sheets.update_caption_hashtags(spreadsheet_id, video['id'], caption, hashtags)
                        
                        # Schedule posts across platforms
                        posting_statuses = social_poster.schedule_posts(merged_video['url'], caption, hashtags)
                        sheets.update_posting_statuses(spreadsheet_id, video['id'], posting_statuses)
                        
                        # Update database
                        db.update_video_status(video['id'], "Completed")
                
                # Sleep for a while before checking again
                time.sleep(config['CHECK_INTERVAL'])
            
            except Exception as e:
                logger.error(f"An error occurred in the main loop: {str(e)}")
                time.sleep(config['ERROR_RETRY_INTERVAL'])

    except Exception as e:
        logger.error(f"A critical error occurred: {str(e)}")
        logger.info("Shutting down the system due to a critical error.")

if __name__ == "__main__":
    main()
