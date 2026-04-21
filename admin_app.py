import streamlit as st
import string
import random
from github_db import get_db, save_db

st.set_page_config(page_title="AIInnovax Admin", layout="wide", initial_sidebar_state="expanded")

# --- PROFESSIONAL UI & CSS ---
st.markdown("""
    <style>
    /* Hide Streamlit default nav */
    [data-testid='stSidebarNav'] {display: none;}
    
    /* Modern Background & Fonts */
    .stApp { background-color: #F0F4F8; }
    
    /* Colorful Metrics & Cards */
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        border-left: 5px solid #1E3A8A; /* Deep Blue Accent */
    }
    div[data-testid="stMetricValue"] { color: #1E3A8A; font-weight: 800; }
    div[data-testid="stMetricLabel"] { color: #64748B; font-weight: 600; font-size: 14px;}
    
    /* Buttons */
    .stButton>button { 
        border-radius: 8px; 
        transition: all 0.2s ease-in-out;
        font-weight: 600;
    }
    .stButton>button:hover { 
        transform: translateY(-2px); 
        box-shadow: 0 4px 12px rgba(0,0,0,0.1); 
    }
    
    /* Centered Login Form Style */
    .login-container {
        background: white;
        padding: 3rem;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.1);
        border: 1px solid #E2E8F0;
    }
    
    /* Headers */
    h1, h2, h3 { color: #0F172A; }
    </style>
""", unsafe_allow_html=True)

db, sha = get_db()

# Initialize Admin Credentials if not in DB
if "admin_settings" not in db:
    db["admin_settings"] = {"email": "admin@aiinnovax.com", "password": "admin"}
    save_db(db, sha, "Initialize admin")

# --- ADMIN AUTHENTICATION (CENTERED + ENTER KEY) ---
if "admin_logged_in" not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    # Use columns to push the login box to the absolute center
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br><br><br>", unsafe_allow_html=True) # Push down vertically
        
        # Wrapping in st.form enables the "Enter" key submission natively
        with st.form("admin_login", clear_on_submit=False):
            st.markdown("<h2 style='text-align: center; color: #1E3A8A;'>🛡️ AIInnovax Admin</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #64748B;'>Secure Vendor Command Center</p>", unsafe_allow_html=True)
            
            admin_email = st.text_input("Email Address")
            admin_password = st.text_input("Password", type="password")
            
            # The form submit button reacts to the Enter key
            submitted = st.form_submit_button("Secure Login", use_container_width=True)
            
            if submitted:
                if admin_email == db["admin_settings"]["email"] and admin_password == db["admin_settings"]["password"]:
                    st.session_state.admin_logged_in = True
                    st.rerun()
                else:
                    st.error("Invalid Credentials. Access Denied.")
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
st.sidebar.markdown("<h2 style='color: #1E3A8A;'>🛡️ AIInnovax</h2>", unsafe_allow_html=True)
if "admin_menu" not in st.session_state:
    st.session_state.admin_menu = "Dashboard"

menu_options = ["Dashboard", "Manage Subscription", "Global Repository"]

if st.session_state.admin_menu == "Profile":
    menu = "Profile"
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
    c3.metric("System Health", "Operational 🟢")
    c4.metric("LLM Gateway", "Active 🟢")

elif menu == "Profile":
    st.header("👤 Admin Security Profile")
    st.write("Update your vendor administrator credentials here.")
    with st.container(border=True):
        new_admin_email = st.text_input("Admin Email", value=db["admin_settings"]["email"])
        
        # DOUBLE PASSWORD VALIDATION
        new_admin_pw = st.text_input("New Password", type="password")
        confirm_admin_pw = st.text_input("Confirm New Password", type="password")
        
        if st.button("Update Admin Credentials", type="primary"):
            if new_admin_pw or confirm_admin_pw:
                if new_admin_pw != confirm_admin_pw:
                    st.error("Passwords do not match. Please try again.")
                elif len(new_admin_pw) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    db["admin_settings"]["email"] = new_admin_email
                    db["admin_settings"]["password"] = new_admin_pw
                    save_db(db, sha, "Admin updated credentials")
                    st.success("Admin Profile Updated Successfully!")
            else:
                # Just update email if passwords are left blank
                db["admin_settings"]["email"] = new_admin_email
                save_db(db, sha, "Admin updated email")
                st.success("Admin Email Updated!")

elif menu == "Manage Subscription":
    st.header("🪪 Manage Subscriptions")
    
    tab_create, tab_manage = st.tabs(["➕ Onboard Customer", "⚙️ Manage Existing"])
    
    with tab_create:
        if "admin_msg" in st.session_state:
            st.success(st.session_state.admin_msg)
            del st.session_state.admin_msg
            
        with st.container(border=True):
            st.subheader("Create New Account")
            
            c1, c2 = st.columns(2)
            with c1:
                new_email = st.text_input("Customer Corporate Email")
                new_company = st.text_input("Company / Organization Name")
            with c2:
                new_password = st.text_input("Initial Password (Auto-generated)", value=generate_password())
                selected_plan = st.selectbox("Subscription Plan", list(PLANS.keys()))
            
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
                        "force_reset": True 
                    }
                    db.setdefault("users", []).append(new_user)
                    save_db(db, sha, f"Admin: Created user {new_email}")
                    
                    st.session_state.admin_msg = f"Account Created! {new_company} is on the {selected_plan} plan ({sop_limit} limit). Password: {new_password}"
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
                st.subheader(f"Edit Profile: {target_user['company']}")
                
                e_col1, e_col2 = st.columns(2)
                with e_col1:
                    edit_plan = st.selectbox("Update Plan", list(PLANS.keys()), index=list(PLANS.keys()).index(target_user["plan"]) if target_user["plan"] in PLANS else 3)
                    if "Premium" in edit_plan:
                        edit_limit = st.number_input("Custom Monthly Limit", value=target_user["limit"])
                    else:
                        edit_limit = PLANS[edit_plan]
                        st.text_input("Monthly Limit (Fixed by Plan)", value=str(edit_limit), disabled=True)
                        
                with e_col2:
                    edit_status = st.selectbox("Account Status", ["Active", "Inactive"], index=0 if target_user["status"] == "Active" else 1)
                    edit_password = st.text_input("Reset Password (Optional)", value=target_user.get("password", ""))
                
                if st.button("Save Subscription Changes", type="primary"):
                    for u in db["users"]:
                        if u["email"] == target_email:
                            u["plan"] = edit_plan
                            u["limit"] = edit_limit
                            u["status"] = edit_status
                            u["password"] = edit_password
                    save_db(db, sha, f"Admin: Updated license for {target_email}")
                    st.session_state.admin_edit_msg = f"Subscription updated successfully for {target_user['company']}."
                    st.rerun()
            
            # --- DELETION WITH RECONFIRMATION ---
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("🚨 Danger Zone: Delete Customer"):
                st.error("Warning: Deleting this customer will revoke their access permanently.")
                confirm_del = st.checkbox(f"I confirm I want to permanently delete **{target_user['company']}**")
                
                if st.button("Delete Customer Account", type="primary"):
                    if confirm_del:
                        db["users"] = [u for u in db["users"] if u["email"] != target_email]
                        save_db(db, sha, f"Admin: DELETED user {target_email}")
                        st.session_state.admin_edit_msg = f"User {target_email} has been permanently deleted."
                        st.rerun()
                    else:
                        st.warning("You must check the confirmation box to proceed with deletion.")

elif menu == "Global Repository":
    st.header("🗄️ Global Repository")
    
    col_filter, col_search = st.columns(2)
    with col_filter:
        customers = [u["company"] for u in db.get("users", [])]
        selected_filter = st.selectbox("Filter by Customer", ["All"] + customers)
    
    with col_search:
        # SEARCH BAR ADDED
        search_query = st.text_input("🔍 Search SOP by Title")
    
    sops = db.get("sops", [])
    
    # Apply Customer Filter
    if selected_filter != "All":
        sops = [s for s in sops if s["customer_registered_name"] == selected_filter]
        
    # Apply Search Filter
    if search_query:
        sops = [s for s in sops if search_query.lower() in s.get("title", "").lower()]
        
    if not sops:
        st.info("No SOPs found matching your criteria.")
        
    for sop in sops:
        with st.expander(f"{sop['date']} | {sop['title']} ({sop['customer_registered_name']})"):
            st.markdown(sop["content"])
