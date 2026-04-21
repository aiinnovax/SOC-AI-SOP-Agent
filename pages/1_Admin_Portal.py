import streamlit as st
from google.cloud import firestore
import json

# Initialize Firestore
db = firestore.Client.from_service_account_info(json.loads(st.secrets["firebase"]["service_account"]))

st.title("🏢 AIInnovax Vendor Admin")

tab1, tab2 = st.tabs(["Client Management", "SOP Audit Vault"])

with tab1:
    st.subheader("Register Organization")
    with st.form("add_client"):
        name = st.text_input("Client Name")
        siem = st.selectbox("SIEM", ["Sentinel", "Splunk", "CrowdStrike"])
        logs = st.text_area("Log Sources")
        submit = st.form_submit_button("Sync to Customer Portal")
        
        if submit:
            # SAVE TO FIREBASE
            db.collection("customers").document(name).set({
                "name": name,
                "siem": siem,
                "logs": logs,
                "license_active": True
            })
            st.success(f"Client {name} is now active and synced.")

with tab2:
    st.subheader("Global SOP Archive")
    # Fetch all generated SOPs from all customers
    sops = db.collection("sops").stream()
    for s in sops:
        data = s.to_dict()
        with st.expander(f"{data['client']} - {data['timestamp']}"):
            st.markdown(data['content'])
