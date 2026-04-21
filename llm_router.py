import os
from litellm import completion
from dotenv import load_dotenv

load_dotenv()

def generate_sop(client_name, siem_type, log_sources, raw_logic):
    system_prompt = f"""
    You are an expert SOC Level 3 Architect and Compliance Auditor. 
    You have been provided with raw detection logic ({siem_type}) triggered in the {client_name} environment.
    
    CRITICAL CONTEXT: {client_name} has the following log sources integrated into their SIEM: {log_sources}.
    
    Your task is to translate the raw detection logic into a standardized Standard Operating Procedure (SOP).
    You MUST output the response in clear Markdown format with the following exact sections:
    
    1. **Executive Summary**: Plain English explanation of what this rule detects.
    2. **MITRE ATT&CK Mapping**: Identify the Tactic, Technique, and T-Code.
    3. **Triage & Investigation Steps**: Provide numbered, step-by-step instructions. You MUST explicitly direct the analyst to cross-reference specific logs from the provided integrated log sources list ({log_sources}) if they are relevant to verifying the attack.
    4. **Containment & Eradication**: Specific actions to stop the threat.
    5. **Tier 1 Rapid Response Checklist**: A short, bulleted checklist for junior analysts.
    """

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Here is the raw {siem_type} logic to analyze:\n\n{raw_logic}"}
    ]

    fallback_models = ["groq/llama3-8b-8192", "openrouter/auto"]

    try:
        response = completion(
            model="gemini/gemini-1.5-pro", 
            messages=messages,
            fallbacks=fallback_models,
            temperature=0.1
        )
        return response.choices[0].message.content
        
    except Exception as e:
        return f"Error generating SOP: {str(e)}"
