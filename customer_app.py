import streamlit as st
import datetime
from github_db import get_db, save_db
from ai_service import generate_sop

st.set_page_config(page_title="SOP-Genie Customer Portal", layout="wide")
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

db, sha = get_db()

# --- AUTHENTICATION ---
st.sidebar.subheader("Terminal Login")
user_email = st.sidebar.text_input("Corporate Email")
user_password = st.sidebar.text_input("Password", type="password")

if not user_email or not user_password:
    st.sidebar.warning("Please enter your credentials.")
    st.stop()

# Find user and verify credentials
current_user = next((u for u in db.get("users", []) if u["email"] == user_email and u.get("password") == user_password), None)

if not current_user:
    st.sidebar.error("Authentication Failed. Invalid email or password.")
    st.stop()

if current_user.get("status", "Active") == "Inactive":
    st.sidebar.error("Account Suspended. Please contact AIInnovax support.")
    st.stop()

st.sidebar.success(f"Authenticated as {current_user['company']}")

# --- SIDEBAR NAV ---
menu = st.sidebar.radio("Mission Control", ["SOP Architect", "My Repository", "License & Usage"])

if menu == "SOP Architect":
    st.title("🔍 SOP-Genie: Architect")
    
    # Check Limits
    if current_user["used"] >= current_user["limit"]:
        st.error(f"Quota Exceeded. You have used {current_user['used']}/{current_user['limit']} SOPs on your current plan. Contact AIInnovax Sales to upgrade.")
        st.stop()
        
    c1, c2 = st.columns([1, 1.5])
    
    with c1:
        st.subheader("1. Threat Context")
        
        my_clients = [c for c in db.get("clients", []) if c.get("owner_uid") == current_user["uid"]]
        
        # Allow them to generate SOPs even if they haven't set up clients yet
        if not my_clients:
            client_name = current_user["company"]
            log_sources = "Standard Enterprise Logs"
            st.info(f"Using default context for {client_name}.")
        else:
            client_names = [c["name"] for c in my_clients]
            selected_client_name = st.selectbox("Target Client", client_names)
            target_client = next(c for c in my_clients if c["name"] == selected_client_name)
            client_name = target_client["name"]
            log_sources = target_client["log_sources"]
            st.caption(f"Mapped Log Sources: {log_sources}")
        
        siem = st.selectbox("Detection Engine", ["Sentinel", "CrowdStrike", "Splunk", "QRadar", "Sigma", "Generic Query", "Manual Scenario"])
        logic = st.text_area("Paste Detection Logic / Query / Scenario", height=150)
        
        if st.button("Synthesize SOP", type="primary", use_container_width=True):
            if logic:
                with st.spinner("AI Intelligence Core processing..."):
                    result = generate_sop(siem, logic, client_name, log_sources)
                    
                    new_sop = {
                        "id": f"sop_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "title": f"{siem} Detection Response",
                        "customer_registered_name": current_user["company"],
                        "client_name": client_name,
                        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                        "content": result,
                        "mod_count": 0
                    }
                    
                    for u in db["users"]:
                        if u["uid"] == current_user["uid"]:
                            u["used"] += 1
                            
                    db.setdefault("sops", []).append(new_sop)
                    save_db(db, sha, f"Customer: {current_user['company']} generated SOP")
                    
                    st.session_state.last_sop = result
                    st.success("SOP Generated and Vaulted.")
                    st.rerun() # Refresh to update quota
            else:
                st.warning("Provide detection logic.")

    with c2:
        st.subheader("2. Operational Output")
        if 'last_sop' in st.session_state:
            st.markdown(st.session_state.last_sop)

elif menu == "My Repository":
    st.title("📂 Organization Vault")
    my_sops = [s for s in db.get("sops", []) if s["customer_registered_name"] == current_user["company"]]
    
    if not my_sops:
        st.info("No SOPs generated yet.")
    
    for sop in my_sops:
        with st.expander(f"{sop['date']} | {sop['title']} (Target: {sop.get('client_name', 'Global')})"):
            st.markdown(sop["content"])
            st.download_button("Download Markdown", sop["content"], file_name=f"{sop['id']}.md")

elif menu == "License & Usage":
    st.title("🪪 Subscription Status")
    
    st.metric("Current Plan", current_user["plan"].split(" (")[0]) # Shows "Basic" instead of "Basic ($25/mo)"
    
    usage_percent = min(current_user["used"] / current_user["limit"], 1.0)
    st.progress(usage_percent)
    
    st.write(f"**Usage:** {current_user['used']} / {current_user['limit']} Monthly SOPs utilized.")
    st.write(f"**Account Status:** {current_user.get('status', 'Active')}")
    st.write(f"**Plan Details:** {current_user['plan']}")
    
    st.divider()
    if "Premium" not in current_user["plan"]:
        st.info("Need higher limits? Reach out to your AIInnovax representative to upgrade your plan.")
