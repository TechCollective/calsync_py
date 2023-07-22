import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from log import *

# update to import scopes and creds from g_auth!

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]


creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
service = build('calendar', 'v3', credentials=creds)


def add_event(summary, start_datetime, end_datetime):
    event = {
        'summary': summary,
        'start': {
            'dateTime': start_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
            'timeZone': 'America/New_York',  # Replace with the appropriate timezone
        },
        'end': {
            'dateTime': end_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
            'timeZone': 'America/New_York',  # Replace with the appropriate timezone
        },
    }

    # try:
    event = service.events().insert(calendarId='primary', body=event).execute()
    log_event(f'Google Event created: {event.get("htmlLink")}')


# Example usage
event_summary = 'Meeting with John'
# Replace with the appropriate start time
start_time = datetime.datetime(2023, 7, 18, 10, 0)
# Replace with the appropriate end time
end_time = datetime.datetime(2023, 7, 18, 11, 0)

try:
    add_event(event_summary, start_time, end_time)
except Exception as e:
    log_error(f'error! {e}')
