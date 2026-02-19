import streamlit as st
from groq import Groq
import json, re, base64, io

st.set_page_config(page_title="DocuAI — Document Intelligence", page_icon="⚡", layout="wide")

try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client  = Groq(api_key=API_KEY)
except:
    st.error("Add GROQ_API_KEY to Streamlit Secrets.")
    st.stop()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500&display=swap');

* { box-sizing: border-box; margin: 0; padding: 0; }
html, body, [class*="css"] { font-family: 'Outfit', sans-serif !important; }

#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"]
{ display:none !important; }
[data-testid="collapsedControl"] { display:flex !important; }

/* ═══ BACKGROUND ═══ */
.stApp {
    background: #06030f;
    min-height: 100vh;
    background-image:
        radial-gradient(ellipse 120% 80% at -10% 0%, rgba(139,92,246,0.2) 0%, transparent 50%),
        radial-gradient(ellipse 80% 60% at 110% 0%, rgba(236,72,153,0.18) 0%, transparent 45%),
        radial-gradient(ellipse 60% 50% at 50% 100%, rgba(6,182,212,0.1) 0%, transparent 50%),
        url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.015'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
}

/* ═══ SIDEBAR ═══ */
section[data-testid="stSidebar"] {
    background: rgba(10,5,20,0.9) !important;
    border-right: 1px solid rgba(139,92,246,0.15) !important;
    backdrop-filter: blur(30px) !important;
}
section[data-testid="stSidebar"] > div { padding-top: 0 !important; }

.sb-header {
    padding: 1.8rem 1.4rem 1.4rem;
    background: linear-gradient(135deg, rgba(139,92,246,0.2), rgba(236,72,153,0.1));
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 0.5rem;
}
.sb-logo {
    font-size: 1.4rem; font-weight: 800; letter-spacing: -0.03em;
    background: linear-gradient(135deg, #a78bfa, #f472b6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.sb-tagline { font-size: 0.65rem; color: rgba(255,255,255,0.3); letter-spacing: 0.12em; text-transform: uppercase; margin-top: 0.2rem; }

.sb-section { padding: 1.2rem 1.4rem; border-bottom: 1px solid rgba(255,255,255,0.04); }
.sb-section-label {
    font-size: 0.6rem; font-weight: 600; letter-spacing: 0.18em;
    text-transform: uppercase; color: rgba(255,255,255,0.2); margin-bottom: 0.9rem;
}

section[data-testid="stSidebar"] .stCheckbox > label {
    font-family: 'Outfit', sans-serif !important;
    font-size: 0.82rem !important; color: rgba(255,255,255,0.45) !important;
    font-weight: 500 !important; transition: color 0.2s !important;
}
section[data-testid="stSidebar"] .stCheckbox > label:hover { color: rgba(255,255,255,0.85) !important; }
section[data-testid="stSidebar"] .stCheckbox > label > div { color: inherit !important; }

.sb-footer {
    padding: 1rem 1.4rem;
    font-size: 0.62rem; color: rgba(255,255,255,0.12);
    font-family: 'JetBrains Mono', monospace; line-height: 1.7;
}

/* ═══ TOPBAR ═══ */
.topbar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1.2rem 2.5rem;
    background: rgba(255,255,255,0.02);
    border-bottom: 1px solid rgba(255,255,255,0.05);
    backdrop-filter: blur(20px);
    margin-bottom: 0;
}
.topbar-brand {
    font-size: 1.1rem; font-weight: 800; letter-spacing: -0.02em;
    background: linear-gradient(90deg, #a78bfa, #f472b6, #22d3ee);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}
.topbar-badges { display: flex; gap: 0.5rem; }
.topbar-badge {
    font-size: 0.6rem; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; padding: 0.25rem 0.7rem; border-radius: 999px;
}
.tb1 { background: rgba(139,92,246,0.15); border: 1px solid rgba(139,92,246,0.3); color: #a78bfa; }
.tb2 { background: rgba(34,211,238,0.1);  border: 1px solid rgba(34,211,238,0.25); color: #22d3ee; }
.tb3 { background: rgba(52,211,153,0.1);  border: 1px solid rgba(52,211,153,0.25); color: #34d399; }

/* ═══ HERO SECTION ═══ */
.hero-section {
    padding: 4rem 2.5rem 2rem;
    display: flex; flex-direction: column;
}
.hero-eyebrow {
    display: inline-flex; align-items: center; gap: 0.6rem;
    font-size: 0.68rem; font-weight: 600; letter-spacing: 0.2em;
    text-transform: uppercase; color: #a78bfa; margin-bottom: 1.5rem;
}
.eyebrow-line { height: 1px; width: 40px; background: linear-gradient(90deg, #a78bfa, transparent); }

.hero-title {
    font-size: clamp(3rem, 5.5vw, 5.5rem);
    font-weight: 900; line-height: 1.0; letter-spacing: -0.04em;
    margin-bottom: 1rem;
}
.ht-1 { color: #ffffff; display: block; }
.ht-2 { display: block; margin-top: 0.1rem;
    background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 50%, #22d3ee 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-size: 200% auto; animation: gradshift 5s ease infinite;
}
@keyframes gradshift { 0%,100%{background-position:0% 50%} 50%{background-position:100% 50%} }

.hero-sub {
    font-size: 1.05rem; font-weight: 400; color: rgba(255,255,255,0.35);
    line-height: 1.7; max-width: 520px; margin-bottom: 2.5rem;
}

/* ═══ FORMAT TAGS ═══ */
.format-tags { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-bottom: 2.5rem; }
.ftag {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.62rem; font-weight: 500; padding: 0.3rem 0.75rem;
    border-radius: 6px; letter-spacing: 0.05em;
    transition: transform 0.2s;
}
.ftag:hover { transform: translateY(-2px); }
.ft-pdf  { background:rgba(248,113,113,0.1); border:1px solid rgba(248,113,113,0.3); color:#f87171; }
.ft-img  { background:rgba(34,211,238,0.1);  border:1px solid rgba(34,211,238,0.3);  color:#22d3ee; }
.ft-doc  { background:rgba(139,92,246,0.1);  border:1px solid rgba(139,92,246,0.3);  color:#a78bfa; }
.ft-xl   { background:rgba(52,211,153,0.1);  border:1px solid rgba(52,211,153,0.3);  color:#34d399; }
.ft-ppt  { background:rgba(251,191,36,0.1);  border:1px solid rgba(251,191,36,0.3);  color:#fbbf24; }

/* ═══ MAIN GRID ═══ */
.main-grid {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 1.5rem; padding: 0 2.5rem 2.5rem;
}
@media (max-width: 900px) { .main-grid { grid-template-columns: 1fr; } }

/* ═══ GLASS CARDS ═══ */
.glass-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px; overflow: hidden;
    backdrop-filter: blur(20px);
    transition: border-color 0.3s, box-shadow 0.3s;
    position: relative;
}
.glass-card:hover {
    border-color: rgba(139,92,246,0.25);
    box-shadow: 0 0 40px rgba(139,92,246,0.08);
}
.glass-card::before {
    content: ''; position: absolute; inset: 0; border-radius: 20px;
    background: linear-gradient(135deg, rgba(139,92,246,0.04) 0%, transparent 60%);
    pointer-events: none;
}

.card-header {
    display: flex; align-items: center; gap: 0.8rem;
    padding: 1.2rem 1.5rem;
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.card-icon {
    width: 36px; height: 36px; border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
}
.ci-purple { background: rgba(139,92,246,0.2); border: 1px solid rgba(139,92,246,0.3); }
.ci-pink   { background: rgba(236,72,153,0.2);  border: 1px solid rgba(236,72,153,0.3);  }
.ci-cyan   { background: rgba(34,211,238,0.15); border: 1px solid rgba(34,211,238,0.25); }
.ci-green  { background: rgba(52,211,153,0.15); border: 1px solid rgba(52,211,153,0.25); }

.card-title { font-size: 0.82rem; font-weight: 700; color: rgba(255,255,255,0.8); }
.card-sub   { font-size: 0.65rem; color: rgba(255,255,255,0.25); margin-top: 0.1rem; }
.card-body  { padding: 1.5rem; }

/* ═══ UPLOAD ZONE ═══ */
.upload-zone {
    border: 1.5px dashed rgba(139,92,246,0.25); border-radius: 14px;
    background: rgba(139,92,246,0.03); transition: all 0.3s; cursor: pointer;
}
.upload-zone:hover { border-color: rgba(139,92,246,0.5); background: rgba(139,92,246,0.06); }

div[data-testid="stFileUploader"] { background:transparent !important; border:none !important; }
div[data-testid="stFileUploadDropzone"] { background:transparent !important; border:none !important; padding:1.8rem 1rem !important; text-align:center; }
div[data-testid="stFileUploadDropzone"] p { color:rgba(255,255,255,0.25) !important; font-family:'Outfit',sans-serif !important; font-size:0.88rem !important; }
div[data-testid="stFileUploadDropzone"] small { color:rgba(255,255,255,0.12) !important; }

/* ═══ FILE CHIP ═══ */
.file-chip {
    display: flex; align-items: center; gap: 0.8rem;
    background: linear-gradient(135deg, rgba(139,92,246,0.1), rgba(236,72,153,0.05));
    border: 1px solid rgba(139,92,246,0.2); border-radius: 12px;
    padding: 0.75rem 1rem; margin-top: 0.8rem;
    animation: fadeup 0.4s ease;
}
@keyframes fadeup { from{opacity:0;transform:translateY(8px)} to{opacity:1;transform:translateY(0)} }
.fc-name { font-family:'JetBrains Mono',monospace; font-size:0.75rem; color:#c4b5fd; flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.fc-ext  { font-family:'JetBrains Mono',monospace; font-size:0.62rem; color:rgba(255,255,255,0.2); background:rgba(255,255,255,0.05); padding:0.15rem 0.5rem; border-radius:4px; }

/* ═══ EXTRACT BUTTON ═══ */
.stButton > button {
    width: 100% !important; margin-top: 1rem !important;
    background: linear-gradient(135deg, #7c3aed, #db2777, #0891b2) !important;
    background-size: 200% auto !important;
    color: white !important; font-family: 'Outfit', sans-serif !important;
    font-weight: 700 !important; font-size: 0.95rem !important;
    border: none !important; border-radius: 12px !important;
    padding: 0.85rem !important; letter-spacing: 0.03em !important;
    transition: all 0.4s ease !important;
    box-shadow: 0 4px 25px rgba(124,58,237,0.3), 0 0 0 1px rgba(255,255,255,0.06) !important;
}
.stButton > button:hover {
    background-position: right !important;
    box-shadow: 0 8px 50px rgba(124,58,237,0.45), 0 0 0 1px rgba(255,255,255,0.1) !important;
    transform: translateY(-2px) !important;
}

/* ═══ PRIVACY SHIELD PANEL ═══ */
.shield-grid { display:grid; grid-template-columns:1fr 1fr; gap:0.5rem; }
.shield-item {
    display:flex; align-items:center; gap:0.5rem;
    background: rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.06);
    border-radius:10px; padding:0.6rem 0.8rem;
    font-size:0.75rem; color:rgba(255,255,255,0.35); font-weight:500;
    transition: all 0.2s;
}
.shield-item.active {
    background:rgba(139,92,246,0.1); border-color:rgba(139,92,246,0.25);
    color:rgba(255,255,255,0.75);
}
.shield-dot { width:6px; height:6px; border-radius:50%; flex-shrink:0; }
.sd-on  { background:#a78bfa; box-shadow:0 0 6px rgba(167,139,250,0.6); }
.sd-off { background:rgba(255,255,255,0.1); }

/* ═══ STATS ═══ */
.stats-3 { display:grid; grid-template-columns:repeat(3,1fr); gap:0.8rem; }
.stat-tile {
    border-radius:14px; padding:1.2rem 1rem; text-align:center;
    position:relative; overflow:hidden;
    animation: statpop 0.5s ease backwards;
}
.stat-tile:nth-child(1){animation-delay:0.1s}
.stat-tile:nth-child(2){animation-delay:0.2s}
.stat-tile:nth-child(3){animation-delay:0.3s}
@keyframes statpop { from{opacity:0;transform:scale(0.9)} to{opacity:1;transform:scale(1)} }

.st-purple { background:rgba(139,92,246,0.1); border:1px solid rgba(139,92,246,0.2); }
.st-pink   { background:rgba(236,72,153,0.1);  border:1px solid rgba(236,72,153,0.2);  }
.st-green  { background:rgba(52,211,153,0.1);  border:1px solid rgba(52,211,153,0.2);  }
.st-orange { background:rgba(251,146,60,0.1);  border:1px solid rgba(251,146,60,0.2);  }

.snum { font-family:'JetBrains Mono',monospace; font-size:1.9rem; font-weight:700; line-height:1; }
.st-purple .snum { color:#a78bfa; }
.st-pink   .snum { color:#f472b6; }
.st-green  .snum { color:#34d399; font-size:1rem; padding-top:0.5rem; }
.st-orange .snum { color:#fb923c; font-size:1rem; padding-top:0.5rem; }
.slbl { font-size:0.58rem; font-weight:600; letter-spacing:0.15em; text-transform:uppercase; color:rgba(255,255,255,0.2); margin-top:0.4rem; }

/* ═══ REDACT TAGS ═══ */
.rtag-wrap { display:flex; flex-wrap:wrap; gap:0.4rem; margin:1rem 0; }
.rtag {
    font-family:'JetBrains Mono',monospace; font-size:0.6rem;
    padding:0.2rem 0.6rem; border-radius:6px;
    background:rgba(236,72,153,0.1); border:1px solid rgba(236,72,153,0.2); color:#f9a8d4;
    animation: tagin 0.3s ease backwards;
}

/* ═══ RESULT PANEL ═══ */
.result-panel {
    border-radius:16px; overflow:hidden;
    border:1px solid rgba(255,255,255,0.07);
    background:rgba(255,255,255,0.02);
    animation: panelin 0.5s ease;
}
@keyframes panelin { from{opacity:0;transform:translateY(12px)} to{opacity:1;transform:translateY(0)} }

.rp-bar {
    display:flex; justify-content:space-between; align-items:center;
    padding:0.9rem 1.3rem;
    background:linear-gradient(135deg, rgba(139,92,246,0.08), rgba(236,72,153,0.05));
    border-bottom:1px solid rgba(255,255,255,0.05);
}
.rp-label { font-size:0.62rem; font-weight:700; letter-spacing:0.15em; text-transform:uppercase; color:rgba(255,255,255,0.25); }
.rp-count { font-family:'JetBrains Mono',monospace; font-size:0.6rem; color:#a78bfa; background:rgba(139,92,246,0.12); border:1px solid rgba(139,92,246,0.2); padding:0.15rem 0.6rem; border-radius:999px; }

.rp-text {
    padding:1.3rem; font-family:'JetBrains Mono',monospace;
    font-size:0.78rem; line-height:2; color:rgba(255,255,255,0.5);
    white-space:pre-wrap; word-break:break-word;
    max-height:360px; overflow-y:auto;
}
.rp-text::-webkit-scrollbar { width:3px; }
.rp-text::-webkit-scrollbar-thumb { background:rgba(139,92,246,0.35); border-radius:2px; }

/* ═══ DOWNLOAD BUTTONS ═══ */
.stDownloadButton > button {
    background:rgba(255,255,255,0.04) !important;
    border:1px solid rgba(255,255,255,0.08) !important;
    color:rgba(255,255,255,0.4) !important;
    font-family:'Outfit',sans-serif !important; font-size:0.82rem !important;
    font-weight:600 !important; border-radius:10px !important;
    padding:0.65rem 1rem !important; width:100% !important; transition:all 0.25s !important;
}
.stDownloadButton > button:hover {
    background:rgba(139,92,246,0.1) !important;
    border-color:rgba(139,92,246,0.35) !important;
    color:#c4b5fd !important;
    box-shadow:0 0 20px rgba(139,92,246,0.15) !important;
}

/* ═══ ANIMATED DIVIDER ═══ */
.anim-divider {
    height:2px; border-radius:2px; margin:0 2.5rem 1.5rem;
    background:linear-gradient(90deg,#7c3aed,#db2777,#0891b2,#059669,#7c3aed);
    background-size:300% auto;
    animation:divmove 4s linear infinite;
}
@keyframes divmove{0%{background-position:0%}100%{background-position:300%}}

/* ═══ TRUST STRIP ═══ */
.trust-strip {
    display:flex; flex-wrap:wrap; justify-content:center; gap:2rem;
    padding:1rem 2.5rem 2rem;
}
.trust-item { display:flex; align-items:center; gap:0.4rem; font-size:0.65rem; font-weight:500; color:rgba(255,255,255,0.18); }
.trust-check { color:#34d399; font-size:0.7rem; }

div[data-testid="stSelectbox"] > div {
    background:rgba(255,255,255,0.04) !important;
    border:1px solid rgba(255,255,255,0.08) !important;
    color:#e2e8f0 !important; border-radius:10px !important;
}
.stAlert { border-radius:12px !important; }
</style>
""", unsafe_allow_html=True)

# ══ SIDEBAR ══════════════════════════════════════════════════════════
st.sidebar.markdown("""
<div class="sb-header">
    <div class="sb-logo">⚡ DocuAI</div>
    <div class="sb-tagline">Document Intelligence Platform</div>
</div>
<div class="sb-section">
    <div class="sb-section-label">🛡️ Privacy Shield</div>
</div>
""", unsafe_allow_html=True)

redact_ids       = st.sidebar.checkbox("🪪  Aadhaar · SSN · PAN · ID",  value=True)
redact_phones    = st.sidebar.checkbox("📞  Phone numbers & emails",     value=True)
redact_banking   = st.sidebar.checkbox("💳  Bank · Cards · UPI",        value=True)
redact_passwords = st.sidebar.checkbox("🔑  Passwords · Keys · OTPs",   value=True)
redact_names     = st.sidebar.checkbox("👤  Personal names",             value=False)
redact_dates     = st.sidebar.checkbox("📅  Dates of birth",             value=False)

st.sidebar.markdown("""<div class="sb-section"><div class="sb-section-label">⚙️ Output</div></div>""", unsafe_allow_html=True)
show_redacted = st.sidebar.checkbox("Show [REDACTED] placeholders", value=True)

st.sidebar.markdown("""
<div class="sb-footer">
    DocuAI · v2.0<br>
    Groq · LLaMA 4 Vision + LLaMA 3.1<br>
    Dual-layer AI + Regex redaction<br>
    © 2025 All rights reserved
</div>
""", unsafe_allow_html=True)

# ══ TOP BAR ══════════════════════════════════════════════════════════
st.markdown("""
<div class="topbar">
    <div class="topbar-brand">⚡ DocuAI — Document Intelligence</div>
    <div class="topbar-badges">
        <span class="topbar-badge tb1">AI Powered</span>
        <span class="topbar-badge tb2">Privacy First</span>
        <span class="topbar-badge tb3">Enterprise</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ══ HERO ═════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero-section">
    <div class="hero-eyebrow">
        <span class="eyebrow-line"></span>
        Intelligent Document Processing
        <span class="eyebrow-line"></span>
    </div>
    <div class="hero-title">
        <span class="ht-1">Extract & Protect</span>
        <span class="ht-2">Any Document.</span>
    </div>
    <div class="hero-sub">
        Upload any document and get clean, structured text in seconds —
        with automatic AI-powered sensitive data redaction.
    </div>
    <div class="format-tags">
        <span class="ftag ft-pdf">📄 PDF</span>
        <span class="ftag ft-img">🖼️ JPG · PNG</span>
        <span class="ftag ft-doc">📝 DOCX</span>
        <span class="ftag ft-xl">📊 XLSX</span>
        <span class="ftag ft-ppt">📑 PPTX</span>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="anim-divider"></div>', unsafe_allow_html=True)

# ══ MAIN GRID ════════════════════════════════════════════════════════
left, right = st.columns([1, 1], gap="large")

with left:
    # Upload card
    st.markdown("""
    <div class="glass-card">
        <div class="card-header">
            <div class="card-icon ci-purple">📤</div>
            <div>
                <div class="card-title">Upload Document</div>
                <div class="card-sub">PDF, Image, Word, Excel, PowerPoint</div>
            </div>
        </div>
        <div class="card-body">
    """, unsafe_allow_html=True)

    st.markdown('<div class="upload-zone">', unsafe_allow_html=True)
    uploaded = st.file_uploader("upload", type=["pdf","png","jpg","jpeg","docx","xlsx","pptx","ppt"], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded:
        sz = uploaded.size/1024
        st.markdown(f"""
        <div class="file-chip">
            <span style="font-size:1.2rem">📎</span>
            <span class="fc-name">{uploaded.name}</span>
            <span class="fc-ext">{uploaded.name.split('.')[-1].upper()} · {"%.0f KB" % sz if sz<1024 else "%.1f MB" % (sz/1024)}</span>
        </div>
        """, unsafe_allow_html=True)

    run = st.button("⚡  Extract & Apply Privacy Shield", use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

with right:
    # Privacy shield status card
    st.markdown("""
    <div class="glass-card">
        <div class="card-header">
            <div class="card-icon ci-pink">🛡️</div>
            <div>
                <div class="card-title">Privacy Shield Status</div>
                <div class="card-sub">Active redaction layers</div>
            </div>
        </div>
        <div class="card-body">
            <div class="shield-grid">
    """, unsafe_allow_html=True)

    shields = [
        ("🪪", "ID Numbers",   redact_ids),
        ("📞", "Phones/Email", redact_phones),
        ("💳", "Banking",      redact_banking),
        ("🔑", "Passwords",    redact_passwords),
        ("👤", "Names",        redact_names),
        ("📅", "Dates of Birth", redact_dates),
    ]
    items_html = ""
    for icon, label, active in shields:
        cls = "shield-item active" if active else "shield-item"
        dot = "sd-on" if active else "sd-off"
        items_html += f'<div class="{cls}"><span class="shield-dot {dot}"></span>{icon} {label}</div>'

    st.markdown(items_html + '</div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

# ══ TRUST STRIP ══════════════════════════════════════════════════════
st.markdown("""
<div class="trust-strip">
    <span class="trust-item"><span class="trust-check">✓</span> No data stored</span>
    <span class="trust-item"><span class="trust-check">✓</span> AI + Regex dual-layer redaction</span>
    <span class="trust-item"><span class="trust-check">✓</span> Hindi label support (नाम, DOB)</span>
    <span class="trust-item"><span class="trust-check">✓</span> Supports 6 file formats</span>
    <span class="trust-item"><span class="trust-check">✓</span> LLaMA 4 Vision OCR</span>
</div>
""", unsafe_allow_html=True)

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
            {"type":"text","text":"Extract ALL text from this image exactly. Return only raw extracted text."}
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
RULES: Keep surrounding text. When uncertain — redact. Source may be Aadhaar/passport/bank doc.
Return ONLY JSON: {{"clean_text":"...","redacted_items":["..."],"redaction_count":0}}
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

    with st.spinner("✨ Extracting document content..."):
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

    st.markdown('<div class="anim-divider"></div>', unsafe_allow_html=True)

    wc=len(clean.split()); is_clean=count==0
    st_cls="st-green" if is_clean else "st-orange"
    st_val="✓ CLEAN" if is_clean else "⚠ REDACTED"

    st.markdown(f"""
    <div style="padding:0 0 1rem">
        <div class="stats-3">
            <div class="stat-tile st-purple">
                <div class="snum">{wc:,}</div>
                <div class="slbl">Words Extracted</div>
            </div>
            <div class="stat-tile st-pink">
                <div class="snum">{count}</div>
                <div class="slbl">Items Redacted</div>
            </div>
            <div class="stat-tile {st_cls}">
                <div class="snum">{st_val}</div>
                <div class="slbl">Document Status</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if items:
        tags="".join(f'<span class="rtag">⛔ {i}</span>' for i in set(items))
        st.markdown(f'<div class="rtag-wrap">{tags}</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="result-panel">
        <div class="rp-bar">
            <span class="rp-label">📄 Extracted Content</span>
            <span class="rp-count">{len(clean):,} characters</span>
        </div>
        <div class="rp-text">{clean}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    ca,cb=st.columns(2)
    ca.download_button("⬇ Download as TXT",clean,f"{uploaded.name}_clean.txt","text/plain",use_container_width=True)
    cb.download_button("⬇ Download as JSON",
        json.dumps({"filename":uploaded.name,"text":clean,"words":wc,"redacted":count,"categories":list(set(items))},indent=2),
        f"{uploaded.name}_clean.json","application/json",use_container_width=True)
