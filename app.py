import streamlit as st
import io
import re
from PIL import Image
import pytesseract

# ⚠ Windows users: uncomment and set path below
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

st.set_page_config(
    page_title="DocVault Enterprise",
    page_icon="🔐",
    layout="wide"
)

# ══════════════════════════════════════════════════════════
# GLOBAL STYLING — Colorful vivid theme
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

/* ══ BASE ══ */
.stApp {
    background: #050714 !important;
    color: #f0f0ff !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
}

/* Vivid animated blob background */
.stApp::before {
    content: '';
    position: fixed; inset: 0;
    background:
        radial-gradient(ellipse 900px 800px at -10% -10%, rgba(99,102,241,0.65)  0%, transparent 55%),
        radial-gradient(ellipse 800px 700px at 110%  15%, rgba(236,72,153,0.55)  0%, transparent 55%),
        radial-gradient(ellipse 700px 650px at 110% 110%, rgba(245,158,11,0.40)  0%, transparent 55%),
        radial-gradient(ellipse 650px 600px at -10% 110%, rgba(16,185,129,0.40)  0%, transparent 55%),
        radial-gradient(ellipse 500px 450px at  50%  50%, rgba(139,92,246,0.18)  0%, transparent 55%),
        radial-gradient(ellipse 400px 350px at  80%  55%, rgba(251,146,60,0.22)  0%, transparent 50%);
    pointer-events: none; z-index: 0;
    animation: blobDrift 22s ease-in-out infinite alternate;
    filter: blur(38px);
}
@keyframes blobDrift {
    0%   { transform: scale(1)    translate(0px,    0px);  }
    25%  { transform: scale(1.03) translate(22px,  -18px); }
    50%  { transform: scale(0.97) translate(-16px,  22px); }
    75%  { transform: scale(1.04) translate(12px,   14px); }
    100% { transform: scale(0.98) translate(-10px, -12px); }
}

.block-container {
    padding-top: 0 !important;
    padding-bottom: 3rem !important;
    max-width: 1260px !important;
    position: relative; z-index: 1;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(255,255,255,0.12); border-radius: 10px; }

/* ══ NAV ══ */
.dv-nav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1.1rem 0;
    border-bottom: 1px solid rgba(255,255,255,0.08);
    margin-bottom: 0;
    background: rgba(5,7,20,0.6);
    backdrop-filter: blur(16px);
}
.dv-logo-wrap { display: flex; align-items: center; gap: 0.5rem; }
.dv-logo-icon {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #6366f1, #ec4899);
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.9rem;
    box-shadow: 0 3px 12px rgba(99,102,241,0.5);
}
.dv-logo-text {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.08rem; font-weight: 800; color: #f0f0ff; letter-spacing: -0.3px;
}
.dv-logo-text span {
    background: linear-gradient(90deg, #a78bfa, #f472b6);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.dv-nav-badge {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem; letter-spacing: 0.18em; text-transform: uppercase;
    color: rgba(255,255,255,0.4); border: 1px solid rgba(255,255,255,0.1);
    background: rgba(255,255,255,0.05);
    padding: 0.28rem 0.9rem; border-radius: 100px;
}
.dv-status {
    display: flex; align-items: center; gap: 0.4rem;
    font-size: 0.78rem; font-weight: 500; color: rgba(255,255,255,0.5);
}
.dv-status-dot {
    width: 7px; height: 7px; background: #22c55e; border-radius: 50%;
    box-shadow: 0 0 8px rgba(34,197,94,0.7); animation: sDot 2.5s ease-in-out infinite;
}
@keyframes sDot { 0%,100%{opacity:1;} 50%{opacity:0.35;} }

/* ══ HERO ══ */
.dv-hero { text-align: center; padding: 2.8rem 0 2.2rem; }
.dv-hero-tag {
    display: inline-flex; align-items: center; gap: 0.4rem;
    background: rgba(99,102,241,0.15); border: 1px solid rgba(99,102,241,0.3);
    border-radius: 100px; padding: 0.3rem 0.95rem;
    font-size: 0.76rem; font-weight: 600; color: #a78bfa;
    margin-bottom: 1.2rem; letter-spacing: 0.03em;
}
.dv-hero-tag::before {
    content: ''; width: 6px; height: 6px;
    background: linear-gradient(135deg, #6366f1, #ec4899);
    border-radius: 50%; flex-shrink: 0;
    animation: tagPulse 2s ease-in-out infinite;
}
@keyframes tagPulse { 0%,100%{opacity:1;} 50%{opacity:0.4;} }
.dv-h1 {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: clamp(2.2rem, 4.5vw, 3.5rem);
    font-weight: 800; line-height: 1.1; letter-spacing: -1px;
    color: #f0f0ff; margin-bottom: 0;
}
.dv-h1-accent {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: clamp(2.2rem, 4.5vw, 3.5rem);
    font-weight: 800; line-height: 1.1; letter-spacing: -1px;
    background: linear-gradient(90deg, #818cf8, #f472b6, #fb923c);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; display: block; margin-bottom: 0.9rem;
}
.dv-hero-sub {
    font-size: 0.97rem; color: rgba(255,255,255,0.45);
    max-width: 450px; margin: 0 auto; line-height: 1.7;
}

/* ══ CARD ══ */
.dv-card {
    background: rgba(10,8,28,0.70);
    border: 1px solid rgba(99,102,241,0.15);
    border-radius: 18px; padding: 1.5rem 1.5rem 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 30px rgba(0,0,0,0.3), 0 1px 4px rgba(0,0,0,0.2);
    backdrop-filter: blur(18px);
}

/* ══ SECTION LABEL ══ */
.dv-sec-label {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: rgba(255,255,255,0.35);
    margin-bottom: 0.9rem; display: flex; align-items: center; gap: 0.5rem;
}
.dv-sec-label::after { content:''; flex:1; height:1px; background:rgba(255,255,255,0.07); }

/* ══ CHECKBOXES ══ */
.stCheckbox > label {
    font-size: 0.9rem !important; font-weight: 500 !important;
    color: rgba(255,255,255,0.75) !important; gap: 0.5rem !important;
}

/* ══ RADIO ══ */
.stRadio > label { font-size: 0.9rem !important; color: rgba(255,255,255,0.7) !important; }
div[data-testid="stRadio"] label { font-size: 0.92rem !important; color: rgba(255,255,255,0.75) !important; }

/* ══ FILE UPLOADER ══ */
[data-testid="stFileUploader"] section {
    background: rgba(99,102,241,0.06) !important;
    border: 2px dashed rgba(99,102,241,0.35) !important;
    border-radius: 14px !important;
    transition: all 0.2s !important;
}
[data-testid="stFileUploader"] section:hover {
    border-color: rgba(99,102,241,0.65) !important;
    background: rgba(99,102,241,0.10) !important;
}
[data-testid="stFileUploader"] section p { color: rgba(255,255,255,0.45) !important; }

/* ══ TEXT AREA / INPUT ══ */
textarea, .stTextInput input {
    background: rgba(255,255,255,0.05) !important;
    border: 1.5px solid rgba(255,255,255,0.1) !important;
    border-radius: 12px !important; color: #f0f0ff !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 0.95rem !important;
    padding: 0.85rem 1rem !important; line-height: 1.6 !important;
    transition: all 0.2s !important; caret-color: #818cf8 !important;
}
textarea:focus, .stTextInput input:focus {
    border-color: rgba(99,102,241,0.55) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important; outline: none !important;
    background: rgba(255,255,255,0.07) !important;
}
textarea::placeholder, .stTextInput input::placeholder { color: rgba(255,255,255,0.25) !important; }

/* ══ PRIMARY BUTTON ══ */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #6366f1, #ec4899) !important;
    border: none !important; border-radius: 12px !important; color: #fff !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 700 !important;
    font-size: 1rem !important; padding: 0.88rem 1.5rem !important;
    margin-top: 0.65rem !important; transition: all 0.2s !important;
    box-shadow: 0 4px 18px rgba(99,102,241,0.45) !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    opacity: 0.9 !important; transform: translateY(-1px) !important;
    box-shadow: 0 8px 28px rgba(99,102,241,0.55) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ══ DOWNLOAD BUTTON ══ */
.stDownloadButton > button {
    background: rgba(255,255,255,0.06) !important;
    border: 1.5px solid rgba(255,255,255,0.12) !important;
    color: rgba(255,255,255,0.7) !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; border-radius: 9px !important;
    padding: 0.48rem 1rem !important; font-size: 0.85rem !important;
    margin-top: 0 !important; transition: all 0.18s !important;
}
.stDownloadButton > button:hover {
    border-color: rgba(99,102,241,0.5) !important;
    color: #a78bfa !important; background: rgba(99,102,241,0.1) !important;
}

/* ══ PROGRESS BAR ══ */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #6366f1, #f472b6) !important;
    border-radius: 100px !important;
}
.stProgress > div > div {
    background: rgba(255,255,255,0.08) !important; border-radius: 100px !important;
}

/* ══ SECURITY BADGES ══ */
.sec-badge-row {
    display: flex; align-items: center; justify-content: space-between;
    background: rgba(255,255,255,0.04); border: 1px solid rgba(255,255,255,0.08);
    border-radius: 10px; padding: 0.7rem 1rem; margin-bottom: 0.5rem;
    transition: background 0.18s;
}
.sec-badge-row:hover { background: rgba(255,255,255,0.07); }
.sec-badge-label { font-size: 0.9rem; font-weight: 600; color: rgba(255,255,255,0.8); }
.sec-badge-pass {
    display: inline-flex; align-items: center; gap: 0.3rem;
    font-size: 0.75rem; font-weight: 700; color: #4ade80;
    background: rgba(74,222,128,0.12); border: 1px solid rgba(74,222,128,0.25);
    border-radius: 6px; padding: 0.18rem 0.55rem;
}
.sec-badge-fail {
    display: inline-flex; align-items: center; gap: 0.3rem;
    font-size: 0.75rem; font-weight: 700; color: #f87171;
    background: rgba(248,113,113,0.12); border: 1px solid rgba(248,113,113,0.25);
    border-radius: 6px; padding: 0.18rem 0.55rem;
}

/* ══ SCORE DISPLAY ══ */
.score-display {
    display: flex; align-items: center; gap: 1.5rem;
    background: rgba(99,102,241,0.08); border: 1px solid rgba(99,102,241,0.2);
    border-radius: 14px; padding: 1rem 1.2rem; margin-top: 0.5rem;
}
.score-num {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 2.2rem; font-weight: 800; line-height: 1;
}
.score-label {
    font-size: 0.62rem; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; color: rgba(255,255,255,0.3); margin-bottom: 0.15rem;
}
.score-bar-wrap { flex: 1; }
.score-bar-bg { height: 8px; background: rgba(255,255,255,0.08); border-radius: 100px; overflow: hidden; }
.score-bar-fill { height: 100%; border-radius: 100px; }

/* ══ OUTPUT HEADER (Copy + Download top-right) ══ */
.output-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 0.75rem;
}
.output-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: rgba(255,255,255,0.35);
    display: flex; align-items: center; gap: 0.5rem;
}
.output-title::after { content:''; width:40px; height:1px; background:rgba(255,255,255,0.07); }
.output-actions { display: flex; align-items: center; gap: 0.5rem; }
.copy-btn {
    display: inline-flex; align-items: center; gap: 0.35rem;
    font-family: 'DM Sans', sans-serif; font-size: 0.8rem; font-weight: 600;
    color: #a78bfa; background: rgba(99,102,241,0.1);
    border: 1.5px solid rgba(99,102,241,0.25);
    border-radius: 8px; padding: 0.38rem 0.85rem; cursor: pointer;
    transition: all 0.18s;
}
.copy-btn:hover { border-color: rgba(99,102,241,0.5); background: rgba(99,102,241,0.18); }

/* ══ SIDEBAR CARDS ══ */
.sc {
    background: rgba(10,8,28,0.72); border: 1px solid rgba(99,102,241,0.14);
    border-radius: 14px; padding: 1.1rem 1.15rem; margin-bottom: 0.85rem;
    box-shadow: 0 3px 20px rgba(0,0,0,0.25); backdrop-filter: blur(14px);
}
.sc-ttl {
    font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.72rem;
    font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
    color: rgba(255,255,255,0.35); margin-bottom: 0.85rem;
    display: flex; align-items: center; gap: 0.45rem;
}
.sc-ttl::after { content:''; flex:1; height:1px; background:rgba(255,255,255,0.07); }

/* ══ ALERTS ══ */
.stAlert { background:rgba(99,102,241,0.1) !important; border:1px solid rgba(99,102,241,0.25) !important; border-radius:10px !important; color:#c7d2fe !important; }
.stSuccess { background:rgba(74,222,128,0.1) !important; border:1px solid rgba(74,222,128,0.22) !important; border-radius:10px !important; color:#86efac !important; }
.stWarning { background:rgba(251,191,36,0.1) !important; border:1px solid rgba(251,191,36,0.22) !important; border-radius:10px !important; color:#fde68a !important; }
.stError   { background:rgba(248,113,113,0.1) !important; border:1px solid rgba(248,113,113,0.22) !important; border-radius:10px !important; color:#fca5a5 !important; }
.stSpinner > div { border-top-color: #818cf8 !important; }
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] { background:transparent !important; }
div[data-testid="stForm"] { background:transparent !important; border:none !important; box-shadow:none !important; padding:0 !important; }

/* ══ TABS ══ */
div[data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.05) !important;
    border-radius: 10px !important; padding: 4px !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    gap: 2px !important; margin-bottom: 1rem !important; width: fit-content !important;
}
div[data-baseweb="tab"] {
    border-radius: 7px !important; color: rgba(255,255,255,0.35) !important;
    font-weight: 600 !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 0.9rem !important; padding: 0.42rem 1.1rem !important; transition: all 0.18s !important;
}
div[aria-selected="true"] {
    background: linear-gradient(135deg, #6366f1, #ec4899) !important;
    color: white !important; box-shadow: 0 2px 10px rgba(99,102,241,0.4) !important;
}
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# SECURITY CONFIG
# ══════════════════════════════════════════════════════════
MALWARE_SIGS = [b"cmd.exe", b"powershell", b"eval(", b"WScript"]
MAGIC_BYTES  = {
    "pdf":  b"%PDF",
    "docx": b"PK",
    "xlsx": b"PK",
    "pptx": b"PK",
    "ppt":  b"\xd0\xcf\x11\xe0"
}

def check_magic(fb, ext):
    return fb.startswith(MAGIC_BYTES[ext]) if ext in MAGIC_BYTES else True

def check_malware(fb):
    return not any(sig in fb for sig in MALWARE_SIGS)

def check_integrity(fb, ext):
    try:
        if ext == "pdf":
            import pypdf; pypdf.PdfReader(io.BytesIO(fb))
        elif ext == "docx":
            import docx; docx.Document(io.BytesIO(fb))
        elif ext == "xlsx":
            import openpyxl; openpyxl.load_workbook(io.BytesIO(fb))
        elif ext in ["pptx","ppt"]:
            from pptx import Presentation; Presentation(io.BytesIO(fb))
        return True
    except: return False

def extract_text(fb, ext):
    if ext in ["png","jpg","jpeg"]:
        return pytesseract.image_to_string(Image.open(io.BytesIO(fb)))
    if ext == "pdf":
        import pypdf
        r = pypdf.PdfReader(io.BytesIO(fb))
        return "\n".join(p.extract_text() or "" for p in r.pages)
    if ext == "docx":
        import docx
        return "\n".join(p.text for p in docx.Document(io.BytesIO(fb)).paragraphs)
    if ext == "xlsx":
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(fb), data_only=True)
        lines = []
        for sh in wb.worksheets:
            for row in sh.iter_rows(values_only=True):
                line = " | ".join(str(c) for c in row if c)
                if line: lines.append(line)
        return "\n".join(lines)
    if ext in ["pptx","ppt"]:
        from pptx import Presentation
        prs = Presentation(io.BytesIO(fb))
        return "\n".join(
            shape.text.strip()
            for slide in prs.slides for shape in slide.shapes
            if hasattr(shape,"text") and shape.text.strip()
        )
    if ext == "txt":
        return fb.decode("utf-8", errors="ignore")
    return None


# ══════════════════════════════════════════════════════════
# NAV
# ══════════════════════════════════════════════════════════
st.markdown("""
<div class="dv-nav">
  <div class="dv-logo-wrap">
    <div class="dv-logo-icon">🔐</div>
    <div class="dv-logo-text">DocVault <span>Enterprise</span></div>
  </div>
  <div class="dv-nav-badge">Secure Document Platform</div>
  <div class="dv-status"><div class="dv-status-dot"></div>Secure Mode</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════
st.markdown("""
<div class="dv-hero">
  <div class="dv-hero-tag">Enterprise-Grade Security</div>
  <h1 class="dv-h1">Secure Document</h1>
  <span class="dv-h1-accent">Validation &amp; Extraction</span>
  <p class="dv-hero-sub">Upload any document — DocVault validates, scans for threats, redacts sensitive data, and extracts clean text securely.</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# LAYOUT
# ══════════════════════════════════════════════════════════
left, right = st.columns([2.3, 1.1], gap="large")

# ══════════════════════════════════════════════════════════
# RIGHT SIDEBAR — always visible
# ══════════════════════════════════════════════════════════
with right:

    # ── SUPPORTED / NOT SUPPORTED ──
    st.markdown("""
<div style="background:rgba(10,8,28,0.72);border:1px solid rgba(99,102,241,0.14);border-radius:14px;padding:1.1rem 1.15rem;margin-bottom:0.85rem;backdrop-filter:blur(14px);box-shadow:0 3px 20px rgba(0,0,0,0.25);">

  <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:0.72rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:rgba(255,255,255,0.35);margin-bottom:0.9rem;display:flex;align-items:center;gap:0.45rem;">
    How It Works
    <span style="flex:1;height:1px;background:rgba(255,255,255,0.07);display:inline-block;"></span>
  </div>

  <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:0.66rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#4ade80;margin-bottom:0.45rem;">✓ &nbsp;Supported Formats</div>

  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid rgba(255,255,255,0.04);">
    <span style="width:17px;height:17px;border-radius:4px;background:rgba(74,222,128,0.12);border:1px solid rgba(74,222,128,0.25);display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#4ade80;flex-shrink:0;">✓</span>
    <span style="font-size:0.84rem;color:rgba(255,255,255,0.55);font-family:'DM Sans',sans-serif;">PDF documents</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid rgba(255,255,255,0.04);">
    <span style="width:17px;height:17px;border-radius:4px;background:rgba(74,222,128,0.12);border:1px solid rgba(74,222,128,0.25);display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#4ade80;flex-shrink:0;">✓</span>
    <span style="font-size:0.84rem;color:rgba(255,255,255,0.55);font-family:'DM Sans',sans-serif;">Word DOCX files</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid rgba(255,255,255,0.04);">
    <span style="width:17px;height:17px;border-radius:4px;background:rgba(74,222,128,0.12);border:1px solid rgba(74,222,128,0.25);display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#4ade80;flex-shrink:0;">✓</span>
    <span style="font-size:0.84rem;color:rgba(255,255,255,0.55);font-family:'DM Sans',sans-serif;">Excel XLSX spreadsheets</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid rgba(255,255,255,0.04);">
    <span style="width:17px;height:17px;border-radius:4px;background:rgba(74,222,128,0.12);border:1px solid rgba(74,222,128,0.25);display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#4ade80;flex-shrink:0;">✓</span>
    <span style="font-size:0.84rem;color:rgba(255,255,255,0.55);font-family:'DM Sans',sans-serif;">PowerPoint PPTX / PPT</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid rgba(255,255,255,0.04);">
    <span style="width:17px;height:17px;border-radius:4px;background:rgba(74,222,128,0.12);border:1px solid rgba(74,222,128,0.25);display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#4ade80;flex-shrink:0;">✓</span>
    <span style="font-size:0.84rem;color:rgba(255,255,255,0.55);font-family:'DM Sans',sans-serif;">Plain TXT files</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid rgba(255,255,255,0.08);">
    <span style="width:17px;height:17px;border-radius:4px;background:rgba(74,222,128,0.12);border:1px solid rgba(74,222,128,0.25);display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#4ade80;flex-shrink:0;">✓</span>
    <span style="font-size:0.84rem;color:rgba(255,255,255,0.55);font-family:'DM Sans',sans-serif;">Images PNG / JPG (OCR)</span>
  </div>

  <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:0.66rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#f87171;margin-top:0.8rem;margin-bottom:0.45rem;">✕ &nbsp;Not Supported</div>

  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid rgba(255,255,255,0.04);">
    <span style="width:17px;height:17px;border-radius:4px;background:rgba(248,113,113,0.1);border:1px solid rgba(248,113,113,0.22);display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#f87171;flex-shrink:0;">✕</span>
    <span style="font-size:0.84rem;color:rgba(255,255,255,0.55);font-family:'DM Sans',sans-serif;">Encrypted / password PDFs</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid rgba(255,255,255,0.04);">
    <span style="width:17px;height:17px;border-radius:4px;background:rgba(248,113,113,0.1);border:1px solid rgba(248,113,113,0.22);display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#f87171;flex-shrink:0;">✕</span>
    <span style="font-size:0.84rem;color:rgba(255,255,255,0.55);font-family:'DM Sans',sans-serif;">Scanned PDFs (no OCR layer)</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid rgba(255,255,255,0.04);">
    <span style="width:17px;height:17px;border-radius:4px;background:rgba(248,113,113,0.1);border:1px solid rgba(248,113,113,0.22);display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#f87171;flex-shrink:0;">✕</span>
    <span style="font-size:0.84rem;color:rgba(255,255,255,0.55);font-family:'DM Sans',sans-serif;">Files &gt; 200 MB</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;">
    <span style="width:17px;height:17px;border-radius:4px;background:rgba(248,113,113,0.1);border:1px solid rgba(248,113,113,0.22);display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#f87171;flex-shrink:0;">✕</span>
    <span style="font-size:0.84rem;color:rgba(255,255,255,0.55);font-family:'DM Sans',sans-serif;">Executable / script files</span>
  </div>

</div>
""", unsafe_allow_html=True)

    # ── REDACTION CONTROLS ──
    st.markdown("""
<div class="sc">
  <div class="sc-ttl">Redaction Controls</div>
</div>
""", unsafe_allow_html=True)

    rc1, rc2 = st.columns(2)
    with rc1:
        aadhaar = st.checkbox("Aadhaar No.")
        pan     = st.checkbox("PAN Number")
        ssn     = st.checkbox("SSN")
    with rc2:
        mobile  = st.checkbox("Mobile No.")
        dob     = st.checkbox("Date of Birth")

    st.markdown("<div style='margin-bottom:0.5rem;'></div>", unsafe_allow_html=True)

    # ── SECURITY INFO ──
    st.markdown("""
<div class="sc">
  <div class="sc-ttl">Security Checks</div>
  <div style="display:flex;flex-direction:column;gap:0.45rem;">
    <div style="display:flex;align-items:center;gap:0.6rem;font-size:0.84rem;color:rgba(255,255,255,0.6);">
      <span style="width:22px;height:22px;border-radius:6px;background:rgba(99,102,241,0.15);border:1px solid rgba(99,102,241,0.28);display:inline-flex;align-items:center;justify-content:center;font-size:0.7rem;flex-shrink:0;">🔍</span>
      File type validation
    </div>
    <div style="display:flex;align-items:center;gap:0.6rem;font-size:0.84rem;color:rgba(255,255,255,0.6);">
      <span style="width:22px;height:22px;border-radius:6px;background:rgba(236,72,153,0.12);border:1px solid rgba(236,72,153,0.25);display:inline-flex;align-items:center;justify-content:center;font-size:0.7rem;flex-shrink:0;">🛡️</span>
      Malware signature scan
    </div>
    <div style="display:flex;align-items:center;gap:0.6rem;font-size:0.84rem;color:rgba(255,255,255,0.6);">
      <span style="width:22px;height:22px;border-radius:6px;background:rgba(74,222,128,0.12);border:1px solid rgba(74,222,128,0.25);display:inline-flex;align-items:center;justify-content:center;font-size:0.7rem;flex-shrink:0;">✅</span>
      Structural integrity check
    </div>
    <div style="display:flex;align-items:center;gap:0.6rem;font-size:0.84rem;color:rgba(255,255,255,0.6);">
      <span style="width:22px;height:22px;border-radius:6px;background:rgba(251,146,60,0.12);border:1px solid rgba(251,146,60,0.25);display:inline-flex;align-items:center;justify-content:center;font-size:0.7rem;flex-shrink:0;">🔒</span>
      PII redaction engine
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# LEFT COLUMN — main content
# ══════════════════════════════════════════════════════════
with left:

    st.markdown('<div class="dv-card">', unsafe_allow_html=True)
    st.markdown('<div class="dv-sec-label">Input Source</div>', unsafe_allow_html=True)

    mode = st.radio(
        "Choose input type:",
        ["📁  Upload File", "📝  Paste Text"],
        horizontal=True,
        label_visibility="collapsed"
    )

    uploaded    = None
    manual_text = None

    if "Upload" in mode:
        uploaded = st.file_uploader(
            "Supported: PDF, DOCX, XLSX, PPTX, PPT, TXT, PNG, JPG",
            type=["pdf","docx","xlsx","pptx","ppt","txt","png","jpg","jpeg"],
            label_visibility="collapsed"
        )
    else:
        manual_text = st.text_area(
            "", height=220,
            placeholder="Paste your document text here…",
            label_visibility="collapsed"
        )

    if st.button("🔐  Secure Extract", key="btn_extract"):

        # ── FILE MODE ──
        if "Upload" in mode:
            if not uploaded:
                st.warning("Please upload a file first.")
                st.stop()

            file_bytes = uploaded.read()
            ext        = uploaded.name.split(".")[-1].lower()

            magic_ok     = check_magic(file_bytes, ext)
            malware_ok   = check_malware(file_bytes)
            integrity_ok = check_integrity(file_bytes, ext)

            st.markdown('<div class="dv-sec-label" style="margin-top:1.2rem;">Security Scan Results</div>', unsafe_allow_html=True)

            def badge(ok):
                return '<span class="sec-badge-pass">✓ Pass</span>' if ok else '<span class="sec-badge-fail">✗ Fail</span>'

            st.markdown(f"""
<div class="sec-badge-row"><span class="sec-badge-label">🔍 File Type Validation</span>{badge(magic_ok)}</div>
<div class="sec-badge-row"><span class="sec-badge-label">🛡️ Malware Scan</span>{badge(malware_ok)}</div>
<div class="sec-badge-row"><span class="sec-badge-label">✅ Integrity Check</span>{badge(integrity_ok)}</div>
""", unsafe_allow_html=True)

            score = 100
            if not magic_ok:     score -= 30
            if not malware_ok:   score -= 40
            if not integrity_ok: score -= 30

            color    = "#4ade80" if score == 100 else ("#fbbf24" if score >= 60 else "#f87171")
            bar_grad = "linear-gradient(90deg,#6366f1,#a78bfa)" if score == 100 else ("linear-gradient(90deg,#f59e0b,#fbbf24)" if score >= 60 else "linear-gradient(90deg,#ef4444,#f87171)")

            st.markdown(f"""
<div class="score-display">
  <div>
    <div class="score-label">Security Score</div>
    <div class="score-num" style="color:{color};">{score}</div>
    <div style="font-size:0.65rem;color:rgba(255,255,255,0.25);font-family:'DM Mono',monospace;">/ 100</div>
  </div>
  <div class="score-bar-wrap">
    <div class="score-label">Scan Confidence</div>
    <div class="score-bar-bg" style="margin-top:0.35rem;">
      <div class="score-bar-fill" style="width:{score}%;background:{bar_grad};"></div>
    </div>
    <div style="font-size:0.72rem;color:{color};font-family:'DM Mono',monospace;margin-top:0.35rem;font-weight:600;">{score}% complete</div>
  </div>
</div>
""", unsafe_allow_html=True)

            if not (magic_ok and malware_ok and integrity_ok):
                st.error("🚫 File blocked — one or more security checks failed.")
                st.stop()

            with st.spinner("Extracting text…"):
                raw_text = extract_text(file_bytes, ext)

        # ── TEXT MODE ──
        else:
            if not manual_text or not manual_text.strip():
                st.warning("Please paste some text first.")
                st.stop()

            raw_text = manual_text

            st.markdown('<div class="dv-sec-label" style="margin-top:1.2rem;">Security Scan Results</div>', unsafe_allow_html=True)
            st.markdown('<div class="sec-badge-row"><span class="sec-badge-label">📝 Text Mode</span><span class="sec-badge-pass">✓ Safe</span></div>', unsafe_allow_html=True)
            st.markdown("""
<div class="score-display">
  <div>
    <div class="score-label">Security Score</div>
    <div class="score-num" style="color:#4ade80;">100</div>
    <div style="font-size:0.65rem;color:rgba(255,255,255,0.25);font-family:'DM Mono',monospace;">/ 100</div>
  </div>
  <div class="score-bar-wrap">
    <div class="score-label">Scan Confidence</div>
    <div class="score-bar-bg" style="margin-top:0.35rem;">
      <div class="score-bar-fill" style="width:100%;background:linear-gradient(90deg,#6366f1,#a78bfa);"></div>
    </div>
    <div style="font-size:0.72rem;color:#4ade80;font-family:'DM Mono',monospace;margin-top:0.35rem;font-weight:600;">100% complete</div>
  </div>
</div>
""", unsafe_allow_html=True)

        if not raw_text or not raw_text.strip():
            st.warning("No readable text found in this file.")
            st.stop()

        # ── REDACT ──
        def redact(text):
            if aadhaar: text = re.sub(r"\b\d{4}\s?\d{4}\s?\d{4}\b", "[REDACTED_AADHAAR]", text)
            if pan:     text = re.sub(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",  "[REDACTED_PAN]", text)
            if mobile:  text = re.sub(r"\b[6-9]\d{9}\b",               "[REDACTED_MOBILE]", text)
            if dob:     text = re.sub(r"\b\d{2}[-/]\d{2}[-/]\d{4}\b", "[REDACTED_DOB]", text)
            if ssn:     text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b",       "[REDACTED_SSN]", text)
            return text

        clean_text = redact(raw_text)
        st.session_state["extracted_text"] = clean_text
        st.success("✅ Extraction complete — text is clean and ready.")

    # ── OUTPUT SECTION ──
    if "extracted_text" in st.session_state and st.session_state["extracted_text"]:
        clean = st.session_state["extracted_text"]

        st.markdown("""
<div class="output-header">
  <div class="output-title">Extracted Output</div>
  <div class="output-actions">
    <button class="copy-btn" onclick="
      const ta = document.querySelector('#dv-output-ta textarea');
      if(ta){navigator.clipboard.writeText(ta.value).then(()=>{
        this.innerHTML='✓ Copied!';
        this.style.color='#4ade80';
        this.style.borderColor='rgba(74,222,128,0.4)';
        this.style.background='rgba(74,222,128,0.1)';
        setTimeout(()=>{
          this.innerHTML='⧉ Copy Text';
          this.style.color='';this.style.borderColor='';this.style.background='';
        },2000);
      });}
    ">⧉ Copy Text</button>
  </div>
</div>
""", unsafe_allow_html=True)

        st.markdown('<div id="dv-output-ta">', unsafe_allow_html=True)
        st.text_area("", clean, height=420, label_visibility="collapsed", key="output_ta")
        st.markdown('</div>', unsafe_allow_html=True)

        col_dl, col_sp = st.columns([1, 3])
        with col_dl:
            st.download_button(
                "⬇ Download Clean Copy",
                data=clean.encode("utf-8"),
                file_name="docvault_clean_output.txt",
                mime="text/plain"
            )

    st.markdown('</div>', unsafe_allow_html=True)
