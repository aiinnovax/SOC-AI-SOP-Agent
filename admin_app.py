import streamlit as st
import string
import random
from github_db import get_db, save_db

# MUST BE FIRST
st.set_page_config(page_title="AIInnovax Admin", layout="wide")

db, sha = get_db()

# Initialize Admin if missing
if "admin_settings" not in db:
    db["admin_settings"] = {"email": "admin@aiinnovax.com", "password": "admin"}
    save_db(db, sha, "Initialize admin")

# --- AUTHENTICATION ---
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.write("<br><br><br>", unsafe_allow_html=True)
        with st.container(border=True):
            with st.form("admin_login_form"):
                st.markdown("<h2 style='text-align: center;'>🛡️ Admin Login</h2>", unsafe_allow_html=True)
                user_input = st.text_input("Email")
                pass_input = st.text_input("Password", type="password")
                if st.form_submit_button("Secure Access", use_container_width=True, type="primary"):
                    if user_input == db["admin_settings"]["email"] and pass_input == db["admin_settings"]["password"]:
                        st.session_state.admin_logged_in = True
                        st.rerun()
                    else:
                        st.error("Invalid Credentials.")
    st.stop()

# --- TOP NAV ---
col_logo, col_profile, col_logout = st.columns([8, 1, 1])
with col_profile:
    if st.button("👤 Profile", use_container_width=True):
        st.session_state.current_page = "Profile"
with col_logout:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.admin_logged_in = False
        st.rerun()
st.divider()

# --- NAVIGATION LOGIC (Fixes 2-click issue) ---
if "current_page" not in st.session_state:
    st.session_state.current_page = "Dashboard"

# Sidebar Radio
menu_options = ["Dashboard", "Manage Subscription", "Global Repository"]
# If we are in Profile, we show a back button in sidebar instead of radio
if st.session_state.current_page == "Profile":
    if st.sidebar.button("← Back to Dashboard"):
        st.session_state.current_page = "Dashboard"
        st.rerun()
    selected_menu = "Profile"
else:
    selected_menu = st.sidebar.radio("Navigation", menu_options, 
                                     index=menu_options.index(st.session_state.current_page))
    st.session_state.current_page = selected_menu

# --- DATA & PLANS ---
PLANS = {"Basic ($25/mo)": 10, "Standard ($75/mo)": 50, "Advance ($150/mo)": 100, "Premium (Custom)": 0}

def generate_password(length=10):
    return ''.join(random.choice(string.ascii_letters + string.digits + "@#$") for _ in range(length))

# --- PAGES ---
if selected_menu == "Dashboard":
    st.header("🏢 Command Center")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Customers", len(db.get("users", [])))
    with c2: st.metric("Total SOPs", len(db.get("sops", [])))
    with c3: st.metric("System Health", "Operational 🟢")
    with c4: st.metric("AI Core", "Multi-Agent Active ⚡")

elif selected_menu == "Profile":
    st.header("👤 Admin Profile Settings")
    with st.container(border=True):
        new_email = st.text_input("Admin Email", value=db["admin_settings"]["email"])
        pw1 = st.text_input("New Password", type="password")
        pw2 = st.text_input("Confirm New Password", type="password")
        if st.button("Update Admin Credentials", type="primary"):
            if pw1 != pw2:
                st.error("Passwords do not match!")
            else:
                db["admin_settings"]["email"] = new_email
                if pw1: db["admin_settings"]["password"] = pw1
                save_db(db, sha)
                st.success("Admin Profile Updated.")

elif selected_menu == "Manage Subscription":
    st.header("🪪 Subscription Management")
    t1, t2 = st.tabs(["➕ Onboard New Customer", "⚙️ Manage Existing"])
    
    with t1:
        if "msg" in st.session_state:
            st.success(st.session_state.msg)
            del st.session_state.msg

        with st.container(border=True):
            col_a, col_b = st.columns(2)
            with col_a:
                nc_email = st.text_input("Customer Email")
                nc_company = st.text_input("Company Name")
            with col_b:
                nc_pass = st.text_input("Temporary Password", value=generate_password())
                nc_plan = st.selectbox("Select Plan", list(PLANS.keys()))
            
            # Dynamic Premium Input
            if "Premium" in nc_plan:
                nc_limit = st.number_input("Manual SOP Limit", min_value=1, value=500)
            else:
                nc_limit = PLANS[nc_plan]
            
            if st.button("Create Account & License", type="primary"):
                if nc_email and nc_company:
                    db["users"].append({
                        "uid": f"u_{random.randint(1000,9999)}",
                        "email": nc_email.strip(), "password": nc_pass, "company": nc_company.strip(),
                        "plan": nc_plan, "limit": nc_limit, "used": 0, "status": "Active", "force_reset": True
                    })
                    save_db(db, sha)
                    st.session_state.msg = f"User Created! Password: {nc_pass}"
                    st.rerun()

    with t2:
        if not db.get("users"):
            st.info("No customers found.")
        else:
            target = st.selectbox("Select Customer to Edit", [u["email"] for u in db["users"]])
            user_ref = next(u for u in db["users"] if u["email"] == target)
            
            with st.container(border=True):
                st.subheader(f"Edit: {user_ref['company']}")
                ec1, ec2 = st.columns(2)
                with ec1:
                    e_plan = st.selectbox("Plan", list(PLANS.keys()), index=list(PLANS.keys()).index(user_ref["plan"]))
                    if "Premium" in e_plan:
                        e_limit = st.number_input("Limit", value=user_ref["limit"])
                    else:
                        e_limit = PLANS[e_plan]
                        st.text_input("Limit (Fixed)", value=str(e_limit), disabled=True)
                with ec2:
                    e_status = st.selectbox("Status", ["Active", "Inactive"], index=0 if user_ref["status"] == "Active" else 1)
                    e_pass = st.text_input("Reset Password", value=user_ref["password"])
                
                if st.button("Save Subscription Changes"):
                    user_ref.update({"plan": e_plan, "limit": e_limit, "status": e_status, "password": e_pass})
                    save_db(db, sha)
                    st.success("Updated Successfully")

            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("🚨 Danger Zone: Delete Customer"):
                st.warning("Deletions are permanent.")
                confirm = st.checkbox(f"I confirm I want to delete {user_ref['company']}")
                if st.button("Execute Deletion", type="primary") and confirm:
                    db["users"] = [u for u in db["users"] if u["email"] != target]
                    save_db(db, sha)
                    st.rerun()

elif selected_menu == "Global Repository":
    st.header("🗄️ Global Repository")
    search = st.text_input("🔍 Search SOPs by Title")
    for s in db.get("sops", []):
        if search.lower() in s["title"].lower():
            with st.expander(f"{s['customer_registered_name']} | {s['title']}"):
                st.markdown(s["content"])
