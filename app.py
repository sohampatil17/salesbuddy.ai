import os
import streamlit as st
import json
import pandas as pd
from dotenv import load_dotenv
from together import Together
import requests
import time
import pickle
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import re

# Load environment variables from .env file
load_dotenv()

# Get environment variables
together_api_key = os.getenv("TOGETHER_API_KEY")
google_credentials_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
BLAND_API_KEY = os.getenv('BLAND_API_KEY')

# Set the path for Google Cloud credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_credentials_path

# Set up Together API client
client = Together(api_key=together_api_key)

# Set page configuration to wide
st.set_page_config(layout="wide")

# Define the function to create a knowledge base
def create_knowledge_base(company_url):
    prompt = f"Create a detailed knowledge base for the company with the URL {company_url}. Include the company name, year founded, headquarters, relevant information, products and solutions, use cases, key features, and any other pertinent details."

    response = client.chat.completions.create(
        model="meta-llama/Llama-3-8b-chat-hf",
        messages=[{"role": "user", "content": prompt}]
    )

    knowledge_base = response.choices[0].message.content.strip()
    return knowledge_base

# Define the function to fetch company details
def fetch_company_details(prompt):
    response1 = client.chat.completions.create(
        model="meta-llama/Llama-3-8b-chat-hf",
        messages=[{"role": "user", "content": prompt}]
    )

    company_list = response1.choices[0].message.content.strip()

    detailed_info_prompt = f"{company_list}. Return me the company name, LinkedIn link (only link), company URL (only link), company size (only approximate number), funding (only dollar amount in approx like $260K or $57M or $1.4B), year founded (only year), and head office location (in city/state/country format). Return me contact of their sales dept (email and phone). Return in JSON format for each company and nothing else besides the JSON text."
    
    response2 = client.chat.completions.create(
        model="meta-llama/Llama-3-8b-chat-hf",
        messages=[{"role": "user", "content": detailed_info_prompt}]
    )
    
    detailed_info = response2.choices[0].message.content.strip()

    if not detailed_info:
        raise ValueError("Received empty response for detailed info.")

    try:
        # Extract the JSON part from the response
        start_index = detailed_info.find('[')
        end_index = detailed_info.rfind(']') + 1
        if start_index == -1 or end_index == -1:
            raise ValueError("No valid JSON found in the response")

        json_str = detailed_info[start_index:end_index]
        company_details = json.loads(json_str)
    except json.JSONDecodeError:
        st.error("Failed to parse JSON. The response might not be in valid JSON format.")
        st.write(f"Raw response: {detailed_info}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        st.write(f"Raw response: {detailed_info}")
        return pd.DataFrame()

    data = []
    for company in company_details:
        company_name = company.get("name", "")
        if not company_name:
            st.write(f"Missing company name in: {company}")  # Debugging line
        formatted_funding = company.get("funding", "")
        data.append([
            company_name,
            company.get("size", ""),
            formatted_funding,
            company.get("founded", ""),
            company.get("head_office", ""),
            company.get("sales_dept", {}).get("email", ""),
            company.get("sales_dept", {}).get("phone", ""),
            ""  # Empty Notes column
        ])

    df = pd.DataFrame(data, columns=[
        "Name", "Size", "Funding", "Year Founded", "Head Office Location", "Sales Email", "Sales Phone", "Notes"
    ])

    return df

def make_ai_call(phone_number, task, knowledge_base, voice='mason', language='eng'):
    headers = {
        'authorization': BLAND_API_KEY,
        'Content-Type': 'application/json'
    }
    data = {
        'phone_number': phone_number,
        'task': task,
        'voice': voice,
        'language': language,
        'request_data': {
            'knowledge_base': knowledge_base
        },
        'record': True,
        'reduce_latency': True,
        'amd': True
    }
    response = requests.post('https://api.bland.ai/v1/calls', json=data, headers=headers)
    return response.json()

def fetch_call_analysis(call_id):
    url = f"https://api.bland.ai/v1/calls/{call_id}/analyze"
    headers = {
        "authorization": BLAND_API_KEY,
        "Content-Type": "application/json"
    }

    payload = {
        "goal": "Extract the contact name, email address, meeting time, buying intent, and provide a summary of the call.",
        "questions": [
            ["What is the contact name?", "string"],
            ["What is the email address?", "string"],
            ["What is the meeting time?", "string"],
            ["What is the buying intent?", "string"],
            ["Provide a summary of the call that includes name, email of the callee, and scheduled meeting time and date.", "string"]
        ]
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return {
            'error': f"Failed to analyze call. Status code: {response.status_code}",
            'details': response.text
        }

def extract_event_details_with_ai(summary):
    api_url = "https://api.together.ai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {together_api_key}",
        "Content-Type": "application/json"
    }
    prompt = f"Extract event details from the following summary and generate a JSON in the exact format as specified below, return nothing but the JSON. :\n\nSummary: {summary} + Assume it is July 2024.\n\n" \
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

        event_details = json.loads(event_details_json)
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        raise Exception(f"Error parsing JSON response: {e}")

    print(event_details)
    return event_details

def authenticate_google_calendar():
    creds = None
    SCOPES = ['https://www.googleapis.com/auth/calendar']
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

def create_event(service, event_details):
    print("starting")
    event = service.events().insert(calendarId='primary', body=event_details).execute()
    print('Event created: %s' % (event.get('htmlLink')))

# Navigation control
if 'step' not in st.session_state:
    st.session_state['step'] = 1

# Step 1: Create Company Knowledge Base
if st.session_state['step'] == 1:
    st.title("Salesbuddy.ai 🔮💹")
    
    company_url = st.text_input("What's your company URL?", key="company_url", help="Enter the company's website URL.")
    
    if st.button("Create Knowledge Base") and company_url:
        with st.spinner("Creating knowledge base...✨"):
            try:
                knowledge_base = create_knowledge_base(company_url)
                st.session_state['company_info'] = knowledge_base.replace("**", "").replace("###", "")
                st.session_state['step'] = 2
            except Exception as e:
                st.error(f"Error creating knowledge base: {e}")

# Step 2: Edit and Save Company Knowledge Base
if st.session_state['step'] == 2:
    
    if 'company_info' in st.session_state:
        knowledge_base = st.session_state['company_info']
        
        st.write("#### Sales Knowledge Base")
        edited_info = st.text_area("Edit your company info below and click save:", knowledge_base, height=400, key="edited_info")
        
        if st.button("Save"):
            st.session_state['company_info'] = edited_info
            st.success("Company information saved!")
            
        if st.button("Next"):
            st.session_state['step'] = 3

# Step 3: Fetch Company Details
if st.session_state['step'] == 3:
    st.title("Salesbuddy.ai 🔮💹")

    input_prompt = st.text_input("Find your next leads here:", key="input_prompt", help="Enter a prompt to fetch company details.")

    if st.button("Find leads ✨"):
        if input_prompt:
            try:
                df = fetch_company_details(input_prompt)
                st.session_state['company_df'] = df
            except Exception as e:
                st.error(f"Error fetching company details: {e}")
        else:
            st.warning("Please enter a prompt to fetch company details.")

    if 'company_df' in st.session_state:
        df = st.session_state['company_df']

        if "Notes" not in df.columns:
            df["Notes"] = ""

        st.write("#### Prospective sales/customers:")

        col1, col2 = st.columns([3, 1])
        with col1:
            selected_company = st.selectbox("Select a company to call:", df["Name"])
        with col2:
            if selected_company:
                selected_row = df[df["Name"] == selected_company].iloc[0]
                phone_number = selected_row["Sales Phone"]
                knowledge_base = st.session_state['company_info']
                task = f"""
                You are calling a salesperson at {selected_company}. Your goal is introduce your company and schedule a follow-up conversation.
                Use the following knowledge base for reference: {knowledge_base}
                Call Flow:
                    Introduce yourself as Oliver and say you are calling from the company mentioned in knowledge base.
                    Introduce in 1 line about your company's offerings.
                    Ask who you are talking to and what their company needs are.
                    Say you are trying to schedule a follow-up conversation with your head of sales.
                    If they need to reschedule, offer some alternate time slots later in the week.
                    Get their name, and email id in order to send a calendar invite.
                    Once the new time and date is confirmed or the original time and date is reconfirmed, thank him and provide your email if he needs to get in touch.
                    Be polite, respectful, and try not to speak too much.
                """
                if st.button("📞", key="make_call"):
                    with st.spinner("Making AI call...🪄"):
                        call_response = make_ai_call(phone_number, task, knowledge_base)
                        if call_response.get('status') == 'success':
                            call_id = call_response.get('call_id')
                            time.sleep(200)
                            analysis_response = fetch_call_analysis(call_id)
                            if 'error' not in analysis_response:
                                call_summary = analysis_response['answers'][-1]
                                df.loc[df['Name'] == selected_company, 'Notes'] = call_summary
                                st.session_state['company_df'] = df
                                st.success("Call completed and summary updated in notes.")
                            else:
                                st.error(f"Failed to analyze call: {analysis_response['error']}")
                                st.write(analysis_response['details'])
                        else:
                            st.error("Failed to make the call.")

        edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True, disabled=["Name", "Size", "Funding", "Year Founded", "Head Office Location", "Sales Email"])

        st.session_state['company_df'] = edited_df

        if st.button("Schedule Meeting 📆"):
            summary = df.loc[df['Name'] == selected_company, 'Notes'].values[0]
            if summary:
                with st.spinner("Scheduling meeting...🪄"):
                    try:
                        creds = authenticate_google_calendar()
                        service = build('calendar', 'v3', credentials=creds)
                        event_details = extract_event_details_with_ai(summary)
                        create_event(service, event_details)
                        st.success("Meeting scheduled successfully! ✅")
                    except Exception as e:
                        st.error(f"Error scheduling meeting: {e}")
