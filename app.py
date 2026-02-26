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
# GLOBAL STYLING — LEXIS AI light style
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

/* ── BASE ── */
.stApp {
    background: #f0f4f8 !important;
    color: #1a2332 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
}

/* Soft gradient mesh — same as LEXIS AI */
.stApp::before {
    content: '';
    position: fixed; inset: 0;
    background:
        radial-gradient(ellipse 1000px 700px at 20% 0%,  rgba(186,230,255,0.50) 0%, transparent 60%),
        radial-gradient(ellipse  800px 600px at 85% 10%, rgba(199,210,254,0.40) 0%, transparent 60%),
        radial-gradient(ellipse  700px 600px at 10% 90%, rgba(167,243,208,0.28) 0%, transparent 60%),
        radial-gradient(ellipse  900px 500px at 90% 95%, rgba(196,181,253,0.22) 0%, transparent 60%);
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
::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }

/* ══ NAV ══ */
.dv-nav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1.1rem 0;
    border-bottom: 1px solid rgba(0,0,0,0.06);
    margin-bottom: 0;
    background: rgba(255,255,255,0.7);
    backdrop-filter: blur(12px);
}
.dv-logo-wrap { display: flex; align-items: center; gap: 0.5rem; }
.dv-logo-icon {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #1d4ed8, #0ea5e9);
    border-radius: 9px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.9rem;
    box-shadow: 0 3px 10px rgba(29,78,216,0.3);
}
.dv-logo-text {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.08rem; font-weight: 800; color: #0f172a; letter-spacing: -0.3px;
}
.dv-logo-text span {
    background: linear-gradient(90deg, #1d4ed8, #0ea5e9);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.dv-nav-badge {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem; letter-spacing: 0.18em; text-transform: uppercase;
    color: #64748b; border: 1px solid #e2e8f0; background: rgba(255,255,255,0.8);
    padding: 0.28rem 0.9rem; border-radius: 100px;
}
.dv-status {
    display: flex; align-items: center; gap: 0.4rem;
    font-size: 0.78rem; font-weight: 500; color: #64748b;
}
.dv-status-dot {
    width: 7px; height: 7px; background: #22c55e; border-radius: 50%;
    box-shadow: 0 0 6px rgba(34,197,94,0.6); animation: sDot 2.5s ease-in-out infinite;
}
@keyframes sDot { 0%,100%{opacity:1;} 50%{opacity:0.4;} }

/* ══ HERO ══ */
.dv-hero { text-align: center; padding: 2.8rem 0 2.2rem; }
.dv-hero-tag {
    display: inline-flex; align-items: center; gap: 0.4rem;
    background: rgba(255,255,255,0.85); border: 1px solid #e2e8f0;
    border-radius: 100px; padding: 0.28rem 0.9rem;
    font-size: 0.75rem; font-weight: 600; color: #475569;
    margin-bottom: 1.2rem; box-shadow: 0 1px 4px rgba(0,0,0,0.06);
}
.dv-hero-tag::before {
    content: ''; width: 6px; height: 6px;
    background: linear-gradient(135deg, #1d4ed8, #0ea5e9);
    border-radius: 50%; flex-shrink: 0;
}
.dv-h1 {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: clamp(2.2rem, 4.5vw, 3.5rem);
    font-weight: 800; line-height: 1.1; letter-spacing: -1px;
    color: #0f172a; margin-bottom: 0;
}
.dv-h1-accent {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: clamp(2.2rem, 4.5vw, 3.5rem);
    font-weight: 800; line-height: 1.1; letter-spacing: -1px;
    background: linear-gradient(90deg, #1d4ed8, #0ea5e9);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; display: block; margin-bottom: 0.9rem;
}
.dv-hero-sub {
    font-size: 0.97rem; color: #64748b;
    max-width: 430px; margin: 0 auto; line-height: 1.7;
}

/* ══ CARD ══ */
.dv-card {
    background: rgba(255,255,255,0.82);
    border: 1px solid rgba(255,255,255,0.9);
    border-radius: 16px; padding: 1.5rem 1.5rem 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 24px rgba(0,0,0,0.06), 0 1px 4px rgba(0,0,0,0.04);
    backdrop-filter: blur(12px);
}

/* ══ SECTION LABEL ══ */
.dv-sec-label {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #64748b;
    margin-bottom: 0.9rem; display: flex; align-items: center; gap: 0.5rem;
}
.dv-sec-label::after { content:''; flex:1; height:1px; background:#e2e8f0; }

/* ══ CHECKBOXES ══ */
.stCheckbox > label {
    font-size: 0.92rem !important; font-weight: 500 !important; color: #334155 !important;
    gap: 0.5rem !important;
}
.stCheckbox > label > span:first-child {
    width: 16px !important; height: 16px !important;
    border: 1.5px solid #cbd5e1 !important; border-radius: 4px !important;
}

/* ══ RADIO ══ */
.stRadio > label { font-size: 0.9rem !important; color: #334155 !important; }
div[data-testid="stRadio"] label { font-size: 0.92rem !important; }

/* ══ FILE UPLOADER ══ */
[data-testid="stFileUploader"] {
    background: #ffffff !important;
    border: 2px dashed #cbd5e1 !important;
    border-radius: 12px !important;
    padding: 1rem !important;
    transition: border-color 0.2s !important;
}
[data-testid="stFileUploader"]:hover { border-color: #3b82f6 !important; }
[data-testid="stFileUploader"] label { font-size: 0.88rem !important; color: #64748b !important; }

/* ══ TEXT AREA / INPUT ══ */
textarea, .stTextInput input {
    background: #ffffff !important; border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important; color: #1a2332 !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 0.95rem !important;
    padding: 0.85rem 1rem !important; line-height: 1.6 !important;
    transition: border-color 0.2s, box-shadow 0.2s !important;
}
textarea:focus, .stTextInput input:focus {
    border-color: #3b82f6 !important;
    box-shadow: 0 0 0 3px rgba(59,130,246,0.1) !important; outline: none !important;
}
textarea::placeholder { color: #94a3b8 !important; }

/* ══ PRIMARY BUTTON ══ */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(90deg, #1d4ed8, #0ea5e9) !important;
    border: none !important; border-radius: 10px !important; color: #fff !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 700 !important;
    font-size: 1rem !important; padding: 0.82rem 1.5rem !important;
    margin-top: 0.65rem !important; transition: all 0.2s !important;
    box-shadow: 0 3px 12px rgba(29,78,216,0.28) !important;
}
.stButton > button:hover {
    opacity: 0.9 !important; transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(29,78,216,0.38) !important;
}

/* ══ DOWNLOAD BUTTON ══ */
.stDownloadButton > button {
    background: #ffffff !important; border: 1.5px solid #e2e8f0 !important;
    color: #475569 !important; font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; border-radius: 8px !important;
    padding: 0.45rem 1rem !important; font-size: 0.85rem !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important; transition: all 0.18s !important;
    margin-top: 0 !important;
}
.stDownloadButton > button:hover {
    border-color: #1d4ed8 !important; color: #1d4ed8 !important; background: #eff6ff !important;
}

/* ══ PROGRESS BAR ══ */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #1d4ed8, #0ea5e9) !important;
    border-radius: 100px !important;
}
.stProgress > div > div {
    background: #e2e8f0 !important; border-radius: 100px !important;
}

/* ══ SECURITY BADGES ══ */
.sec-badge-row {
    display: flex; align-items: center; justify-content: space-between;
    background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px;
    padding: 0.7rem 1rem; margin-bottom: 0.5rem;
}
.sec-badge-label { font-size: 0.9rem; font-weight: 600; color: #334155; }
.sec-badge-pass {
    display: inline-flex; align-items: center; gap: 0.3rem;
    font-size: 0.78rem; font-weight: 700; color: #16a34a;
    background: #dcfce7; border: 1px solid #bbf7d0;
    border-radius: 6px; padding: 0.18rem 0.55rem;
}
.sec-badge-fail {
    display: inline-flex; align-items: center; gap: 0.3rem;
    font-size: 0.78rem; font-weight: 700; color: #dc2626;
    background: #fee2e2; border: 1px solid #fecaca;
    border-radius: 6px; padding: 0.18rem 0.55rem;
}

/* ══ SCORE DISPLAY ══ */
.score-display {
    display: flex; align-items: center; gap: 1.5rem;
    background: #f8fafc; border: 1px solid #e2e8f0;
    border-radius: 12px; padding: 1rem 1.2rem; margin-top: 0.5rem;
}
.score-num {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 2.2rem; font-weight: 800; line-height: 1;
}
.score-label { font-size: 0.62rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #94a3b8; margin-bottom: 0.15rem; }
.score-bar-wrap { flex: 1; }
.score-bar-bg { height: 8px; background: #e2e8f0; border-radius: 100px; overflow: hidden; }
.score-bar-fill { height: 100%; border-radius: 100px; }

/* ══ OUTPUT HEADER (Copy + Download top-right) ══ */
.output-header {
    display: flex; align-items: center; justify-content: space-between;
    margin-bottom: 0.75rem;
}
.output-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #64748b;
    display: flex; align-items: center; gap: 0.5rem;
}
.output-title::after { content:''; width:40px; height:1px; background:#e2e8f0; }
.output-actions {
    display: flex; align-items: center; gap: 0.5rem;
}
.copy-btn {
    display: inline-flex; align-items: center; gap: 0.35rem;
    font-family: 'DM Sans', sans-serif; font-size: 0.8rem; font-weight: 600;
    color: #475569; background: #ffffff; border: 1.5px solid #e2e8f0;
    border-radius: 7px; padding: 0.38rem 0.85rem; cursor: pointer;
    transition: all 0.18s; text-decoration: none;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}
.copy-btn:hover { border-color: #1d4ed8; color: #1d4ed8; background: #eff6ff; }

/* ══ SIDEBAR CARDS ══ */
.sc {
    background: rgba(255,255,255,0.85); border: 1px solid rgba(255,255,255,0.9);
    border-radius: 14px; padding: 1.1rem 1.15rem; margin-bottom: 0.85rem;
    box-shadow: 0 3px 16px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.04);
    backdrop-filter: blur(10px);
}
.sc-ttl {
    font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.72rem;
    font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
    color: #475569; margin-bottom: 0.85rem; display:flex; align-items:center; gap:0.45rem;
}
.sc-ttl::after { content:''; flex:1; height:1px; background:#e2e8f0; }

/* ══ ALERTS ══ */
.stAlert { background:#eff6ff !important; border:1px solid #bfdbfe !important; border-radius:10px !important; color:#1e40af !important; }
.stSpinner > div { border-top-color: #1d4ed8 !important; }
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
    except:
        return False

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
  <span class="dv-h1-accent">Validation & Extraction</span>
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
<div style="background:rgba(255,255,255,0.85);border:1px solid rgba(255,255,255,0.9);border-radius:14px;padding:1.1rem 1.15rem;margin-bottom:0.85rem;box-shadow:0 3px 16px rgba(0,0,0,0.06);backdrop-filter:blur(10px);">
  <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:0.72rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:#475569;margin-bottom:0.9rem;display:flex;align-items:center;gap:0.45rem;">
    How It Works
    <span style="flex:1;height:1px;background:#e2e8f0;display:inline-block;"></span>
  </div>

  <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:0.66rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#16a34a;margin-bottom:0.45rem;">✓ &nbsp;Supported Formats</div>
  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid #f8fafc;">
    <span style="width:17px;height:17px;border-radius:4px;background:#dcfce7;border:1px solid #bbf7d0;display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#16a34a;flex-shrink:0;">✓</span>
    <span style="font-size:0.84rem;color:#475569;font-family:'DM Sans',sans-serif;">PDF documents</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid #f8fafc;">
    <span style="width:17px;height:17px;border-radius:4px;background:#dcfce7;border:1px solid #bbf7d0;display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#16a34a;flex-shrink:0;">✓</span>
    <span style="font-size:0.84rem;color:#475569;font-family:'DM Sans',sans-serif;">Word DOCX files</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid #f8fafc;">
    <span style="width:17px;height:17px;border-radius:4px;background:#dcfce7;border:1px solid #bbf7d0;display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#16a34a;flex-shrink:0;">✓</span>
    <span style="font-size:0.84rem;color:#475569;font-family:'DM Sans',sans-serif;">Excel XLSX spreadsheets</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid #f8fafc;">
    <span style="width:17px;height:17px;border-radius:4px;background:#dcfce7;border:1px solid #bbf7d0;display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#16a34a;flex-shrink:0;">✓</span>
    <span style="font-size:0.84rem;color:#475569;font-family:'DM Sans',sans-serif;">PowerPoint PPTX / PPT</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid #f8fafc;">
    <span style="width:17px;height:17px;border-radius:4px;background:#dcfce7;border:1px solid #bbf7d0;display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#16a34a;flex-shrink:0;">✓</span>
    <span style="font-size:0.84rem;color:#475569;font-family:'DM Sans',sans-serif;">Plain TXT files</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid #e2e8f0;">
    <span style="width:17px;height:17px;border-radius:4px;background:#dcfce7;border:1px solid #bbf7d0;display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#16a34a;flex-shrink:0;">✓</span>
    <span style="font-size:0.84rem;color:#475569;font-family:'DM Sans',sans-serif;">Images PNG / JPG (OCR)</span>
  </div>

  <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:0.66rem;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;color:#dc2626;margin-top:0.8rem;margin-bottom:0.45rem;">✕ &nbsp;Not Supported</div>
  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid #f8fafc;">
    <span style="width:17px;height:17px;border-radius:4px;background:#fee2e2;border:1px solid #fecaca;display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#dc2626;flex-shrink:0;">✕</span>
    <span style="font-size:0.84rem;color:#475569;font-family:'DM Sans',sans-serif;">Encrypted / password PDFs</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid #f8fafc;">
    <span style="width:17px;height:17px;border-radius:4px;background:#fee2e2;border:1px solid #fecaca;display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#dc2626;flex-shrink:0;">✕</span>
    <span style="font-size:0.84rem;color:#475569;font-family:'DM Sans',sans-serif;">Scanned PDFs (no OCR layer)</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;border-bottom:1px solid #f8fafc;">
    <span style="width:17px;height:17px;border-radius:4px;background:#fee2e2;border:1px solid #fecaca;display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#dc2626;flex-shrink:0;">✕</span>
    <span style="font-size:0.84rem;color:#475569;font-family:'DM Sans',sans-serif;">Files &gt; 200 MB</span>
  </div>
  <div style="display:flex;align-items:center;gap:0.5rem;padding:0.3rem 0;">
    <span style="width:17px;height:17px;border-radius:4px;background:#fee2e2;border:1px solid #fecaca;display:inline-flex;align-items:center;justify-content:center;font-size:0.6rem;color:#dc2626;flex-shrink:0;">✕</span>
    <span style="font-size:0.84rem;color:#475569;font-family:'DM Sans',sans-serif;">Executable / script files</span>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── REDACTION CONTROLS (sidebar) ──
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
    <div style="display:flex;align-items:center;gap:0.6rem;font-size:0.84rem;color:#334155;">
      <span style="width:22px;height:22px;border-radius:6px;background:#dbeafe;border:1px solid #bfdbfe;display:inline-flex;align-items:center;justify-content:center;font-size:0.7rem;color:#1d4ed8;flex-shrink:0;">🔍</span>
      File type validation
    </div>
    <div style="display:flex;align-items:center;gap:0.6rem;font-size:0.84rem;color:#334155;">
      <span style="width:22px;height:22px;border-radius:6px;background:#dbeafe;border:1px solid #bfdbfe;display:inline-flex;align-items:center;justify-content:center;font-size:0.7rem;color:#1d4ed8;flex-shrink:0;">🛡️</span>
      Malware signature scan
    </div>
    <div style="display:flex;align-items:center;gap:0.6rem;font-size:0.84rem;color:#334155;">
      <span style="width:22px;height:22px;border-radius:6px;background:#dbeafe;border:1px solid #bfdbfe;display:inline-flex;align-items:center;justify-content:center;font-size:0.7rem;color:#1d4ed8;flex-shrink:0;">✅</span>
      Structural integrity check
    </div>
    <div style="display:flex;align-items:center;gap:0.6rem;font-size:0.84rem;color:#334155;">
      <span style="width:22px;height:22px;border-radius:6px;background:#dbeafe;border:1px solid #bfdbfe;display:inline-flex;align-items:center;justify-content:center;font-size:0.7rem;color:#1d4ed8;flex-shrink:0;">🔒</span>
      PII redaction engine
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# LEFT COLUMN — main content
# ══════════════════════════════════════════════════════════
with left:

    # ── INPUT SOURCE ──
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

            # Security results
            st.markdown('<div class="dv-sec-label" style="margin-top:1.2rem;">Security Scan Results</div>', unsafe_allow_html=True)

            def badge(ok):
                if ok:
                    return '<span class="sec-badge-pass">✓ Pass</span>'
                return '<span class="sec-badge-fail">✗ Fail</span>'

            st.markdown(f"""
<div class="sec-badge-row"><span class="sec-badge-label">🔍 File Type Validation</span>{badge(magic_ok)}</div>
<div class="sec-badge-row"><span class="sec-badge-label">🛡️ Malware Scan</span>{badge(malware_ok)}</div>
<div class="sec-badge-row"><span class="sec-badge-label">✅ Integrity Check</span>{badge(integrity_ok)}</div>
""", unsafe_allow_html=True)

            score = 100
            if not magic_ok:     score -= 30
            if not malware_ok:   score -= 40
            if not integrity_ok: score -= 30

            pct   = score / 100
            color = "#16a34a" if score == 100 else ("#d97706" if score >= 60 else "#dc2626")

            st.markdown(f"""
<div class="score-display">
  <div>
    <div class="score-label">Security Score</div>
    <div class="score-num" style="color:{color};">{score}</div>
    <div style="font-size:0.68rem;color:#94a3b8;font-family:'DM Mono',monospace;">/ 100</div>
  </div>
  <div class="score-bar-wrap">
    <div class="score-label">Scan Confidence</div>
    <div class="score-bar-bg" style="margin-top:0.3rem;">
      <div class="score-bar-fill" style="width:{score}%;background:{'linear-gradient(90deg,#16a34a,#4ade80)' if score==100 else ('linear-gradient(90deg,#d97706,#fbbf24)' if score>=60 else 'linear-gradient(90deg,#dc2626,#f87171)')};"></div>
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
            st.markdown("""
<div class="sec-badge-row"><span class="sec-badge-label">📝 Text Mode</span><span class="sec-badge-pass">✓ Safe</span></div>
""", unsafe_allow_html=True)
            st.markdown("""
<div class="score-display">
  <div>
    <div class="score-label">Security Score</div>
    <div class="score-num" style="color:#16a34a;">100</div>
    <div style="font-size:0.68rem;color:#94a3b8;font-family:'DM Mono',monospace;">/ 100</div>
  </div>
  <div class="score-bar-wrap">
    <div class="score-label">Scan Confidence</div>
    <div class="score-bar-bg" style="margin-top:0.3rem;">
      <div class="score-bar-fill" style="width:100%;background:linear-gradient(90deg,#16a34a,#4ade80);"></div>
    </div>
    <div style="font-size:0.72rem;color:#16a34a;font-family:'DM Mono',monospace;margin-top:0.35rem;font-weight:600;">100% complete</div>
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

        # Output header with Copy + Download top-right
        st.markdown("""
<div class="output-header">
  <div class="output-title">Extracted Output</div>
  <div class="output-actions" id="dv-output-actions">
    <button class="copy-btn" onclick="
      const ta = document.querySelector('#dv-output-ta textarea');
      if(ta){navigator.clipboard.writeText(ta.value).then(()=>{
        this.innerHTML='✓ Copied!';
        this.style.color='#16a34a';
        this.style.borderColor='#16a34a';
        this.style.background='#f0fdf4';
        setTimeout(()=>{
          this.innerHTML='⧉ Copy Text';
          this.style.color='';this.style.borderColor='';this.style.background='';
        },2000);
      });}
    ">⧉ Copy Text</button>
  </div>
</div>
""", unsafe_allow_html=True)

        # Text area with DOM id for JS copy
        st.markdown('<div id="dv-output-ta">', unsafe_allow_html=True)
        st.text_area("", clean, height=420, label_visibility="collapsed", key="output_ta")
        st.markdown('</div>', unsafe_allow_html=True)

        # Download clean copy button (native Streamlit — below the text area)
        col_dl, col_sp = st.columns([1, 3])
        with col_dl:
            st.download_button(
                "⬇ Download Clean Copy",
                data=clean.encode("utf-8"),
                file_name="docvault_clean_output.txt",
                mime="text/plain"
            )

    st.markdown('</div>', unsafe_allow_html=True)



