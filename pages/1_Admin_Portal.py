import streamlit as st
import json
from github import Github
from datetime import datetime

st.set_page_config(page_title="AIInnovax | Vendor Admin", layout="wide")

# --- GITHUB SYNC SETUP ---
try:
    token = st.secrets["GITHUB_TOKEN"]
    repo_path = st.secrets["REPO_PATH"]
    g = Github(token)
    repo = g.get_repo(repo_path)
except Exception as e:
    st.error("Authentication Error: check your Secrets in Streamlit Cloud.")
    st.stop()

st.title("🏢 Vendor Management Portal")
st.markdown("Use this secure panel to manage client licenses and security contexts.")

# --- ADD CLIENT SECTION ---
with st.container(border=True):
    st.subheader("Register New Organization")
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("Organization Name")
        siem = st.selectbox("Primary SIEM", ["Sentinel", "Splunk", "CrowdStrike", "QRadar"])
    with c2:
        tier = st.selectbox("Subscription Tier", ["Standard", "Pro", "Enterprise MSSP"])
        status = st.toggle("Active License", value=True)

    logs = st.text_area("Authorized Log Sources", placeholder="e.g. Azure AD, O365, Fortigate")

    if st.button("Commit to Infrastructure", type="primary"):
        if name and logs:
            # 1. Fetch current database
            file = repo.get_contents("database.json")
            db = json.loads(file.decoded_content.decode())

            # 2. Add/Update client
            new_client = {
                "name": name,
                "siem": siem,
                "logs": logs,
                "tier": tier,
                "active": status,
                "updated_at": datetime.now().strftime("%Y-%m-%d")
            }
            
            # Remove old entry if exists and append new
            db["customers"] = [c for c in db["customers"] if c["name"] != name]
            db["customers"].append(new_client)

            # 3. Push back to GitHub
            repo.update_file(file.path, f"Admin: Updated {name}", json.dumps(db, indent=4), file.sha)
            st.success(f"Success! {name} infrastructure is now synced.")
            st.balloons()
        else:
            st.warning("Organization name and logs are required.")

# --- PREVIEW SECTION ---
st.divider()
st.subheader("Global Directory")
file = repo.get_contents("database.json")
current_db = json.loads(file.decoded_content.decode())
if current_db["customers"]:
    st.table(current_db["customers"])
