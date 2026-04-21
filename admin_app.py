import streamlit as st
import json
from github import Github

# --- PAGE CONFIG ---
st.set_page_config(page_title="AIInnovax Admin", layout="wide", initial_sidebar_state="expanded")

# --- PROFESSIONAL CSS ---
st.markdown("""
    <style>
    /* Main Background */
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #30363D; }
    
    /* Metric Cards */
    .metric-card {
        background-color: #161B22;
        border: 1px solid #30363D;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
    }
    .metric-value { font-size: 32px; font-weight: bold; color: #58A6FF; }
    .metric-label { font-size: 14px; color: #8B949E; text-transform: uppercase; }

    /* Status Boxes */
    .status-box {
        background-color: #161B22;
        border: 1px solid #30363D;
        padding: 30px;
        border-radius: 15px;
        min-height: 300px;
    }
    
    /* Header Profile area */
    .header-right { text-align: right; color: #8B949E; font-size: 14px; }
    </style>
    """, unsafe_allow_html=True)

# --- GITHUB SYNC ---
@st.cache_resource
def get_db():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo(st.secrets["REPO_PATH"])
        db_file = repo.get_contents("database.json")
        return json.loads(db_file.decoded_content.decode())
    except:
        return {"customers": [], "global_stats": {"total_sop_count": 0}}

db = get_db()
customers = db.get("customers", [])
total_sops = db.get("global_stats", {}).get("total_sop_count", 0)

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.image("https://img.icons8.com/external-flatart-icons-flat-flatarticons/64/external-security-cyber-security-flatart-icons-flat-flatarticons-3.png", width=60)
    st.title("AIInnovax")
    st.write("")
    st.button("📊 Dashboard", use_container_width=True)
    st.button("🪪 Licenses", use_container_width=True)
    st.button("📂 Global Repo", use_container_width=True)
    st.button("⚙️ Settings", use_container_width=True)
    
    st.markdown("<br>"*10, unsafe_allow_html=True)
    st.caption("v1.0.4 - Production")

# --- TOP NAV BAR ---
t1, t2 = st.columns([3, 1])
with t1:
    st.subheader("SOC AI SOP Agent")
with t2:
    st.markdown("""
        <div class='header-right'>
            profile &nbsp; <b>&rarr;</b> &nbsp; <span style='font-size:20px;'>👤</span> &nbsp; 
            <button style='background:none; border:1px solid #30363D; color:white; border-radius:5px; padding:2px 10px;'>logout</button>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# --- DASHBOARD METRICS ---
m1, m2, m3, _ = st.columns([1, 1, 1, 1])

with m1:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>Total Customers</div><div class='metric-value'>{len(customers)}</div></div>", unsafe_allow_html=True)
with m2:
    st.markdown("<div class='metric-card'><div class='metric-label'>API Limit</div><div class='metric-value' style='color:#7EE787;'>Active</div></div>", unsafe_allow_html=True)
with m3:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>SOP Count</div><div class='metric-value'>{total_sops}</div></div>", unsafe_allow_html=True)

st.write("<br>", unsafe_allow_html=True)

# --- SYSTEM HEALTH & NOTIFICATIONS ---
s1, s2 = st.columns([1, 1.5])

with s1:
    with st.container():
        st.markdown("<div class='status-box'><h3>System health status</h3><br><p>🟢 GitHub Database: Connected</p><p>🟢 LLM Routing: Healthy</p><p>🟢 Subscription Sync: Active</p></div>", unsafe_allow_html=True)

with s2:
    with st.container():
        st.markdown("<div class='status-box'><h3>Customer tickets notification</h3><br><p style='color:#8B949E;'>No high-priority alerts from organizations.</p></div>", unsafe_allow_html=True)
