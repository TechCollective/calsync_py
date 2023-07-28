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
        log_event(
            f'Google Event {event_body[id]} created: {event.get("htmlLink")}')
    except Exception as e:
        log_error(f'Error adding Google Event: {e}')


def modify_event(event_body):
    try:
        event = service.events().patch(calendarId='primary',
                                       eventId=event_body['id'], body=event_body).execute()
        log_event(
            f'Google Event {event_body[id]} modified: {event.get("htmlLink")}')
    except Exception as e:
        log_error(f'Error modifying Google Event: {e}')


def delete_event(event_id):
    try:
        event = service.events().delete(calendarId='primary',
                                        eventId=event_id).execute()
        log_event(f'Google Event deleted: {event_id}')
    except Exception as e:
        log_error(f'Error deleting Google Event: {event_id}: {e}')


def event_exists(event_id):
    try:
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        return True
    except:
        return False


def delete_event(event_id):
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        log_event(f'Event with ID {event_id} has been deleted.')
    except Exception as e:
        log_error(f'An error occurred while deleting the event: {e}')
