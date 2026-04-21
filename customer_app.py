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
    st.subheader("Terminal Login")
    login_email = st.text_input("Corporate Email")
    login_password = st.text_input("Password", type="password")
    
    if st.button("Login", type="primary"):
        matched_user = next((u for u in db.get("users", []) if u["email"] == login_email and u.get("password") == login_password), None)
        
        if matched_user:
            if matched_user.get("status", "Active") == "Inactive":
                st.error("Account Suspended. Please contact AIInnovax support.")
            else:
                st.session_state.logged_in_email = matched_user["email"]
                st.rerun()
        else:
            st.error("Authentication Failed. Invalid email or password.")
    st.stop()

# --- FETCH FRESH USER DATA ---
current_user = next((u for u in db.get("users", []) if u["email"] == st.session_state.logged_in_email), None)

if not current_user or current_user.get("status", "Active") == "Inactive":
    st.session_state.logged_in_email = None
    st.rerun()

# --- TOP NAVIGATION (Profile & Logout) ---
col_spacer, col_profile, col_logout = st.columns([8, 1, 1])
with col_profile:
    if st.button("👤 Profile", use_container_width=True):
        st.session_state.cust_menu = "Profile"
with col_logout:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in_email = None
        st.rerun()
st.divider()

# --- FORCE PASSWORD RESET (First Time Login) ---
if current_user.get("force_reset", False):
    st.title("🔒 Action Required: Reset Password")
    st.warning("For security purposes, you must change your auto-generated temporary password before accessing the portal.")
    
    new_pw = st.text_input("New Password", type="password")
    confirm_pw = st.text_input("Confirm New Password", type="password")
    
    if st.button("Update Security Credentials", type="primary"):
        if new_pw == confirm_pw and len(new_pw) >= 6:
            for u in db["users"]:
                if u["email"] == current_user["email"]:
                    u["password"] = new_pw
                    u["force_reset"] = False # Unlock the account
            save_db(db, sha, f"Customer: {current_user['company']} reset their password.")
            st.success("Password Updated Successfully! Accessing Portal...")
            st.rerun()
        else:
            st.error("Passwords must match and be at least 6 characters long.")
    st.stop() # Prevent access to the rest of the portal

st.sidebar.success(f"Connected: {current_user['company']}")

# --- SIDEBAR NAV ---
if "cust_menu" not in st.session_state:
    st.session_state.cust_menu = "SOP Architect"

menu_options = ["SOP Architect", "My Repository", "License & Usage"]
if st.session_state.cust_menu == "Profile":
    menu = "Profile"
    if st.sidebar.button("← Back to Portal"):
        st.session_state.cust_menu = "SOP Architect"
        st.rerun()
else:
    menu = st.sidebar.radio("Mission Control", menu_options, index=menu_options.index(st.session_state.cust_menu))
    st.session_state.cust_menu = menu

# --- PAGE ROUTING ---
if menu == "Profile":
    st.title("👤 My Profile")
    st.write(f"**Company:** {current_user['company']}")
    st.write(f"**Email:** {current_user['email']}")
    
    with st.container(border=True):
        st.subheader("Update Password")
        update_pw = st.text_input("New Password", type="password", key="upw1")
        confirm_update = st.text_input("Confirm New Password", type="password", key="upw2")
        
        if st.button("Save New Password"):
            if update_pw == confirm_update and len(update_pw) >= 6:
                for u in db["users"]:
                    if u["email"] == current_user["email"]:
                        u["password"] = update_pw
                save_db(db, sha, f"Customer: {current_user['company']} manually updated password.")
                st.success("Password Updated Successfully!")
            else:
                st.error("Passwords must match and be at least 6 characters.")

elif menu == "SOP Architect":
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
