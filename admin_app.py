import streamlit as st
import string
import random
from github_db import get_db, save_db

st.set_page_config(page_title="AIInnovax Admin", layout="wide")

db, sha = get_db()

# --- CENTERED LOGIN ---
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.write("<br><br>", unsafe_allow_html=True)
        with st.form("admin_login"):
            st.markdown("<h2 style='text-align: center;'>🛡️ Admin Login</h2>", unsafe_allow_html=True)
            user = st.text_input("Email")
            pw = st.text_input("Password", type="password")
            if st.form_submit_button("Secure Access", use_container_width=True, type="primary"):
                if user == db["admin_settings"]["email"] and pw == db["admin_settings"]["password"]:
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else: st.error("Unauthorized")
    st.stop()

# --- NAVIGATION ---
col_l, col_p, col_o = st.columns([8, 1, 1])
with col_p:
    if st.button("👤 Profile"): st.session_state.amenu = "Profile"
with col_o:
    if st.button("🚪 Logout"): 
        st.session_state.admin_logged_in = False
        st.rerun()

if "amenu" not in st.session_state: st.session_state.amenu = "Dashboard"
menu = st.sidebar.radio("Navigation", ["Dashboard", "Manage Subscription", "Global Repository"], 
                        index=["Dashboard", "Manage Subscription", "Global Repository"].index(st.session_state.amenu) if st.session_state.amenu != "Profile" else 0)

if st.session_state.amenu == "Profile":
    st.header("👤 Security Profile")
    with st.container(border=True):
        email = st.text_input("Admin Email", value=db["admin_settings"]["email"])
        pw1 = st.text_input("New Password", type="password")
        pw2 = st.text_input("Confirm Password", type="password")
        if st.button("Update Profile"):
            if pw1 == pw2:
                db["admin_settings"].update({"email": email, "password": pw1 if pw1 else db["admin_settings"]["password"]})
                save_db(db, sha)
                st.success("Updated")
            else: st.error("Password mismatch")
else:
    if menu == "Dashboard":
        st.header("🏢 Command Center")
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Customers", len(db["users"]))
        c2.metric("SOPs", len(db["sops"]))
        c3.metric("Status", "Operational 🟢")
        c4.metric("AI Core", "Multi-Agent Active ⚡")

    elif menu == "Manage Subscription":
        t1, t2 = st.tabs(["➕ New Customer", "⚙️ Manage"])
        with t1:
            with st.form("new_u"):
                e = st.text_input("Email")
                c = st.text_input("Company")
                p = st.selectbox("Plan", ["Basic ($25/mo)", "Standard ($75/mo)", "Advance ($150/mo)", "Premium (Custom)"])
                if st.form_submit_button("Create"):
                    limits = {"Basic ($25/mo)": 10, "Standard ($75/mo)": 50, "Advance ($150/mo)": 100, "Premium (Custom)": 500}
                    db["users"].append({"uid": f"u_{random.randint(100,999)}", "email": e, "company": c, "plan": p, "limit": limits[p], "used": 0, "status": "Active", "password": "temp", "force_reset": True})
                    save_db(db, sha)
                    st.success("Account Created")

        with t2:
            target = st.selectbox("Select Customer", [u["email"] for u in db["users"]])
            user_ref = next(u for u in db["users"] if u["email"] == target)
            with st.expander("🚨 Danger Zone"):
                confirm = st.checkbox(f"Delete {user_ref['company']}?")
                if st.button("Execute Deletion") and confirm:
                    db["users"] = [u for u in db["users"] if u["email"] != target]
                    save_db(db, sha)
                    st.rerun()

    elif menu == "Global Repository":
        st.header("🗄️ Global Repository")
        search = st.text_input("🔍 Search SOPs")
        for s in db["sops"]:
            if search.lower() in s["title"].lower():
                with st.expander(f"{s['customer_registered_name']} | {s['title']}"):
                    st.markdown(s["content"])
