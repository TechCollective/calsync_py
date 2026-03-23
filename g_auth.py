"""
Run this script once to authorize the app and generate token.json.
If token.json already exists and is valid, it will be refreshed if expired.
"""

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# If modifying these scopes, delete token.json and re-run this script.
SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

creds = None

if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        print("Token refreshed successfully.")
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        print("Authorization complete.")

    with open('token.json', 'w') as token:
        token.write(creds.to_json())
    print("token.json saved.")
else:
    print("Existing token is still valid. No action needed.")
