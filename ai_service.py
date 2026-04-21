import os
from litellm import completion

# Swap this single variable to change the entire platform's brain
ACTIVE_MODEL = "gemini/gemini-1.5-flash"

def generate_sop(siem, logic, client_name, log_sources):
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

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Logic to analyze:\n{logic}"}
    ]

    try:
        response = completion(
            model=ACTIVE_MODEL, 
            messages=messages, 
            temperature=0.1,
            timeout=45,
            api_version="v1" # Explicitly tell Google to use the stable v1 API
        )
        return response.choices[0].message.content
    except Exception as e:
        # This will now display the exact error on your screen instead of spinning
        return f"🚨 **SOP SYNTHESIS ERROR:** API Connection Failed. Please check your GEMINI_API_KEY. \n\n**Technical Details:** {str(e)}"
