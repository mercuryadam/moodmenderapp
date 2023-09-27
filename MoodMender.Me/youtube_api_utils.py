from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'
CLIENT_SECRETS_FILE = 'path/to/your/client_secret.json'

def get_authenticated_service():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_console()
    return build(API_SERVICE_NAME, API_VERSION, credentials=credentials)

def get_liked_video_details(service):
    results = service.videos().list(
        part='snippet',
        myRating='like',
        maxResults=50  # You can set this to the number of liked videos you want to fetch
    ).execute()

    liked_video_details = []
    for item in results['items']:
        title = item['snippet']['title']
        description = ' '.join(item['snippet']['description'].split()[:20])
        liked_video_details.append({'title': title, 'description': description})

    return liked_video_details
