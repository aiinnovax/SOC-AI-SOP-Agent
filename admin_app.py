import streamlit as st
import string
import random
from github_db import get_db, save_db

st.set_page_config(page_title="AIInnovax Admin", layout="wide", initial_sidebar_state="expanded")

db, sha = get_db()

# Initialize Admin Credentials if not in DB
if "admin_settings" not in db:
    db["admin_settings"] = {"email": "admin@aiinnovax.com", "password": "admin"}
    save_db(db, sha, "Initialize admin")

# --- CENTERED LOGIN SCREEN ---
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.write("<br><br><br>", unsafe_allow_html=True)
        with st.container(border=True):
            with st.form("admin_login_form"):
                st.markdown("<h2 style='text-align: center;'>🛡️ AIInnovax Admin</h2>", unsafe_allow_html=True)
                st.markdown("<p style='text-align: center;'>Vendor Command Center</p>", unsafe_allow_html=True)
                admin_email = st.text_input("Admin Email")
                admin_password = st.text_input("Password", type="password")
                if st.form_submit_button("Secure Login", use_container_width=True, type="primary"):
                    if admin_email == db["admin_settings"]["email"] and admin_password == db["admin_settings"]["password"]:
                        st.session_state.admin_logged_in = True
                        st.rerun()
                    else:
                        st.error("Invalid Credentials.")
    st.stop()

# --- TOP NAVIGATION ---
col_logo, col_profile, col_logout = st.columns([8, 1, 1])
with col_profile:
    if st.button("👤 Profile", use_container_width=True):
        st.session_state.admin_menu = "Profile"
with col_logout:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.admin_logged_in = False
        st.rerun()
st.divider()

PLANS = {"Basic ($25/mo)": 10, "Standard ($75/mo)": 50, "Advance ($150/mo)": 100, "Premium (Custom)": 0}

def generate_password(length=10):
    return ''.join(random.choice(string.ascii_letters + string.digits + "@#$") for _ in range(length))

# --- SIDEBAR ---
st.sidebar.title("🛡️ AIInnovax")
if "admin_menu" not in st.session_state:
    st.session_state.admin_menu = "Dashboard"

if st.session_state.admin_menu == "Profile":
    menu = "Profile"
    if st.sidebar.button("← Back to Dashboard"):
        st.session_state.admin_menu = "Dashboard"
        st.rerun()
else:
    menu = st.sidebar.radio("Menu", ["Dashboard", "Manage Subscription", "Global Repository"], index=["Dashboard", "Manage Subscription", "Global Repository"].index(st.session_state.admin_menu))
    st.session_state.admin_menu = menu

# --- DASHBOARD METRICS ---
if menu == "Dashboard":
    st.header("🏢 Command Dashboard")
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Total Customers", len(db.get("users", [])))
    with c2: st.metric("Total SOPs", len(db.get("sops", [])))
    with c3: st.metric("System Health", "Healthy 🟢")
    with c4: st.metric("Groq Llama-3", "Active ⚡") # Changed label

elif menu == "Profile":
    st.header("👤 Admin Security Profile")
    with st.container(border=True):
        new_admin_email = st.text_input("Admin Email", value=db["admin_settings"]["email"])
        new_admin_pw = st.text_input("New Password", type="password")
        confirm_admin_pw = st.text_input("Confirm New Password", type="password")
        
        if st.button("Update Admin Credentials", type="primary"):
            if new_admin_pw or confirm_admin_pw:
                if new_admin_pw != confirm_admin_pw:
                    st.error("Passwords do not match!")
                elif len(new_admin_pw) < 6:
                    st.error("Password must be 6+ characters.")
                else:
                    db["admin_settings"]["email"] = new_admin_email
                    db["admin_settings"]["password"] = new_admin_pw
                    save_db(db, sha, "Admin updated credentials")
                    st.success("Profile Updated Successfully!")
            else:
                db["admin_settings"]["email"] = new_admin_email
                save_db(db, sha, "Admin updated email")
                st.success("Email Updated!")

elif menu == "Manage Subscription":
    st.header("🪪 Manage Subscriptions")
    tab_create, tab_manage = st.tabs(["➕ Onboard Customer", "⚙️ Manage Existing"])
    
    with tab_create:
        if "admin_msg" in st.session_state:
            st.success(st.session_state.admin_msg)
            del st.session_state.admin_msg
            
        with st.container(border=True):
            c1, c2 = st.columns(2)
            with c1:
                new_email = st.text_input("Customer Corporate Email")
                new_company = st.text_input("Company Name")
            with c2:
                new_password = st.text_input("Initial Password (Auto)", value=generate_password())
                selected_plan = st.selectbox("Subscription Plan", list(PLANS.keys()))
            
            if "Premium" in selected_plan:
                sop_limit = st.number_input("Custom Monthly SOP Limit", min_value=1, value=500)
            else:
                sop_limit = PLANS[selected_plan]
            
            if st.button("Create Account", type="primary"):
                if new_email and new_company:
                    new_user = {
                        "uid": f"usr_{new_company.replace(' ', '').lower()}_{random.randint(100,999)}",
                        "email": new_email.strip(), "password": new_password, "company": new_company.strip(),
                        "plan": selected_plan, "limit": sop_limit, "used": 0, "status": "Active", "force_reset": True 
                    }
                    db.setdefault("users", []).append(new_user)
                    save_db(db, sha, f"Admin created {new_email}")
                    st.session_state.admin_msg = f"Account Created! Password: {new_password}"
                    st.rerun()

    with tab_manage:
        if "admin_edit_msg" in st.session_state:
            st.success(st.session_state.admin_edit_msg)
            del st.session_state.admin_edit_msg

        if not db.get("users"):
            st.info("No customers onboarded.")
        else:
            user_emails = [u["email"] for u in db["users"]]
            target_email = st.selectbox("Select Customer to Manage", user_emails)
            target_user = next(u for u in db["users"] if u["email"] == target_email)
            
            with st.container(border=True):
                st.subheader(f"Edit Profile: {target_user['company']}")
                e_col1, e_col2 = st.columns(2)
                with e_col1:
                    edit_plan = st.selectbox("Update Plan", list(PLANS.keys()), index=list(PLANS.keys()).index(target_user["plan"]) if target_user["plan"] in PLANS else 3)
                    if "Premium" in edit_plan:
                        edit_limit = st.number_input("Custom Monthly Limit", value=target_user["limit"])
                    else:
                        edit_limit = PLANS[edit_plan]
                        st.text_input("Fixed Limit", value=str(edit_limit), disabled=True)
                with e_col2:
                    edit_status = st.selectbox("Status", ["Active", "Inactive"], index=0 if target_user["status"] == "Active" else 1)
                    edit_password = st.text_input("Reset Password", value=target_user.get("password", ""))
                
                if st.button("Save Changes", type="primary"):
                    for u in db["users"]:
                        if u["email"] == target_email:
                            u.update({"plan": edit_plan, "limit": edit_limit, "status": edit_status, "password": edit_password})
                    save_db(db, sha, f"Admin updated {target_email}")
                    st.session_state.admin_edit_msg = "Updated successfully."
                    st.rerun()
            
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("🚨 Danger Zone: Delete Customer"):
                st.error("This is permanent.")
                confirm_del = st.checkbox(f"I confirm I want to delete **{target_user['company']}**")
                if st.button("Delete Account", type="primary"):
                    if confirm_del:
                        db["users"] = [u for u in db["users"] if u["email"] != target_email]
                        save_db(db, sha, f"Admin DELETED {target_email}")
                        st.session_state.admin_edit_msg = f"User {target_email} deleted."
                        st.rerun()
                    else:
                        st.warning("You must check the confirmation box.")

elif menu == "Global Repository":
    st.header("🗄️ Global Repository")
    col_filter, col_search = st.columns(2)
    with col_filter:
        customers = [u["company"] for u in db.get("users", [])]
        selected_filter = st.selectbox("Filter by Customer", ["All"] + customers)
    with col_search:
        search_query = st.text_input("🔍 Search SOP by Title")
    
    sops = db.get("sops", [])
    if selected_filter != "All": sops = [s for s in sops if s["customer_registered_name"] == selected_filter]
    if search_query: sops = [s for s in sops if search_query.lower() in s.get("title", "").lower()]
        
    for sop in sops:
        with st.expander(f"{sop['date']} | {sop['title']} ({sop['customer_registered_name']})"):
            st.markdown(sop["content"])
