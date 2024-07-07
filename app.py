import os
import streamlit as st
from together import Together
from models import Company, SalesContact
import json
import pandas as pd

# Set up Together API client
together_api_key = os.getenv("TOGETHER_API_KEY")
client = Together(api_key=together_api_key)

st.title("Company Details Fetcher")

input_prompt = st.text_input("Enter your prompt for company details:")

if st.button("Fetch Company Details"):
    if input_prompt:
        response1 = client.chat.completions.create(
            model="meta-llama/Llama-3-8b-chat-hf",
            messages=[{"role": "user", "content": input_prompt}]
        )
        
        company_list = response1.choices[0].message.content.strip()

        detailed_info_prompt = f"{company_list}. Return me the LinkedIn link (only link), company size (only approximate number), funding (only dollar amount), year founded (only year), and head office location (in city/state/country format). Return me contact of their sales dept (email and phone). Return in JSON format for each company and nothing else besides the JSON text."
        
        response2 = client.chat.completions.create(
            model="meta-llama/Llama-3-8b-chat-hf",
            messages=[{"role": "user", "content": detailed_info_prompt}]
        )
        
        detailed_info = response2.choices[0].message.content.strip()

        try:
            # Check if detailed_info is empty or invalid
            if not detailed_info:
                raise ValueError("Received empty response for detailed info.")

            # Attempt to clean the response and ensure it's valid JSON
            detailed_info = detailed_info.replace('\n', '')
            detailed_info = detailed_info[detailed_info.find('['):detailed_info.rfind(']')+1]

            # Ensure it's valid JSON by attempting to load it
            company_details = json.loads(detailed_info)
            
            # Convert to DataFrame
            data = []
            for company in company_details:
                data.append([
                    company.get("name", ""),
                    company.get("linkedin", ""),
                    company.get("size", ""),
                    company.get("funding", ""),
                    company.get("founded", ""),
                    company.get("head_office", ""),
                    company.get("sales_dept", {}).get("email", ""),
                    company.get("sales_dept", {}).get("phone", "")
                ])

            df = pd.DataFrame(data, columns=[
                "Name", "LinkedIn", "Size", "Funding", "Year Founded", "Head Office Location", "Sales Email", "Sales Phone"
            ])

            # Display DataFrame as table
            st.write(df)

        except json.JSONDecodeError:
            st.error("Failed to parse JSON. The response might not be in valid JSON format.")
        except Exception as e:
            st.error(f"Error: {e}")
    else:
        st.warning("Please enter a prompt to fetch company details.")
