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
                
                # Bulletproof regex to catch any variation of the mermaid block
                mermaid_match = re.search(r'
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1
4. Click **Build SOP**.

Scroll down on the right side. Do you see the **GREEN** box and the visual chart, or did you get the **RED** box telling us the AI got lazy and skipped the step? Let me know exactly what you see!
