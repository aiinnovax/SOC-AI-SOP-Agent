import streamlit as st
from groq import Groq
import google.generativeai as genai
import requests
import json

# --- AI ENGINE CONFIGURATION ---
# Toggle between "GROQ", "GEMINI", or "OPENROUTER" to change the platform brain
ACTIVE_ENGINE = "GROQ" 

def get_tavily_intel(query):
    """
    Connects to Tavily AI to fetch real-time threat intelligence and CVE data.
    This ensures SOPs are not just generic but include current-day threat data.
    """
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
        results = data.get('results', [])
        return "\n".join([f"- {r['content']}" for r in results])
    except Exception:
        return "Intelligence core unreachable. Falling back to internal knowledge base."

def generate_sop(siem, logic, client_name, log_sources):
    """
    The main synthesis engine. It researches the threat first, 
    then routes the data to the active AI agent.
    """
    
    # 1. Research phase (Tavily)
    research_query = f"Incident response steps and recent vulnerabilities for {siem} {logic[:50]}"
    intel_context = get_tavily_intel(research_query)

    # 2. Architect the Prompt
    system_prompt = f"""
    You are SOP-Genie, a Senior Cyber Security Architect specializing in Managed Security Services (MSS).
    Your task is to translate raw technical detection logic into a professional Standard Operating Procedure (SOP).
    
    TARGET CLIENT: {client_name}
    SPECIFIC LOG SOURCES: {log_sources}
    REAL-TIME THREAT INTEL: {intel_context}
    
    You MUST output the response in professional Markdown with these exact sections:
    1. **Executive Summary**: A plain-English explanation of what this detection logic is looking for.
    2. **Cyber Kill Chain Phase**: Identify where this falls in the attack lifecycle.
    3. **MITRE ATT&CK Mapping**: Tactic name and Technique IDs (e.g., T1059).
    4. **GRC Compliance Mapping**: Reference ISO 27001, NIST, or SOC2 relevance.
    5. **Identification (Triage)**: Step-by-step instructions for a Tier 1 analyst.
    6. **Investigation (Scoping)**: Deep-dive steps for a Tier 2 analyst using {log_sources}.
    7. **Containment**: Immediate actions to stop the threat.
    8. **Eradication & Recovery**: Steps to clean the environment and restore service.
    9. **Tier 1 Rapid Response Checklist**: A bulleted quick-action list.
    10. **Visual Decision Tree**: A Mermaid.js flowchart mapping the triage path. Enclose in a ```mermaid block.
    """

    # 3. Routing Phase
    try:
        # --- GROQ ENGINE (Llama 3 70B) ---
        if ACTIVE_ENGINE == "GROQ":
            raw_key = st.secrets.get("GROQ_API_KEY", "").strip().replace('"', '').replace("'", "")
            if not raw_key: return "🚨 ERROR: GROQ_API_KEY is missing."
            
            client = Groq(api_key=raw_key)
            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Detection Logic to Analyze:\n{logic}"}
                ],
                temperature=0.1,
                max_tokens=2048
            )
            return completion.choices[0].message.content

        # --- GEMINI ENGINE (Google 1.5 Flash) ---
        elif ACTIVE_ENGINE == "GEMINI":
            raw_key = st.secrets.get("GEMINI_API_KEY", "").strip().replace('"', '').replace("'", "")
            if not raw_key: return "🚨 ERROR: GEMINI_API_KEY is missing."
            
            genai.configure(api_key=raw_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"{system_prompt}\n\nLogic:\n{logic}")
            return response.text

        # --- OPENROUTER ENGINE (Claude 3.5 Sonnet / GPT-4) ---
        elif ACTIVE_ENGINE == "OPENROUTER":
            raw_key = st.secrets.get("OPENROUTER_API_KEY", "").strip().replace('"', '').replace("'", "")
            if not raw_key: return "🚨 ERROR: OPENROUTER_API_KEY is missing."
            
            response = requests.post(
                url="[https://openrouter.ai/api/v1/chat/completions](https://openrouter.ai/api/v1/chat/completions)",
                headers={"Authorization": f"Bearer {raw_key}"},
                data=json.dumps({
                    "model": "anthropic/claude-3.5-sonnet",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Logic:\n{logic}"}
                    ]
                })
            )
            return response.json()['choices'][0]['message']['content']

    except Exception as e:
        return f"🚨 **AI ENGINE ERROR ({ACTIVE_ENGINE}):** {str(e)}"

    return "No active AI engine selected in configuration."
