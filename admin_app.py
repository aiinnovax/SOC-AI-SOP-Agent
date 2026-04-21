import streamlit as st
import string
import random
from github_db import get_db, save_db

st.set_page_config(page_title="AIInnovax Admin", layout="wide")
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

db, sha = get_db()

# --- HELPER VARS ---
PLANS = {
    "Basic ($25/mo)": 10,
    "Standard ($75/mo)": 50,
    "Advance ($150/mo)": 100,
    "Premium (Custom)": 500  # Default premium limit
}

def generate_password(length=10):
    chars = string.ascii_letters + string.digits + "@#$"
    return ''.join(random.choice(chars) for i in range(length))

# --- SIDEBAR NAV ---
st.sidebar.title("🛡️ AIInnovax Admin")
menu = st.sidebar.radio("Navigation", ["Dashboard", "Manage Subscription", "Global Repository"])

if menu == "Dashboard":
    st.header("🏢 Central Command Dashboard")
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Customers", len(db.get("users", [])))
    c2.metric("Total SOPs Generated", len(db.get("sops", [])))
    c3.metric("System Health", "Operational")
    c4.metric("LLM Routing", "Active")
    
    st.divider()
    st.subheader("Recent System Alerts")
    st.info("System fully synced with GitHub Unified Storage.")

elif menu == "Manage Subscription":
    st.header("🪪 Manage Subscription")
    
    tab_create, tab_manage = st.tabs(["➕ Create Customer Account", "⚙️ Manage Existing Customers"])
    
    with tab_create:
        with st.container(border=True):
            st.subheader("Onboard New Customer")
            with st.form("create_user_form"):
                col1, col2 = st.columns(2)
                with col1:
                    new_email = st.text_input("Customer Email")
                    new_company = st.text_input("Company Name")
                with col2:
                    new_password = st.text_input("Initial Password (Auto-generated)", value=generate_password())
                    selected_plan = st.selectbox("Subscription Plan", list(PLANS.keys()))
                
                premium_limit = st.number_input("Custom SOP Limit (Applies only if Premium is selected)", value=500, min_value=1)
                
                if st.form_submit_button("Create Account & Assign License", type="primary"):
                    if new_email and new_company:
                        sop_limit = premium_limit if "Premium" in selected_plan else PLANS[selected_plan]
                        
                        new_user = {
                            "uid": f"usr_{new_company.replace(' ', '').lower()}_{random.randint(100,999)}",
                            "email": new_email.strip(),
                            "password": new_password,
                            "company": new_company.strip(),
                            "plan": selected_plan,
                            "limit": sop_limit,
                            "used": 0,
                            "status": "Active"
                        }
                        
                        db.setdefault("users", []).append(new_user)
                        save_db(db, sha, f"Admin: Created user {new_email}")
                        st.success(f"Successfully created account for {new_company}. Provide them with the email and password.")
                        st.rerun()
                    else:
                        st.error("Email and Company Name are required.")
                        
    with tab_manage:
        if not db.get("users"):
            st.info("No customers onboarded yet.")
        else:
            user_emails = [u["email"] for u in db["users"]]
            target_email = st.selectbox("Select Customer to Manage", user_emails)
            target_user = next(u for u in db["users"] if u["email"] == target_email)
            
            with st.container(border=True):
                st.subheader(f"Edit License: {target_user['company']}")
                with st.form("edit_user_form"):
                    e_col1, e_col2 = st.columns(2)
                    with e_col1:
                        edit_plan = st.selectbox("Update Plan", list(PLANS.keys()), index=list(PLANS.keys()).index(target_user["plan"]) if target_user["plan"] in PLANS else 3)
                        edit_limit = st.number_input("Monthly SOP Limit", value=target_user["limit"])
                    with e_col2:
                        edit_status = st.selectbox("Account Status", ["Active", "Inactive"], index=0 if target_user["status"] == "Active" else 1)
                        edit_password = st.text_input("Reset Password", value=target_user.get("password", ""))
                    
                    if st.form_submit_button("Save Changes", type="primary"):
                        for u in db["users"]:
                            if u["email"] == target_email:
                                u["plan"] = edit_plan
                                u["limit"] = edit_limit
                                u["status"] = edit_status
                                u["password"] = edit_password
                        
                        save_db(db, sha, f"Admin: Updated license for {target_email}")
                        st.success("Customer profile updated successfully.")
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
            st.markdown(f"**Client Context:** {sop.get('client_name', 'Global')}")
            st.markdown(sop["content"])
