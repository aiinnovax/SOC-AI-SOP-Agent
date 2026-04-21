import streamlit as st
import json
from github import Github
from llm_router import generate_sop

st.set_page_config(page_title="Customer Portal", layout="wide")

# --- GITHUB DATABASE SETUP ---
@st.cache_resource
def get_github_repo():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        return g.get_repo(st.secrets["REPO_PATH"])
    except Exception as e:
        st.error("Cloud database connection failed.")
        st.stop()

repo = get_github_repo()

def get_db():
    file_content = repo.get_contents("database.json")
    return json.loads(file_content.decoded_content.decode())

db = get_db()
clients = db.get("customers", [])

st.title("🔍 Customer Portal: SOP Architect")

if not clients:
    st.warning("No organizations available. Please ask AIInnovax support to register your environment.")
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
                    sop_result = generate_sop(client_data['name'], client_data['siem'], client_data['logs'], raw_logic)
                    
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
