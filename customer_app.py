import streamlit as st
import datetime
from github_db import get_db, save_db
from ai_service import generate_sop

st.set_page_config(page_title="SOP-Genie Customer Portal", layout="wide")
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

db, sha = get_db()

# --- AUTHENTICATION SESSION STATE ---
if "logged_in_email" not in st.session_state:
    st.session_state.logged_in_email = None

if not st.session_state.logged_in_email:
    # --- LOGIN SCREEN ---
    st.sidebar.subheader("Terminal Login")
    login_email = st.sidebar.text_input("Corporate Email")
    login_password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login", type="primary", use_container_width=True):
        # Verify credentials against DB
        matched_user = next((u for u in db.get("users", []) if u["email"] == login_email and u.get("password") == login_password), None)
        
        if matched_user:
            if matched_user.get("status", "Active") == "Inactive":
                st.sidebar.error("Account Suspended. Please contact AIInnovax support.")
            else:
                # Store email in session and reload
                st.session_state.logged_in_email = matched_user["email"]
                st.rerun()
        else:
            st.sidebar.error("Authentication Failed. Invalid email or password.")
    st.stop() # Stop execution here if not logged in

# --- FETCH FRESH USER DATA ---
# This ensures we always have the latest quota even after a page reload
current_user = next((u for u in db.get("users", []) if u["email"] == st.session_state.logged_in_email), None)

# Security check in case admin deleted the account while they were logged in
if not current_user or current_user.get("status", "Active") == "Inactive":
    st.session_state.logged_in_email = None
    st.rerun()

st.sidebar.success(f"Authenticated as {current_user['company']}")

# --- LOGOUT BUTTON ---
if st.sidebar.button("Logout", use_container_width=True):
    st.session_state.logged_in_email = None
    st.rerun()

st.sidebar.divider()

# --- SIDEBAR NAV ---
menu = st.sidebar.radio("Mission Control", ["SOP Architect", "My Repository", "License & Usage"])

if menu == "SOP Architect":
    st.title("🔍 SOP-Genie: Architect")
    
    if current_user["used"] >= current_user["limit"]:
        st.error(f"Quota Exceeded. You have used {current_user['used']}/{current_user['limit']} SOPs on your current plan. Contact AIInnovax Sales to upgrade.")
        st.stop()
        
    c1, c2 = st.columns([1, 1.5])
    
    with c1:
        st.subheader("1. Threat Context")
        
        my_clients = [c for c in db.get("clients", []) if c.get("owner_uid") == current_user["uid"]]
        
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
                    st.rerun() 
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
    
    st.metric("Current Plan", current_user["plan"].split(" (")[0]) 
    
    usage_percent = min(current_user["used"] / current_user["limit"], 1.0)
    st.progress(usage_percent)
    
    st.write(f"**Usage:** {current_user['used']} / {current_user['limit']} Monthly SOPs utilized.")
    st.write(f"**Account Status:** {current_user.get('status', 'Active')}")
    st.write(f"**Plan Details:** {current_user['plan']}")
    
    st.divider()
    if "Premium" not in current_user["plan"]:
        st.info("Need higher limits? Reach out to your AIInnovax representative to upgrade your plan.")
