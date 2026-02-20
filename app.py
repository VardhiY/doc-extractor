import streamlit as st
from groq import Groq
import json, re, base64, io

st.set_page_config(page_title="DocuAI", page_icon="⚡", layout="wide")

try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client  = Groq(api_key=API_KEY)
except:
    st.error("Add GROQ_API_KEY to Streamlit Secrets."); st.stop()

# ── SESSION STATE (init once) ─────────────────────────────────────────
for k, v in {"tab":"Extract","history":[],"ri":True,"rp":True,"rb":True,"rpw":True,"rn":True,"rd":True}.items():
    if k not in st.session_state: st.session_state[k] = v

# ── CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Fira+Code:wght@400;500&display=swap');

*{box-sizing:border-box;margin:0;padding:0;}
html,body,[class*="css"]{font-family:'Inter',sans-serif !important;}

#MainMenu,footer,header,.stDeployButton,
[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"]
{display:none !important;}
[data-testid="collapsedControl"]{display:flex !important;}

.stApp{
    background:#080c0f;
    background-image:
        radial-gradient(ellipse 70% 50% at 100% 0%,rgba(180,255,50,0.07) 0%,transparent 55%),
        radial-gradient(ellipse 50% 40% at 0% 100%,rgba(180,255,50,0.04) 0%,transparent 50%);
}

/* SIDEBAR */
section[data-testid="stSidebar"]{background:#0b0f12 !important;border-right:1px solid rgba(180,255,50,0.08) !important;}
section[data-testid="stSidebar"]>div{padding:0 !important;}
.sb-logo{padding:1.8rem 1.4rem 1.3rem;border-bottom:1px solid rgba(255,255,255,0.04);}
.sb-icon{display:inline-flex;align-items:center;justify-content:center;width:32px;height:32px;background:#b4ff32;border-radius:8px;font-size:0.9rem;margin-bottom:0.5rem;}
.sb-brand{font-size:1.1rem;font-weight:800;color:#fff;letter-spacing:-0.02em;}
.sb-ver{font-family:'Fira Code',monospace;font-size:0.58rem;color:rgba(255,255,255,0.2);margin-top:0.15rem;}
.sb-sec{padding:1.1rem 1.4rem;border-bottom:1px solid rgba(255,255,255,0.04);}
.sb-lbl{font-size:0.58rem;font-weight:700;letter-spacing:0.2em;text-transform:uppercase;color:rgba(255,255,255,0.2);margin-bottom:0.8rem;}
.sb-footer{padding:1.1rem 1.4rem;font-family:'Fira Code',monospace;font-size:0.58rem;color:rgba(255,255,255,0.12);line-height:1.8;}

section[data-testid="stSidebar"] .stCheckbox>label{
    font-family:'Inter',sans-serif !important;font-size:0.8rem !important;
    font-weight:500 !important;color:rgba(255,255,255,0.4) !important;
    padding:0.45rem 0 !important;
}
section[data-testid="stSidebar"] .stCheckbox>label:hover{color:rgba(255,255,255,0.8) !important;}
section[data-testid="stSidebar"] .stCheckbox input:checked+div{background:#b4ff32 !important;border-color:#b4ff32 !important;}

/* MAIN */
.main{padding:1.8rem 2.2rem;}

/* NAV */
.nav{display:flex;align-items:center;justify-content:space-between;margin-bottom:2rem;}
.pulse{width:7px;height:7px;border-radius:50%;background:#b4ff32;box-shadow:0 0 8px #b4ff32;display:inline-block;animation:glow 2s infinite;}
@keyframes glow{0%,100%{box-shadow:0 0 6px #b4ff32;}50%{box-shadow:0 0 18px #b4ff32,0 0 35px rgba(180,255,50,0.3);}}
.nav-status{display:flex;align-items:center;gap:0.5rem;font-size:0.7rem;font-weight:600;color:rgba(255,255,255,0.3);}

/* Tab buttons override */
div[data-testid="stHorizontalBlock"] .stButton>button{
    background:rgba(255,255,255,0.04) !important;color:rgba(255,255,255,0.35) !important;
    border:1px solid rgba(255,255,255,0.07) !important;border-radius:8px !important;
    font-size:0.75rem !important;font-weight:600 !important;
    padding:0.4rem 0.8rem !important;box-shadow:none !important;margin-top:0 !important;
    transition:all 0.2s !important;
}
div[data-testid="stHorizontalBlock"] .stButton>button:hover{
    background:rgba(180,255,50,0.08) !important;border-color:rgba(180,255,50,0.2) !important;
    color:#b4ff32 !important;transform:none !important;box-shadow:none !important;
}
div[data-testid="stHorizontalBlock"] .stButton>button[kind="primary"]{
    background:rgba(180,255,50,0.12) !important;border-color:rgba(180,255,50,0.3) !important;color:#b4ff32 !important;
}

/* HERO */
.hero{margin-bottom:2rem;}
.hero-tag{font-size:0.63rem;font-weight:700;letter-spacing:0.2em;text-transform:uppercase;color:#b4ff32;margin-bottom:0.7rem;}
.hero-h1{font-size:clamp(2.5rem,4vw,4.5rem);font-weight:900;letter-spacing:-0.04em;line-height:1.0;color:#fff;}
.hero-h1 em{font-style:normal;background:linear-gradient(90deg,#b4ff32,#4ade80);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.hero-sub{font-size:0.9rem;color:rgba(255,255,255,0.28);font-weight:400;line-height:1.6;margin-top:0.6rem;max-width:480px;}

/* CARDS */
.card{background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.07);border-radius:18px;overflow:hidden;position:relative;transition:border-color 0.3s;}
.card:hover{border-color:rgba(180,255,50,0.18);}
.card::after{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(180,255,50,0.25),transparent);}
.ch{display:flex;align-items:center;justify-content:space-between;padding:1.1rem 1.4rem;border-bottom:1px solid rgba(255,255,255,0.05);}
.ch-left{display:flex;align-items:center;gap:0.7rem;}
.cico{width:36px;height:36px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1rem;}
.ico-g{background:rgba(180,255,50,0.12);border:1px solid rgba(180,255,50,0.2);}
.ico-w{background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.1);}
.ct{font-size:0.83rem;font-weight:700;color:#fff;}
.cd{font-size:0.63rem;color:rgba(255,255,255,0.25);margin-top:0.1rem;}
.cbadge{font-family:'Fira Code',monospace;font-size:0.57rem;padding:0.2rem 0.6rem;border-radius:5px;}
.bg{background:rgba(180,255,50,0.1);border:1px solid rgba(180,255,50,0.2);color:#b4ff32;}
.bw{background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.08);color:rgba(255,255,255,0.3);}
.cb{padding:1.3rem 1.4rem;}

/* FORMAT TAGS */
.fmt-row{display:flex;flex-wrap:wrap;gap:0.4rem;margin-bottom:0.9rem;}
.fmt{font-family:'Fira Code',monospace;font-size:0.58rem;font-weight:500;padding:0.2rem 0.6rem;border-radius:5px;letter-spacing:0.04em;}
.f1{background:rgba(248,113,113,0.08);border:1px solid rgba(248,113,113,0.2);color:#f87171;}
.f2{background:rgba(96,165,250,0.08);border:1px solid rgba(96,165,250,0.2);color:#60a5fa;}
.f3{background:rgba(167,139,250,0.08);border:1px solid rgba(167,139,250,0.2);color:#a78bfa;}
.f4{background:rgba(52,211,153,0.08);border:1px solid rgba(52,211,153,0.2);color:#34d399;}
.f5{background:rgba(251,191,36,0.08);border:1px solid rgba(251,191,36,0.2);color:#fbbf24;}

/* UPLOAD */
.upload-drop{border:1.5px dashed rgba(180,255,50,0.2);border-radius:12px;background:rgba(180,255,50,0.02);transition:all 0.3s;}
.upload-drop:hover{border-color:rgba(180,255,50,0.4);background:rgba(180,255,50,0.04);}
div[data-testid="stFileUploader"]{background:transparent !important;border:none !important;}
div[data-testid="stFileUploadDropzone"]{background:transparent !important;border:none !important;padding:1.8rem 1rem !important;text-align:center;}
div[data-testid="stFileUploadDropzone"] p{color:rgba(255,255,255,0.2) !important;font-size:0.85rem !important;}
div[data-testid="stFileUploadDropzone"] small{color:rgba(255,255,255,0.1) !important;}

/* FILE CHIP */
.fp{display:flex;align-items:center;gap:0.7rem;background:rgba(180,255,50,0.06);border:1px solid rgba(180,255,50,0.15);border-radius:10px;padding:0.65rem 1rem;margin-top:0.7rem;}
.fp-name{font-family:'Fira Code',monospace;font-size:0.72rem;color:#b4ff32;flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.fp-tag{font-family:'Fira Code',monospace;font-size:0.6rem;padding:0.12rem 0.45rem;border-radius:4px;background:rgba(255,255,255,0.06);color:rgba(255,255,255,0.3);}

/* MAIN BUTTON */
.stButton>button{
    width:100% !important;margin-top:0.9rem !important;
    background:#b4ff32 !important;color:#080c0f !important;
    font-family:'Inter',sans-serif !important;font-weight:800 !important;
    font-size:0.88rem !important;border:none !important;border-radius:11px !important;
    padding:0.82rem !important;letter-spacing:0.01em !important;
    box-shadow:0 0 25px rgba(180,255,50,0.2) !important;transition:all 0.3s !important;
}
.stButton>button:hover{background:#c8ff50 !important;box-shadow:0 0 45px rgba(180,255,50,0.4) !important;transform:translateY(-2px) !important;}

/* SHIELD ROWS in card */
.tog{display:flex;align-items:center;justify-content:space-between;padding:0.55rem 0.8rem;border-radius:9px;border:1px solid rgba(255,255,255,0.05);background:rgba(255,255,255,0.02);margin-bottom:0.45rem;}
.tog.on{background:rgba(180,255,50,0.06);border-color:rgba(180,255,50,0.15);}
.tog-lbl{font-size:0.78rem;font-weight:500;color:rgba(255,255,255,0.35);}
.tog.on .tog-lbl{color:rgba(255,255,255,0.78);}
.tog-pill{width:36px;height:19px;border-radius:10px;position:relative;background:rgba(255,255,255,0.08);}
.tog-pill.on{background:rgba(180,255,50,0.3);}
.tog-pill::after{content:'';position:absolute;top:3px;left:3px;width:13px;height:13px;border-radius:50%;background:rgba(255,255,255,0.25);transition:all 0.2s;}
.tog-pill.on::after{left:20px;background:#b4ff32;box-shadow:0 0 7px rgba(180,255,50,0.7);}

/* DIVIDER */
.gline{height:1px;background:linear-gradient(90deg,transparent,rgba(180,255,50,0.2),transparent);margin:1.5rem 0;}

/* STATS */
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:0.8rem;margin-bottom:1.2rem;}
.sbox{border-radius:13px;padding:1.1rem 0.9rem;text-align:center;position:relative;overflow:hidden;}
.sbox::before{content:'';position:absolute;top:0;left:0;right:0;height:2px;}
.sg{background:rgba(180,255,50,0.07);border:1px solid rgba(180,255,50,0.15);}  
.sg::before{background:linear-gradient(90deg,#b4ff32,#4ade80);}
.sw{background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.07);}
.sw::before{background:linear-gradient(90deg,rgba(255,255,255,0.3),rgba(255,255,255,0.08));}
.sok{background:rgba(180,255,50,0.07);border:1px solid rgba(180,255,50,0.15);}
.sok::before{background:linear-gradient(90deg,#b4ff32,#4ade80);}
.serr{background:rgba(251,146,60,0.07);border:1px solid rgba(251,146,60,0.15);}
.serr::before{background:linear-gradient(90deg,#fb923c,#f87171);}
.sn{font-family:'Fira Code',monospace;font-size:1.8rem;font-weight:500;line-height:1;}
.sg .sn,.sok .sn{color:#b4ff32;}
.sw .sn{color:#fff;}
.serr .sn{color:#fb923c;font-size:1rem;padding-top:0.45rem;}
.sok .sn{font-size:1rem;padding-top:0.45rem;}
.sl{font-size:0.56rem;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;color:rgba(255,255,255,0.18);margin-top:0.4rem;}

/* RESULT */
.rcard{background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.07);border-radius:16px;overflow:hidden;position:relative;}
.rcard::after{content:'';position:absolute;top:0;left:0;right:0;height:1px;background:linear-gradient(90deg,transparent,rgba(180,255,50,0.35),transparent);}
.rbar{display:flex;justify-content:space-between;align-items:center;padding:0.85rem 1.3rem;background:rgba(180,255,50,0.03);border-bottom:1px solid rgba(255,255,255,0.05);}
.rlbl{font-size:0.6rem;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;color:rgba(255,255,255,0.25);}
.rmeta{font-family:'Fira Code',monospace;font-size:0.6rem;color:#b4ff32;}
.rbody{padding:1.3rem;font-family:'Fira Code',monospace;font-size:0.77rem;line-height:1.95;color:rgba(255,255,255,0.45);white-space:pre-wrap;word-break:break-word;max-height:370px;overflow-y:auto;}
.rbody::-webkit-scrollbar{width:3px;}
.rbody::-webkit-scrollbar-thumb{background:rgba(180,255,50,0.25);border-radius:2px;}

/* TAGS */
.trow{display:flex;flex-wrap:wrap;gap:0.4rem;margin-bottom:1rem;}
.rtag{font-family:'Fira Code',monospace;font-size:0.6rem;padding:0.2rem 0.58rem;border-radius:5px;background:rgba(251,146,60,0.08);border:1px solid rgba(251,146,60,0.2);color:#fb923c;}

/* DOWNLOAD */
.stDownloadButton>button{
    background:rgba(255,255,255,0.04) !important;border:1px solid rgba(255,255,255,0.08) !important;
    color:rgba(255,255,255,0.35) !important;font-family:'Inter',sans-serif !important;
    font-size:0.8rem !important;font-weight:600 !important;border-radius:9px !important;
    padding:0.6rem 1rem !important;width:100% !important;transition:all 0.2s !important;
}
.stDownloadButton>button:hover{background:rgba(180,255,50,0.07) !important;border-color:rgba(180,255,50,0.25) !important;color:#b4ff32 !important;}
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div class="sb-logo">
    <div class="sb-icon">⚡</div>
    <div class="sb-brand">DocuAI</div>
    <div class="sb-ver">v2.0 · enterprise</div>
</div>
<div class="sb-sec"><div class="sb-lbl">🛡️ Privacy Shield</div></div>
""", unsafe_allow_html=True)

# Simple native checkboxes — fastest, zero rerun
ri  = st.sidebar.checkbox("🪪  Aadhaar · SSN · PAN",   value=st.session_state.ri,  key="ri")
rp  = st.sidebar.checkbox("📞  Phone & Email",          value=st.session_state.rp,  key="rp")
rb  = st.sidebar.checkbox("💳  Bank · Cards · UPI",    value=st.session_state.rb,  key="rb")
rpw = st.sidebar.checkbox("🔑  Passwords · Keys",      value=st.session_state.rpw, key="rpw")
rn  = st.sidebar.checkbox("👤  Personal Names",         value=st.session_state.rn,  key="rn")
rd  = st.sidebar.checkbox("📅  Dates of Birth",         value=st.session_state.rd,  key="rd")

st.sidebar.markdown('<div class="sb-sec"><div class="sb-lbl">⚙️ Output</div></div>', unsafe_allow_html=True)
show_redacted = st.sidebar.checkbox("Show [REDACTED] tags", value=True, key="sr")

st.sidebar.markdown("""
<div class="sb-footer">
    Powered by Groq<br>
    LLaMA 4 Vision · LLaMA 3.1<br>
    Dual-layer redaction<br>
    © 2025 DocuAI
</div>
""", unsafe_allow_html=True)

active = sum([ri, rp, rb, rpw, rn, rd])

# ── MAIN ──────────────────────────────────────────────────────────────
st.markdown('<div class="main">', unsafe_allow_html=True)

# Tab nav
t1, t2, t3, _, ts = st.columns([1, 1, 1, 5, 2.5])
with t1:
    if st.button("⚡ Extract", type="primary" if st.session_state.tab=="Extract" else "secondary"): st.session_state.tab="Extract"
with t2:
    if st.button("🕓 History", type="primary" if st.session_state.tab=="History" else "secondary"): st.session_state.tab="History"
with t3:
    if st.button("⚙️ Settings", type="primary" if st.session_state.tab=="Settings" else "secondary"): st.session_state.tab="Settings"
with ts:
    st.markdown('<div class="nav-status" style="justify-content:flex-end;padding-top:0.35rem"><span class="pulse"></span>&nbsp; AI Engine Online</div>', unsafe_allow_html=True)

st.markdown('<div class="gline"></div>', unsafe_allow_html=True)

# ── HISTORY ───────────────────────────────────────────────────────────
if st.session_state.tab == "History":
    st.markdown('<div class="hero"><div class="hero-tag">🕓 Session Logs</div><div class="hero-h1">Extraction <em>History</em></div></div>', unsafe_allow_html=True)
    if not st.session_state.history:
        st.markdown('<div class="card" style="padding:3rem;text-align:center"><div style="font-size:2rem;margin-bottom:0.8rem">📂</div><div style="color:rgba(255,255,255,0.25);font-size:0.88rem">No history yet. Upload a document to begin.</div></div>', unsafe_allow_html=True)
    else:
        for h in st.session_state.history:
            c = "#b4ff32" if h["status"]=="CLEAN" else "#fb923c"
            st.markdown(f'<div class="card" style="padding:1rem 1.4rem;margin-bottom:0.7rem;display:flex;align-items:center;justify-content:space-between"><div><div style="font-size:0.82rem;font-weight:700;color:#fff">📎 {h["name"]}</div><div style="font-size:0.63rem;color:rgba(255,255,255,0.22);font-family:Fira Code,monospace;margin-top:0.2rem">{h["words"]:,} words · {h["redacted"]} redacted · {h["time"]}</div></div><div style="font-family:Fira Code,monospace;font-size:0.68rem;color:{c};background:rgba(255,255,255,0.04);padding:0.28rem 0.75rem;border-radius:7px;border:1px solid {c}33">{h["status"]}</div></div>', unsafe_allow_html=True)
        if st.button("🗑️ Clear History"): st.session_state.history=[]; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True); st.stop()

# ── SETTINGS ──────────────────────────────────────────────────────────
if st.session_state.tab == "Settings":
    st.markdown('<div class="hero"><div class="hero-tag">⚙️ Configuration</div><div class="hero-h1">App <em>Settings</em></div></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="medium")
    with c1:
        st.markdown("""<div class="card"><div class="ch"><div class="ch-left"><div class="cico ico-g">🤖</div><div><div class="ct">AI Models</div><div class="cd">Groq inference engine</div></div></div></div><div class="cb">
        <div class="tog on"><span class="tog-lbl">Extraction Model</span><span style="font-family:Fira Code,monospace;font-size:0.6rem;color:#b4ff32">LLaMA 4 Scout Vision</span></div>
        <div class="tog on"><span class="tog-lbl">Redaction Model</span><span style="font-family:Fira Code,monospace;font-size:0.6rem;color:#b4ff32">LLaMA 3.1-8B Instant</span></div>
        <div class="tog on"><span class="tog-lbl">Temperature</span><span style="font-family:Fira Code,monospace;font-size:0.6rem;color:#b4ff32">0.0 (deterministic)</span></div>
        <div class="tog on"><span class="tog-lbl">Redaction Layers</span><span style="font-family:Fira Code,monospace;font-size:0.6rem;color:#b4ff32">AI + Regex fallback</span></div>
        </div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""<div class="card"><div class="ch"><div class="ch-left"><div class="cico ico-w">📁</div><div><div class="ct">File Formats</div><div class="cd">Supported input types</div></div></div></div><div class="cb">
        <div class="tog on"><span class="tog-lbl">📄 PDF</span><span style="font-family:Fira Code,monospace;font-size:0.6rem;color:#b4ff32">pypdf + Vision OCR</span></div>
        <div class="tog on"><span class="tog-lbl">🖼️ Images</span><span style="font-family:Fira Code,monospace;font-size:0.6rem;color:#b4ff32">JPG, PNG via LLaMA 4</span></div>
        <div class="tog on"><span class="tog-lbl">📝 DOCX</span><span style="font-family:Fira Code,monospace;font-size:0.6rem;color:#b4ff32">python-docx</span></div>
        <div class="tog on"><span class="tog-lbl">📊 XLSX</span><span style="font-family:Fira Code,monospace;font-size:0.6rem;color:#b4ff32">openpyxl all sheets</span></div>
        <div class="tog on"><span class="tog-lbl">📑 PPTX</span><span style="font-family:Fira Code,monospace;font-size:0.6rem;color:#b4ff32">python-pptx + Vision</span></div>
        </div></div>""", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True); st.stop()

# ── EXTRACT TAB ───────────────────────────────────────────────────────
st.markdown('<div class="hero"><div class="hero-tag">⚡ Document Intelligence Platform</div><div class="hero-h1">Extract, Shield & <em>Deliver.</em></div><div class="hero-sub">Upload any document. Get clean structured text instantly with automatic AI-powered redaction.</div></div>', unsafe_allow_html=True)

col1, col2 = st.columns([1.15, 0.85], gap="medium")

with col1:
    st.markdown('<div class="card"><div class="ch"><div class="ch-left"><div class="cico ico-g">📤</div><div><div class="ct">Upload Document</div><div class="cd">PDF, Image, Word, Excel, PowerPoint</div></div></div><span class="cbadge bg">AI Ready</span></div><div class="cb"><div class="fmt-row"><span class="fmt f1">PDF</span><span class="fmt f2">JPG·PNG</span><span class="fmt f3">DOCX</span><span class="fmt f4">XLSX</span><span class="fmt f5">PPTX</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="upload-drop">', unsafe_allow_html=True)
    uploaded = st.file_uploader("u", type=["pdf","png","jpg","jpeg","docx","xlsx","pptx","ppt"], label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
    if uploaded:
        sz=uploaded.size/1024
        st.markdown(f'<div class="fp"><span>📎</span><span class="fp-name">{uploaded.name}</span><span class="fp-tag">{uploaded.name.split(".")[-1].upper()}</span><span class="fp-tag">{"%.0f KB"%sz if sz<1024 else "%.1f MB"%(sz/1024)}</span></div>', unsafe_allow_html=True)
    run = st.button("⚡  Extract & Apply Privacy Shield", use_container_width=True)
    st.markdown('</div></div>', unsafe_allow_html=True)

with col2:
    shields=[("🪪","Aadhaar · SSN · PAN",ri),("📞","Phone & Email",rp),("💳","Bank · Cards · UPI",rb),("🔑","Passwords · Keys",rpw),("👤","Personal Names",rn),("📅","Dates of Birth",rd)]
    rows="".join(f'<div class="tog {"on" if a else ""}"><span class="tog-lbl">{ic} &nbsp;{lb}</span><div class="tog-pill {"on" if a else ""}"></div></div>' for ic,lb,a in shields)
    st.markdown(f'<div class="card"><div class="ch"><div class="ch-left"><div class="cico ico-w">🛡️</div><div><div class="ct">Privacy Shield</div><div class="cd">{active}/6 active · toggle in sidebar ☰</div></div></div><span class="cbadge {"bg" if active>0 else "bw"}">{"ON" if active>0 else "OFF"}</span></div><div class="cb">{rows}</div></div>', unsafe_allow_html=True)

# ── LOGIC ─────────────────────────────────────────────────────────────
def build_rules():
    r=[]
    if ri:  r.append("Aadhaar (12-digit, XXXX XXXX XXXX), SSN, PAN (ABCDE1234F), passport, driving license, voter ID")
    if rp:  r.append("phone numbers (+91 or 10-digit), email addresses")
    if rb:  r.append("bank account numbers, IFSC codes, credit/debit card numbers, CVV, UPI IDs")
    if rpw: r.append("passwords, API keys, tokens, OTPs, PINs")
    if rn:  r.append("full names appearing after labels like 'Name:', 'नाम:'")
    if rd:  r.append("dates of birth in any format, DOB, जन्म तिथि")
    return r

@st.cache_data(show_spinner=False)
def pdf_text(fb):
    try:
        import pypdf; r=pypdf.PdfReader(io.BytesIO(fb))
        return "".join(p.extract_text() or "" for p in r.pages).strip() or None
    except: return None

@st.cache_data(show_spinner=False)
def docx_text(fb):
    try:
        import docx; d=docx.Document(io.BytesIO(fb))
        return "\n".join(p.text for p in d.paragraphs if p.text.strip()).strip() or None
    except: return None

@st.cache_data(show_spinner=False)
def xlsx_text(fb):
    try:
        import openpyxl; wb=openpyxl.load_workbook(io.BytesIO(fb),data_only=True); rows=[]
        for s in wb.worksheets:
            rows.append(f"[Sheet: {s.title}]")
            for row in s.iter_rows(values_only=True):
                l=" | ".join(str(c) for c in row if c is not None)
                if l.strip(): rows.append(l)
        return "\n".join(rows).strip() or None
    except: return None

@st.cache_data(show_spinner=False)
def pptx_text(fb):
    try:
        from pptx import Presentation; p=Presentation(io.BytesIO(fb)); lines=[]
        for i,s in enumerate(p.slides,1):
            lines.append(f"[Slide {i}]")
            for sh in s.shapes:
                if hasattr(sh,"text") and sh.text.strip(): lines.append(sh.text.strip())
        return "\n".join(lines).strip() or None
    except: return None

@st.cache_data(show_spinner=False)
def img_text(fb, mime):
    b64=base64.b64encode(fb).decode()
    r=client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role":"user","content":[
            {"type":"image_url","image_url":{"url":f"data:{mime};base64,{b64}"}},
            {"type":"text","text":"""Analyze this image:
1. Extract ALL visible text exactly as it appears (signs, labels, documents, watermarks, etc.)
2. If little/no text, describe what you see in detail (people, objects, setting, colors, actions)

Format:
TEXT FOUND:
[extracted text or 'No readable text found']

IMAGE DESCRIPTION:
[detailed description of image contents]"""}
        ]}], max_tokens=2000)
    return r.choices[0].message.content.strip()

def regex_redact(text, ph):
    c=0; rm=[]
    if ri:
        n=re.sub(r'\b\d{4}\s?\d{4}\s?\d{4}\b',ph,text)
        if n!=text: c+=1;rm.append("Aadhaar");text=n
        n=re.sub(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b',ph,text)
        if n!=text: c+=1;rm.append("PAN");text=n
    if rp:
        n=re.sub(r'\b(\+91[\s-]?)?[6-9]\d{9}\b',ph,text)
        if n!=text: c+=1;rm.append("phone");text=n
        n=re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',ph,text)
        if n!=text: c+=1;rm.append("email");text=n
    if rb:
        n=re.sub(r'\b(?:\d[ -]*?){13,16}\b',ph,text)
        if n!=text: c+=1;rm.append("card");text=n
        n=re.sub(r'\b[A-Z]{4}0[A-Z0-9]{6}\b',ph,text)
        if n!=text: c+=1;rm.append("IFSC");text=n
    if rd:
        n=re.sub(r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}\b',ph,text)
        if n!=text: c+=1;rm.append("DOB");text=n
    if rn:
        n=re.sub(r'(Name|नाम)\s*[:\-]\s*[A-Za-z\s]{3,40}',lambda m:m.group(0).split(':')[0]+': '+ph,text)
        if n!=text: c+=1;rm.append("name");text=n
    return text, rm, c

def ai_redact(text, rules):
    ph = "[REDACTED]" if show_redacted else "████"
    if not rules: return text, [], 0
    resp=client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role":"system","content":"Strict data privacy engine. Return only valid JSON."},
            {"role":"user","content":f'Redact ALL sensitive data with "{ph}".\nREDACT:\n'+"\n".join(f"- {r}" for r in rules)+f'\nKeep surrounding text. When uncertain redact it.\nReturn ONLY JSON: {{"clean_text":"...","redacted_items":["..."],"redaction_count":0}}\nTEXT:\n{text[:6000]}'}
        ], temperature=0.0, max_tokens=4000)
    raw=re.sub(r'```json|```','',resp.choices[0].message.content.strip()).strip()
    try:
        res=json.loads(raw); clean=res.get("clean_text",text); items=res.get("redacted_items",[]); count=res.get("redaction_count",0)
        clean,ei,ec=regex_redact(clean,ph)
        return clean, items+ei, count+ec
    except: return regex_redact(text, ph)

# ── PROCESS ───────────────────────────────────────────────────────────
if run and not uploaded:
    st.error("Please upload a document first.")

if run and uploaded:
    fb=uploaded.read(); mime=uploaded.type; name=uploaded.name.lower(); raw=None

    with st.spinner("⚡ Extracting..."):
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
    st.session_state.history.insert(0,{"name":uploaded.name,"words":wc,"redacted":count,"status":"CLEAN" if is_clean else "REDACTED","time":datetime.now().strftime("%d %b %Y, %I:%M %p")})

    st.markdown('<div class="gline"></div>', unsafe_allow_html=True)
    sc="sok" if is_clean else "serr"; sv="✓ CLEAN" if is_clean else "⚠ REDACTED"
    st.markdown(f'<div class="stats"><div class="sbox sg"><div class="sn">{wc:,}</div><div class="sl">Words</div></div><div class="sbox sw"><div class="sn">{count}</div><div class="sl">Redacted</div></div><div class="sbox {sc}"><div class="sn">{sv}</div><div class="sl">Status</div></div></div>', unsafe_allow_html=True)

    if items:
        st.markdown('<div class="trow">'+"".join(f'<span class="rtag">⛔ {i}</span>' for i in set(items))+'</div>', unsafe_allow_html=True)

    st.markdown(f'<div class="rcard"><div class="rbar"><span class="rlbl">Extracted Content</span><span class="rmeta">{len(clean):,} chars · {wc:,} words</span></div><div class="rbody">{clean}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    ca,cb=st.columns(2)
    ca.download_button("⬇ TXT", clean, f"{uploaded.name}_clean.txt","text/plain",use_container_width=True)
    cb.download_button("⬇ JSON", json.dumps({"file":uploaded.name,"text":clean,"words":wc,"redacted":count,"categories":list(set(items))},indent=2), f"{uploaded.name}_clean.json","application/json",use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)
