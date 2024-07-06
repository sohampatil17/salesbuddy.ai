from __future__ import print_function
import datetime
import os.path
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_calendar():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            # Redirect URI should match the one registered in Google Cloud Console
            flow.redirect_uri = 'http://localhost:8080/'
            creds = flow.run_local_server(port=8080)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def create_event(service):
    event = {
    "summary": "CRM Integration Demo",
    "location": "Zoom Meeting",
    "description": "A demo of the CRM integration process with our technical specialist.",
    "start": {
        "dateTime": "2024-07-12T10:00:00-07:00",
        "timeZone": "America/Los_Angeles"
    },
    "end": {
        "dateTime": "2024-07-12T11:00:00-07:00",
        "timeZone": "America/Los_Angeles"
    },
    "attendees": [
        {
        "email": "taylor@example.com"
        },
        {
        "email": "alex@xyzsolutions.com"
        }
    ],
    "reminders": {
        "useDefault": False,
        "overrides": [
        {
            "method": "email",
            "minutes": 24 * 60
        },
        {
            "method": "popup",
            "minutes": 10
        }
        ]
    }
    }


    event = service.events().insert(calendarId='primary', body=event).execute()
    print('Event created: %s' % (event.get('htmlLink')))

def main():
    creds = authenticate_google_calendar()
    service = build('calendar', 'v3', credentials=creds)
    create_event(service)

if __name__ == '__main__':
    main()
