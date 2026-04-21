import streamlit as st
import json
import base64
from github import Github
from datetime import datetime

st.set_page_config(page_title="AIInnovax Admin", layout="wide")

# --- 1. GITHUB AUTHENTICATION ---
# Ensure GITHUB_TOKEN and REPO_PATH are in Streamlit Secrets
try:
    # REPO_PATH should be "username/repository-name"
    token = st.secrets["GITHUB_TOKEN"]
    repo_path = st.secrets["REPO_PATH"] 
    
    g = Github(token)
    repo = g.get_repo(repo_path)
except Exception as e:
    st.error("Authentication Error: Please check GITHUB_TOKEN and REPO_PATH in Streamlit Secrets.")
    st.stop()

st.title("🏢 Vendor Admin: Infrastructure Manager")
st.markdown("Use this portal to register new organizations and sync their context to the cloud.")

# --- 2. ADD NEW CLIENT LOGIC ---
with st.container(border=True):
    st.subheader("Register New Organization")
    
    col1, col2 = st.columns(2)
    with col1:
        client_name = st.text_input("Customer Name", placeholder="e.g. Infosys")
        siem_type = st.selectbox("SIEM Platform", ["Sentinel", "Splunk", "CrowdStrike", "QRadar"])
    
    with col2:
        license_tier = st.selectbox("License Tier", ["Standard", "Pro", "MSSP Enterprise"])
        status = st.radio("Initial Status", ["Active", "Trial", "Inactive"], horizontal=True)

    log_sources = st.text_area("Log Sources (Comma Separated)", 
                               placeholder="e.g. Azure AD, Palo Alto FW, Office 365, Windows Events")

    if st.button("Sync & Commit to GitHub", type="primary", use_container_width=True):
        if not client_name or not log_sources:
            st.warning("Please provide both a Client Name and Log Sources.")
        else:
            with st.spinner("Writing to GitHub Database..."):
                # A. Get the current database.json
                file_content = repo.get_contents("database.json")
                db = json.loads(file_content.decoded_content.decode())
                
                # B. Check if client exists, otherwise add
                new_entry = {
                    "name": client_name,
                    "siem": siem_type,
                    "logs": log_sources,
                    "tier": license_tier,
                    "status": status,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                # Update existing or append new
                updated = False
                for i, cust in enumerate(db["customers"]):
                    if cust["name"] == client_name:
                        db["customers"][i] = new_entry
                        updated = True
                        break
                
                if not updated:
                    db["customers"].append(new_entry)
                
                # C. Update the file in GitHub
                commit_msg = f"Admin: Updated {client_name} configuration"
                repo.update_file(
                    file_content.path, 
                    commit_msg, 
                    json.dumps(db, indent=4), 
                    file_content.sha
                )
                
                st.success(f"Successfully synced {client_name} to GitHub!")
                st.balloons()

# --- 3. AUDIT VIEW ---
st.markdown("---")
st.subheader("Existing Organizations (Sync Preview)")

# Pull fresh data to show the table
file_content = repo.get_contents("database.json")
current_db = json.loads(file_content.decoded_content.decode())

if current_db["customers"]:
    st.table(current_db["customers"])
else:
    st.info("No customers registered yet.")
