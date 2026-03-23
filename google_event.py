import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from log import *

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]
creds = None

if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
service = build('calendar', 'v3', credentials=creds)


def add_event(event_body):
    try:
        event = service.events().insert(calendarId='primary', body=event_body).execute()
        log_event(f'Google Event created: {event.get("htmlLink")}')
    except Exception as e:
        log_error(f'Error adding Google Event: {event_body["id"]}: {e}')


def modify_event(event_body):
    try:
        event = service.events().patch(calendarId='primary',
                                       eventId=event_body['id'], body=event_body).execute()
        log_event(f'Google Event modified: {event.get("htmlLink")}')
    except Exception as e:
        log_error(f'Error modifying Google Event: {event_body["id"]}: {e}')


def event_exists(event_id):
    try:
        service.events().get(calendarId='primary', eventId=event_id).execute()
        return True
    except HttpError as e:
        if e.resp.status in (404, 410):
            return False
        log_error(f'Google API error checking if event {event_id} exists: {e}')
        raise
    except Exception as e:
        log_error(f'Unexpected error checking if event {event_id} exists: {e}')
        raise


def delete_event(event_id):
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        log_event(f'Google Event deleted: {event_id}')
    except HttpError as e:
        if e.resp.status == 410:
            log_event(f'Google Event {event_id} already deleted, skipping')
        else:
            log_error(f'Error deleting Google Event {event_id}: {e}')
    except Exception as e:
        log_error(f'Error deleting Google Event {event_id}: {e}')
