import streamlit as st
from groq import Groq
import google.generativeai as genai
import requests
import json

# --- ENGINE CONFIGURATION ---
# Options: "GROQ", "GEMINI", "OPENROUTER"
ACTIVE_ENGINE = "GROQ" 

def get_tavily_intel(query):
    """Fetches real-time threat intelligence via Tavily API."""
    api_key = st.secrets.get("TAVILY_API_KEY", "").strip()
    if not api_key: return "No real-time intel available."
    
    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={"api_key": api_key, "query": query, "search_depth": "advanced"},
            timeout=10
        )
        data = response.json()
        return "\n".join([f"- {r['content']}" for r in data.get('results', [])[:3]])
    except:
        return "Intelligence core unreachable."

def generate_sop(siem, logic, client_name, log_sources):
    # 1. Real-time Research
    intel = get_tavily_intel(f"Incident response steps for {siem} {logic[:50]}")

    system_prompt = f"""
    You are SOP-Genie, a Senior SOC Architect. Create a technical SOP for {client_name}.
    LOG SOURCES: {log_sources}
    REAL-TIME INTEL: {intel}
    
    Output Markdown: Executive Summary, Kill Chain, MITRE Mapping, GRC Mapping, 
    Triage, Investigation, Containment, Eradication, and a Mermaid flowchart.
    """

    # --- ROUTING LOGIC ---
    try:
        if ACTIVE_ENGINE == "GROQ":
            client = Groq(api_key=st.secrets["GROQ_API_KEY"].strip())
            res = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": logic}],
                temperature=0.1
            )
            return res.choices[0].message.content

        elif ACTIVE_ENGINE == "GEMINI":
            genai.configure(api_key=st.secrets["GEMINI_API_KEY"].strip())
            model = genai.GenerativeModel('gemini-1.5-flash')
            res = model.generate_content(f"{system_prompt}\n\n{logic}")
            return res.text

        elif ACTIVE_ENGINE == "OPENROUTER":
            res = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {st.secrets['OPENROUTER_API_KEY'].strip()}"},
                data=json.dumps({
                    "model": "anthropic/claude-3.5-sonnet",
                    "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": logic}]
                })
            )
            return res.json()['choices'][0]['message']['content']

    except Exception as e:
        return f"🚨 **AI ENGINE ERROR ({ACTIVE_ENGINE}):** {str(e)}"
