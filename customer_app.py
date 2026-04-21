import streamlit as st
import datetime
from github_db import get_db, save_db
from ai_service import generate_sop

st.set_page_config(page_title="SOP-Genie Portal", layout="wide")

db, sha = get_db()

# --- AUTHENTICATION ---
if "user_email" not in st.session_state:
    st.session_state.user_email = None

if not st.session_state.user_email:
    _, center, _ = st.columns([1, 1.5, 1])
    with center:
        st.write("<br><br>", unsafe_allow_html=True)
        with st.container(border=True):
            with st.form("login"):
                st.markdown("<h2 style='text-align: center;'>⚡ SOP-Genie</h2>", unsafe_allow_html=True)
                le = st.text_input("Corporate Email")
                lp = st.text_input("Password", type="password")
                if st.form_submit_button("Access Terminal", use_container_width=True, type="primary"):
                    matched = next((u for u in db.get("users", []) if u["email"] == le and u["password"] == lp), None)
                    if matched:
                        st.session_state.user_email = matched["email"]
                        st.rerun()
                    else: st.error("Invalid Credentials")
    st.stop()

current_user = next(u for u in db["users"] if u["email"] == st.session_state.user_email)

# --- TOP NAV ---
col_l, col_p, col_o = st.columns([8, 1, 1])
with col_p:
    if st.button("👤 Profile", use_container_width=True): st.session_state.cmenu = "Profile"
with col_o:
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.user_email = None
        st.rerun()
st.divider()

if "cmenu" not in st.session_state: st.session_state.cmenu = "SOP Architect"

# Sidebar
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
    st.header("👤 Profile Settings")
    with st.container(border=True):
        up1 = st.text_input("New Password", type="password")
        up2 = st.text_input("Confirm New Password", type="password")
        if st.button("Update Security Credentials"):
            if up1 == up2 and len(up1) >= 6:
                current_user["password"] = up1
                save_db(db, sha)
                st.success("Password Updated")
            else: st.error("Match error or too short")

elif menu == "SOP Architect":
    st.title("🔍 SOP Architect")
    if current_user["used"] >= current_user["limit"]:
        st.error("Monthly Quota Reached. Contact AIInnovax Support.")
        st.stop()

    c1, c2 = st.columns([1, 1.5])
    with c1:
        with st.container(border=True):
            st.subheader("1. Target Context")
            # RESTORED: Client selection based on owner_uid
            my_clients = [c for c in db.get("clients", []) if c.get("owner_uid") == current_user["uid"]]
            
            if not my_clients:
                client_name = current_user["company"]
                log_sources = "Standard Enterprise Logs"
                st.info(f"Using default: {client_name}")
            else:
                target_c = st.selectbox("Select Client", [c["name"] for c in my_clients])
                client_data = next(c for c in my_clients if c["name"] == target_c)
                client_name = client_data["name"]
                log_sources = client_data["log_sources"]
                st.caption(f"Sources: {log_sources}")

            siem = st.selectbox("Detection Engine", ["Sentinel", "CrowdStrike", "Splunk", "QRadar", "Generic"])
            logic = st.text_area("Detection Logic / KQL / Sigma", height=200)
            
            if st.button("Synthesize SOP", type="primary", use_container_width=True):
                with st.spinner("AI Multi-Agent Core Analyzing..."):
                    res = generate_sop(siem, logic, client_name, log_sources)
                    # Deduct quota and save only on success
                    if "ERROR" not in res:
                        db["sops"].append({
                            "id": f"sop_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                            "title": f"{siem} Response SOP",
                            "customer_registered_name": current_user["company"],
                            "client_name": client_name,
                            "date": str(datetime.date.today()),
                            "content": res
                        })
                        for u in db["users"]:
                            if u["email"] == current_user["email"]: u["used"] += 1
                        save_db(db, sha)
                        st.session_state.last_sop = res
                        st.rerun()
                    else: st.error(res)

    with c2:
        with st.container(border=True):
            st.subheader("2. Operational Output")
            if "last_sop" in st.session_state:
                st.markdown(st.session_state.last_sop)

elif menu == "My Repository":
    st.title("📂 Organization Vault")
    my_sops = [s for s in db.get("sops", []) if s["customer_registered_name"] == current_user["company"]]
    for s in my_sops:
        with st.expander(f"{s['date']} | {s['title']} ({s.get('client_name', 'Global')})"):
            st.markdown(s["content"])
            st.download_button("Download .md", s["content"], file_name=f"{s['id']}.md")

elif menu == "License & Usage":
    st.title("🪪 Subscription")
    st.metric("SOPs Generated", f"{current_user['used']} / {current_user['limit']}")
    st.progress(min(current_user["used"] / current_user["limit"], 1.0))
