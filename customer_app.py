import streamlit as st
import datetime
from github_db import get_db, save_db
from ai_service import generate_sop

st.set_page_config(page_title="SOP-Genie Portal", layout="wide", initial_sidebar_state="expanded")

db, sha = get_db()

# --- CENTERED LOGIN SCREEN ---
if "logged_in_email" not in st.session_state:
    st.session_state.logged_in_email = None

if not st.session_state.logged_in_email:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.write("<br><br><br>", unsafe_allow_html=True)
        with st.container(border=True):
            with st.form("customer_login_form"):
                st.markdown("<h2 style='text-align: center;'>⚡ SOP-Genie Portal</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center;'>Secure Enterprise Login</p>", unsafe_allow_html=True)
                login_email = st.text_input("Corporate Email")
                login_password = st.text_input("Password", type="password")
                if st.form_submit_button("Access Terminal", use_container_width=True, type="primary"):
                    matched_user = next((u for u in db.get("users", []) if u["email"] == login_email and u.get("password") == login_password), None)
                    if matched_user:
                        if matched_user.get("status", "Active") == "Inactive":
                            st.error("Account Suspended. Contact Support.")
                        else:
                            st.session_state.logged_in_email = matched_user["email"]
                            st.rerun()
                    else:
                        st.error("Invalid email or password.")
    st.stop()

current_user = next((u for u in db.get("users", []) if u["email"] == st.session_state.logged_in_email), None)
if not current_user or current_user.get("status", "Active") == "Inactive":
    st.session_state.logged_in_email = None
    st.rerun()

# --- TOP NAVIGATION ---
col_logo, col_profile, col_logout = st.columns([8, 1, 1])
with col_profile:
    if st.button("👤 Profile", use_container_width=True):
        st.session_state.cust_menu = "Profile"
with col_logout:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in_email = None
        st.rerun()
st.divider()

# --- FORCE PASSWORD RESET ---
if current_user.get("force_reset", False):
    st.title("🔒 Action Required: Secure Your Account")
    st.warning("Please update your auto-generated temporary password.")
    with st.container(border=True):
        new_pw = st.text_input("New Password", type="password")
        confirm_pw = st.text_input("Confirm New Password", type="password")
        
        if st.button("Update Security Credentials", type="primary"):
            if new_pw == confirm_pw and len(new_pw) >= 6:
                for u in db["users"]:
                    if u["email"] == current_user["email"]:
                        u["password"] = new_pw
                        u["force_reset"] = False
                save_db(db, sha, f"Customer {current_user['company']} reset password.")
                st.success("Password Updated Successfully! Accessing Portal...")
                st.rerun()
            else:
                st.error("Passwords must match and be at least 6 characters.")
    st.stop()

# --- SIDEBAR NAV ---
st.sidebar.title(f"{current_user['company']}")
if "cust_menu" not in st.session_state:
    st.session_state.cust_menu = "SOP Architect"

if st.session_state.cust_menu == "Profile":
    menu = "Profile"
    if st.sidebar.button("← Back to Portal"):
        st.session_state.cust_menu = "SOP Architect"
        st.rerun()
else:
    menu = st.sidebar.radio("Mission Control", ["SOP Architect", "My Repository", "License & Usage"], index=["SOP Architect", "My Repository", "License & Usage"].index(st.session_state.cust_menu))
    st.session_state.cust_menu = menu

# --- ROUTING ---
if menu == "Profile":
    st.title("👤 My Security Profile")
    with st.container(border=True):
        st.subheader("Update Password")
        update_pw = st.text_input("New Password", type="password")
        confirm_update = st.text_input("Confirm New Password", type="password")
        if st.button("Save New Password", type="primary"):
            if update_pw == confirm_update and len(update_pw) >= 6:
                for u in db["users"]:
                    if u["email"] == current_user["email"]: u["password"] = update_pw
                save_db(db, sha, f"Customer {current_user['company']} updated password.")
                st.success("Password Updated Successfully!")
            else:
                st.error("Passwords must match and be 6+ characters.")

elif menu == "SOP Architect":
    st.title("🔍 SOP-Genie: Architect")
    if current_user["used"] >= current_user["limit"]:
        st.error(f"Quota Exceeded. ({current_user['used']}/{current_user['limit']}). Contact Sales.")
        st.stop()
        
    c1, c2 = st.columns([1, 1.5])
    with c1:
        with st.container(border=True):
            st.subheader("Threat Context")
            client_name = current_user["company"]
            log_sources = "Standard Enterprise Logs"
            st.info(f"Targeting Default Context: {client_name}")
            
            siem = st.selectbox("Detection Engine", ["Sentinel", "CrowdStrike", "Splunk", "QRadar", "Generic"])
            logic = st.text_area("Paste Detection Logic / Query", height=150)
            
            if st.button("Synthesize SOP", type="primary", use_container_width=True):
                if logic:
                    with st.spinner("Processing..."):
                        result = generate_sop(siem, logic, client_name, log_sources)
                        new_sop = {
                            "id": f"sop_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}", "title": f"{siem} Response",
                            "customer_registered_name": current_user["company"], "client_name": client_name,
                            "date": datetime.datetime.now().strftime("%Y-%m-%d"), "content": result
                        }
                        for u in db["users"]:
                            if u["uid"] == current_user["uid"]: u["used"] += 1
                        db.setdefault("sops", []).append(new_sop)
                        save_db(db, sha, f"Customer {current_user['company']} generated SOP")
                        st.session_state.last_sop = result
                        st.rerun() 

    with c2:
        with st.container(border=True):
            st.subheader("Operational Output")
            if 'last_sop' in st.session_state: st.markdown(st.session_state.last_sop)

elif menu == "My Repository":
    st.title("📂 Organization Vault")
    my_sops = [s for s in db.get("sops", []) if s["customer_registered_name"] == current_user["company"]]
    for sop in my_sops:
        with st.expander(f"{sop['date']} | {sop['title']}"):
            st.markdown(sop["content"])
            st.download_button("Download Markdown", sop["content"], file_name=f"{sop['id']}.md")

elif menu == "License & Usage":
    st.title("🪪 Subscription Status")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Current Plan", current_user["plan"].split(" (")[0])
    with c2: st.metric("SOPs Used", current_user["used"])
    with c3: st.metric("Total Limit", current_user["limit"])
    
    st.progress(min(current_user["used"] / current_user["limit"], 1.0))
    st.write(f"Account Status: **{current_user.get('status', 'Active')}**")
