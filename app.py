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
# GLOBAL STYLING — Soft light lavender neumorphic
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

/* ══ BASE ══ */
.stApp {
    background: #eceef8 !important;
    color: #2d2f4a !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
}

/* Soft lavender gradient mesh — like reference */
.stApp::before {
    content: '';
    position: fixed; inset: 0;
    background:
        radial-gradient(ellipse 1100px 800px at  15%   0%, rgba(200,196,255,0.60) 0%, transparent 60%),
        radial-gradient(ellipse  900px 700px at  90%  10%, rgba(255,196,230,0.45) 0%, transparent 60%),
        radial-gradient(ellipse  800px 700px at   5%  90%, rgba(196,224,255,0.40) 0%, transparent 60%),
        radial-gradient(ellipse 1000px 600px at  95% 100%, rgba(220,196,255,0.38) 0%, transparent 60%),
        radial-gradient(ellipse  600px 500px at  50%  50%, rgba(255,210,240,0.20) 0%, transparent 55%);
    pointer-events: none; z-index: 0;
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
::-webkit-scrollbar-thumb { background: #c8c6e8; border-radius: 10px; }

/* ══ NAV ══ */
.dv-nav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1.1rem 0;
    border-bottom: 1px solid rgba(150,140,200,0.15);
    margin-bottom: 0;
    background: rgba(240,238,255,0.65);
    backdrop-filter: blur(14px);
}
.dv-logo-wrap { display: flex; align-items: center; gap: 0.5rem; }
.dv-logo-icon {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #8b7ff5, #d46bc8);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.88rem;
    box-shadow: 0 4px 14px rgba(139,127,245,0.35);
}
.dv-logo-text {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.08rem; font-weight: 800;
    color: #2d2f4a; letter-spacing: -0.3px;
}
.dv-logo-text span {
    background: linear-gradient(90deg, #8b7ff5, #d46bc8);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.dv-nav-badge {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem; letter-spacing: 0.18em; text-transform: uppercase;
    color: #8882b8;
    border: 1px solid rgba(139,127,245,0.2);
    background: rgba(255,255,255,0.55);
    padding: 0.28rem 0.9rem; border-radius: 100px;
    box-shadow: 0 1px 4px rgba(139,127,245,0.1);
}
.dv-status {
    display: flex; align-items: center; gap: 0.4rem;
    font-size: 0.78rem; font-weight: 500; color: #8882b8;
}
.dv-status-dot {
    width: 7px; height: 7px; background: #5dd88a; border-radius: 50%;
    box-shadow: 0 0 7px rgba(93,216,138,0.6); animation: sDot 2.5s ease-in-out infinite;
}
@keyframes sDot { 0%,100%{opacity:1;} 50%{opacity:0.35;} }

/* ══ HERO ══ */
.dv-hero { text-align: center; padding: 2.8rem 0 2.2rem; }
.dv-hero-tag {
    display: inline-flex; align-items: center; gap: 0.4rem;
    background: rgba(255,255,255,0.70);
    border: 1px solid rgba(139,127,245,0.22);
    border-radius: 100px; padding: 0.3rem 0.95rem;
    font-size: 0.76rem; font-weight: 600; color: #7b6fd4;
    margin-bottom: 1.2rem; letter-spacing: 0.03em;
    box-shadow: 0 2px 10px rgba(139,127,245,0.12);
}
.dv-hero-tag::before {
    content: ''; width: 6px; height: 6px;
    background: linear-gradient(135deg, #8b7ff5, #d46bc8);
    border-radius: 50%; flex-shrink: 0;
    animation: tagPulse 2.2s ease-in-out infinite;
}
@keyframes tagPulse { 0%,100%{opacity:1;transform:scale(1);} 50%{opacity:0.4;transform:scale(0.8);} }

.dv-h1 {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: clamp(2.2rem, 4.5vw, 3.5rem);
    font-weight: 800; line-height: 1.1; letter-spacing: -1px;
    color: #1e1f38; margin-bottom: 0;
}
.dv-h1-accent {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: clamp(2.2rem, 4.5vw, 3.5rem);
    font-weight: 800; line-height: 1.1; letter-spacing: -1px;
    background: linear-gradient(90deg, #8b7ff5, #d46bc8, #f0a0d0);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; display: block; margin-bottom: 0.9rem;
}
.dv-hero-sub {
    font-size: 0.97rem; color: #7a7aa0;
    max-width: 450px; margin: 0 auto; line-height: 1.7;
}

/* ══ CARD — neumorphic light ══ */
.dv-card {
    background: rgba(240,238,255,0.82);
    border: 1px solid rgba(255,255,255,0.85);
    border-radius: 20px; padding: 1.5rem 1.5rem 1rem;
    margin-bottom: 1rem;
    box-shadow:
        8px  8px 20px rgba(180,175,220,0.35),
       -4px -4px 14px rgba(255,255,255,0.80);
    backdrop-filter: blur(14px);
}

/* ══ SECTION LABEL ══ */
.dv-sec-label {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #a8a4cc;
    margin-bottom: 0.9rem; display: flex; align-items: center; gap: 0.5rem;
}
.dv-sec-label::after { content:''; flex:1; height:1px; background:rgba(139,127,245,0.15); }

/* ══ CHECKBOXES ══ */
.stCheckbox > label {
    font-size: 0.9rem !important; font-weight: 500 !important;
    color: #4a4870 !important; gap: 0.5rem !important;
}

/* ══ RADIO ══ */
div[data-testid="stRadio"] label {
    font-size: 0.92rem !important; color: #4a4870 !important;
}

/* ══ FILE UPLOADER ══ */
[data-testid="stFileUploader"] section {
    background: rgba(255,255,255,0.55) !important;
    border: 2px dashed rgba(139,127,245,0.28) !important;
    border-radius: 16px !important;
    transition: all 0.2s !important;
    box-shadow: inset 2px 2px 6px rgba(180,175,220,0.15) !important;
}
[data-testid="stFileUploader"] section:hover {
    border-color: rgba(139,127,245,0.55) !important;
    background: rgba(255,255,255,0.72) !important;
}
[data-testid="stFileUploader"] section p { color: #9a96c4 !important; font-size: 0.88rem !important; }

/* ══ TEXT AREA / INPUT ══ */
textarea, .stTextInput input {
    background: rgba(255,255,255,0.65) !important;
    border: 1.5px solid rgba(139,127,245,0.2) !important;
    border-radius: 14px !important; color: #2d2f4a !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 0.95rem !important;
    padding: 0.85rem 1rem !important; line-height: 1.6 !important;
    transition: all 0.2s !important; caret-color: #8b7ff5 !important;
    box-shadow: inset 2px 2px 6px rgba(180,175,220,0.2),
                inset -2px -2px 6px rgba(255,255,255,0.7) !important;
}
textarea:focus, .stTextInput input:focus {
    border-color: rgba(139,127,245,0.5) !important;
    box-shadow: 0 0 0 3px rgba(139,127,245,0.12),
                inset 2px 2px 6px rgba(180,175,220,0.15) !important;
    outline: none !important; background: rgba(255,255,255,0.82) !important;
}
textarea::placeholder, .stTextInput input::placeholder { color: #b8b4d8 !important; }

/* ══ PRIMARY BUTTON ══ */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #8b7ff5, #d46bc8) !important;
    border: none !important; border-radius: 14px !important; color: #fff !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 700 !important;
    font-size: 1rem !important; padding: 0.88rem 1.5rem !important;
    margin-top: 0.65rem !important; transition: all 0.22s !important;
    box-shadow: 0 5px 20px rgba(139,127,245,0.38), 0 2px 6px rgba(139,127,245,0.2) !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    opacity: 0.92 !important; transform: translateY(-2px) !important;
    box-shadow: 0 10px 28px rgba(139,127,245,0.48) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ══ DOWNLOAD BUTTON ══ */
.stDownloadButton > button {
    background: rgba(255,255,255,0.72) !important;
    border: 1.5px solid rgba(139,127,245,0.22) !important;
    color: #7b6fd4 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; border-radius: 10px !important;
    padding: 0.42rem 0.95rem !important; font-size: 0.82rem !important;
    margin-top: 0 !important; transition: all 0.18s !important;
    box-shadow: 3px 3px 8px rgba(180,175,220,0.28), -2px -2px 6px rgba(255,255,255,0.8) !important;
}
.stDownloadButton > button:hover {
    border-color: rgba(139,127,245,0.48) !important;
    color: #6356d4 !important;
    background: rgba(255,255,255,0.88) !important;
    box-shadow: 4px 4px 12px rgba(139,127,245,0.22), -2px -2px 8px rgba(255,255,255,0.9) !important;
}

/* ══ PROGRESS BAR ══ */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #8b7ff5, #d46bc8) !important;
    border-radius: 100px !important;
}
.stProgress > div > div {
    background: rgba(139,127,245,0.12) !important; border-radius: 100px !important;
}

/* ══ SECURITY BADGES ══ */
.sec-badge-row {
    display: flex; align-items: center; justify-content: space-between;
    background: rgba(255,255,255,0.58);
    border: 1px solid rgba(255,255,255,0.85);
    border-radius: 12px; padding: 0.68rem 1rem; margin-bottom: 0.45rem;
    box-shadow: 3px 3px 8px rgba(180,175,220,0.22), -2px -2px 6px rgba(255,255,255,0.75);
    transition: box-shadow 0.18s;
}
.sec-badge-row:hover {
    box-shadow: 4px 4px 12px rgba(180,175,220,0.32), -2px -2px 8px rgba(255,255,255,0.85);
}
.sec-badge-label { font-size: 0.9rem; font-weight: 600; color: #3d3b60; }
.sec-badge-pass {
    display: inline-flex; align-items: center; gap: 0.3rem;
    font-size: 0.74rem; font-weight: 700; color: #2e9e5e;
    background: rgba(93,216,138,0.14); border: 1px solid rgba(93,216,138,0.3);
    border-radius: 6px; padding: 0.16rem 0.52rem;
}
.sec-badge-fail {
    display: inline-flex; align-items: center; gap: 0.3rem;
    font-size: 0.74rem; font-weight: 700; color: #c03e3e;
    background: rgba(220,100,100,0.12); border: 1px solid rgba(220,100,100,0.25);
    border-radius: 6px; padding: 0.16rem 0.52rem;
}

/* ══ SCORE DISPLAY ══ */
.score-display {
    display: flex; align-items: center; gap: 1.5rem;
    background: rgba(255,255,255,0.62);
    border: 1px solid rgba(255,255,255,0.88);
    border-radius: 16px; padding: 1rem 1.2rem; margin-top: 0.5rem;
    box-shadow: 5px 5px 14px rgba(180,175,220,0.28), -3px -3px 10px rgba(255,255,255,0.80);
}
.score-num {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 2.2rem; font-weight: 800; line-height: 1;
}
.score-label {
    font-size: 0.62rem; font-weight: 600; letter-spacing: 0.1em;
    text-transform: uppercase; color: #a8a4cc; margin-bottom: 0.15rem;
}
.score-bar-wrap { flex: 1; }
.score-bar-bg { height: 8px; background: rgba(139,127,245,0.12); border-radius: 100px; overflow: hidden; }
.score-bar-fill { height: 100%; border-radius: 100px; }

/* ══ OUTPUT HEADER — Copy + Download side by side, top right ══ */
.output-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 0.7rem;
}
.output-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #a8a4cc;
    display: flex; align-items: center; gap: 0.5rem;
}
.output-title::after { content:''; width:36px; height:1px; background:rgba(139,127,245,0.18); }
.output-actions { display: flex; align-items: center; gap: 0.45rem; }

/* shared pill button */
.action-pill {
    display: inline-flex; align-items: center; gap: 0.32rem;
    font-family: 'DM Sans', sans-serif; font-size: 0.79rem; font-weight: 600;
    border-radius: 9px; padding: 0.38rem 0.82rem;
    cursor: pointer; transition: all 0.18s; border: 1.5px solid;
    text-decoration: none; white-space: nowrap;
    box-shadow: 3px 3px 8px rgba(180,175,220,0.25), -2px -2px 6px rgba(255,255,255,0.80);
}
.copy-pill {
    color: #7b6fd4;
    background: rgba(255,255,255,0.72);
    border-color: rgba(139,127,245,0.25);
}
.copy-pill:hover {
    border-color: rgba(139,127,245,0.50);
    background: rgba(255,255,255,0.90);
    box-shadow: 4px 4px 12px rgba(139,127,245,0.18), -2px -2px 8px rgba(255,255,255,0.9);
}
.dl-pill {
    color: #c05a9a;
    background: rgba(255,255,255,0.72);
    border-color: rgba(212,107,200,0.25);
}
.dl-pill:hover {
    border-color: rgba(212,107,200,0.50);
    background: rgba(255,255,255,0.90);
    box-shadow: 4px 4px 12px rgba(212,107,200,0.18), -2px -2px 8px rgba(255,255,255,0.9);
}

/* ══ SIDEBAR CARDS ══ */
.sc {
    background: rgba(240,238,255,0.80);
    border: 1px solid rgba(255,255,255,0.88);
    border-radius: 16px; padding: 1.1rem 1.15rem; margin-bottom: 0.85rem;
    box-shadow: 6px 6px 16px rgba(180,175,220,0.30), -3px -3px 10px rgba(255,255,255,0.78);
}
.sc-ttl {
    font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.72rem;
    font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
    color: #a8a4cc; margin-bottom: 0.85rem;
    display: flex; align-items: center; gap: 0.45rem;
}
.sc-ttl::after { content:''; flex:1; height:1px; background:rgba(139,127,245,0.14); }

/* ══ ALERTS ══ */
.stAlert   { background:rgba(139,127,245,0.08) !important; border:1px solid rgba(139,127,245,0.22) !important; border-radius:12px !important; color:#6356d4 !important; }
.stSuccess { background:rgba(93,216,138,0.10)  !important; border:1px solid rgba(93,216,138,0.25)  !important; border-radius:12px !important; color:#2e9e5e  !important; }
.stWarning { background:rgba(255,190,80,0.10)  !important; border:1px solid rgba(255,190,80,0.25)  !important; border-radius:12px !important; color:#b07020  !important; }
.stError   { background:rgba(220,100,100,0.09) !important; border:1px solid rgba(220,100,100,0.22) !important; border-radius:12px !important; color:#c03e3e  !important; }
.stSpinner > div { border-top-color: #8b7ff5 !important; }
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] { background:transparent !important; }
div[data-testid="stForm"] { background:transparent !important; border:none !important; box-shadow:none !important; padding:0 !important; }
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
# RIGHT SIDEBAR
# ══════════════════════════════════════════════════════════
with right:

    # ── SUPPORTED / NOT SUPPORTED ──
    st.markdown("""
<div style="background:rgba(240,238,255,0.80);border:1px solid rgba(255,255,255,0.88);border-radius:16px;padding:1.1rem 1.15rem;margin-bottom:0.85rem;box-shadow:6px 6px 16px rgba(180,175,220,0.30),-3px -3px 10px rgba(255,255,255,0.78);">

  <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:0.72rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#a8a4cc;margin-bottom:0.9rem;display:flex;align-items:center;gap:0.45rem;">
    How It Works
    <span style="flex:1;height:1px;background:rgba(139,127,245,0.14);display:inline-block;"></span>
  </div>

  <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:0.66rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#2e9e5e;margin-bottom:0.45rem;">✓ &nbsp;Supported Formats</div>

  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid rgba(139,127,245,0.07);">
    <span style="width:17px;height:17px;border-radius:4px;background:rgba(93,216,138,0.14);border:1px solid rgba(93,216,138,0.28);display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#2e9e5e;flex-shrink:0;">✓</span>
    <span style="font-size:0.84rem;color:#5a587a;font-family:'DM Sans',sans-serif;">PDF documents</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid rgba(139,127,245,0.07);">
    <span style="width:17px;height:17px;border-radius:4px;background:rgba(93,216,138,0.14);border:1px solid rgba(93,216,138,0.28);display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#2e9e5e;flex-shrink:0;">✓</span>
    <span style="font-size:0.84rem;color:#5a587a;font-family:'DM Sans',sans-serif;">Word DOCX files</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid rgba(139,127,245,0.07);">
    <span style="width:17px;height:17px;border-radius:4px;background:rgba(93,216,138,0.14);border:1px solid rgba(93,216,138,0.28);display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#2e9e5e;flex-shrink:0;">✓</span>
    <span style="font-size:0.84rem;color:#5a587a;font-family:'DM Sans',sans-serif;">Excel XLSX spreadsheets</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid rgba(139,127,245,0.07);">
    <span style="width:17px;height:17px;border-radius:4px;background:rgba(93,216,138,0.14);border:1px solid rgba(93,216,138,0.28);display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#2e9e5e;flex-shrink:0;">✓</span>
    <span style="font-size:0.84rem;color:#5a587a;font-family:'DM Sans',sans-serif;">PowerPoint PPTX / PPT</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid rgba(139,127,245,0.07);">
    <span style="width:17px;height:17px;border-radius:4px;background:rgba(93,216,138,0.14);border:1px solid rgba(93,216,138,0.28);display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#2e9e5e;flex-shrink:0;">✓</span>
    <span style="font-size:0.84rem;color:#5a587a;font-family:'DM Sans',sans-serif;">Plain TXT files</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid rgba(139,127,245,0.12);">
    <span style="width:17px;height:17px;border-radius:4px;background:rgba(93,216,138,0.14);border:1px solid rgba(93,216,138,0.28);display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#2e9e5e;flex-shrink:0;">✓</span>
    <span style="font-size:0.84rem;color:#5a587a;font-family:'DM Sans',sans-serif;">Images PNG / JPG (OCR)</span>
  </div>

  <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:0.66rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#c03e3e;margin-top:0.8rem;margin-bottom:0.45rem;">✕ &nbsp;Not Supported</div>

  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid rgba(139,127,245,0.07);">
    <span style="width:17px;height:17px;border-radius:4px;background:rgba(220,100,100,0.1);border:1px solid rgba(220,100,100,0.22);display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#c03e3e;flex-shrink:0;">✕</span>
    <span style="font-size:0.84rem;color:#5a587a;font-family:'DM Sans',sans-serif;">Encrypted / password PDFs</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid rgba(139,127,245,0.07);">
    <span style="width:17px;height:17px;border-radius:4px;background:rgba(220,100,100,0.1);border:1px solid rgba(220,100,100,0.22);display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#c03e3e;flex-shrink:0;">✕</span>
    <span style="font-size:0.84rem;color:#5a587a;font-family:'DM Sans',sans-serif;">Scanned PDFs (no OCR layer)</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid rgba(139,127,245,0.07);">
    <span style="width:17px;height:17px;border-radius:4px;background:rgba(220,100,100,0.1);border:1px solid rgba(220,100,100,0.22);display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#c03e3e;flex-shrink:0;">✕</span>
    <span style="font-size:0.84rem;color:#5a587a;font-family:'DM Sans',sans-serif;">Files &gt; 200 MB</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;">
    <span style="width:17px;height:17px;border-radius:4px;background:rgba(220,100,100,0.1);border:1px solid rgba(220,100,100,0.22);display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#c03e3e;flex-shrink:0;">✕</span>
    <span style="font-size:0.84rem;color:#5a587a;font-family:'DM Sans',sans-serif;">Executable / script files</span>
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
    <div style="display:flex;align-items:center;gap:0.6rem;font-size:0.84rem;color:#5a587a;">
      <span style="width:22px;height:22px;border-radius:7px;background:rgba(139,127,245,0.12);border:1px solid rgba(139,127,245,0.22);display:inline-flex;align-items:center;justify-content:center;font-size:0.7rem;flex-shrink:0;">🔍</span>
      File type validation
    </div>
    <div style="display:flex;align-items:center;gap:0.6rem;font-size:0.84rem;color:#5a587a;">
      <span style="width:22px;height:22px;border-radius:7px;background:rgba(212,107,200,0.12);border:1px solid rgba(212,107,200,0.22);display:inline-flex;align-items:center;justify-content:center;font-size:0.7rem;flex-shrink:0;">🛡️</span>
      Malware signature scan
    </div>
    <div style="display:flex;align-items:center;gap:0.6rem;font-size:0.84rem;color:#5a587a;">
      <span style="width:22px;height:22px;border-radius:7px;background:rgba(93,216,138,0.12);border:1px solid rgba(93,216,138,0.22);display:inline-flex;align-items:center;justify-content:center;font-size:0.7rem;flex-shrink:0;">✅</span>
      Structural integrity check
    </div>
    <div style="display:flex;align-items:center;gap:0.6rem;font-size:0.84rem;color:#5a587a;">
      <span style="width:22px;height:22px;border-radius:7px;background:rgba(255,180,80,0.12);border:1px solid rgba(255,180,80,0.22);display:inline-flex;align-items:center;justify-content:center;font-size:0.7rem;flex-shrink:0;">🔒</span>
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

            color    = "#2e9e5e" if score == 100 else ("#b07020" if score >= 60 else "#c03e3e")
            bar_grad = "linear-gradient(90deg,#8b7ff5,#d46bc8)" if score == 100 else ("linear-gradient(90deg,#f59e0b,#fbbf24)" if score >= 60 else "linear-gradient(90deg,#ef4444,#f87171)")

            st.markdown(f"""
<div class="score-display">
  <div>
    <div class="score-label">Security Score</div>
    <div class="score-num" style="color:{color};">{score}</div>
    <div style="font-size:0.65rem;color:#b8b4d8;font-family:'DM Mono',monospace;">/ 100</div>
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
    <div class="score-num" style="color:#2e9e5e;">100</div>
    <div style="font-size:0.65rem;color:#b8b4d8;font-family:'DM Mono',monospace;">/ 100</div>
  </div>
  <div class="score-bar-wrap">
    <div class="score-label">Scan Confidence</div>
    <div class="score-bar-bg" style="margin-top:0.35rem;">
      <div class="score-bar-fill" style="width:100%;background:linear-gradient(90deg,#8b7ff5,#d46bc8);"></div>
    </div>
    <div style="font-size:0.72rem;color:#2e9e5e;font-family:'DM Mono',monospace;margin-top:0.35rem;font-weight:600;">100% complete</div>
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

        # ── OUTPUT HEADER: title left, Copy + Download Clean Copy RIGHT ──
        st.markdown(f"""
<div class="output-header">
  <div class="output-title">Extracted Output</div>
  <div class="output-actions">
    <button class="action-pill copy-pill" id="dv-copy-btn" onclick="
      const ta = document.querySelector('#dv-output-ta textarea');
      if(ta){{navigator.clipboard.writeText(ta.value).then(()=>{{
        this.innerHTML='✓ Copied!';
        this.style.color='#2e9e5e';
        this.style.borderColor='rgba(93,216,138,0.4)';
        this.style.background='rgba(93,216,138,0.1)';
        setTimeout(()=>{{
          this.innerHTML='⧉ Copy Text';
          this.style.color='';this.style.borderColor='';this.style.background='';
        }},2000);
      }});}}
    ">⧉ Copy Text</button>
    <a class="action-pill dl-pill" id="dv-dl-btn"
       href="data:text/plain;charset=utf-8,{__import__('urllib.parse', fromlist=['quote']).quote(clean)}"
       download="docvault_clean_output.txt">⬇ Download Clean Copy</a>
  </div>
</div>
""", unsafe_allow_html=True)

        st.markdown('<div id="dv-output-ta">', unsafe_allow_html=True)
        st.text_area("", clean, height=420, label_visibility="collapsed", key="output_ta")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
