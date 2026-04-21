import streamlit as st
import streamlit.components.v1 as components
import os
import re
from dotenv import load_dotenv
from llm_router import generate_sop

# Load the secret keys
load_dotenv()

st.set_page_config(page_title="Customer Portal PoC", layout="wide")

st.title("AIInnovax - SOC Mission Control (PoC)")
st.markdown("---")

# Sidebar for Debugging
with st.sidebar:
    st.header("Settings")
    show_debug = st.checkbox("Show Raw AI Output (Debug)")

col_input, col_output = st.columns([1, 1.5])

with col_input:
    st.subheader("1. Client Context")
    client_name = st.selectbox("Select Client", ["Acme Corp", "Global Finance Inc", "HealthPlus Healthcare"])
    siem_type = st.selectbox("Select SIEM", ["Sentinel", "Splunk", "QRadar", "CrowdStrike Falcon", "Generic Query"])
    log_sources = st.text_input("Integrated Log Sources (Comma separated)", value="Azure AD, Palo Alto Firewalls, Office 365 Audit Logs, Windows Event Logs")
    
    st.markdown("---")
    st.subheader("2. Detection Logic")
    raw_logic = st.text_area("Paste Raw KQL/Sigma/SPL here:", height=200, placeholder="SecurityEvent | where EventID == 4624...")
    generate_btn = st.button("Build SOP", type="primary", use_container_width=True)

with col_output:
    st.subheader("Generated SOP & Triage Plan")
    
    if generate_btn:
        if raw_logic.strip() == "":
            st.warning("Please paste some detection logic first.")
        else:
            with st.spinner(f"Analyzing {siem_type} logic for {client_name}..."):
                # Call our router with all context
                sop_result = generate_sop(client_name, siem_type, log_sources, raw_logic)
                
                if show_debug:
                    st.divider()
                    st.write("### Raw AI Output:")
                    st.code(sop_result)
                
                # Safer extraction of Mermaid code without complex regex
                mermaid_code = ""
                if "```mermaid" in sop_result.lower():
                    try:
                        # Split the string to find the content between the backticks
                        parts = sop_result.split("```")
                        for part in parts:
                            if part.strip().lower().startswith("mermaid"):
                                # Extract just the mermaid code (removing the word 'mermaid' from the start)
                                mermaid_code = part.strip()[7:].strip()
                                break
                    except Exception:
                        mermaid_code = ""

                # Display the main Markdown text (excluding the mermaid block for clean look)
                # We'll replace the mermaid block with an empty string for the main display
                display_text = re.sub(r'```[Mm]ermaid.*?```', '', sop_result, flags=re.DOTALL)
                st.markdown(display_text)
                
                if mermaid_code:
                    st.success("Visual Decision Tree Generated!")
                    st.markdown("---")
                    
                    # Modern Mermaid rendering block
                    mermaid_html = f"""
                    <div class="mermaid" style="background-color: white; padding: 20px; border-radius: 10px; border: 1px solid #ddd;">
                    {mermaid_code}
                    </div>
                    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
                    <script>
                        mermaid.initialize({{ 
                            startOnLoad: true, 
                            theme: 'default',
                            securityLevel: 'loose'
                        }});
                    </script>
                    """
                    components.html(mermaid_html, height=600, scrolling=True)
                else:
                    st.info("Note: No visual flowchart was generated for this specific query.")
