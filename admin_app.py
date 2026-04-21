import streamlit as st
import json
from github import Github

# --- 1. CONFIG & PROFESSIONAL THEME ---
st.set_page_config(page_title="AIInnovax Admin", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #0E1117; color: #FFFFFF; }
    [data-testid="stSidebar"] { background-color: #161B22; border-right: 1px solid #30363D; }
    
    /* Metrics */
    .metric-card {
        background-color: #161B22; border: 1px solid #30363D;
        padding: 20px; border-radius: 10px; text-align: center;
    }
    .metric-value { font-size: 32px; font-weight: bold; color: #58A6FF; }
    
    /* Status Boxes */
    .status-box {
        background-color: #161B22; border: 1px solid #30363D;
        padding: 30px; border-radius: 15px; min-height: 280px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GITHUB DATA SYNC ---
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

# --- 3. CUSTOM SIDEBAR NAVIGATION (State Managed) ---
if 'menu' not in st.session_state:
    st.session_state.menu = "Dashboard"

with st.sidebar:
    st.title("Logo")
    st.write("")
    if st.button("📊 Dashboard", use_container_width=True):
        st.session_state.menu = "Dashboard"
    if st.button("🪪 Licenses", use_container_width=True):
        st.session_state.menu = "Licenses"
    if st.button("📂 Global Repo", use_container_width=True):
        st.session_state.menu = "Repo"
    if st.button("⚙️ Settings", use_container_width=True):
        st.session_state.menu = "Settings"
    
    st.markdown("<br>"*10, unsafe_allow_html=True)
    st.button("       ", disabled=True)

# --- 4. TOP NAV BAR ---
t1, t2 = st.columns([3, 1])
with t1:
    st.subheader("SOC AI SOP Agent")
with t2:
    st.markdown("<div style='text-align: right;'>profile &nbsp; <b>&rarr;</b> &nbsp; 👤 &nbsp; <button>logout</button></div>", unsafe_allow_html=True)

st.markdown("---")

# --- 5. PAGE LOGIC ---

if st.session_state.menu == "Dashboard":
    # METRICS
    m1, m2, m3, _ = st.columns([1, 1, 1, 1])
    with m1:
        st.markdown(f"<div class='metric-card'>TOTAL CUSTOMERS<br><div class='metric-value'>{len(customers)}</div></div>", unsafe_allow_html=True)
    with m2:
        st.markdown("<div class='metric-card'>API LIMIT<br><div class='metric-value' style='color:#7EE787;'>Active</div></div>", unsafe_allow_html=True)
    with m3:
        st.markdown(f"<div class='metric-card'>SOP COUNT<br><div class='metric-value'>{total_sops}</div></div>", unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)

    # HEALTH & TICKETS
    s1, s2 = st.columns([1, 1.5])
    with s1:
        st.markdown("<div class='status-box'><h3>System health status</h3><br>🟢 GitHub Sync: Active<br>🟢 AI Gateway: Healthy</div>", unsafe_allow_html=True)
    with s2:
        st.markdown("<div class='status-box'><h3>Customer tickets notification</h3><br><p style='color:#8B949E;'>No active notifications.</p></div>", unsafe_allow_html=True)

elif st.session_state.menu == "Licenses":
    st.header("🪪 Subscription Licenses")
    st.table(customers)

elif st.session_state.menu == "Repo":
    st.header("📂 Global Repository")
    st.info("Archive of all generated SOPs will appear here.")

elif st.session_state.menu == "Settings":
    st.header("⚙️ Admin Settings")
    st.write("Configure API keys and Global thresholds.")
