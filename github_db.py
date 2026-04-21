import streamlit as st
import json
from github import Github

@st.cache_resource
def get_repo():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        return g.get_repo(st.secrets["REPO_PATH"])
    except Exception as e:
        st.error(f"Database Connection Error: {e}")
        st.stop()

def get_db():
    repo = get_repo()
    try:
        content = repo.get_contents("database.json")
        return json.loads(content.decoded_content.decode()), content.sha
    except:
        return {"users": [], "clients": [], "sops": []}, None

def save_db(new_db, current_sha, commit_message="Update DB"):
    repo = get_repo()
    file_path = "database.json"
    repo.update_file(
        file_path, 
        commit_message, 
        json.dumps(new_db, indent=4), 
        current_sha
    )
