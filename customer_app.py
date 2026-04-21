import streamlit as st
import datetime
from github_db import get_db, save_db
from ai_service import generate_sop

st.set_page_config(page_title="SOP-Genie Customer Portal", layout="wide")
st.markdown("<style>[data-testid='stSidebarNav'] {display: none;}</style>", unsafe_allow_html=True)

# --- AUTHENTICATION (Mocked for Streamlit simplicity, replace with Firebase Auth/Streamlit-Auth if needed) ---
st.sidebar.subheader("Terminal Login")
user_email = st.sidebar.text_input("Corporate Email", value="soc@infosys.com")

db, sha = get_db()

# Find user in DB
current_user = next((u for u in db.get("users", []) if u["email"] == user_email), None)

if not current_user:
    st.error("Authentication Failed. No active license found for this email.")
    st.stop()

# --- SIDEBAR NAV ---
menu = st.sidebar.radio("Mission Control", ["SOP Architect", "My Repository", "License & Usage"])

if menu == "SOP Architect":
    st.title("🔍 SOP-Genie: Architect")
    
    # 1. Check Subscription Limits
    if current_user["used"] >= current_user["limit"]:
        st.error(f"Quota Exceeded. You have used {current_user['used']}/{current_user['limit']} SOPs on the {current_user['plan']} plan. Contact AIInnovax Sales.")
        st.stop()
        
    c1, c2 = st.columns([1, 1.5])
    
    with c1:
        st.subheader("1. Threat Context")
        
        # Filter clients belonging to this user
        my_clients = [c for c in db.get("clients", []) if c["owner_uid"] == current_user["uid"]]
        
        if not my_clients:
            st.warning("Please configure a Client in Settings first.")
            st.stop()
            
        client_names = [c["name"] for c in my_clients]
        selected_client_name = st.selectbox("Target Client", client_names)
        target_client = next(c for c in my_clients if c["name"] == selected_client_name)
        
        st.caption(f"Mapped Log Sources: {target_client['log_sources']}")
        
        siem = st.selectbox("Detection Engine", ["Sentinel", "CrowdStrike", "Splunk", "QRadar", "Sigma"])
        logic = st.text_area("Paste Detection Logic / Query", height=150)
        
        if st.button("Synthesize SOP", type="primary", use_container_width=True):
            if logic:
                with st.spinner("AI Intelligence Core processing..."):
                    # Generate SOP
                    result = generate_sop(siem, logic, target_client["name"], target_client["log_sources"])
                    
                    # Update DB (Increment usage, save SOP)
                    new_sop = {
                        "id": f"sop_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                        "title": f"{siem} Detection Response",
                        "customer_registered_name": current_user["company"],
                        "client_name": target_client["name"],
                        "date": datetime.datetime.now().strftime("%Y-%m-%d"),
                        "content": result,
                        "mod_count": 0
                    }
                    
                    # Apply changes to DB dictionary
                    for u in db["users"]:
                        if u["uid"] == current_user["uid"]:
                            u["used"] += 1
                            
                    db["sops"].append(new_sop)
                    save_db(db, sha, f"Customer: {current_user['company']} generated SOP")
                    
                    st.session_state.last_sop = result
                    st.success("SOP Generated and Vaulted.")
            else:
                st.warning("Provide detection logic.")

    with c2:
        st.subheader("2. Operational Output")
        if 'last_sop' in st.session_state:
            st.markdown(st.session_state.last_sop)

elif menu == "My Repository":
    st.title("📂 Organization Vault")
    my_sops = [s for s in db.get("sops", []) if s["customer_registered_name"] == current_user["company"]]
    
    for sop in my_sops:
        with st.expander(f"{sop['date']} | {sop['title']} (Target: {sop['client_name']})"):
            st.markdown(sop["content"])
            st.download_button("Download Markdown", sop["content"], file_name=f"{sop['id']}.md")

elif menu == "License & Usage":
    st.title("🪪 Subscription Status")
    
    st.metric("Current Plan", current_user["plan"])
    st.progress(current_user["used"] / current_user["limit"])
    st.write(f"Usage: **{current_user['used']} / {current_user['limit']}** Monthly SOPs utilized.")
    if current_user["plan"] != "Enterprise":
        st.button("Upgrade to Next Tier")
