import streamlit as st
from groq import Groq
import google.generativeai as genai
import requests
import json

# ==============================
# 🔧 CONFIGURATION
# ==============================
ACTIVE_ENGINE = "GEMINI"  # Change to GROQ / OPENROUTER if needed

# Configure Gemini ONCE
genai.configure(api_key=st.secrets.get("GEMINI_API_KEY"))


# ==============================
# 🔍 GEMINI MODEL FALLBACK
# ==============================
def get_gemini_model():
    """Try multiple Gemini models to avoid 404 errors."""
    model_list = [
        "gemini-pro",  # most stable
        "gemini-1.0-pro",
        "gemini-1.5-flash-latest",
    ]

    for m in model_list:
        try:
            return genai.GenerativeModel(m)
        except Exception:
            continue

    raise Exception("No compatible Gemini model found. Check API key or SDK.")


# ==============================
# 🌐 TAVILY INTELLIGENCE
# ==============================
def get_tavily_intel(query):
    raw_key = st.secrets.get("TAVILY_API_KEY", "").strip().replace('"', '').replace("'", "")
    
    if not raw_key:
        return "No real-time threat intelligence available."

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
        results = data.get("results", [])

        return "\n".join([f"- {r.get('content', '')}" for r in results])

    except Exception as e:
        return f"Tavily Error: {str(e)}"


# ==============================
# 🧠 SOP GENERATOR
# ==============================
def generate_sop(siem, logic, client_name, log_sources):

    # 🔎 Research phase
    research_query = f"Incident response steps and vulnerabilities for {siem} {logic[:200]}"
    intel_context = get_tavily_intel(research_query)

    # 🧾 Prompt
    system_prompt = f"""
You are SOP-Genie, a Senior Cyber Security Architect specializing in MSS.

TARGET CLIENT: {client_name}
LOG SOURCES: {log_sources}
THREAT INTEL: {intel_context}

You MUST output in Markdown with:
1. Executive Summary
2. Kill Chain Phase
3. MITRE ATT&CK Mapping
4. GRC Mapping
5. Tier 1 Triage
6. Tier 2 Investigation
7. Containment
8. Eradication & Recovery
9. Tier 1 Checklist
10. Mermaid Decision Tree
"""

    # ==============================
    # 🚀 ENGINE ROUTING
    # ==============================
    try:

        # ---------- GEMINI ----------
        if ACTIVE_ENGINE == "GEMINI":
            model = get_gemini_model()

            response = model.generate_content(
                f"{system_prompt}\n\nDetection Logic:\n{logic}"
            )

            return getattr(response, "text", "⚠️ Empty Gemini response")

        # ---------- GROQ ----------
        elif ACTIVE_ENGINE == "GROQ":
            raw_key = st.secrets.get("GROQ_API_KEY", "").strip().replace('"', '').replace("'", "")
            
            if not raw_key:
                return "🚨 GROQ_API_KEY missing"

            client = Groq(api_key=raw_key)

            completion = client.chat.completions.create(
                model="llama3-70b-8192",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": logic}
                ],
                temperature=0.1,
                max_tokens=2048
            )

            return completion.choices[0].message.content

        # ---------- OPENROUTER ----------
        elif ACTIVE_ENGINE == "OPENROUTER":
            raw_key = st.secrets.get("OPENROUTER_API_KEY", "")

            if not raw_key:
                return "🚨 OPENROUTER_API_KEY missing"

            response = requests.post(
                url="https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {raw_key}",
                    "Content-Type": "application/json"
                },
                data=json.dumps({
                    "model": "anthropic/claude-3.5-sonnet",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": logic}
                    ]
                })
            )

            data = response.json()

            return data.get("choices", [{}])[0].get("message", {}).get("content", "⚠️ Empty response")

    except Exception as e:
        return f"🚨 ERROR ({ACTIVE_ENGINE}): {str(e)}"

    return "⚠️ No engine selected"
