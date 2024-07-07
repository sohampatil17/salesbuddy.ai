import os
from together import Together

client = Together(api_key=os.environ.get("TOGETHER_API_KEY"))

response1 = client.chat.completions.create(
    model="meta-llama/Llama-3-8b-chat-hf",
    messages=[{"role": "user", "content": "Give me a list of 5-10 B2B payment gateway companies in USA." + "Return strictly the list in one sentence format"}],
)

company_list = response1.choices[0].message.content
print("Company List:", company_list)

# Second request: Get detailed information about the sales teams of the listed companies
response2 = client.chat.completions.create(
    model="meta-llama/Llama-3-8b-chat-hf",
    messages=[{"role": "user", "content": f"{company_list}. Return me the Linkedin link (only link), company size (only approximate number), funding (only dollar amount), year founded (only year), and headoffice location (in city/state/country format). return me contact of their sales dept (email and phone). Return in JSON format for each company and nothing else besides the JSON text"}],
)

print(response2.choices[0].message.content)