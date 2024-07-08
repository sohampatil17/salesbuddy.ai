import os
import streamlit as st
from together import Together
import json
import pandas as pd

# Set up Together API client
together_api_key = os.getenv("TOGETHER_API_KEY")
client = Together(api_key=together_api_key)

st.set_page_config(layout="wide")  # Set the page layout to wide

st.title("Company Details Fetcher")

input_prompt = st.text_input("Enter your prompt for company details:")

# Function to fetch company details
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

    # Check if detailed_info is empty or invalid
    if not detailed_info:
        raise ValueError("Received empty response for detailed info.")

    # Attempt to clean the response and ensure it's valid JSON
    detailed_info = detailed_info.replace('\n', '').replace('\r', '')
    detailed_info = detailed_info[detailed_info.find('['):detailed_info.rfind(']')+1]

    # Ensure it's valid JSON by attempting to load it
    try:
        company_details = json.loads(detailed_info)
    except json.JSONDecodeError:
        st.error("Failed to parse JSON. The response might not be in valid JSON format.")
        st.write(f"Raw response: {detailed_info}")
        return pd.DataFrame()

    # Convert to DataFrame
    data = []
    for company in company_details:
        company_name = company.get("name") or company.get("company", "")
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

# Fetch and display company details
if st.button("Fetch Company Details"):
    if input_prompt:
        df = fetch_company_details(input_prompt)
        st.session_state['company_df'] = df
    else:
        st.warning("Please enter a prompt to fetch company details.")

# Display the company details DataFrame
if 'company_df' in st.session_state:
    df = st.session_state['company_df']

    # Add a Notes column if it doesn't exist
    if "Notes" not in df.columns:
        df["Notes"] = ""

    # Display the DataFrame with editable phone numbers and notes
    edited_df = st.data_editor(df, num_rows="dynamic", use_container_width=True)

    # Update the session state with the edited DataFrame
    st.session_state['company_df'] = edited_df
