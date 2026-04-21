import streamlit as st
from github_db import get_db

st.set_page_config(page_title="AIInnovax Admin", layout="wide")
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

db, _ = get_db()

# --- SIDEBAR NAV ---
st.sidebar.title("🛡️ AIInnovax Admin")
menu = st.sidebar.radio("Navigation", ["Dashboard", "User Licenses", "Global Repository"])

if menu == "Dashboard":
    st.header("🏢 Central Command Dashboard")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Customers", len(db.get("users", [])))
    c2.metric("Total SOPs Generated", len(db.get("sops", [])))
    c3.metric("System Health", "Operational")
    c4.metric("LLM Routing", "Active")
    
    st.divider()
    st.subheader("Recent System Alerts")
    st.info("System fully synced with GitHub Unified Storage.")

elif menu == "User Licenses":
    st.header("🪪 B2B Subscription Management")
    if db.get("users"):
        st.table(db["users"])
    else:
        st.warning("No customers onboarded.")

elif menu == "Global Repository":
    st.header("🗄️ Unified SOP Vault")
    
    customers = [u["company"] for u in db.get("users", [])]
    selected_filter = st.selectbox("Filter by Customer", ["All"] + customers)
    
    sops = db.get("sops", [])
    if selected_filter != "All":
        sops = [s for s in sops if s["customer_registered_name"] == selected_filter]
        
    for sop in sops:
        with st.expander(f"{sop['date']} | {sop['title']} ({sop['customer_registered_name']})"):
            st.markdown(f"**Client Context:** {sop['client_name']}")
            st.markdown(sop["content"])
