import streamlit as st
import os
import re
from google.cloud import firestore
from google.oauth2 import service_account
import json
from llm_router import generate_sop

# --- DATABASE SETUP ---
# In a real setup, you'd use st.secrets for the JSON key. 
# For now, we will handle Client data in the app state to get you running immediately.
if 'clients' not in st.session_state:
    st.session_state.clients = [
        {"name": "Acme Corp", "siem": "Sentinel", "logs": "Azure AD, O365, Palo Alto"},
        {"name": "Global Bank", "siem": "Splunk", "logs": "Windows Events, Cisco ISE, CrowdStrike"}
    ]

# --- UI CONFIG ---
st.set_page_config(page_title="AIInnovax Mission Control", layout="wide")

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🛡️ AIInnovax")
    page = st.radio("Navigation", ["Customer Portal", "Admin Portal"])
    st.markdown("---")
    show_debug = st.checkbox("Show AI Debug")

# --- ADMIN PORTAL ---
if page == "Admin Portal":
    st.header("🏢 Admin Portal: Client Management")
    st.write("Register new organizations and map their security infrastructure.")
    
    with st.expander("➕ Register New Client", expanded=True):
        new_name = st.text_input("Client Name")
        new_siem = st.selectbox("SIEM Vendor", ["Sentinel", "Splunk", "CrowdStrike", "QRadar"])
        new_logs = st.text_area("Log Sources (Comma Separated)", placeholder="e.g. AWS CloudTrail, Carbon Black, Fortigate")
        
        if st.button("Initialize Client Environment"):
            if new_name and new_logs:
                st.session_state.clients.append({"name": new_name, "siem": new_siem, "logs": new_logs})
                st.success(f"Successfully deployed environment for {new_name}")
                st.rerun()
            else:
                st.error("Please fill in all fields.")

    st.subheader("Existing Organizations")
    for c in st.session_state.clients:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            col1.write(f"**{c['name']}** ({c['siem']})")
            col1.caption(f"Sources: {c['logs']}")
            if col2.button("Delete", key=c['name']):
                st.session_state.clients.remove(c)
                st.rerun()

# --- CUSTOMER PORTAL ---
elif page == "Customer Portal":
    st.header("🔍 Customer Portal: SOP Architect")
    
    col_in, col_out = st.columns([1, 1.5])
    
    with col_in:
        st.subheader("1. Select Context")
        client_names = [c['name'] for c in st.session_state.clients]
        selected_client_name = st.selectbox("Organization", client_names)
        
        # Auto-fetch the logs/siem based on selection
        client_data = next(c for c in st.session_state.clients if c['name'] == selected_client_name)
        st.info(f"**SIEM:** {client_data['siem']}\n\n**Log Sources:** {client_data['logs']}")
        
        st.subheader("2. Detection Logic")
        raw_logic = st.text_area("Paste Query (KQL/SPL/Sigma):", height=200)
        
        generate_btn = st.button("Build SOP", type="primary", use_container_width=True)

    with col_out:
        st.subheader("Automated Triage Plan")
        if generate_btn:
            if not raw_logic:
                st.warning("Please provide detection logic.")
            else:
                with st.spinner("AI Architect is analyzing..."):
                    sop_result = generate_sop(
                        client_data['name'], 
                        client_data['siem'], 
                        client_data['logs'], 
                        raw_logic
                    )
                    
                    if show_debug:
                        st.code(sop_result)

                    # Extract Mermaid
                    parts = sop_result.split("```")
                    mermaid_code = ""
                    clean_text = sop_result
                    
                    for part in parts:
                        if part.strip().lower().startswith("mermaid"):
                            mermaid_code = part.strip()[7:].strip()
                            # Remove mermaid from display text
                            clean_text = clean_text.replace(f"```{part}```", "")
                    
                    st.markdown(clean_text)
                    
                    if mermaid_code:
                        st.markdown("### Visual Decision Tree")
                        import streamlit.components.v1 as components
                        mermaid_html = f"""
                        <div class="mermaid" style="background-color:white; padding:20px; border-radius:10px;">
                        {mermaid_code}
                        </div>
                        <script src="[https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js](https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js)"></script>
                        <script>mermaid.initialize({{startOnLoad:true}});</script>
                        """
                        components.html(mermaid_html, height=500, scrolling=True)