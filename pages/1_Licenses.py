import streamlit as st
import json
from github import Github

st.set_page_config(page_title="Licenses | Admin", layout="wide")

# Fetch data
g = Github(st.secrets["GITHUB_TOKEN"])
repo = g.get_repo(st.secrets["REPO_PATH"])
db = json.loads(repo.get_contents("database.json").decoded_content.decode())

st.title("🪪 Active Subscriptions")
st.write("These are the organizations that have purchased SOC AI SOP Agent.")

if db["customers"]:
    # We only show Organization name and their Subscription level
    st.table(db["customers"])
else:
    st.info("No active subscriptions.")
