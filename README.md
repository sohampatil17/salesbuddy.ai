## Find Leads, Call Clients & Schedule Meetings w AI 🔮🤖
<br>
<img width="1165" alt="Screenshot 2024-07-08 at 9 31 48 PM" src="https://github.com/sohampatil17/salesbuddy.ai/assets/66875241/f6801500-3fda-4a6c-b81b-41e6eaf67be1">


## 💡 Inspiration
Sales processes can be incredibly time-consuming and complex. Sales teams often juggle multiple tasks like lead generation, client communication, and meeting scheduling. We were inspired by the need to streamline these tasks using AI, making the entire process more efficient and less tedious. Imagine having a smart buddy that can handle all your sales tasks effortlessly! 💡✨

## What it does 📚 ➡️ 🔍 ➡️ 📞 ➡️ 📅
1)  Creates a detailed **knowledge base** for your company using URL and company webpage.  
2) Conducts **sales research** and finds clients using LLMs and formats the data.  
3) Makes **AI-driven calls** to potential clients and analyzes call recordings.  
4) **Schedules meetings** on your Google Calendar from call summary using AI.  

Imagine a personal sales assistant that works tirelessly to keep your pipeline full and your schedule organized!

## 🛠️ How we built it
- **Together API (Llama-3-8b)** for sales research (AI-driven content generation).
- **BlandAI** for calling the client with voice agents and analyzing the call recordings. Example call prompt -   
`Introduce yourself as Oliver and say you are calling from the company mentioned.`
- **Google Calendar API** for scheduling meetings using data from call summary.
- **Streamlit** for the user-friendly interface.

Our backend connects to these services to fetch and process data, ensuring a smooth user experience.

## 🌟 Challenges we ran into
- Integrating multiple APIs and ensuring they work seamlessly.
- Structured formatting of LLM outputs Though LLMs are good at generating content, it's really hard to get them in the proper format in order to build tools or tables
- Finding AI calling agents that sound natural, engaging, and simulating a real salesperson.

## 🏆 Accomplishments that we're proud of
- Successfully automating the entire sales process from leads research to meetings.
- Integrating company knowledge base to make AI calls and find clients.
- Learning about LLM parsing and output formatting + LLM eval knowledge.

## 🧠 What we learned
I discovered how powerful AI can be in automating repetitive tasks and boosting efficiency. Throughout my project, I experimented with various large language models (LLMs) and evaluated their performance. I learned a lot about integrating APIs effectively and handling call summaries and transcription. I also tried different call agents, including Twilio, to find the best fit for my needs. This journey has shown me just how much AI can transform the sales process and add real value to businesses.

## 🌟 What's next for Salesbuddy.ai
- Enhancing AI capabilities to handle even more complex sales scenarios like automating follow up calls.
- Adding CRM integrations like Salesforce or Hubspot to make the sales process even smoother.
- Piloting projects with sales companies and startups to iterate on the MVP.
