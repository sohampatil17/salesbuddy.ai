import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get environment variables
BLAND_API_KEY = os.getenv('BLAND_API_KEY')

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
            ["Provide a summary of the call.", "string"]
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

if __name__ == "__main__":
    call_id = "91e85302-f51d-423c-93a5-4cba46aab6d8"  # Replace with actual call ID
    analysis_result = fetch_call_analysis(call_id)
    
    if 'error' not in analysis_result:
        print("Analysis Result:")
        for key, value in analysis_result.items():
            print(f"{key}: {value}")
    else:
        print(analysis_result['error'])
        print(analysis_result['details'])
