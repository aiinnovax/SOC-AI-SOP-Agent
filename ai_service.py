import streamlit as st
from groq import Groq
import google.generativeai as genai
import requests
import json

# --- CONFIG ---
model = genai.GenerativeModel("gemini-pro")

genai.configure(api_key=st.secrets.get("GEMINI_API_KEY"))


def get_tavily_intel(query):
    raw_key = st.secrets.get("TAVILY_API_KEY", "").strip().replace('"', '').replace("'", "")
    if not raw_key:
        return "No real-time threat intelligence context available."

    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": raw_key,
                "query": query,
                "search_depth": "advanced",
                "max_results": 3
            },
            timeout=10
        )
        data = response.json()
        return "\n".join([f"- {r['content']}" for r in data.get('results', [])])
    except Exception as e:
        return f"Tavily Error: {str(e)}"


def generate_sop(siem, logic, client_name, log_sources):

    research_query = f"Incident response steps and vulnerabilities for {siem} {logic[:200]}"
    intel_context = get_tavily_intel(research_query)

    system_prompt = f"""..."""  # keep yours

    try:
        if ACTIVE_ENGINE == "GEMINI":
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"{system_prompt}\n\nLogic:\n{logic}")
            return getattr(response, "text", "⚠️ Empty response from Gemini")

        elif ACTIVE_ENGINE == "GROQ":
            client = Groq(api_key=st.secrets.get("GROQ_API_KEY"))
            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": logic}
                ],
            )
            return completion.choices[0].message.content

        elif ACTIVE_ENGINE == "OPENROUTER":
            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {st.secrets.get('OPENROUTER_API_KEY')}"},
                data=json.dumps({
                    "model": "anthropic/claude-3.5-sonnet",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": logic}
                    ]
                })
            )
            return response.json()['choices'][0]['message']['content']

    except Exception as e:
        return f"🚨 ERROR ({ACTIVE_ENGINE}): {str(e)}"

    return "No engine selected"
