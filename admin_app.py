import streamlit as st
import json
import time

# --- 1. CONFIG & REACT-STYLE CSS ---
st.set_page_config(page_title="Central Command Console", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* Mimic index.css and React Tailwind styling */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;700;900&display=swap');
    
    .stApp { background-color: #f8fafc; font-family: 'Inter', sans-serif; color: #0f172a; }
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e2e8f0; }
    [data-testid="stSidebarNav"] { display: none; } /* Hide default nav */
    
    /* Typography Utilities */
    .font-black { font-weight: 900; }
    .tracking-widest { letter-spacing: 0.2em; }
    .uppercase { text-transform: uppercase; }
    
    /* Dashboard Widgets */
    .react-widget {
        background-color: white; border: 1px solid #f1f5f9; border-radius: 2.5rem;
        padding: 2rem; text-align: center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        transition: all 0.3s ease;
    }
    .react-widget:hover { border-color: #e9d5ff; transform: translateY(-2px); }
    
    /* System Health & Support Box */
    .health-box { background-color: white; border: 1px solid #f1f5f9; border-radius: 3rem; padding: 2rem; text-align: center; }
    .support-box { background-color: #0f172a; color: white; border-radius: 3.5rem; padding: 2.5rem; position: relative; }
    .support-item { background-color: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 2rem; padding: 1.5rem; margin-bottom: 1rem; }
    
    /* Nav Buttons */
    .nav-btn {
        display: block; width: 100%; padding: 1rem; margin-bottom: 0.5rem;
        background-color: transparent; border: none; border-radius: 1rem;
        color: #64748b; font-weight: 900; font-size: 11px; letter-spacing: 0.1em;
        text-transform: uppercase; text-align: left; cursor: pointer;
    }
    
    /* Hide top header */
    header { visibility: hidden; }
    </style>
""", unsafe_allow_html=True)

# --- 2. MOCK DATABASE (Replaces Firebase logic from App.tsx) ---
# In production, you would load this from your GitHub database.json
if 'db' not in st.session_state:
    st.session_state.db = {
        "users": [
            {"uid": "usr_1", "email": "admin@infosys.com", "plan": "Enterprise", "seats": 50, "quota": 450, "status": "active"},
            {"uid": "usr_2", "email": "secops@acme.com", "plan": "Pro", "seats": 10, "quota": 120, "status": "active"},
            {"uid": "usr_3", "email": "trial@startup.io", "plan": "Free", "seats": 1, "quota": 5, "status": "suspended"}
        ],
        "sops": [
            {"id": "sop_001", "title": "Ransomware Containment", "customer": "Infosys", "date": "2026-04-21", "tokens": 1240},
            {"id": "sop_002", "title": "Phishing Triage Pipeline", "customer": "Infosys", "date": "2026-04-20", "tokens": 850},
            {"id": "sop_003", "title": "Failed Logon Anomaly", "customer": "Acme Corp", "date": "2026-04-19", "tokens": 600}
        ]
    }

# --- 3. STATE MANAGEMENT ---
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 'command'
if 'selected_user' not in st.session_state:
    st.session_state.selected_user = None

def switch_tab(tab):
    st.session_state.active_tab = tab

# --- 4. SIDEBAR (Mimics App.tsx RailNavItem) ---
with st.sidebar:
    st.markdown("<div style='text-align:center; padding: 20px 0;'><h2 class='font-black tracking-widest uppercase' style='font-size:12px; color:#0f172a;'>AIINNOVAX</h2></div>", unsafe_allow_html=True)
    st.write("---")
    
    # Custom Sidebar Navigation
    st.button("⚡ COMMAND PAGE", on_click=switch_tab, args=('command',), use_container_width=True, type="primary" if st.session_state.active_tab == 'command' else "secondary")
    st.button("🪪 USER LICENSE", on_click=switch_tab, args=('license',), use_container_width=True, type="primary" if st.session_state.active_tab == 'license' else "secondary")
    st.button("📂 SOP REPOSITORY", on_click=switch_tab, args=('repository',), use_container_width=True, type="primary" if st.session_state.active_tab == 'repository' else "secondary")
    
    st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
    st.button("⏏ EXIT TO EDITOR", use_container_width=True)

# --- 5. TOP HEADER (Mimics CentralCommandConsole.tsx Header) ---
h1, h2 = st.columns([3, 1])
with h1:
    st.markdown(f"<div style='padding: 1rem 2rem;'><span style='background:#ecfdf5; color:#059669; padding: 5px 15px; border-radius:10px; font-size:10px;' class='font-black tracking-widest uppercase'>● Administrative Persistence: 100%</span></div>", unsafe_allow_html=True)
with h2:
    st.markdown("<div style='padding: 1rem; text-align:right;' class='font-black uppercase text-slate-400' style='font-size:10px;'>aiinnovax@gmail.com</div>", unsafe_allow_html=True)

# --- 6. TABS LOGIC ---

if st.session_state.active_tab == 'command':
    st.markdown("<div style='padding: 0 2rem;'>", unsafe_allow_html=True)
    
    # Analytics Widgets
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(f"<div class='react-widget'><div style='font-size:2rem;' class='font-black'>{len(st.session_state.db['users'])}</div><div style='font-size:10px; color:#94a3b8;' class='font-black tracking-widest uppercase'>Total Customers</div></div>", unsafe_allow_html=True)
    with m2:
        st.markdown(f"<div class='react-widget'><div style='font-size:2rem;' class='font-black'>{len(st.session_state.db['sops'])}</div><div style='font-size:10px; color:#94a3b8;' class='font-black tracking-widest uppercase'>SOP Count</div></div>", unsafe_allow_html=True)
    with m3:
        st.markdown("<div class='react-widget'><div style='font-size:2rem;' class='font-black'>575</div><div style='font-size:10px; color:#94a3b8;' class='font-black tracking-widest uppercase'>Gemini 3 Reqs</div></div>", unsafe_allow_html=True)
    with m4:
        st.markdown("<div class='react-widget'><div style='font-size:2rem;' class='font-black'>42.5K</div><div style='font-size:10px; color:#94a3b8;' class='font-black tracking-widest uppercase'>Tokens Used</div></div>", unsafe_allow_html=True)

    st.write("<br>", unsafe_allow_html=True)

    # Health & Support
    s1, s2 = st.columns([1, 2])
    with s1:
        st.markdown("""
            <div class='health-box'>
                <p style='font-size:10px; color:#94a3b8;' class='font-black tracking-widest uppercase'>System Health Status</p>
                <div style='font-size:2rem; color:#0f172a;' class='font-black uppercase'>OPERATIONAL</div>
                <p style='font-size:9px; color:#10b981;' class='font-black tracking-widest uppercase'>Latency: 42ms // Green Level</p>
                <hr style='border:none; border-top:1px solid #f1f5f9; margin: 20px 0;'>
                <div style='display:flex; justify-content:space-between; font-size:9px;' class='font-black uppercase'>
                    <span style='color:#10b981'>● SOP Engine</span>
                    <span style='color:#10b981'>● Auth Node</span>
                    <span style='color:#fbbf24'>● Matrix Sync</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    with s2:
        st.markdown("""
            <div class='support-box'>
                <p style='font-size:10px; color:#64748b;' class='font-black tracking-widest uppercase'>Priority Support Queue</p>
                <h3 style='font-size:1.2rem; font-style:italic;' class='font-black uppercase mb-4'>Customer Incident Queries</h3>
                <div class='support-item'>
                    <div style='font-size:12px;' class='font-black uppercase'>TechCorp Industries</div>
                    <div style='font-size:9px; color:#64748b;' class='font-black tracking-widest uppercase'>SOP Export logic bypass on Edge</div>
                </div>
                <div class='support-item'>
                    <div style='font-size:12px;' class='font-black uppercase'>BioLink Systems</div>
                    <div style='font-size:9px; color:#64748b;' class='font-black tracking-widest uppercase'>Intelligence core latency spike</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.active_tab == 'license':
    st.markdown("<div style='padding: 0 2rem;'>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2.5])
    
    with c1:
        st.markdown("<p style='font-size:10px; color:#94a3b8;' class='font-black tracking-widest uppercase'>User Authorization Registry</p>", unsafe_allow_html=True)
        for user in st.session_state.db['users']:
            if st.button(f"{user['email']}\n({user['plan']} Node)", key=user['uid'], use_container_width=True):
                st.session_state.selected_user = user

    with c2:
        if st.session_state.selected_user:
            u = st.session_state.selected_user
            st.markdown(f"""
                <div style='background:white; border:1px solid #f1f5f9; border-radius:3rem; padding:3rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);'>
                    <div style='display:inline-block; background:#0f172a; color:white; padding:5px 15px; border-radius:10px; font-size:9px;' class='font-black tracking-widest uppercase'>Verified Entity</div>
                    <h2 style='font-size:2rem; margin-top:10px;' class='font-black uppercase text-slate-900'>{u['email']}</h2>
                    <p style='font-size:10px; color:#94a3b8;' class='font-black tracking-widest uppercase mb-4'>Universal Identifier: {u['uid']}</p>
                    <hr style='border:none; border-top:1px solid #f1f5f9; margin: 20px 0;'>
                </div>
            """, unsafe_allow_html=True)
            
            # Interactive Controls
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                st.markdown("<p style='font-size:9px; color:#94a3b8;' class='font-black tracking-widest uppercase'>Allocation Tier</p>", unsafe_allow_html=True)
                st.selectbox("Tier", ["Free", "Pro", "Enterprise"], index=["Free", "Pro", "Enterprise"].index(u['plan']), label_visibility="collapsed")
            with sc2:
                st.markdown("<p style='font-size:9px; color:#94a3b8;' class='font-black tracking-widest uppercase'>Node Capacity</p>", unsafe_allow_html=True)
                st.number_input("Seats", value=u['seats'], label_visibility="collapsed")
            with sc3:
                st.markdown("<p style='font-size:9px; color:#94a3b8;' class='font-black tracking-widest uppercase'>Status Control</p>", unsafe_allow_html=True)
                st.button("Re-Authorize" if u['status'] == 'suspended' else "Suspend", type="primary", use_container_width=True)
        else:
            st.info("Select a user from the registry to view details.")
    st.markdown("</div>", unsafe_allow_html=True)

elif st.session_state.active_tab == 'repository':
    st.markdown("<div style='padding: 0 2rem;'>", unsafe_allow_html=True)
    st.markdown("""
        <div style='background:white; border:1px solid #f1f5f9; border-radius:3rem; padding:3rem; text-align:center; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 2rem;'>
            <h3 style='font-size:1.5rem;' class='font-black uppercase text-slate-900'>SOP Repository Hub</h3>
            <p style='font-size:11px; color:#94a3b8;' class='font-black tracking-widest uppercase italic'>Organizational procedure retrieval subsystem.</p>
        </div>
    """, unsafe_allow_html=True)

    # SOP Grid (Mimics SOPGroup in React)
    for sop in st.session_state.db['sops']:
        st.markdown(f"""
            <div style='background:white; border:1px solid #f1f5f9; border-radius:2.5rem; padding:2rem; margin-bottom: 1rem; box-shadow: 0 2px 4px rgba(0,0,0,0.02);'>
                <div style='display:flex; justify-content:space-between; margin-bottom: 1rem;'>
                    <span style='background:#faf5ff; color:#9333ea; padding:5px 10px; border-radius:8px; font-size:9px;' class='font-black tracking-widest uppercase'>PID: {sop['id']}</span>
                    <span style='color:#94a3b8; font-size:9px;' class='font-black tracking-widest uppercase'>{sop['date']}</span>
                </div>
                <h4 style='font-size:1.2rem; color:#0f172a;' class='font-black uppercase'>{sop['title']}</h4>
                <div style='margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #f8fafc; font-size:8px; color:#cbd5e1;' class='font-black uppercase italic'>
                    {sop['customer']} // {sop['tokens']} Unified Tokens
                </div>
            </div>
        """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
