from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class GoogleSheetsHandler:
    def __init__(self, credentials_json):
        self.credentials = Credentials.from_authorized_user_file(credentials_json, ['https://www.googleapis.com/auth/spreadsheets'])
        self.service = build('sheets', 'v4', credentials=self.credentials)
    
    def log_video(self, spreadsheet_id, video):
        try:
            range_name = 'Sheet1!A:C'
            values = [[video['id'], video['title'], video['url']]]
            body = {'values': values}
            result = self.service.spreadsheets().values().append(
                spreadsheetId=spreadsheet_id, range=range_name,
                valueInputOption='USER_ENTERED', body=body).execute()
            print(f"{result.get('updates').get('updatedCells')} cells appended.")
        except HttpError as error:
            print(f"An error occurred: {error}")
    
    def update_shorts_status(self, spreadsheet_id, video_id, status):
        self._update_cell(spreadsheet_id, video_id, 'D', status)
    
    def update_merge_status(self, spreadsheet_id, video_id, status):
        self._update_cell(spreadsheet_id, video_id, 'E', status)
    
    def update_transcription(self, spreadsheet_id, video_id, transcription):
        self._update_cell(spreadsheet_id, video_id, 'F', transcription)
    
    def update_caption_hashtags(self, spreadsheet_id, video_id, caption, hashtags):
        self._update_cell(spreadsheet_id, video_id, 'G', caption)
        self._update_cell(spreadsheet_id, video_id, 'H', hashtags)
    
    def update_posting_statuses(self, spreadsheet_id, video_id, statuses):
        self._update_cell(spreadsheet_id, video_id, 'I', statuses.get('facebook', ''))
        self._update_cell(spreadsheet_id, video_id, 'J', statuses.get('twitter', ''))
        self._update_cell(spreadsheet_id, video_id, 'K', statuses.get('instagram', ''))
    
    def _update_cell(self, spreadsheet_id, video_id, column, value):
        try:
            range_name = f'Sheet1!{column}:${column}'
            result = self.service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id, range=range_name).execute()
            rows = result.get('values', [])
            
            row_index = None
            for i, row in enumerate(rows):
                if row and row[0] == video_id:
                    row_index = i + 1
                    break
            
            if row_index:
                range_name = f'Sheet1!{column}{row_index}'
                body = {'values': [[value]]}
                result = self.service.spreadsheets().values().update(
                    spreadsheetId=spreadsheet_id, range=range_name,
                    valueInputOption='USER_ENTERED', body=body).execute()
                print(f"{result.get('updatedCells')} cells updated.")
            else:
                print(f"Video ID {video_id} not found in the spreadsheet.")
        except HttpError as error:
            print(f"An error occurred: {error}")

    def get_spreadsheet_id_from_url(self, url):
        # Extract the spreadsheet ID from the URL
        # This is a simple implementation and might need to be adjusted based on the exact URL format
        parts = url.split('/')
        return parts[-2]
