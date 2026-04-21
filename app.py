import streamlit as st
import json
from github import Github
from llm_router import generate_sop

# --- UI CONFIG ---
st.set_page_config(page_title="AIInnovax Mission Control", layout="wide")

# --- GITHUB DATABASE SETUP ---
@st.cache_resource
def get_github_repo():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        return g.get_repo(st.secrets["REPO_PATH"])
    except Exception as e:
        st.error(f"GitHub Connection Failed. Check your Streamlit Secrets. Error: {e}")
        st.stop()

repo = get_github_repo()

def get_db():
    """Reads the latest database.json from GitHub"""
    file_content = repo.get_contents("database.json")
    return json.loads(file_content.decoded_content.decode()), file_content

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    st.title("🛡️ AIInnovax")
    page = st.radio("Navigation", ["Customer Portal", "Admin Portal"])
    st.markdown("---")
    show_debug = st.checkbox("Show AI Debug")

# Fetch current database state
db, db_file = get_db()
clients = db.get("customers", [])

# --- ADMIN PORTAL ---
if page == "Admin Portal":
    st.header("🏢 Admin Portal: Client Management")
    st.write("Register new organizations and map their security infrastructure.")
    
    with st.expander("➕ Register New Client", expanded=True):
        new_name = st.text_input("Client Name")
        new_siem = st.selectbox("SIEM Vendor", ["Sentinel", "Splunk", "CrowdStrike", "QRadar"])
        new_logs = st.text_area("Log Sources (Comma Separated)", placeholder="e.g. AWS CloudTrail, Carbon Black, Fortigate")
        
        if st.button("Initialize Client Environment"):
            if new_name and new_logs:
                with st.spinner("Syncing to GitHub Database..."):
                    # Check if client exists, update or append
                    new_client_data = {"name": new_name, "siem": new_siem, "logs": new_logs}
                    db["customers"] = [c for c in clients if c["name"] != new_name]
                    db["customers"].append(new_client_data)
                    
                    # Push back to GitHub
                    repo.update_file(
                        db_file.path, 
                        f"Admin: Synced {new_name}", 
                        json.dumps(db, indent=4), 
                        db_file.sha
                    )
                    st.success(f"Successfully deployed and saved environment for {new_name}")
                    st.rerun()
            else:
                st.error("Please fill in all fields.")

    st.subheader("Existing Organizations")
    if not clients:
        st.info("No clients registered yet.")
    for c in clients:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            col1.write(f"**{c['name']}** ({c['siem']})")
            col1.caption(f"Sources: {c['logs']}")
            if col2.button("Delete", key=c['name']):
                db["customers"] = [cust for cust in clients if cust["name"] != c["name"]]
                repo.update_file(
                    db_file.path, 
                    f"Admin: Deleted {c['name']}", 
                    json.dumps(db, indent=4), 
                    db_file.sha
                )
                st.rerun()

# --- CUSTOMER PORTAL ---
elif page == "Customer Portal":
    st.header("🔍 Customer Portal: SOP Architect")
    
    if not clients:
        st.warning("No organizations available. Please ask your Vendor Admin to register a client.")
    else:
        col_in, col_out = st.columns([1, 1.5])
        
        with col_in:
            st.subheader("1. Select Context")
            client_names = [c['name'] for c in clients]
            selected_client_name = st.selectbox("Organization", client_names)
            
            client_data = next(c for c in clients if c['name'] == selected_client_name)
            st.info(f"**SIEM:** {client_data['siem']}\n\n**Log Sources:** {client_data['logs']}")
            
            st.subheader("2. Detection Logic")
            raw_logic = st.text_area("Paste Query (KQL/SPL/Sigma):", height=200)
            
            generate_btn = st.button("Build SOP", type="primary", use_container_width=True)

        with col_out:
            st.subheader("Automated Triage Plan")
            if generate_btn:
                if not raw_logic:
                    st.warning("Please provide detection logic.")
                else:
                    with st.spinner("AI Architect is analyzing..."):
                        sop_result = generate_sop(
                            client_data['name'], 
                            client_data['siem'], 
                            client_data['logs'], 
                            raw_logic
                        )
                        
                        if show_debug:
                            st.code(sop_result)

                        parts = sop_result.split("```")
                        mermaid_code = ""
                        clean_text = sop_result
                        
                        for part in parts:
                            if part.strip().lower().startswith("mermaid"):
                                mermaid_code = part.strip()[7:].strip()
                                clean_text = clean_text.replace(f"```{part}```", "")
                        
                        st.markdown(clean_text)
                        
                        if mermaid_code:
                            st.markdown("### Visual Decision Tree")
                            import streamlit.components.v1 as components
                            mermaid_html = f"""
                            <div class="mermaid" style="background-color:white; padding:20px; border-radius:10px;">
                            {mermaid_code}
                            </div>
                            <script src="[https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js](https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js)"></script>
                            <script>mermaid.initialize({{startOnLoad:true}});</script>
                            """
                            components.html(mermaid_html, height=500, scrolling=True)
