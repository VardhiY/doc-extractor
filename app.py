import streamlit as st
from groq import Groq
import json, re, base64, io

st.set_page_config(
    page_title="DocVault · AI Extractor",
    page_icon="🔐",
    layout="wide",
)

try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client  = Groq(api_key=API_KEY)
except Exception:
    st.error("⚠️ API key not configured. Add GROQ_API_KEY to Streamlit Secrets.")
    st.stop()

# ══════════════════════════════════════════════════════════════════════
# MASTER CSS
# ══════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Syne:wght@700;800&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

.stApp {
    background: #06060f !important;
    color: #eeeef8 !important;
    min-height: 100vh;
    background-image:
        radial-gradient(ellipse 110% 55% at 50% -5%, rgba(120,255,80,0.09) 0%, transparent 55%),
        radial-gradient(ellipse 60% 45% at 10% 85%, rgba(80,100,255,0.06) 0%, transparent 50%),
        radial-gradient(ellipse 50% 40% at 90% 60%, rgba(255,80,180,0.04) 0%, transparent 50%);
    background-attachment: fixed;
}

/* Hide chrome */
#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display:none !important; }

/* Center main content */
.main .block-container {
    max-width: 800px !important;
    margin: 0 auto !important;
    padding: 0 1.5rem 5rem !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #08080f !important;
    border-right: 1px solid #12122a !important;
    min-width: 250px !important;
}
[data-testid="stSidebar"] * { color: #6060a0 !important; font-size: 0.82rem !important; }
[data-testid="stSidebar"] h2 { color: #c0c0e0 !important; font-size: 1rem !important; }
[data-testid="stSidebar"] .stSlider label { color: #8080b0 !important; }
[data-testid="collapsedControl"] { display:flex !important; visibility:visible !important; }

/* ─── HERO ─── */
.hero {
    text-align: center;
    padding: 3rem 1rem 1.5rem;
    position: relative;
}
.hero-aura {
    position: absolute;
    top: -30px; left: 50%;
    transform: translateX(-50%);
    width: 600px; height: 220px;
    background: radial-gradient(ellipse, rgba(110,255,70,0.13) 0%, transparent 65%);
    filter: blur(30px);
    pointer-events: none;
}
.eyebrow {
    display: inline-flex; align-items: center; gap: 0.45rem;
    border: 1px solid rgba(110,255,70,0.28);
    background: rgba(110,255,70,0.08);
    color: #90ff50; padding: 0.3rem 1rem;
    border-radius: 999px; font-size: 0.68rem;
    font-weight: 700; letter-spacing: 0.16em;
    text-transform: uppercase; margin-bottom: 1.3rem;
}
.live-dot {
    width: 7px; height: 7px; background: #90ff50;
    border-radius: 50%;
    box-shadow: 0 0 0 0 rgba(144,255,80,0.5);
    animation: ping 2s infinite;
    display: inline-block; flex-shrink: 0;
}
@keyframes ping {
    0%   { box-shadow: 0 0 0 0   rgba(144,255,80,0.55); }
    70%  { box-shadow: 0 0 0 9px rgba(144,255,80,0);    }
    100% { box-shadow: 0 0 0 0   rgba(144,255,80,0);    }
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 4.8rem; font-weight: 800;
    line-height: 1; letter-spacing: -0.02em;
    color: #eeeef8; margin-bottom: 0.5rem;
}
.hero-title .g {
    background: linear-gradient(120deg, #90ff50 0%, #40ffc8 50%, #4080ff 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.hero-sub {
    font-size: 0.92rem; color: #3a3a68; font-weight: 400;
    max-width: 400px; margin: 0 auto; line-height: 1.65;
}

/* ─── SECTION DIVIDER ─── */
.sec-head {
    font-size: 0.65rem; font-weight: 800;
    letter-spacing: 0.18em; text-transform: uppercase;
    color: #2e2e58; margin: 2rem 0 0.9rem;
    display: flex; align-items: center; gap: 0.6rem;
}
.sec-head::after {
    content: ''; flex: 1; height: 1px;
    background: linear-gradient(90deg, #141430 0%, transparent 100%);
}

/* ─── SECURITY FEATURE CARDS (top intro) ─── */
.shield-banner {
    background: linear-gradient(135deg, #0c0c1e 0%, #090914 100%);
    border: 1px solid #161630;
    border-radius: 22px;
    padding: 1.6rem 1.8rem;
    position: relative; overflow: hidden;
    margin-bottom: 0.5rem;
}
.shield-banner::before {
    content: '';
    position: absolute; top:0; left:0; right:0; height:1px;
    background: linear-gradient(90deg, transparent, #90ff50 40%, #40ffc8 60%, transparent);
    opacity: 0.55;
}
.shield-banner::after {
    content: '🛡️';
    position: absolute; right: -5px; top: -15px;
    font-size: 8rem; opacity: 0.025;
    transform: rotate(-5deg); pointer-events: none;
}
.shield-row-title {
    display: flex; align-items: center; gap: 0.7rem;
    margin-bottom: 1.2rem;
}
.shield-badge {
    background: rgba(144,255,80,0.1);
    border: 1px solid rgba(144,255,80,0.22);
    color: #90ff50; padding: 0.18rem 0.7rem;
    border-radius: 6px; font-size: 0.62rem;
    font-weight: 800; letter-spacing: 0.14em; text-transform: uppercase;
}
.shield-title { font-weight: 700; font-size: 1rem; color: #d0d0f0; }
.shield-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 0.65rem;
}
.shield-item {
    background: rgba(255,255,255,0.02);
    border: 1px solid #111128; border-radius: 14px;
    padding: 0.85rem 1rem;
    display: flex; align-items: flex-start; gap: 0.75rem;
    transition: all 0.22s ease; cursor: default;
}
.shield-item:hover {
    background: rgba(144,255,80,0.04);
    border-color: rgba(144,255,80,0.18);
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0,0,0,0.3);
}
.si-icon { font-size: 1.45rem; line-height:1; flex-shrink:0; margin-top:0.05rem; }
.si-name { font-size: 0.78rem; font-weight: 700; color: #b8b8e0; margin-bottom: 0.18rem; }
.si-desc { font-size: 0.66rem; color: #2e2e58; line-height: 1.4; }

/* ─── SENSITIVE DATA TOGGLE CARDS ─── */
.redact-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 0.7rem;
    margin-bottom: 0.5rem;
}
.redact-card {
    background: #0a0a1a; border-radius: 18px;
    border: 1.5px solid #141430;
    padding: 1.1rem 1.15rem;
    display: flex; align-items: center; gap: 0.9rem;
    transition: all 0.22s ease; position: relative; overflow: hidden;
    cursor: pointer; user-select: none;
}
.redact-card::before {
    content: '';
    position: absolute; inset: 0;
    border-radius: 18px;
    background: linear-gradient(135deg, rgba(144,255,80,0.04), transparent);
    opacity: 0; transition: opacity 0.22s;
}
.redact-card:hover::before { opacity: 1; }
.redact-card:hover { border-color: rgba(144,255,80,0.22); transform: translateY(-2px); box-shadow: 0 10px 30px rgba(0,0,0,0.35); }

.redact-card.ON  { border-color: rgba(144,255,80,0.35); background: rgba(144,255,80,0.05); }
.redact-card.ON::before { opacity:1; }
.redact-card.ON .rc-icon-wrap { background: rgba(144,255,80,0.12); border-color: rgba(144,255,80,0.25); }
.redact-card.ON .rc-name { color: #d8ffc8; }
.redact-card.ON .rc-toggle { background: #90ff50; border-color: #90ff50; }
.redact-card.ON .rc-toggle::after { transform: translateX(18px); background: #050510; }

.rc-icon-wrap {
    width: 42px; height: 42px; border-radius: 12px;
    background: rgba(255,255,255,0.03);
    border: 1px solid #1c1c38;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.3rem; flex-shrink: 0;
    transition: all 0.22s;
}
.rc-body { flex: 1; }
.rc-name { font-size: 0.8rem; font-weight: 700; color: #8080b0; margin-bottom: 0.15rem; transition: color 0.2s; }
.rc-desc { font-size: 0.65rem; color: #282848; line-height: 1.35; }

/* Custom toggle pill */
.rc-toggle {
    width: 38px; height: 20px; border-radius: 999px;
    background: #141430; border: 1.5px solid #202048;
    position: relative; flex-shrink: 0;
    transition: all 0.22s ease;
}
.rc-toggle::after {
    content: '';
    position: absolute; top: 2px; left: 2px;
    width: 12px; height: 12px; border-radius: 50%;
    background: #282858; transition: all 0.22s ease;
}

/* ─── UPLOAD ─── */
div[data-testid="stFileUploader"] {
    background: #09091a !important;
    border: 2px dashed #181836 !important;
    border-radius: 20px !important;
    padding: 2rem 1.5rem !important;
    transition: all 0.3s ease !important;
}
div[data-testid="stFileUploader"]:hover {
    border-color: rgba(144,255,80,0.3) !important;
    background: rgba(144,255,80,0.025) !important;
}
div[data-testid="stFileUploader"] label { color: #303060 !important; font-size: 0.82rem !important; }

/* File chip */
.file-chip {
    display: inline-flex; align-items: center; gap: 0.5rem;
    background: #0c0c1e; border: 1px solid #1c1c38;
    border-radius: 999px; padding: 0.38rem 0.9rem;
    font-size: 0.73rem; color: #6060a0;
    font-family: 'JetBrains Mono', monospace; margin: 0.5rem 0;
}
.cdot { width:6px; height:6px; background:#90ff50; border-radius:50%; flex-shrink:0; }

/* ─── CTA BUTTON ─── */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #90ff50 0%, #40ffc8 100%) !important;
    color: #030310 !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 800 !important; font-size: 1rem !important;
    letter-spacing: 0.07em !important; text-transform: uppercase !important;
    border: none !important; border-radius: 16px !important;
    padding: 0.9rem !important; transition: all 0.25s !important;
}
.stButton > button:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 18px 55px rgba(144,255,80,0.28) !important;
    filter: brightness(1.06) !important;
}
.stButton > button:active { transform: translateY(-1px) !important; }

/* ─── SCAN ROWS ─── */
.scan-row {
    display: flex; align-items: center; gap: 0.9rem;
    background: #09091a; border: 1px solid #141430;
    border-radius: 14px; padding: 0.8rem 1.1rem;
    margin-bottom: 0.5rem;
}
.scan-row.ok  { border-left: 3px solid #90ff50; }
.scan-row.bad { border-left: 3px solid #ff4070; }
.s-icon { font-size: 1.1rem; flex-shrink: 0; }
.s-label { font-weight: 700; font-size: 0.8rem; color: #b0b0d8; min-width: 130px; }
.s-msg { font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: #2e2e58; flex: 1; }
.s-badge {
    padding: 0.18rem 0.65rem; border-radius: 6px;
    font-size: 0.65rem; font-weight: 800; letter-spacing: 0.1em;
    text-transform: uppercase; flex-shrink: 0;
}
.s-ok  { background: rgba(144,255,80,0.1);  border:1px solid rgba(144,255,80,0.25); color:#90ff50; }
.s-bad { background: rgba(255,64,112,0.1);  border:1px solid rgba(255,64,112,0.25); color:#ff4070; }

/* ─── ALERTS ─── */
.alert { border-radius:14px; padding:1rem 1.2rem; margin:0.7rem 0; font-size:0.83rem; line-height:1.6; font-weight:500; }
.a-ok   { background:rgba(144,255,80,0.07);  border:1px solid rgba(144,255,80,0.22);  color:#a0ff60; }
.a-bad  { background:rgba(255,64,112,0.07);  border:1px solid rgba(255,64,112,0.25);  color:#ff6090; }
.a-warn { background:rgba(255,200,50,0.07);  border:1px solid rgba(255,200,50,0.22);  color:#ffc832; }
.a-info { background:rgba(80,160,255,0.07);  border:1px solid rgba(80,160,255,0.22);  color:#60a8ff; }

/* ─── STATS ─── */
.stats { display:grid; grid-template-columns:repeat(3,1fr); gap:0.8rem; margin:0.8rem 0; }
.stat-c {
    background:#09091a; border:1px solid #141430; border-radius:18px;
    padding:1.15rem 0.8rem; text-align:center; position:relative; overflow:hidden;
    transition: transform 0.2s;
}
.stat-c:hover { transform: translateY(-3px); }
.stat-c::after {
    content:''; position:absolute; bottom:0; left:0; right:0; height:2px;
    background:linear-gradient(90deg,#90ff50,#40ffc8); opacity:0.35;
}
.stat-n { font-family:'Syne',sans-serif; font-size:2.1rem; font-weight:800; color:#90ff50; line-height:1; margin-bottom:0.28rem; }
.stat-l { font-size:0.62rem; font-weight:800; letter-spacing:0.13em; text-transform:uppercase; color:#1e1e48; }

/* ─── TAGS ─── */
.tag-row { display:flex; flex-wrap:wrap; gap:0.35rem; margin:0.6rem 0; }
.rtag {
    display:inline-flex; align-items:center; gap:0.3rem;
    padding:0.22rem 0.7rem; border-radius:999px;
    font-size:0.67rem; font-weight:700;
    background:rgba(255,64,128,0.09); border:1px solid rgba(255,64,128,0.22); color:#ff80b0;
}

/* ─── RESULT PANEL ─── */
.result-panel {
    background:#070714; border:1px solid #141430;
    border-radius:20px; overflow:hidden; margin-top:0.8rem;
}
.rp-header {
    background:#0c0c1e; border-bottom:1px solid #141430;
    padding:0.65rem 1.2rem;
    display:flex; align-items:center; justify-content:space-between;
}
.rp-dots { display:flex; gap:0.35rem; }
.rpd { width:11px; height:11px; border-radius:50%; display:inline-block; }
.rpd-r{background:#ff5f56;} .rpd-y{background:#ffbd2e;} .rpd-g{background:#27c93f;}
.rp-title { font-size:0.65rem; font-weight:800; letter-spacing:0.13em; text-transform:uppercase; color:#252548; }
.rp-body {
    padding:1.4rem; font-family:'JetBrains Mono',monospace;
    font-size:0.78rem; line-height:1.9; color:#9090c0;
    white-space:pre-wrap; word-break:break-word;
    max-height:420px; overflow-y:auto;
}
.rp-body::-webkit-scrollbar { width:4px; }
.rp-body::-webkit-scrollbar-thumb { background:#1c1c38; border-radius:4px; }

/* ─── DOWNLOAD BUTTONS ─── */
[data-testid="stDownloadButton"] button {
    background:#0c0c1e !important; color:#7070a0 !important;
    border:1px solid #181838 !important; border-radius:12px !important;
    font-size:0.8rem !important; font-weight:600 !important;
    font-family:'Outfit',sans-serif !important;
    padding:0.65rem !important; width:100% !important;
    transition:all 0.2s !important;
}
[data-testid="stDownloadButton"] button:hover {
    border-color:rgba(144,255,80,0.3) !important;
    color:#90ff50 !important; background:rgba(144,255,80,0.05) !important;
}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# SIDEBAR — only security limit
# ══════════════════════════════════════════════════════════════════════
st.sidebar.markdown("## ⚙️ Settings")
st.sidebar.markdown("**🛡️ Security Limit**")
max_size_mb = st.sidebar.slider("Max file size (MB)", 1, 20, 10)
show_redacted = st.sidebar.checkbox("Show [REDACTED] placeholders", value=True)
st.sidebar.markdown("---")
st.sidebar.markdown("<small style='color:#141432'>DocVault AI · v3.2</small>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# SESSION STATE for toggle cards
# ══════════════════════════════════════════════════════════════════════
defaults = {
    "r_ids": True, "r_phones": True,
    "r_banking": True, "r_passwords": True,
    "r_names": True, "r_dates": True,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ══════════════════════════════════════════════════════════════════════
# SECURITY ENGINE
# ══════════════════════════════════════════════════════════════════════
MALWARE_SIGS = [
    b"TVqQAAMAAAAEAAAA", b"\x4d\x5a\x90\x00", b"\x7fELF",
    b"/JavaScript", b"/JS ", b"eval(", b"unescape(", b"/OpenAction",
    b"/AA ", b"/Launch", b"cmd.exe", b"powershell", b"WScript",
    b"ActiveXObject", b"AutoOpen", b"Auto_Open", b"AutoExec",
    b"Shell(", b"CreateObject(", b"WScript.Shell", b"AAAA"*20,
]
MAGIC = {
    "pdf": [(0,b"%PDF")], "png":[(0,b"\x89PNG\r\n\x1a\n")],
    "jpg": [(0,b"\xff\xd8\xff")], "jpeg":[(0,b"\xff\xd8\xff")],
    "docx":[(0,b"PK\x03\x04")], "xlsx":[(0,b"PK\x03\x04")],
    "pptx":[(0,b"PK\x03\x04")], "ppt":[(0,b"\xd0\xcf\x11\xe0")],
}

def chk_size(fb, mx):
    s = len(fb)/(1024*1024)
    return s<=mx, f"{s:.1f} MB {'· OK' if s<=mx else f'· limit {mx} MB'}"

def chk_magic(fb, ext):
    ext = ext.lower().lstrip(".")
    if ext not in MAGIC: return True, "Format check skipped"
    for off, m in MAGIC[ext]:
        if fb[off:off+len(m)]==m: return True, f"Signature valid · {ext.upper()} confirmed"
    return False, f"Content mismatch for .{ext} — possible disguised file"

def chk_virus(fb):
    hits=[sig.decode("utf-8",errors="replace").strip()[:35] for sig in MALWARE_SIGS if sig in fb]
    return (False,f"Threat: {', '.join(set(hits[:3]))}") if hits else (True,"No malware signatures found")

def chk_integrity(fb, ext):
    ext=ext.lower().lstrip(".")
    try:
        if ext=="pdf":
            import pypdf; r=pypdf.PdfReader(io.BytesIO(fb)); _=len(r.pages)
        elif ext=="docx":
            import docx; docx.Document(io.BytesIO(fb))
        elif ext=="xlsx":
            import openpyxl; openpyxl.load_workbook(io.BytesIO(fb),data_only=True)
        elif ext in("pptx","ppt"):
            from pptx import Presentation; Presentation(io.BytesIO(fb))
        return True,"File opened cleanly · No corruption"
    except Exception as e:
        return False,f"Cannot open file · {str(e)[:80]}"

def security_scan(fb, fname, mx):
    ext=fname.rsplit(".",1)[-1] if "." in fname else ""
    checks=[
        ("📦","File Size",    chk_size(fb,mx)),
        ("🔍","File Type",    chk_magic(fb,ext)),
        ("🦠","Virus Scan",   chk_virus(fb)),
        ("🧩","Integrity",    chk_integrity(fb,ext)),
    ]
    results=[(ico,lbl,ok,msg) for ico,lbl,(ok,msg) in checks]
    return all(ok for _,_,ok,_ in results), results

# ══════════════════════════════════════════════════════════════════════
# EXTRACTION
# ══════════════════════════════════════════════════════════════════════
def extract_pdf(fb):
    try:
        import pypdf; r=pypdf.PdfReader(io.BytesIO(fb))
        return ("".join(p.extract_text() or "" for p in r.pages)).strip() or None
    except: return None

def extract_docx(fb):
    try:
        import docx; doc=docx.Document(io.BytesIO(fb))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip()) or None
    except: return None

def extract_xlsx(fb):
    try:
        import openpyxl; wb=openpyxl.load_workbook(io.BytesIO(fb),data_only=True)
        rows=[]
        for sh in wb.worksheets:
            rows.append(f"[Sheet: {sh.title}]")
            for row in sh.iter_rows(values_only=True):
                l=" | ".join(str(c) for c in row if c is not None)
                if l.strip(): rows.append(l)
        return "\n".join(rows) or None
    except: return None

def extract_pptx(fb):
    try:
        from pptx import Presentation; prs=Presentation(io.BytesIO(fb)); lines=[]
        for i,slide in enumerate(prs.slides,1):
            lines.append(f"[Slide {i}]")
            for sh in slide.shapes:
                if hasattr(sh,"text") and sh.text.strip(): lines.append(sh.text.strip())
        return "\n".join(lines) or None
    except: return None

def extract_image(fb, mime):
    b64=base64.b64encode(fb).decode()
    r=client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role":"user","content":[
            {"type":"image_url","image_url":{"url":f"data:{mime};base64,{b64}"}},
            {"type":"text","text":"Extract ALL visible text. Then describe the image.\n\nTEXT FOUND:\n[text or 'None']\n\nIMAGE DESCRIPTION:\n[description]"}
        ]}], max_tokens=2000)
    return r.choices[0].message.content.strip()

# ══════════════════════════════════════════════════════════════════════
# REDACTION
# ══════════════════════════════════════════════════════════════════════
def build_rules():
    rules=[]
    if st.session_state.r_ids:       rules.append("Government IDs: Aadhaar (12-digit), SSN, PAN (ABCDE1234F), passport, driving licence, voter ID")
    if st.session_state.r_phones:    rules.append("Phone numbers, mobile numbers (+91 or 10-digit), email addresses")
    if st.session_state.r_banking:   rules.append("Bank account numbers, IFSC codes, credit/debit card numbers, CVV, UPI IDs")
    if st.session_state.r_passwords: rules.append("Passwords, API keys, secret keys, tokens, OTPs, PINs")
    if st.session_state.r_names:     rules.append("Full personal names on identity documents")
    if st.session_state.r_dates:     rules.append("Dates of birth in any format, DOB, जन्म तिथि")
    return rules

def regex_redact(text, ph):
    count=0; removed=[]
    def sub(pat,name):
        nonlocal text,count
        n=re.sub(pat,ph,text)
        if n!=text: count+=1; removed.append(name); text=n
    if st.session_state.r_ids:
        sub(r'\b\d{4}\s?\d{4}\s?\d{4}\b',"Aadhaar number")
        sub(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b',"PAN number")
    if st.session_state.r_phones:
        sub(r'\b(\+91[\s-]?)?[6-9]\d{9}\b',"phone number")
        sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', "email address")
    if st.session_state.r_banking:
        sub(r'\b(?:\d[ -]*?){13,16}\b',"card number")
        sub(r'\b[A-Z]{4}0[A-Z0-9]{6}\b',"IFSC code")
    if st.session_state.r_dates:
        sub(r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}\b',"date of birth")
    if st.session_state.r_names:
        n=re.sub(r'(Name|नाम)\s*[:\-]\s*[A-Za-z\s]{3,40}',
                 lambda m:m.group(0).split(':')[0]+': '+ph, text)
        if n!=text: count+=1; removed.append("name field"); text=n
    return text,removed,count

def redact_sensitive(text, rules):
    if not rules: return text,[],0
    ph="[REDACTED]" if show_redacted else "████"
    prompt=f"""You are a strict data-privacy engine. Redact ALL sensitive info.

CATEGORIES:
{chr(10).join(f'- {r}' for r in rules)}

Replace each sensitive value with "{ph}". Preserve all surrounding text. When uncertain, redact.
Return ONLY valid JSON: {{"clean_text":"...","redacted_items":["..."],"redaction_count":0}}

TEXT:
{text[:6000]}"""
    r=client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role":"system","content":"Return only valid JSON."},
                  {"role":"user","content":prompt}],
        temperature=0.0, max_tokens=4000)
    raw=re.sub(r'```json|```','',r.choices[0].message.content.strip()).strip()
    try:
        res=json.loads(raw)
        clean=res.get("clean_text",text)
        items=res.get("redacted_items",[])
        cnt=res.get("redaction_count",0)
        clean,extra,ec=regex_redact(clean,ph)
        return clean,items+extra,cnt+ec
    except:
        return regex_redact(text,"[REDACTED]" if show_redacted else "████")

# ══════════════════════════════════════════════════════════════════════
# PAGE — HERO
# ══════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <div class="hero-aura"></div>
  <div class="eyebrow"><span class="live-dot"></span>&nbsp;AI · Secure · Private</div>
  <div class="hero-title">Doc<span class="g">Vault</span></div>
  <div class="hero-sub">Extract text from any document, scan for threats, and auto-redact sensitive data — in seconds.</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# SECURITY FEATURES INTRO
# ══════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-head">🛡️ Security Engine</div>', unsafe_allow_html=True)
st.markdown("""
<div class="shield-banner">
  <div class="shield-row-title">
    <span class="shield-badge">All Active</span>
    <span class="shield-title">4-Layer File Protection</span>
  </div>
  <div class="shield-grid">
    <div class="shield-item">
      <div class="si-icon">📦</div>
      <div>
        <div class="si-name">File Size Limit</div>
        <div class="si-desc">Oversized files are rejected before processing begins</div>
      </div>
    </div>
    <div class="shield-item">
      <div class="si-icon">🦠</div>
      <div>
        <div class="si-name">Virus / Malware Scan</div>
        <div class="si-desc">Byte-level scan for PE executables, macro exploits & PDF attacks</div>
      </div>
    </div>
    <div class="shield-item">
      <div class="si-icon">🧩</div>
      <div>
        <div class="si-name">Corrupted File Detection</div>
        <div class="si-desc">Files that fail to open are immediately rejected</div>
      </div>
    </div>
    <div class="shield-item">
      <div class="si-icon">🔍</div>
      <div>
        <div class="si-name">File Type Verification</div>
        <div class="si-desc">Magic-byte check catches renamed or disguised files</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# SENSITIVE DATA TOGGLE CARDS — interactive via Streamlit buttons
# ══════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-head">🔒 What counts as sensitive?</div>', unsafe_allow_html=True)
st.markdown("<p style='font-size:0.78rem;color:#282858;margin-bottom:0.9rem;'>Select which data types to auto-redact from your document.</p>", unsafe_allow_html=True)

REDACT_OPTIONS = [
    ("r_ids",       "🪪", "Aadhaar / SSN / ID",    "Government ID numbers, PAN, passport, driving licence"),
    ("r_phones",    "📞", "Phone & Email",          "Mobile numbers, landlines, email addresses"),
    ("r_banking",   "💳", "Bank / Card Numbers",    "Account numbers, IFSC, credit/debit cards, UPI IDs"),
    ("r_passwords", "🔑", "Passwords & Secret Keys","API keys, tokens, PINs, OTPs, passwords"),
    ("r_names",     "👤", "Personal Names",         "Full names on identity or official documents"),
    ("r_dates",     "📅", "Dates of Birth",         "DOB in any format, जन्म तिथि, year of birth"),
]

# Render 2-column grid of toggle cards using Streamlit columns + buttons
cols = st.columns(2)
for i, (key, icon, name, desc) in enumerate(REDACT_OPTIONS):
    active = st.session_state[key]
    on_cls  = "ON" if active else ""
    tog_style = (
        "background:#90ff50;border-color:#90ff50;" if active else
        "background:#141430;border-color:#202048;"
    )
    thumb_style = (
        "transform:translateX(18px);background:#050510;" if active else
        "transform:translateX(0);background:#282858;"
    )
    card_html = f"""
    <div class="redact-card {on_cls}" style="margin-bottom:0;">
      <div class="rc-icon-wrap">{icon}</div>
      <div class="rc-body">
        <div class="rc-name">{name}</div>
        <div class="rc-desc">{desc}</div>
      </div>
      <div class="rc-toggle" style="{tog_style}">
        <span style="position:absolute;top:2px;left:2px;width:12px;height:12px;
          border-radius:50%;transition:all 0.22s ease;{thumb_style}
          display:inline-block;"></span>
      </div>
    </div>
    """
    with cols[i % 2]:
        st.markdown(card_html, unsafe_allow_html=True)
        btn_label = f"{'✅ ON' if active else '○ OFF'} — {name}"
        if st.button(btn_label, key=f"btn_{key}", use_container_width=True):
            st.session_state[key] = not st.session_state[key]
            st.rerun()

# Show active summary
active_names = [name for key,_,name,_ in REDACT_OPTIONS if st.session_state[key]]
if active_names:
    tags_html = "".join(f'<span class="rtag">✓ {n}</span>' for n in active_names)
    st.markdown(f'<div class="tag-row" style="margin-top:0.6rem;">{tags_html}</div>', unsafe_allow_html=True)
else:
    st.markdown('<div class="alert a-warn" style="margin-top:0.5rem;">⚠️ No redaction rules selected — full text will be shown as-is.</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════
# UPLOAD
# ══════════════════════════════════════════════════════════════════════
st.markdown('<div class="sec-head">📎 Upload Document</div>', unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Drop your file here — PDF, Word, Excel, PowerPoint, or Image",
    type=["pdf","png","jpg","jpeg","docx","xlsx","pptx","ppt"],
    label_visibility="collapsed"
)

if uploaded:
    st.markdown(
        f'<div class="file-chip"><span class="cdot"></span>'
        f'&nbsp;{uploaded.name}&nbsp;·&nbsp;{uploaded.type}&nbsp;·&nbsp;{uploaded.size/1024:.1f} KB</div>',
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)
run = st.button("🔐  Scan · Extract · Redact", use_container_width=True)

# ══════════════════════════════════════════════════════════════════════
# PIPELINE
# ══════════════════════════════════════════════════════════════════════
if run and not uploaded:
    st.markdown('<div class="alert a-warn">⚠️ Please upload a file first.</div>', unsafe_allow_html=True)
    st.stop()

if run and uploaded:
    file_bytes = uploaded.read()
    mime = uploaded.type
    name = uploaded.name.lower()

    # ── SECURITY SCAN ──
    st.markdown('<div class="sec-head">🛡️ Security Scan</div>', unsafe_allow_html=True)
    with st.spinner("Running 4-layer security scan..."):
        passed, scan_results = security_scan(file_bytes, name, max_size_mb)

    for ico, lbl, ok, msg in scan_results:
        cls = "ok" if ok else "bad"
        bc  = "s-ok" if ok else "s-bad"
        bt  = "PASSED" if ok else "FAILED"
        st.markdown(f"""
        <div class="scan-row {cls}">
          <span class="s-icon">{ico}</span>
          <span class="s-label">{lbl}</span>
          <span class="s-msg">{msg}</span>
          <span class="s-badge {bc}">{bt}</span>
        </div>""", unsafe_allow_html=True)

    if not passed:
        st.markdown('<div class="alert a-bad">🚫 <strong>File rejected.</strong> One or more security checks failed. Please upload a clean, valid file.</div>', unsafe_allow_html=True)
        st.stop()

    st.markdown('<div class="alert a-ok">✅ <strong>All 4 security checks passed.</strong> Proceeding to extraction.</div>', unsafe_allow_html=True)

    # ── EXTRACT ──
    st.markdown('<div class="sec-head">📖 Extraction</div>', unsafe_allow_html=True)
    raw_text = None
    with st.spinner("Extracting text..."):
        try:
            if name.endswith(".pdf"):
                raw_text = extract_pdf(file_bytes)
                if not raw_text:
                    st.markdown('<div class="alert a-info">ℹ️ Native PDF extraction empty — using AI Vision OCR...</div>', unsafe_allow_html=True)
                    raw_text = extract_image(file_bytes, "application/pdf")
            elif name.endswith((".png",".jpg",".jpeg")):
                raw_text = extract_image(file_bytes, mime)
            elif name.endswith(".docx"):
                raw_text = extract_docx(file_bytes)
            elif name.endswith(".xlsx"):
                raw_text = extract_xlsx(file_bytes)
            elif name.endswith((".pptx",".ppt")):
                raw_text = extract_pptx(file_bytes)
                if not raw_text: raw_text = extract_image(file_bytes, mime)
        except Exception as e:
            st.markdown(f'<div class="alert a-bad">❌ Extraction error: {e}</div>', unsafe_allow_html=True)

    if not raw_text or len(raw_text.strip()) < 5:
        st.markdown('<div class="alert a-warn">⚠️ No readable text found in this file.</div>', unsafe_allow_html=True)
        st.stop()

    # ── REDACT ──
    st.markdown('<div class="sec-head">🔒 Redaction</div>', unsafe_allow_html=True)
    rules = build_rules()
    clean_text, items, count = raw_text, [], 0

    if rules:
        with st.spinner("AI scanning for sensitive data..."):
            try:
                clean_text, items, count = redact_sensitive(raw_text, rules)
            except Exception as e:
                st.markdown(f'<div class="alert a-warn">⚠️ AI redaction failed, using regex fallback: {e}</div>', unsafe_allow_html=True)
                clean_text, items, count = regex_redact(raw_text, "[REDACTED]" if show_redacted else "████")
    else:
        st.markdown('<div class="alert a-info">ℹ️ No redaction rules active.</div>', unsafe_allow_html=True)

    # ── RESULTS ──
    st.markdown('<div class="sec-head">📊 Results</div>', unsafe_allow_html=True)

    slabel = "✅ CLEAN" if count==0 else "🔒 REDACTED"
    scolor = "#90ff50" if count==0 else "#ff80b0"

    st.markdown(f"""
    <div class="stats">
      <div class="stat-c">
        <div class="stat-n">{len(clean_text.split()):,}</div>
        <div class="stat-l">Words Extracted</div>
      </div>
      <div class="stat-c">
        <div class="stat-n">{count}</div>
        <div class="stat-l">Items Redacted</div>
      </div>
      <div class="stat-c">
        <div class="stat-n" style="color:{scolor};font-size:1.05rem;padding-top:0.55rem">{slabel}</div>
        <div class="stat-l">Document Status</div>
      </div>
    </div>""", unsafe_allow_html=True)

    if items:
        tags="".join(f'<span class="rtag">✕ {i}</span>' for i in set(items))
        st.markdown(f'<div class="tag-row">{tags}</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="result-panel">
      <div class="rp-header">
        <div class="rp-dots"><span class="rpd rpd-r"></span><span class="rpd rpd-y"></span><span class="rpd rpd-g"></span></div>
        <div class="rp-title">📝 &nbsp;Extracted Output</div>
        <div></div>
      </div>
      <div class="rp-body">{clean_text}</div>
    </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.download_button("⬇️ Download .txt", clean_text, f"{uploaded.name}_clean.txt", "text/plain", use_container_width=True)
    c2.download_button(
        "⬇️ Download .json",
        json.dumps({"filename":uploaded.name,"extracted_text":clean_text,
                    "redacted_count":count,"redacted_categories":list(set(items)),
                    "security_scan":{r[1]:r[2] for r in scan_results}},indent=2),
        f"{uploaded.name}_clean.json","application/json",use_container_width=True
    )
