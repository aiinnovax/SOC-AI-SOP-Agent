import streamlit as st
import streamlit.components.v1 as components
import os
import re
from dotenv import load_dotenv
from llm_router import generate_sop

load_dotenv()

st.set_page_config(page_title="Customer Portal PoC", layout="wide")

st.title("AIInnovax - SOC Mission Control (PoC)")
st.markdown("---")

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
                sop_result = generate_sop(client_name, siem_type, log_sources, raw_logic)
                
                # Extract the Mermaid block using regex
                mermaid_match = re.search(r'```mermaid\n(.*?)\n```', sop_result, re.DOTALL)
                
                if mermaid_match:
                    mermaid_code = mermaid_match.group(1)
                    
                    # Remove the raw mermaid block from the text so it doesn't print as plain text
                    clean_markdown = re.sub(r'```mermaid\n(.*?)\n```', '', sop_result, flags=re.DOTALL)
                    
                    # Display the text SOP
                    st.markdown(clean_markdown)
                    
                    # Render the Mermaid chart via HTML component
                    st.markdown("### Visual Decision Tree")
                    mermaid_html = f"""
                    <div class="mermaid">
                    {mermaid_code}
                    </div>
                    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
                    <script>mermaid.initialize({{startOnLoad:true}});</script>
                    """
                    components.html(mermaid_html, height=500, scrolling=True)
                else:
                    # If the AI failed to generate the chart, display everything as normal text
                    st.markdown(sop_result)
