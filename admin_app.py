import streamlit as st
import string
import random
from github_db import get_db, save_db

st.set_page_config(page_title="AIInnovax Admin", layout="wide")
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

db, sha = get_db()

# Initialize Admin Credentials if not in DB
if "admin_settings" not in db:
    db["admin_settings"] = {"email": "admin@aiinnovax.com", "password": "admin"}
    save_db(db, sha, "Initialize admin")

# --- ADMIN AUTHENTICATION ---
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    st.subheader("🛡️ Vendor Admin Login")
    admin_email = st.text_input("Email")
    admin_password = st.text_input("Password", type="password")
    if st.button("Login", type="primary"):
        if admin_email == db["admin_settings"]["email"] and admin_password == db["admin_settings"]["password"]:
            st.session_state.admin_logged_in = True
            st.rerun()
        else:
            st.error("Invalid Admin Credentials")
    st.stop()

# --- TOP NAVIGATION (Profile & Logout) ---
col_spacer, col_profile, col_logout = st.columns([8, 1, 1])
with col_profile:
    if st.button("👤 Profile", use_container_width=True):
        st.session_state.admin_menu = "Profile"
with col_logout:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.admin_logged_in = False
        st.rerun()
st.divider()

# --- FIXED SUBSCRIPTION PLANS ---
PLANS = {
    "Basic ($25/mo)": 10,
    "Standard ($75/mo)": 50,
    "Advance ($150/mo)": 100,
    "Premium (Custom)": 0 # Dynamic
}

def generate_password(length=10):
    chars = string.ascii_letters + string.digits + "@#$"
    return ''.join(random.choice(chars) for i in range(length))

# --- SIDEBAR NAV ---
st.sidebar.title("🛡️ AIInnovax Admin")
if "admin_menu" not in st.session_state:
    st.session_state.admin_menu = "Dashboard"

menu_options = ["Dashboard", "Manage Subscription", "Global Repository"]
# If they clicked profile, it overrides the sidebar visually
if st.session_state.admin_menu == "Profile":
    menu = "Profile"
    # Provide a way back
    if st.sidebar.button("← Back to Dashboard"):
        st.session_state.admin_menu = "Dashboard"
        st.rerun()
else:
    menu = st.sidebar.radio("Navigation", menu_options, index=menu_options.index(st.session_state.admin_menu))
    st.session_state.admin_menu = menu

# --- PAGE ROUTING ---
if menu == "Dashboard":
    st.header("🏢 Central Command Dashboard")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Customers", len(db.get("users", [])))
    c2.metric("Total SOPs Generated", len(db.get("sops", [])))
    c3.metric("System Health", "Operational")
    c4.metric("LLM Routing", "Active")

elif menu == "Profile":
    st.header("👤 Admin Profile")
    st.write("Update your vendor administrator credentials here.")
    with st.container(border=True):
        new_admin_email = st.text_input("Admin Email", value=db["admin_settings"]["email"])
        new_admin_pw = st.text_input("New Password", type="password")
        if st.button("Update Admin Credentials", type="primary"):
            db["admin_settings"]["email"] = new_admin_email
            if new_admin_pw:
                db["admin_settings"]["password"] = new_admin_pw
            save_db(db, sha, "Admin updated credentials")
            st.success("Admin Profile Updated!")

elif menu == "Manage Subscription":
    st.header("🪪 Manage Subscription")
    
    tab_create, tab_manage = st.tabs(["➕ Create Customer Account", "⚙️ Manage Existing Customers"])
    
    with tab_create:
        if "admin_msg" in st.session_state:
            st.success(st.session_state.admin_msg)
            del st.session_state.admin_msg
            
        with st.container(border=True):
            st.subheader("Onboard New Customer")
            
            c1, c2 = st.columns(2)
            with c1:
                new_email = st.text_input("Customer Email")
                new_company = st.text_input("Company Name")
            with c2:
                new_password = st.text_input("Initial Password (Auto-generated)", value=generate_password())
                selected_plan = st.selectbox("Subscription Plan", list(PLANS.keys()))
            
            # DYNAMIC: Only show manual count if Premium is selected
            if "Premium" in selected_plan:
                sop_limit = st.number_input("Custom Monthly SOP Limit", min_value=1, value=500)
            else:
                sop_limit = PLANS[selected_plan]
            
            if st.button("Create Account & Assign License", type="primary"):
                if new_email and new_company:
                    new_user = {
                        "uid": f"usr_{new_company.replace(' ', '').lower()}_{random.randint(100,999)}",
                        "email": new_email.strip(),
                        "password": new_password,
                        "company": new_company.strip(),
                        "plan": selected_plan,
                        "limit": sop_limit,
                        "used": 0,
                        "status": "Active",
                        "force_reset": True # Forces customer to change password on first login
                    }
                    
                    db.setdefault("users", []).append(new_user)
                    save_db(db, sha, f"Admin: Created user {new_email}")
                    
                    st.session_state.admin_msg = f"Account Created! {new_company} has the {selected_plan} plan ({sop_limit} SOPs). Password: {new_password}"
                    st.rerun()
                else:
                    st.error("Email and Company Name are required.")
                        
    with tab_manage:
        if "admin_edit_msg" in st.session_state:
            st.success(st.session_state.admin_edit_msg)
            del st.session_state.admin_edit_msg

        if not db.get("users"):
            st.info("No customers onboarded yet.")
        else:
            user_emails = [u["email"] for u in db["users"]]
            target_email = st.selectbox("Select Customer to Manage", user_emails)
            target_user = next(u for u in db["users"] if u["email"] == target_email)
            
            with st.container(border=True):
                st.subheader(f"Edit License: {target_user['company']}")
                
                e_col1, e_col2 = st.columns(2)
                with e_col1:
                    edit_plan = st.selectbox("Update Plan", list(PLANS.keys()), index=list(PLANS.keys()).index(target_user["plan"]) if target_user["plan"] in PLANS else 3)
                    
                    # DYNAMIC limit editing based on plan
                    if "Premium" in edit_plan:
                        edit_limit = st.number_input("Custom Monthly Limit", value=target_user["limit"])
                    else:
                        edit_limit = PLANS[edit_plan]
                        st.text_input("Monthly Limit (Fixed by Plan)", value=str(edit_limit), disabled=True)
                        
                with e_col2:
                    edit_status = st.selectbox("Account Status", ["Active", "Inactive"], index=0 if target_user["status"] == "Active" else 1)
                    edit_password = st.text_input("Reset Password (Optional)", value=target_user.get("password", ""))
                
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button("Save Changes", type="primary", use_container_width=True):
                        for u in db["users"]:
                            if u["email"] == target_email:
                                u["plan"] = edit_plan
                                u["limit"] = edit_limit
                                u["status"] = edit_status
                                u["password"] = edit_password
                        
                        save_db(db, sha, f"Admin: Updated license for {target_email}")
                        st.session_state.admin_edit_msg = f"Subscription updated successfully for {target_user['company']}."
                        st.rerun()
                        
                with btn_col2:
                    if st.button("🚨 Delete Customer", use_container_width=True):
                        db["users"] = [u for u in db["users"] if u["email"] != target_email]
                        save_db(db, sha, f"Admin: DELETED user {target_email}")
                        st.session_state.admin_edit_msg = f"User {target_email} has been permanently deleted."
                        st.rerun()

elif menu == "Global Repository":
    st.header("🗄️ Unified SOP Vault")
    customers = [u["company"] for u in db.get("users", [])]
    selected_filter = st.selectbox("Filter by Customer", ["All"] + customers)
    
    sops = db.get("sops", [])
    if selected_filter != "All":
        sops = [s for s in sops if s["customer_registered_name"] == selected_filter]
        
    for sop in sops:
        with st.expander(f"{sop['date']} | {sop['title']} ({sop['customer_registered_name']})"):
            st.markdown(sop["content"])
