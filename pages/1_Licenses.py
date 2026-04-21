import streamlit as st
import json
from github import Github

st.set_page_config(page_title="AIInnovax | Licenses", layout="wide")

# Fetch data
g = Github(st.secrets["GITHUB_TOKEN"])
repo = g.get_repo(st.secrets["REPO_PATH"])
db = json.loads(repo.get_contents("database.json").decoded_content.decode())

st.title("🪪 Subscription Management")
st.write("Overview of organizations authorized to use the AI SOP Agent.")

# Professional Table
if db["customers"]:
    st.dataframe(
        db["customers"], 
        column_config={
            "name": "Organization",
            "tier": "Service Tier",
            "status": st.column_config.StatusColumn("Status")
        },
        use_container_width=True,
        hide_index=True
    )
else:
    st.info("No active subscriptions found.")
