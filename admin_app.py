import streamlit as st
import json
from github import Github

# --- 1. PAGE CONFIG & BOX STYLING ---
st.set_page_config(page_title="AIInnovax Admin", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 2px solid #000; }
    .metric-box { border: 3px solid #000; border-radius: 20px; padding: 25px; text-align: center; background-color: white; height: 160px; }
    .status-area { border: 3px solid #000; border-radius: 40px; padding: 40px; min-height: 350px; background-color: white; }
    .stButton>button { border: 2px solid #000; border-radius: 10px; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GITHUB DATABASE SYNC ---
@st.cache_resource
def get_db():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo(st.secrets["REPO_PATH"])
        content = repo.get_contents("database.json")
        return json.loads(content.decoded_content.decode())
    except:
        return {"customers": [], "global_stats": {}}

db = get_db()
customers = db.get("customers", [])
stats = db.get("global_stats", {})

# --- 3. SIDEBAR NAVIGATION ---
with st.sidebar:
    st.markdown("### Logo")
    st.write("")
    st.button("Dashboard", use_container_width=True)
    st.button("Licenses", use_container_width=True)
    st.button("Global Repo", use_container_width=True)
    st.button("Settings", use_container_width=True)
    st.markdown("<br>" * 10, unsafe_allow_html=True)
    st.button("       ", disabled=True, use_container_width=True)

# --- 4. TOP HEADER ---
col_title, col_auth = st.columns([3, 1])
with col_title:
    st.subheader("SOC AI SOP Agent")

with col_auth:
    st.markdown(
        "<div style='text-align: right; font-size: 16px;'>"
        "profile &nbsp; ➡ &nbsp; <span style='font-size: 22px;'>◯</span> &nbsp; "
        "<button style='padding: 2px 10px; border-radius: 5px; cursor: pointer;'>logout</button>"
        "</div>", 
        unsafe_allow_html=True
    )

st.write("---")

# --- 5. DASHBOARD METRICS (As per Paint File) ---
m1, m2, m3, _ = st.columns([1, 1, 1, 1])

with m1:
    st.markdown(f"<div class='metric-box'>Total Customers<br><h1>{len(customers)}</h1></div>", unsafe_allow_html=True)
with m2:
    st.markdown("<div class='metric-box'>API Limit<br><h1>Active</h1></div>", unsafe_allow_html=True)
with m3:
    st.markdown(f"<div class='metric-box'>SOP Count<br><h1>{stats.get('total_sop_count', 0)}</h1></div>", unsafe_allow_html=True)

st.write("<br>", unsafe_allow_html=True)

# --- 6. SYSTEM HEALTH & NOTIFICATIONS ---
s1, s2 = st.columns([1, 1.5])

with s1:
    st.markdown(
        "<div class='status-area'>"
        "<h3>System health status</h3><br>"
        "<p style='color: green; font-weight: bold;'>✔ GitHub Data Sync: Online</p>"
        "<p style='color: green; font-weight: bold;'>✔ Licensing Server: Online</p>"
        "</div>", 
        unsafe_allow_html=True
    )

with s2:
    st.markdown(
        "<div class='status-area'>"
        "<h3>Customer tickets notification</h3><br>"
        "<p style='color: #888;'>No active support requests from Organizations.</p>"
        "</div>", 
        unsafe_allow_html=True
    )
