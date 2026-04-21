import streamlit as st
from groq import Groq

def generate_sop(siem, logic, client_name, log_sources):
    # Retrieve Groq API Key from Streamlit Secrets
    api_key = st.secrets["GROQ_API_KEY"]
    
    if not api_key:
        return "🚨 **SOP SYNTHESIS ERROR:** GROQ_API_KEY not found in Streamlit Secrets."

    client = Groq(api_key=api_key)

    system_prompt = f"""
    You are SOP-Genie, an expert SOC Operational Procedure Architect.
    Translate the following {siem} detection logic into a structured SOP for {client_name}.
    
    CRITICAL CONTEXT: Tailor the investigation steps strictly to these log sources: {log_sources}.
    
    You MUST output Markdown with these exact sections:
    1. **Executive Summary**: Plain English logic translation.
    2. **Cyber Kill Chain Phase**: Identify the phase.
    3. **MITRE ATT&CK Mapping**: Tactic and Technique IDs.
    4. **GRC Compliance Mapping**: ISO 27001, SOC2, or GDPR relevance.
    5. **Identification (Triage)**: Numbered steps.
    6. **Investigation (Scoping)**: Numbered steps.
    7. **Containment**: Numbered steps.
    8. **Eradication & Recovery**: Numbered steps.
    9. **Tier 1 Rapid Response Checklist**: Bulleted checklist.
    10. **Visual Decision Tree**: A Mermaid.js flowchart mapping the triage path. Enclose in a ```mermaid block.
    """

    try:
        # Using Llama 3 70B for high-quality technical reasoning
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
