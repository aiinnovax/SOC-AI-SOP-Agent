import streamlit as st
from groq import Groq

def generate_sop(siem, logic, client_name, log_sources):
    # Retrieve and strip whitespace to prevent 401 errors
    raw_key = st.secrets.get("GROQ_API_KEY", "")
    api_key = raw_key.strip().replace('"', '').replace("'", "")
    
    if not api_key:
        return "🚨 **SOP SYNTHESIS ERROR:** GROQ_API_KEY not found in Streamlit Secrets."

    try:
        client = Groq(api_key=api_key)

        system_prompt = f"""
        You are SOP-Genie, an expert SOC Operational Procedure Architect.
        Translate the following {siem} detection logic into a structured SOP for {client_name}.
        Tailor the investigation steps to these log sources: {log_sources}.
        
        Output Markdown with: Executive Summary, Kill Chain Phase, MITRE Mapping, GRC Mapping, 
        Triage Steps, Investigation, Containment, Eradication, Checklist, and a Mermaid Flowchart.
        """

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Logic to analyze:\n{logic}"}
            ],
            model="llama3-70b-8192",
            temperature=0.1,
            max_tokens=2048,
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"🚨 **SOP SYNTHESIS ERROR:** Groq Connection Failed. \n\n**Technical Details:** {str(e)}"
