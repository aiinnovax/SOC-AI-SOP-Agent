import streamlit as st
import datetime
from github_db import get_db, save_db
from ai_service import generate_sop

st.set_page_config(page_title="SOP-Genie Portal", layout="wide")

db, sha = get_db()

# --- AUTH SESSION ---
if "user_email" not in st.session_state:
    st.session_state.user_email = None

if not st.session_state.user_email:
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.write("<br><br><br>", unsafe_allow_html=True)
        with st.container(border=True):
            with st.form("cust_login"):
                st.markdown("<h2 style='text-align: center;'>⚡ SOP-Genie</h2>", unsafe_allow_html=True)
                le = st.text_input("Corporate Email")
                lp = st.text_input("Password", type="password")
                if st.form_submit_button("Login", use_container_width=True, type="primary"):
                    matched = next((u for u in db.get("users", []) if u["email"] == le and u["password"] == lp), None)
                    if matched:
                        if matched["status"] == "Active":
                            st.session_state.user_email = matched["email"]
                            st.rerun()
                        else: st.error("Account Suspended.")
                    else: st.error("Invalid Login.")
    st.stop()

# Fresh Fetch
current_user = next(u for u in db["users"] if u["email"] == st.session_state.user_email)

# --- TOP NAV ---
col_l, col_p, col_o = st.columns([8, 1, 1])
with col_p:
    if st.button("👤 Profile"): st.session_state.cmenu = "Profile"
with col_o:
    if st.button("🚪 Logout"):
        st.session_state.user_email = None
        st.rerun()
st.divider()

# --- FORCE RESET ---
if current_user.get("force_reset", False):
    st.title("🔒 Security Update")
    st.warning("Update your temporary password.")
    with st.container(border=True):
        np1 = st.text_input("New Password", type="password")
        np2 = st.text_input("Confirm Password", type="password")
        if st.button("Update Password"):
            if np1 == np2 and len(np1) >= 6:
                current_user["password"] = np1
                current_user["force_reset"] = False
                save_db(db, sha)
                st.success("Security Updated.")
                st.rerun()
            else: st.error("Invalid Match or too short.")
    st.stop()

# --- NAVIGATION ---
if "cmenu" not in st.session_state: st.session_state.cmenu = "SOP Architect"
st.sidebar.title(f"{current_user['company']}")

if st.session_state.cmenu == "Profile":
    if st.sidebar.button("← Back to Portal"):
        st.session_state.cmenu = "SOP Architect"
        st.rerun()
    menu = "Profile"
else:
    menu = st.sidebar.radio("Mission Control", ["SOP Architect", "My Repository", "License & Usage"],
                            index=["SOP Architect", "My Repository", "License & Usage"].index(st.session_state.cmenu))
    st.session_state.cmenu = menu

# --- PAGES ---
if menu == "Profile":
    st.header("👤 My Profile")
    with st.container(border=True):
        st.write(f"Company: {current_user['company']}")
        up1 = st.text_input("New Password", type="password")
        up2 = st.text_input("Confirm New Password", type="password")
        if st.button("Save New Password"):
            if up1 == up2 and len(up1) >= 6:
                current_user["password"] = up1
                save_db(db, sha)
                st.success("Password Updated.")
            else: st.error("Invalid Confirmation.")

elif menu == "SOP Architect":
    st.title("🔍 SOP Architect")
    if current_user["used"] >= current_user["limit"]:
        st.error("Quota Exceeded.")
        st.stop()
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        with st.container(border=True):
            siem = st.selectbox("SIEM", ["Sentinel", "CrowdStrike", "Splunk", "Generic"])
            logic = st.text_area("Logic", height=200)
            if st.button("Synthesize SOP", type="primary"):
                with st.spinner("Analyzing..."):
                    res = generate_sop(siem, logic, current_user["company"], "Standard Logs")
                    db["sops"].append({"id": str(datetime.datetime.now().timestamp()), "title": f"{siem} Response", "customer_registered_name": current_user["company"], "content": res, "date": str(datetime.date.today())})
                    current_user["used"] += 1
                    save_db(db, sha)
                    st.session_state.last_sop = res
                    st.rerun()

    with col2:
        if "last_sop" in st.session_state:
            st.markdown(st.session_state.last_sop)

elif menu == "My Repository":
    st.title("📂 My Repository")
    for s in db.get("sops", []):
        if s["customer_registered_name"] == current_user["company"]:
            with st.expander(s["title"]):
                st.markdown(s["content"])

elif menu == "License & Usage":
    st.title("🪪 License")
    st.metric("SOPs Used", f"{current_user['used']} / {current_user['limit']}")
    st.progress(min(current_user["used"] / current_user["limit"], 1.0))
