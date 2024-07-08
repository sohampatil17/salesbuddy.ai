import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get environment variables
BLAND_API_KEY = os.getenv('BLAND_API_KEY')

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

def analyze_call(call_id):
    headers = {
        'authorization': BLAND_API_KEY,
        'Content-Type': 'application/json'
    }
    response = requests.post(f'https://api.bland.ai/v1/calls/{call_id}/analyze', headers=headers)
    return response.json()

if __name__ == "__main__":
    phone_number = "+1 7022660600"  # Example phone number
    company_url = "https://ramp.com"
    company_name = "Ramp"
    knowledge_base = """
        
        """

    task = f"""
    You are calling from {company_name} to schedule a follow-up conversation with a sales specialist.
    Use the following knowledge base for reference: {knowledge_base}
    Goal: Collect contact name, email address, meeting time, and buying intent (high, low, medium). 
    Also, provide a summary of the call.
    """

    call_response = make_ai_call(phone_number, task, knowledge_base)
    print("Call Response:", call_response)

    if call_response['status'] == 'success':
        call_id = call_response['call_id']
        analysis_response = analyze_call(call_id)
        print("Analysis Response:", analysis_response)
