from __future__ import print_function
import datetime
import os.path
import pickle
import json
import re
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import requests

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def authenticate_google_calendar():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=8080)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

together_api_key = os.getenv("TOGETHER_API_KEY")

def extract_event_details_with_ai(summary):
    api_url = "https://api.together.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {together_api_key}",
        "Content-Type": "application/json"
    }
    prompt = f"Extract event details from the following summary and generate a JSON in the exact format as specified below, return nothiing but the JSON. :\n\nSummary: {summary}\n\n" \
             "JSON Format:\n" \
             "{{\n" \
             "  \"summary\": \"Event Title\",\n" \
             "  \"location\": \"Event Location\",\n" \
             "  \"description\": \"Event Description\",\n" \
             "  \"start\": {{\n" \
             "    \"dateTime\": \"YYYY-MM-DDTHH:MM:SS-07:00\",\n" \
             "    \"timeZone\": \"America/Los_Angeles\"\n" \
             "  }},\n" \
             "  \"end\": {{\n" \
             "    \"dateTime\": \"YYYY-MM-DDTHH:MM:SS-07:00\",\n" \
             "    \"timeZone\": \"America/Los_Angeles\"\n" \
             "  }},\n" \
             "  \"attendees\": [\n" \
             "    {{\n" \
             "      \"email\": \"attendee@example.com\"\n" \
             "    }}\n" \
             "  ],\n" \
             "  \"reminders\": {{\n" \
             "    \"useDefault\": False,\n" \
             "    \"overrides\": [\n" \
             "      {{\n" \
             "        \"method\": \"email\",\n" \
             "        \"minutes\": 24 * 60\n" \
             "      }},\n" \
             "      {{\n" \
             "        \"method\": \"popup\",\n" \
             "        \"minutes\": 10\n" \
             "      }}\n" \
             "    ]\n" \
             "  }}\n" \
             "}}\n Ensure again you are returning only the JSON and nothing else."

    data = {
        "model": "meta-llama/Llama-3-8b-chat-hf",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(api_url, headers=headers, json=data)
    
    # Debugging output
    print(f"API response status code: {response.status_code}")
    print(f"API response text: {response.text}")

    if response.status_code != 200:
        raise Exception(f"API request failed with status code {response.status_code}: {response.text}")

    try:
        response_data = response.json()
        event_details_message = response_data['choices'][0]['message']['content'].strip()

        # Debugging output to see the exact message content
        print(f"Event details message: {event_details_message}")

        # Extract JSON from the message content by finding the first and last curly brackets
        json_start = event_details_message.find('{')
        json_end = event_details_message.rfind('}') + 1
        if json_start == -1 or json_end == -1:
            raise ValueError("No JSON content found in the response message")
        
        event_details_json = event_details_message[json_start:json_end]
        event_details_json = event_details_json.replace('```', '').strip()  # Remove backticks if any
        print(f"Event details JSON: {event_details_json}")  # Debugging output to see the extracted JSON string

        # Additional cleanup for any unexpected characters
        event_details_json = re.sub(r'\\n', '', event_details_json)
        event_details_json = re.sub(r'\\', '', event_details_json)
        event_details_json = re.sub(r'\s+', ' ', event_details_json)
        
        # Remove trailing commas if present
        event_details_json = re.sub(r',\s*}', '}', event_details_json)
        event_details_json = re.sub(r',\s*]', ']', event_details_json)

        # # Print problematic part of the JSON string
        # error_pos = 399  # Position mentioned in the error message
        # if error_pos < len(event_details_json):
        #     print(f"Character at position {error_pos}: '{event_details_json[error_pos]}'")
        #     print(f"Surrounding context: '{event_details_json[error_pos-20:error_pos+20]}'")

        event_details = json.loads(event_details_json)
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        raise Exception(f"Error parsing JSON response: {e}")

    print(event_details)
    return event_details

def create_event(service, event_details):
    print("starting")
    event = service.events().insert(calendarId='primary', body=event_details).execute()
    print('Event created: %s' % (event.get('htmlLink')))

def main():
    summary = "John at john@gmail.com is interested in learning more about Ramp's payment platform and solutions for businesses. A meeting has been scheduled for this Friday at 2pm to discuss further." + "Assume year is July 2024."
    creds = authenticate_google_calendar()
    service = build('calendar', 'v3', credentials=creds)
    event_details = extract_event_details_with_ai(summary)
    create_event(service, event_details)

if __name__ == '__main__':
    main()
