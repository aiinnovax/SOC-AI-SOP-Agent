import streamlit as st
import json
from github import Github

st.set_page_config(page_title="AIInnovax | Admin Portal", layout="wide")

# --- GITHUB DATABASE SETUP ---
@st.cache_resource
def get_github_repo():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        return g.get_repo(st.secrets["REPO_PATH"])
    except Exception as e:
        st.error("GitHub Connection Failed. Check Streamlit Secrets.")
        st.stop()

repo = get_github_repo()

def get_db():
    file_content = repo.get_contents("database.json")
    return json.loads(file_content.decoded_content.decode()), file_content

db, db_file = get_db()
clients = db.get("customers", [])

st.title("🏢 Admin Portal: Client Management")
st.write("Register new organizations and map their security infrastructure.")

with st.expander("➕ Register New Client", expanded=True):
    new_name = st.text_input("Client Name")
    new_siem = st.selectbox("SIEM Vendor", ["Sentinel", "Splunk", "CrowdStrike", "QRadar"])
    new_logs = st.text_area("Log Sources (Comma Separated)", placeholder="e.g. AWS CloudTrail, Carbon Black, Fortigate")
    
    if st.button("Initialize Client Environment"):
        if new_name and new_logs:
            with st.spinner("Syncing to GitHub Database..."):
                new_client_data = {"name": new_name, "siem": new_siem, "logs": new_logs}
                db["customers"] = [c for c in clients if c["name"] != new_name]
                db["customers"].append(new_client_data)
                
                repo.update_file(
                    db_file.path, 
                    f"Admin: Synced {new_name}", 
                    json.dumps(db, indent=4), 
                    db_file.sha
                )
                st.success(f"Successfully deployed environment for {new_name}")
                st.rerun()
        else:
            st.error("Please fill in all fields.")

st.subheader("Existing Organizations")
if not clients:
    st.info("No clients registered yet.")
for c in clients:
    with st.container(border=True):
        col1, col2 = st.columns([3, 1])
        col1.write(f"**{c['name']}** ({c['siem']})")
        col1.caption(f"Sources: {c['logs']}")
        if col2.button("Delete", key=c['name']):
            db["customers"] = [cust for cust in clients if cust["name"] != c["name"]]
            repo.update_file(db_file.path, f"Admin: Deleted {c['name']}", json.dumps(db, indent=4), db_file.sha)
            st.rerun()
