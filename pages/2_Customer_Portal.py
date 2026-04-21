import streamlit as st
from google.cloud import firestore
import json
from llm_router import generate_sop

db = firestore.Client.from_service_account_info(json.loads(st.secrets["firebase"]["service_account"]))

st.title("🔍 SOC Mission Control")

# 1. AUTH SYNC: Get specific client data from Firebase
# In Phase 2, this will filter based on the logged-in user's email
clients_ref = db.collection("customers").stream()
client_map = {c.id: c.to_dict() for c in clients_ref}

selected_org = st.selectbox("Select Organization", list(client_map.keys()))
config = client_map[selected_org]

st.info(f"Connected to {config['siem']} | Context: {config['logs']}")

# 2. SOP GENERATION
logic = st.text_area("Paste Detection Logic")
if st.button("Generate SOP"):
    result = generate_sop(config['name'], config['siem'], config['logs'], logic)
    st.markdown(result)
    
    # 3. SYNC BACK: Store in Firebase for Admin Audit
    db.collection("sops").add({
        "client": config['name'],
        "content": result,
        "timestamp": firestore.SERVER_TIMESTAMP
    })
