import streamlit as st
import google.generativeai as genai

def generate_sop(siem, logic, client_name, log_sources):
    # Retrieve API Key from Streamlit Secrets
    api_key = st.secrets["GEMINI_API_KEY"]
    
    if not api_key:
        return "🚨 **SOP SYNTHESIS ERROR:** GEMINI_API_KEY not found in Streamlit Secrets."

    # Configure the official Google SDK
    genai.configure(api_key=api_key)
    
    # Initialize the model
    model = genai.GenerativeModel('gemini-1.5-flash')

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
        # Generate Content
        response = model.generate_content(
            f"{system_prompt}\n\nLogic to analyze:\n{logic}",
            generation_config=genai.types.GenerationConfig(
                temperature=0.1
            )
        )
        return response.text
    except Exception as e:
        return f"🚨 **SOP SYNTHESIS ERROR:** Connection Failed. \n\n**Technical Details:** {str(e)}"
