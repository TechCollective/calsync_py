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


# def add_event_old(event_id, summary, start_datetime, end_datetime):
#     event = {
#         'id': event_id,
#         'summary': summary,
#         'start': {
#             'dateTime': start_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
#             'timeZone': 'America/New_York',  # Replace with the appropriate timezone
#         },
#         'end': {
#             'dateTime': end_datetime.strftime('%Y-%m-%dT%H:%M:%S'),
#             'timeZone': 'America/New_York',  # Replace with the appropriate timezone
#         },
#     }

#     # try:
#     event = service.events().insert(calendarId='primary', body=event).execute()
#     log_event(f'Google Event created: {event.get("htmlLink")}')


def add_event(event_body):
    try:
        event = service.events().insert(calendarId='primary', body=event_body).execute()
        log_event(f'Google Event created: {event.get("htmlLink")}')
    except Exception as e:
        log_error(f'Error adding Google Event: {event_body[id]}: {e}')


def modify_event(event_body):
    try:
        event = service.events().patch(calendarId='primary',
                                       eventId=event_body['id'], body=event_body).execute()
        log_event(f'Google Event modified: {event.get("htmlLink")}')
    except Exception as e:
        log_error(f'Error modifying Google Event: {event_body[id]}: {e}')


def delete_event(event_id):
    try:
        event = service.events().delete(calendarId='primary',
                                        eventId=event_id).execute()
        log_event(f'Google Event deleted: {event_id}')
    except Exception as e:
        log_error(f'Error deleting Google Event: {event_id}: {e}')

# def delete_event(event_id):
#     try:
#         service.events().delete(calendarId='primary', eventId=event_id).execute()
#         print(f'Event with ID {event_id} has been deleted.')
#     except Exception as e:
#         print(f'An error occurred while deleting the event: {e}')


# event_summary = 'Test'
# start_time = datetime.datetime(2023, 7, 18, 10, 0)
# end_time = datetime.datetime(2023, 7, 18, 11, 0)

# event_id = 10000  # needs to be at least 5 digits!
# try:
#     add_event(event_id, event_summary, start_time, end_time)
# except Exception as e:
#     log_error(f'error! {e}')


# Function to check if a Google Calendar event exists
def event_exists(event_id):
    try:
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        return True
    except:
        return False


# Example usage
# event_id_to_check = 10001  # Replace with the event ID you want to check
# event_exists(event_id_to_check)


# Function to delete a Google Calendar event
def delete_event(event_id):
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        print(f'Event with ID {event_id} has been deleted.')
    except Exception as e:
        print(f'An error occurred while deleting the event: {e}')


# Example usage
# event_id_to_delete = 10000  # Replace with the event ID you want to delete
# delete_event(event_id_to_delete)
