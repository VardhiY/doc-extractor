import streamlit as st
from groq import Groq
import json, re, base64, io

st.set_page_config(page_title="DocuAI", page_icon="⚡", layout="wide")

try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client  = Groq(api_key=API_KEY)
except:
    st.error("Add GROQ_API_KEY to Streamlit Secrets.")
    st.stop()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Fira+Code:wght@400;500&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }

#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"]
{ display:none !important; }
[data-testid="collapsedControl"] { display:flex !important; }

/* ═══ ROOT BACKGROUND ═══ */
.stApp {
    background: #080c0f;
    background-image:
        radial-gradient(ellipse 60% 40% at 100% 0%, rgba(180,255,50,0.06) 0%, transparent 55%),
        radial-gradient(ellipse 50% 40% at 0% 100%, rgba(180,255,50,0.04) 0%, transparent 50%);
}

/* ═══ SIDEBAR ═══ */
section[data-testid="stSidebar"] {
    background: #0b0f12 !important;
    border-right: 1px solid rgba(180,255,50,0.08) !important;
    width: 260px !important;
}
section[data-testid="stSidebar"] > div { padding: 0 !important; }

.sb-top {
    padding: 2rem 1.4rem 1.4rem;
    border-bottom: 1px solid rgba(255,255,255,0.04);
}
.sb-logo-row { display:flex; align-items:center; gap:0.6rem; margin-bottom:0.3rem; }
.sb-icon {
    width:34px; height:34px; border-radius:9px;
    background: #b4ff32; display:flex; align-items:center;
    justify-content:center; font-size:1rem; flex-shrink:0;
}
.sb-brand { font-size:1.1rem; font-weight:800; color:#fff; letter-spacing:-0.02em; }
.sb-version { font-family:'Fira Code',monospace; font-size:0.6rem; color:rgba(255,255,255,0.18); letter-spacing:0.08em; }

.sb-section { padding:1.3rem 1.4rem; border-bottom:1px solid rgba(255,255,255,0.04); }
.sb-section-label {
    font-size:0.58rem; font-weight:700; letter-spacing:0.2em;
    text-transform:uppercase; color:rgba(255,255,255,0.2); margin-bottom:1rem;
}

section[data-testid="stSidebar"] .stCheckbox > label {
    font-family:'Inter',sans-serif !important;
    font-size:0.82rem !important; font-weight:500 !important;
    color:rgba(255,255,255,0.4) !important; transition:color 0.2s !important;
    gap:0.6rem !important;
}
section[data-testid="stSidebar"] .stCheckbox > label:hover { color:rgba(255,255,255,0.85) !important; }
section[data-testid="stSidebar"] .stCheckbox input:checked + div { background:#b4ff32 !important; border-color:#b4ff32 !important; }

.sb-stat-row { display:grid; grid-template-columns:1fr 1fr; gap:0.6rem; margin-top:0.3rem; }
.sb-stat {
    background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06);
    border-radius:10px; padding:0.7rem; text-align:center;
}
.sb-stat-num { font-size:1.3rem; font-weight:800; color:#b4ff32; line-height:1; }
.sb-stat-lbl { font-size:0.55rem; font-weight:600; letter-spacing:0.12em; text-transform:uppercase; color:rgba(255,255,255,0.2); margin-top:0.25rem; }

.sb-footer { padding:1.2rem 1.4rem; font-family:'Fira Code',monospace; font-size:0.58rem; color:rgba(255,255,255,0.1); line-height:1.8; }

/* ═══ MAIN CONTENT ═══ */
.main-wrap { padding:2rem 2.5rem; }

/* ═══ TOP NAV ═══ */
.top-nav {
    display:flex; align-items:center; justify-content:space-between;
    margin-bottom:2.5rem;
}
.nav-tabs { display:flex; gap:0.3rem; background:rgba(255,255,255,0.04); padding:0.3rem; border-radius:10px; }
.nav-tab {
    font-size:0.75rem; font-weight:600; padding:0.4rem 1rem;
    border-radius:7px; color:rgba(255,255,255,0.35); cursor:pointer;
    transition:all 0.2s; border:none; background:transparent;
}
.nav-tab.active { background:rgba(180,255,50,0.12); color:#b4ff32; }

.nav-status { display:flex; align-items:center; gap:0.5rem; }
.status-dot { width:7px; height:7px; border-radius:50%; background:#b4ff32; box-shadow:0 0 8px #b4ff32; animation:glow 2s infinite; }
@keyframes glow { 0%,100%{box-shadow:0 0 6px #b4ff32;} 50%{box-shadow:0 0 18px #b4ff32,0 0 35px rgba(180,255,50,0.3);} }
.status-text { font-size:0.72rem; font-weight:600; color:rgba(255,255,255,0.35); }

/* ═══ HERO ═══ */
.hero { margin-bottom:2.5rem; }
.hero-label {
    font-size:0.65rem; font-weight:700; letter-spacing:0.2em;
    text-transform:uppercase; color:#b4ff32; margin-bottom:0.8rem;
}
.hero-h1 {
    font-size:clamp(2.8rem,4.5vw,4.8rem); font-weight:900;
    letter-spacing:-0.04em; line-height:1.0; color:#fff; margin-bottom:0.5rem;
}
.hero-h1 em {
    font-style:normal;
    background:linear-gradient(90deg,#b4ff32,#4ade80);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.hero-sub { font-size:0.95rem; color:rgba(255,255,255,0.3); font-weight:400; line-height:1.6; max-width:520px; }

/* ═══ CARD GRID ═══ */
.card-grid { display:grid; grid-template-columns:1.1fr 0.9fr; gap:1.2rem; margin-bottom:1.2rem; }

/* ═══ CARDS ═══ */
.card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px; overflow:hidden;
    backdrop-filter: blur(20px);
    transition: border-color 0.3s, transform 0.2s;
    position: relative;
}
.card:hover { border-color:rgba(180,255,50,0.2); transform:translateY(-1px); }
.card::after {
    content:''; position:absolute; top:0; left:0; right:0; height:1px;
    background:linear-gradient(90deg,transparent,rgba(180,255,50,0.3),transparent);
}

.card-head {
    display:flex; align-items:center; justify-content:space-between;
    padding:1.2rem 1.5rem;
    border-bottom:1px solid rgba(255,255,255,0.05);
}
.card-head-left { display:flex; align-items:center; gap:0.75rem; }
.card-ico {
    width:38px; height:38px; border-radius:11px;
    display:flex; align-items:center; justify-content:center; font-size:1.05rem;
}
.ico-green { background:rgba(180,255,50,0.12); border:1px solid rgba(180,255,50,0.2); }
.ico-white { background:rgba(255,255,255,0.06); border:1px solid rgba(255,255,255,0.1); }

.card-title { font-size:0.85rem; font-weight:700; color:#fff; letter-spacing:-0.01em; }
.card-desc  { font-size:0.65rem; color:rgba(255,255,255,0.25); margin-top:0.1rem; }
.card-badge {
    font-family:'Fira Code',monospace; font-size:0.58rem; font-weight:500;
    padding:0.2rem 0.6rem; border-radius:6px; letter-spacing:0.05em;
}
.badge-green { background:rgba(180,255,50,0.1); border:1px solid rgba(180,255,50,0.2); color:#b4ff32; }
.badge-dim   { background:rgba(255,255,255,0.05); border:1px solid rgba(255,255,255,0.08); color:rgba(255,255,255,0.3); }
.card-body { padding:1.4rem 1.5rem; }

/* ═══ UPLOAD ═══ */
.upload-drop {
    border:1.5px dashed rgba(180,255,50,0.2); border-radius:14px;
    background:rgba(180,255,50,0.02);
    transition:all 0.3s; position:relative; overflow:hidden;
}
.upload-drop:hover { border-color:rgba(180,255,50,0.45); background:rgba(180,255,50,0.05); }
div[data-testid="stFileUploader"] { background:transparent !important; border:none !important; }
div[data-testid="stFileUploadDropzone"] {
    background:transparent !important; border:none !important;
    padding:2.2rem 1rem !important; text-align:center;
}
div[data-testid="stFileUploadDropzone"] p { color:rgba(255,255,255,0.2) !important; font-size:0.88rem !important; }
div[data-testid="stFileUploadDropzone"] small { color:rgba(255,255,255,0.1) !important; }

.file-pill {
    display:flex; align-items:center; gap:0.75rem;
    background:rgba(180,255,50,0.06); border:1px solid rgba(180,255,50,0.15);
    border-radius:12px; padding:0.75rem 1rem; margin-top:0.8rem;
    animation:slideup 0.35s ease;
}
@keyframes slideup { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
.fp-name { font-family:'Fira Code',monospace; font-size:0.73rem; color:#b4ff32; flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.fp-tag  { font-family:'Fira Code',monospace; font-size:0.6rem; padding:0.15rem 0.5rem; border-radius:5px; background:rgba(255,255,255,0.06); color:rgba(255,255,255,0.3); }

/* ═══ FORMAT PILLS ═══ */
.fmt-row { display:flex; flex-wrap:wrap; gap:0.4rem; margin-bottom:1rem; }
.fmt {
    font-family:'Fira Code',monospace; font-size:0.58rem; font-weight:500;
    padding:0.2rem 0.6rem; border-radius:5px; letter-spacing:0.05em;
}
.f1{background:rgba(248,113,113,0.08);border:1px solid rgba(248,113,113,0.2);color:#f87171;}
.f2{background:rgba(96,165,250,0.08);border:1px solid rgba(96,165,250,0.2);color:#60a5fa;}
.f3{background:rgba(167,139,250,0.08);border:1px solid rgba(167,139,250,0.2);color:#a78bfa;}
.f4{background:rgba(52,211,153,0.08);border:1px solid rgba(52,211,153,0.2);color:#34d399;}
.f5{background:rgba(251,191,36,0.08);border:1px solid rgba(251,191,36,0.2);color:#fbbf24;}

/* ═══ TAB BUTTONS ═══ */
div[data-testid="stHorizontalBlock"] .stButton > button {
    background: rgba(255,255,255,0.04) !important;
    color: rgba(255,255,255,0.4) !important;
    font-size: 0.75rem !important; font-weight: 600 !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
    border-radius: 8px !important; padding: 0.45rem 0.5rem !important;
    box-shadow: none !important; margin-top: 0 !important;
}
div[data-testid="stHorizontalBlock"] .stButton > button:hover {
    background: rgba(180,255,50,0.08) !important;
    border-color: rgba(180,255,50,0.2) !important;
    color: #b4ff32 !important; transform: none !important;
    box-shadow: none !important;
}
div[data-testid="stHorizontalBlock"] .stButton > button[kind="primary"] {
    background: rgba(180,255,50,0.12) !important;
    border-color: rgba(180,255,50,0.3) !important;
    color: #b4ff32 !important;
}

/* ═══ MAIN EXTRACT BUTTON ═══ */
.stButton > button {
    width:100% !important; margin-top:1rem !important;
    background:#b4ff32 !important; color:#080c0f !important;
    font-family:'Inter',sans-serif !important; font-weight:800 !important;
    font-size:0.9rem !important; border:none !important;
    border-radius:12px !important; padding:0.85rem !important;
    letter-spacing:0.01em !important; transition:all 0.3s !important;
    box-shadow:0 0 30px rgba(180,255,50,0.2) !important;
}
.stButton > button:hover {
    background:#c8ff50 !important;
    box-shadow:0 0 50px rgba(180,255,50,0.4), 0 4px 20px rgba(0,0,0,0.3) !important;
    transform:translateY(-2px) !important;
}

/* ═══ SHIELD ITEMS ═══ */
.shield-list { display:flex; flex-direction:column; gap:0.5rem; }
.shield-item {
    display:flex; align-items:center; justify-content:space-between;
    padding:0.65rem 0.9rem; border-radius:10px;
    border:1px solid rgba(255,255,255,0.05);
    background:rgba(255,255,255,0.02); transition:all 0.2s;
}
.shield-item.on { background:rgba(180,255,50,0.06); border-color:rgba(180,255,50,0.15); }
.shield-label { font-size:0.78rem; font-weight:500; color:rgba(255,255,255,0.35); }
.shield-item.on .shield-label { color:rgba(255,255,255,0.75); }
.shield-toggle {
    width:28px; height:16px; border-radius:8px; position:relative;
    background:rgba(255,255,255,0.08); flex-shrink:0;
    transition:background 0.2s;
}
.shield-toggle.on { background:rgba(180,255,50,0.3); }
.shield-toggle::after {
    content:''; position:absolute; top:2px; left:2px;
    width:12px; height:12px; border-radius:50%;
    background:rgba(255,255,255,0.3); transition:all 0.2s;
}
.shield-toggle.on::after { left:14px; background:#b4ff32; box-shadow:0 0 6px rgba(180,255,50,0.5); }

/* ═══ RESULT AREA ═══ */
.result-card {
    background:rgba(255,255,255,0.02);
    border:1px solid rgba(255,255,255,0.07); border-radius:20px;
    overflow:hidden; animation:cardin 0.5s ease;
    position:relative;
}
.result-card::after {
    content:''; position:absolute; top:0; left:0; right:0; height:1px;
    background:linear-gradient(90deg,transparent,rgba(180,255,50,0.4),transparent);
}
@keyframes cardin { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:translateY(0)} }

.rc-header {
    display:flex; align-items:center; justify-content:space-between;
    padding:1rem 1.5rem;
    background:rgba(180,255,50,0.03);
    border-bottom:1px solid rgba(255,255,255,0.05);
}
.rc-title { font-size:0.7rem; font-weight:700; letter-spacing:0.15em; text-transform:uppercase; color:rgba(255,255,255,0.3); }
.rc-meta  { font-family:'Fira Code',monospace; font-size:0.62rem; color:#b4ff32; }
.rc-body  {
    padding:1.5rem; font-family:'Fira Code',monospace; font-size:0.78rem;
    line-height:2; color:rgba(255,255,255,0.45);
    white-space:pre-wrap; word-break:break-word;
    max-height:380px; overflow-y:auto;
}
.rc-body::-webkit-scrollbar { width:3px; }
.rc-body::-webkit-scrollbar-thumb { background:rgba(180,255,50,0.25); border-radius:2px; }

/* ═══ STATS ═══ */
.stat-strip { display:grid; grid-template-columns:repeat(3,1fr); gap:0.8rem; margin:1.2rem 0; }
.stat-box {
    background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06);
    border-radius:14px; padding:1.1rem 0.9rem; text-align:center;
    position:relative; overflow:hidden; animation:statpop 0.4s ease backwards;
}
.stat-box:nth-child(1){animation-delay:0.05s}
.stat-box:nth-child(2){animation-delay:0.12s}
.stat-box:nth-child(3){animation-delay:0.2s}
@keyframes statpop { from{opacity:0;transform:scale(0.92)} to{opacity:1;transform:scale(1)} }
.stat-box::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; }
.sb-g::before { background:linear-gradient(90deg,#b4ff32,#4ade80); }
.sb-w::before { background:linear-gradient(90deg,rgba(255,255,255,0.3),rgba(255,255,255,0.1)); }
.sb-ok::before{ background:linear-gradient(90deg,#b4ff32,#4ade80); }
.sb-wr::before{ background:linear-gradient(90deg,#fb923c,#f87171); }

.sn { font-family:'Fira Code',monospace; font-size:1.9rem; font-weight:500; color:#fff; line-height:1; }
.sb-g  .sn { color:#b4ff32; }
.sb-w  .sn { color:#fff; }
.sb-ok .sn { color:#b4ff32; font-size:0.95rem; padding-top:0.4rem; }
.sb-wr .sn { color:#fb923c; font-size:0.95rem; padding-top:0.4rem; }
.sl { font-size:0.57rem; font-weight:700; letter-spacing:0.15em; text-transform:uppercase; color:rgba(255,255,255,0.2); margin-top:0.4rem; }

/* ═══ TAGS ═══ */
.tag-row { display:flex; flex-wrap:wrap; gap:0.4rem; margin:0.8rem 0 1.2rem; }
.rtag { font-family:'Fira Code',monospace; font-size:0.6rem; padding:0.2rem 0.6rem; border-radius:6px; background:rgba(251,146,60,0.08); border:1px solid rgba(251,146,60,0.2); color:#fb923c; }

/* ═══ DOWNLOAD ═══ */
.stDownloadButton > button {
    background:rgba(255,255,255,0.04) !important;
    border:1px solid rgba(255,255,255,0.08) !important;
    color:rgba(255,255,255,0.35) !important;
    font-family:'Inter',sans-serif !important; font-size:0.8rem !important;
    font-weight:600 !important; border-radius:10px !important;
    padding:0.65rem 1rem !important; width:100% !important; transition:all 0.25s !important;
}
.stDownloadButton > button:hover {
    background:rgba(180,255,50,0.08) !important;
    border-color:rgba(180,255,50,0.25) !important;
    color:#b4ff32 !important;
}

/* ═══ DIVIDER ═══ */
.g-line { height:1px; background:linear-gradient(90deg,transparent,rgba(180,255,50,0.25),transparent); margin:1.5rem 0; }

div[data-testid="stSelectbox"] > div { background:rgba(255,255,255,0.04) !important; border:1px solid rgba(255,255,255,0.08) !important; color:#fff !important; border-radius:10px !important; }
</style>
""", unsafe_allow_html=True)

# ══ SIDEBAR ══════════════════════════════════════════════════════════
st.sidebar.markdown("""
<div class="sb-top">
    <div class="sb-logo-row">
        <div class="sb-icon">⚡</div>
        <div>
            <div class="sb-brand">DocuAI</div>
            <div class="sb-version">v2.0 · enterprise</div>
        </div>
    </div>
</div>
<div class="sb-section">
    <div class="sb-section-label">Privacy Shield</div>
</div>
""", unsafe_allow_html=True)

redact_ids       = st.sidebar.checkbox("🪪  Aadhaar · SSN · PAN",      value=True)
redact_phones    = st.sidebar.checkbox("📞  Phone & Email",             value=True)
redact_banking   = st.sidebar.checkbox("💳  Bank · Cards · UPI",       value=True)
redact_passwords = st.sidebar.checkbox("🔑  Passwords · Keys",         value=True)
redact_names     = st.sidebar.checkbox("👤  Personal Names",            value=True)
redact_dates     = st.sidebar.checkbox("📅  Dates of Birth",            value=True)

st.sidebar.markdown("""<div class="sb-section"><div class="sb-section-label">Output</div></div>""", unsafe_allow_html=True)
show_redacted = st.sidebar.checkbox("Show [REDACTED] tags", value=True)

active = sum([redact_ids,redact_phones,redact_banking,redact_passwords,redact_names,redact_dates])
st.sidebar.markdown(f"""
<div class="sb-section">
    <div class="sb-section-label">Shield Status</div>
    <div class="sb-stat-row">
        <div class="sb-stat"><div class="sb-stat-num">{active}</div><div class="sb-stat-lbl">Active</div></div>
        <div class="sb-stat"><div class="sb-stat-num">{6-active}</div><div class="sb-stat-lbl">Inactive</div></div>
    </div>
</div>
<div class="sb-footer">
    Powered by Groq<br>
    LLaMA 4 Vision · LLaMA 3.1<br>
    AI + Regex dual-layer<br>
    © 2025 DocuAI
</div>
""", unsafe_allow_html=True)

# ══ MAIN ═════════════════════════════════════════════════════════════
st.markdown('<div class="main-wrap">', unsafe_allow_html=True)

# Top nav
if "active_tab" not in st.session_state:
    st.session_state.active_tab = "Extract"
if "history" not in st.session_state:
    st.session_state.history = []

tab_col1, tab_col2, tab_col3, _, status_col = st.columns([1.2, 1.2, 1.2, 5, 2.5])
with tab_col1:
    if st.button("⚡ Extract", use_container_width=True,
                 type="primary" if st.session_state.active_tab=="Extract" else "secondary"):
        st.session_state.active_tab = "Extract"
with tab_col2:
    if st.button("🕓 History", use_container_width=True,
                 type="primary" if st.session_state.active_tab=="History" else "secondary"):
        st.session_state.active_tab = "History"
with tab_col3:
    if st.button("⚙️ Settings", use_container_width=True,
                 type="primary" if st.session_state.active_tab=="Settings" else "secondary"):
        st.session_state.active_tab = "Settings"
with status_col:
    st.markdown("""
    <div class="nav-status" style="justify-content:flex-end;padding-top:0.4rem">
        <div class="status-dot"></div>
        <div class="status-text">AI Engine Online</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="g-line"></div>', unsafe_allow_html=True)

# ── HISTORY TAB ───────────────────────────────────────────────────────
if st.session_state.active_tab == "History":
    st.markdown("""
    <div class="hero" style="margin-bottom:1.2rem">
        <div class="hero-label">🕓 Extraction History</div>
        <div class="hero-h1" style="font-size:2.5rem">Recent <em>Sessions</em></div>
    </div>
    """, unsafe_allow_html=True)
    if not st.session_state.history:
        st.markdown("""
        <div class="card" style="text-align:center;padding:3rem">
            <div style="font-size:2.5rem;margin-bottom:1rem">📂</div>
            <div style="color:rgba(255,255,255,0.3);font-size:0.9rem">No extraction history yet.<br>Upload a document to get started.</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        for h in st.session_state.history:
            color = "#b4ff32" if h["status"]=="CLEAN" else "#fb923c"
            st.markdown(f"""
            <div class="card" style="margin-bottom:0.8rem;padding:1rem 1.5rem">
                <div style="display:flex;align-items:center;justify-content:space-between">
                    <div>
                        <div style="font-size:0.82rem;font-weight:700;color:#fff">📎 {h['name']}</div>
                        <div style="font-size:0.65rem;color:rgba(255,255,255,0.25);margin-top:0.2rem;font-family:Fira Code,monospace">{h['words']:,} words · {h['redacted']} redacted · {h['time']}</div>
                    </div>
                    <div style="font-family:Fira Code,monospace;font-size:0.72rem;color:{color};background:rgba(255,255,255,0.05);padding:0.3rem 0.8rem;border-radius:8px;border:1px solid {color}33">{h['status']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.history = []
            st.rerun()
    st.stop()

# ── SETTINGS TAB ──────────────────────────────────────────────────────
if st.session_state.active_tab == "Settings":
    st.markdown("""
    <div class="hero" style="margin-bottom:1.2rem">
        <div class="hero-label">⚙️ Configuration</div>
        <div class="hero-h1" style="font-size:2.5rem">App <em>Settings</em></div>
    </div>
    """, unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="card" style="padding:1.5rem">
            <div class="card-title" style="margin-bottom:1rem">🤖 AI Model Info</div>
        """, unsafe_allow_html=True)
        st.markdown("""
        <div class="shield-list">
            <div class="shield-item on"><span class="shield-label">Extraction Model</span><span style="font-family:Fira Code,monospace;font-size:0.62rem;color:#b4ff32">LLaMA 4 Scout Vision</span></div>
            <div class="shield-item on"><span class="shield-label">Redaction Model</span><span style="font-family:Fira Code,monospace;font-size:0.62rem;color:#b4ff32">LLaMA 3.1-8B Instant</span></div>
            <div class="shield-item on"><span class="shield-label">API Provider</span><span style="font-family:Fira Code,monospace;font-size:0.62rem;color:#b4ff32">Groq Cloud</span></div>
            <div class="shield-item on"><span class="shield-label">Temperature</span><span style="font-family:Fira Code,monospace;font-size:0.62rem;color:#b4ff32">0.0 (deterministic)</span></div>
            <div class="shield-item on"><span class="shield-label">Redaction Layers</span><span style="font-family:Fira Code,monospace;font-size:0.62rem;color:#b4ff32">AI + Regex fallback</span></div>
        </div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class="card" style="padding:1.5rem">
            <div class="card-title" style="margin-bottom:1rem">📁 Supported Formats</div>
            <div class="shield-list">
                <div class="shield-item on"><span class="shield-label">📄 PDF</span><span style="font-family:Fira Code,monospace;font-size:0.62rem;color:#b4ff32">pypdf + Vision fallback</span></div>
                <div class="shield-item on"><span class="shield-label">🖼️ Images</span><span style="font-family:Fira Code,monospace;font-size:0.62rem;color:#b4ff32">JPG, PNG via Vision OCR</span></div>
                <div class="shield-item on"><span class="shield-label">📝 DOCX</span><span style="font-family:Fira Code,monospace;font-size:0.62rem;color:#b4ff32">python-docx</span></div>
                <div class="shield-item on"><span class="shield-label">📊 XLSX</span><span style="font-family:Fira Code,monospace;font-size:0.62rem;color:#b4ff32">openpyxl all sheets</span></div>
                <div class="shield-item on"><span class="shield-label">📑 PPTX</span><span style="font-family:Fira Code,monospace;font-size:0.62rem;color:#b4ff32">python-pptx + Vision</span></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    st.stop()

# Hero
st.markdown("""
<div class="hero">
    <div class="hero-label">⚡ Document Intelligence Platform</div>
    <div class="hero-h1">Extract, Shield &<br><em>Deliver.</em></div>
    <div class="hero-sub">Upload any document. Get structured text instantly with automatic AI-powered sensitive data redaction.</div>
</div>
""", unsafe_allow_html=True)

# Card grid
col1, col2 = st.columns([1.15, 0.85], gap="medium")

with col1:
    st.markdown("""
    <div class="card">
        <div class="card-head">
            <div class="card-head-left">
                <div class="card-ico ico-green">📤</div>
                <div>
                    <div class="card-title">Upload Document</div>
                    <div class="card-desc">Drag & drop or click to browse</div>
                </div>
            </div>
            <span class="card-badge badge-green">AI Ready</span>
        </div>
        <div class="card-body">
            <div class="fmt-row">
                <span class="fmt f1">PDF</span>
                <span class="fmt f2">JPG · PNG</span>
                <span class="fmt f3">DOCX</span>
                <span class="fmt f4">XLSX</span>
                <span class="fmt f5">PPTX</span>
            </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="upload-drop">', unsafe_allow_html=True)
    uploaded = st.file_uploader("up", type=["pdf","png","jpg","jpeg","docx","xlsx","pptx","ppt"], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded:
        sz = uploaded.size/1024
        st.markdown(f"""
        <div class="file-pill">
            <span>📎</span>
            <span class="fp-name">{uploaded.name}</span>
            <span class="fp-tag">{uploaded.name.split('.')[-1].upper()}</span>
            <span class="fp-tag">{"%.0f KB"%sz if sz<1024 else "%.1f MB"%(sz/1024)}</span>
        </div>""", unsafe_allow_html=True)

    run = st.button("⚡  Extract & Apply Privacy Shield", use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

with col2:
    shields = [
        ("🪪", "Aadhaar · SSN · PAN", redact_ids),
        ("📞", "Phone & Email",        redact_phones),
        ("💳", "Bank · Cards · UPI",  redact_banking),
        ("🔑", "Passwords · Keys",    redact_passwords),
        ("👤", "Personal Names",       redact_names),
        ("📅", "Dates of Birth",       redact_dates),
    ]
    items_html = "".join(
        f'<div class="shield-item {"on" if a else ""}"><span class="shield-label">{ic} {lb}</span><div class="shield-toggle {"on" if a else ""}"></div></div>'
        for ic,lb,a in shields
    )
    st.markdown(f"""
    <div class="card">
        <div class="card-head">
            <div class="card-head-left">
                <div class="card-ico ico-white">🛡️</div>
                <div>
                    <div class="card-title">Privacy Shield</div>
                    <div class="card-desc">{active} of 6 layers active</div>
                </div>
            </div>
            <span class="card-badge {"badge-green" if active>0 else "badge-dim"}">{"ACTIVE" if active>0 else "OFF"}</span>
        </div>
        <div class="card-body">
            <div class="shield-list">{items_html}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # close main-wrap

# ══ LOGIC ════════════════════════════════════════════════════════════
def build_rules():
    r=[]
    if redact_ids:       r.append("Aadhaar (12-digit, XXXX XXXX XXXX), SSN, PAN (ABCDE1234F), passport, driving license, voter ID")
    if redact_phones:    r.append("phone numbers (+91 or 10-digit), email addresses")
    if redact_banking:   r.append("bank account numbers, IFSC codes, credit/debit card numbers, CVV, UPI IDs")
    if redact_passwords: r.append("passwords, API keys, tokens, OTPs, PINs")
    if redact_names:     r.append("full names after 'Name:', 'नाम:'")
    if redact_dates:     r.append("dates of birth in any format, DOB, जन्म तिथि")
    return r

def pdf_text(fb):
    try:
        import pypdf; r=pypdf.PdfReader(io.BytesIO(fb))
        return "".join(p.extract_text() or "" for p in r.pages).strip()
    except: return None

def docx_text(fb):
    try:
        import docx; d=docx.Document(io.BytesIO(fb))
        return "\n".join(p.text for p in d.paragraphs if p.text.strip()).strip()
    except: return None

def xlsx_text(fb):
    try:
        import openpyxl; wb=openpyxl.load_workbook(io.BytesIO(fb),data_only=True); rows=[]
        for s in wb.worksheets:
            rows.append(f"[Sheet: {s.title}]")
            for row in s.iter_rows(values_only=True):
                l=" | ".join(str(c) for c in row if c is not None)
                if l.strip(): rows.append(l)
        return "\n".join(rows).strip()
    except: return None

def pptx_text(fb):
    try:
        from pptx import Presentation; p=Presentation(io.BytesIO(fb)); lines=[]
        for i,s in enumerate(p.slides,1):
            lines.append(f"[Slide {i}]")
            for sh in s.shapes:
                if hasattr(sh,"text") and sh.text.strip(): lines.append(sh.text.strip())
        return "\n".join(lines).strip()
    except: return None

def img_text(fb,mime):
    b64=base64.b64encode(fb).decode()
    r=client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role":"user","content":[
            {"type":"image_url","image_url":{"url":f"data:{mime};base64,{b64}"}},
            {"type":"text","text":"Extract ALL text from this image exactly. Return only raw text."}
        ]}],max_tokens=2000)
    return r.choices[0].message.content.strip()

def regex_redact(text,ph):
    c=0;rm=[]
    if redact_ids:
        n=re.sub(r'\b\d{4}\s?\d{4}\s?\d{4}\b',ph,text)
        if n!=text: c+=1;rm.append("Aadhaar");text=n
        n=re.sub(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b',ph,text)
        if n!=text: c+=1;rm.append("PAN");text=n
    if redact_phones:
        n=re.sub(r'\b(\+91[\s-]?)?[6-9]\d{9}\b',ph,text)
        if n!=text: c+=1;rm.append("phone");text=n
        n=re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',ph,text)
        if n!=text: c+=1;rm.append("email");text=n
    if redact_banking:
        n=re.sub(r'\b(?:\d[ -]*?){13,16}\b',ph,text)
        if n!=text: c+=1;rm.append("card");text=n
        n=re.sub(r'\b[A-Z]{4}0[A-Z0-9]{6}\b',ph,text)
        if n!=text: c+=1;rm.append("IFSC");text=n
    if redact_dates:
        n=re.sub(r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}\b',ph,text)
        if n!=text: c+=1;rm.append("DOB");text=n
    if redact_names:
        n=re.sub(r'(Name|नाम)\s*[:\-]\s*[A-Za-z\s]{3,40}',lambda m:m.group(0).split(':')[0]+': '+ph,text)
        if n!=text: c+=1;rm.append("name");text=n
    return text,rm,c

def ai_redact(text,rules):
    ph="[REDACTED]" if show_redacted else "████"
    if not rules: return text,[],0
    resp=client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role":"system","content":"Strict data privacy engine. Return only valid JSON."},
            {"role":"user","content":f"""Redact ALL sensitive data. Replace with "{ph}".
REDACT: {chr(10).join(f'- {r}' for r in rules)}
RULES: Keep surrounding text. When uncertain redact it. Return ONLY JSON:
{{"clean_text":"...","redacted_items":["..."],"redaction_count":0}}
TEXT: {text[:6000]}"""}
        ],temperature=0.0,max_tokens=4000)
    raw=re.sub(r'```json|```','',resp.choices[0].message.content.strip()).strip()
    try:
        res=json.loads(raw); clean=res.get("clean_text",text)
        items=res.get("redacted_items",[]); count=res.get("redaction_count",0)
        clean,ei,ec=regex_redact(clean,ph)
        return clean,items+ei,count+ec
    except: return regex_redact(text,"[REDACTED]" if show_redacted else "████")

# ══ PROCESS ══════════════════════════════════════════════════════════
if run and not uploaded:
    st.error("Please upload a document first.")

if run and uploaded:
    fb=uploaded.read(); mime=uploaded.type; name=uploaded.name.lower(); raw=None

    with st.spinner("⚡ Extracting document..."):
        try:
            if   name.endswith(".pdf"):                  raw=pdf_text(fb) or img_text(fb,"application/pdf")
            elif name.endswith((".png",".jpg",".jpeg")): raw=img_text(fb,mime)
            elif name.endswith(".docx"):                 raw=docx_text(fb)
            elif name.endswith(".xlsx"):                 raw=xlsx_text(fb)
            elif name.endswith((".pptx",".ppt")):        raw=pptx_text(fb) or img_text(fb,mime)
        except Exception as e: st.error(f"Extraction error: {e}")

    if not raw or len(raw.strip())<5:
        st.error("Could not extract text from this file."); st.stop()

    rules=build_rules(); clean,items,count=raw,[],0
    if rules:
        with st.spinner("🛡️ Privacy Shield scanning..."):
            try:    clean,items,count=ai_redact(raw,rules)
            except: clean,items,count=regex_redact(raw,"[REDACTED]" if show_redacted else "████")

    from datetime import datetime
    wc=len(clean.split()); is_clean=count==0
    sc="sb-ok" if is_clean else "sb-wr"
    sv="✓ CLEAN" if is_clean else "⚠ REDACTED"

    # Save to history
    st.session_state.history.insert(0, {
        "name": uploaded.name,
        "words": wc,
        "redacted": count,
        "status": "CLEAN" if is_clean else "REDACTED",
        "time": datetime.now().strftime("%d %b %Y, %I:%M %p")
    })

    st.markdown('<div class="main-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="g-line"></div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="stat-strip">
        <div class="stat-box sb-g"><div class="sn">{wc:,}</div><div class="sl">Words Extracted</div></div>
        <div class="stat-box sb-w"><div class="sn">{count}</div><div class="sl">Items Redacted</div></div>
        <div class="stat-box {sc}"><div class="sn">{sv}</div><div class="sl">Document Status</div></div>
    </div>
    """, unsafe_allow_html=True)

    if items:
        tags="".join(f'<span class="rtag">⛔ {i}</span>' for i in set(items))
        st.markdown(f'<div class="tag-row">{tags}</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="result-card">
        <div class="rc-header">
            <span class="rc-title">Extracted Content</span>
            <span class="rc-meta">{len(clean):,} chars · {wc:,} words</span>
        </div>
        <div class="rc-body">{clean}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    ca,cb=st.columns(2)
    ca.download_button("⬇ Download TXT", clean, f"{uploaded.name}_clean.txt","text/plain",use_container_width=True)
    cb.download_button("⬇ Download JSON",
        json.dumps({"filename":uploaded.name,"text":clean,"words":wc,"redacted":count,"categories":list(set(items))},indent=2),
        f"{uploaded.name}_clean.json","application/json",use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)
