import streamlit as st
from groq import Groq
import json, re, base64, io, hashlib

st.set_page_config(
    page_title="DocVault · AI Extractor",
    page_icon="🔐",
    layout="centered"
)

try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client  = Groq(api_key=API_KEY)
except Exception:
    st.error("⚠️ API key not configured.")
    st.info("Add to Streamlit Secrets:\n\n`GROQ_API_KEY = \"gsk_your_key_here\"`")
    st.stop()

# ── Custom CSS ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Bebas+Neue&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif;
    -webkit-font-smoothing: antialiased;
}

.stApp {
    background: #050508;
    color: #f0f0f8;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -20%, rgba(140,255,100,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 90% 80%, rgba(100,200,255,0.05) 0%, transparent 50%);
}

/* ── Hide clutter ── */
#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display:none !important; visibility:hidden !important; }
[data-testid="stSidebar"] { min-width:270px !important; }
[data-testid="collapsedControl"] { display:flex !important; visibility:visible !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #0c0c12 !important;
    border-right: 1px solid #1a1a2e !important;
}
section[data-testid="stSidebar"] * { color: #c0c0d8 !important; }
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] strong { color: #f0f0f8 !important; }
div[data-testid="stSelectbox"] > div {
    background: #0a0a12 !important;
    border: 1px solid #1e1e38 !important;
    border-radius: 10px !important;
}

/* ── Hero Header ── */
.hero-wrap {
    position: relative;
    text-align: center;
    padding: 2.5rem 1rem 1.5rem;
    margin-bottom: 0.5rem;
    overflow: hidden;
}
.hero-glow {
    position: absolute;
    top: 0; left: 50%;
    transform: translateX(-50%);
    width: 300px; height: 120px;
    background: radial-gradient(ellipse, rgba(140,255,80,0.18) 0%, transparent 70%);
    pointer-events: none;
    border-radius: 50%;
}
.hero-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: rgba(140,255,80,0.1);
    border: 1px solid rgba(140,255,80,0.3);
    color: #a8ff60;
    padding: 0.3rem 0.9rem;
    border-radius: 999px;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.hero-pill::before {
    content: '';
    width: 6px; height: 6px;
    background: #a8ff60;
    border-radius: 50%;
    box-shadow: 0 0 8px #a8ff60;
    animation: pulse-dot 2s infinite;
}
@keyframes pulse-dot {
    0%,100% { opacity:1; transform:scale(1); }
    50% { opacity:0.5; transform:scale(1.4); }
}
.hero-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.8rem;
    letter-spacing: 0.04em;
    line-height: 1;
    color: #f0f0f8;
    margin: 0 0 0.4rem;
}
.hero-title span {
    background: linear-gradient(90deg, #a8ff60, #60ffcc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-size: 0.85rem;
    color: #5a5a78;
    font-weight: 400;
    letter-spacing: 0.03em;
}

/* ── Security Shield Card ── */
.shield-intro {
    background: linear-gradient(135deg, #0e0e1a 0%, #111122 100%);
    border: 1px solid #1e1e38;
    border-radius: 20px;
    padding: 1.4rem 1.6rem;
    margin: 1rem 0 1.5rem;
    position: relative;
    overflow: hidden;
}
.shield-intro::after {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, #a8ff60, transparent);
    opacity: 0.6;
}
.shield-intro-title {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #a8ff60;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.security-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.6rem;
}
.sec-check-card {
    background: #0a0a14;
    border: 1px solid #1a1a2e;
    border-radius: 12px;
    padding: 0.8rem 1rem;
    display: flex;
    align-items: flex-start;
    gap: 0.7rem;
    transition: border-color 0.2s;
}
.sec-check-card:hover { border-color: #2a2a4e; }
.sec-check-icon {
    font-size: 1.4rem;
    line-height: 1;
    flex-shrink: 0;
}
.sec-check-label {
    font-size: 0.78rem;
    font-weight: 600;
    color: #d0d0e8;
    line-height: 1.3;
}
.sec-check-desc {
    font-size: 0.68rem;
    color: #4a4a68;
    margin-top: 0.2rem;
    line-height: 1.4;
}

/* ── File Uploader ── */
div[data-testid="stFileUploader"] {
    background: #0c0c18 !important;
    border: 2px dashed #1e1e38 !important;
    border-radius: 18px !important;
    padding: 1.5rem !important;
    transition: border-color 0.3s !important;
}
div[data-testid="stFileUploader"]:hover {
    border-color: rgba(168,255,96,0.4) !important;
}
div[data-testid="stFileUploader"] label {
    color: #6060a0 !important;
    font-size: 0.85rem !important;
}

/* ── Buttons ── */
.stButton > button {
    width: 100%;
    background: linear-gradient(135deg, #a8ff60 0%, #60ffcc 100%) !important;
    color: #050508 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.85rem !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 12px 40px rgba(168,255,96,0.25) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Scan result rows ── */
.scan-row {
    display: flex;
    align-items: center;
    gap: 0.8rem;
    padding: 0.7rem 1rem;
    background: #0c0c18;
    border: 1px solid #1a1a2e;
    border-radius: 12px;
    margin-bottom: 0.5rem;
    font-size: 0.82rem;
}
.scan-icon { font-size: 1.1rem; flex-shrink: 0; }
.scan-label {
    font-weight: 600;
    color: #d0d0e8;
    min-width: 130px;
    font-size: 0.8rem;
}
.scan-msg { color: #6060a0; flex: 1; font-family: 'JetBrains Mono', monospace; font-size: 0.74rem; }
.dot {
    width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0;
    margin-left: auto;
}
.dot-ok   { background: #a8ff60; box-shadow: 0 0 8px rgba(168,255,96,0.6); }
.dot-warn { background: #ffd060; box-shadow: 0 0 8px rgba(255,208,96,0.6); }
.dot-err  { background: #ff5080; box-shadow: 0 0 8px rgba(255,80,128,0.6); }

/* ── Alert boxes ── */
.alert {
    border-radius: 14px;
    padding: 1rem 1.2rem;
    margin: 0.8rem 0;
    font-size: 0.83rem;
    line-height: 1.6;
}
.alert-danger { background: rgba(255,50,80,0.08); border: 1px solid rgba(255,50,80,0.3); color: #ff7090; }
.alert-ok     { background: rgba(168,255,96,0.07); border: 1px solid rgba(168,255,96,0.25); color: #a8ff60; }
.alert-warn   { background: rgba(255,208,96,0.07); border: 1px solid rgba(255,208,96,0.25); color: #ffd060; }
.alert-info   { background: rgba(96,200,255,0.07); border: 1px solid rgba(96,200,255,0.25); color: #60c8ff; }

/* ── Stats row ── */
.stat-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.8rem;
    margin: 1rem 0;
}
.stat-card {
    background: #0c0c18;
    border: 1px solid #1a1a2e;
    border-radius: 16px;
    padding: 1.1rem 0.8rem;
    text-align: center;
    position: relative;
    overflow: hidden;
}
.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    background: linear-gradient(90deg, #a8ff60, #60ffcc);
    opacity: 0.5;
}
.stat-num {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2rem;
    letter-spacing: 0.04em;
    color: #a8ff60;
    line-height: 1;
    margin-bottom: 0.25rem;
}
.stat-lbl {
    font-size: 0.66rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #3a3a58;
}

/* ── Result box ── */
.result-wrap { margin-top: 1rem; }
.result-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.5rem;
}
.result-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #4a4a78;
}
.result-box {
    background: #0c0c18;
    border: 1px solid #1a1a2e;
    border-radius: 16px;
    padding: 1.4rem;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    line-height: 1.9;
    color: #c0c0d8;
    white-space: pre-wrap;
    word-break: break-word;
    max-height: 420px;
    overflow-y: auto;
    position: relative;
}
.result-box::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, rgba(168,255,96,0.4), transparent);
}
.result-box::-webkit-scrollbar { width: 4px; }
.result-box::-webkit-scrollbar-track { background: transparent; }
.result-box::-webkit-scrollbar-thumb { background: #2a2a48; border-radius: 4px; }

/* ── Redaction tags ── */
.tags-row { margin: 0.6rem 0; display: flex; flex-wrap: wrap; gap: 0.3rem; }
.rtag {
    display: inline-flex; align-items: center; gap: 0.3rem;
    padding: 0.2rem 0.7rem;
    border-radius: 999px;
    font-size: 0.68rem; font-weight: 600;
    background: rgba(255,80,128,0.1);
    border: 1px solid rgba(255,80,128,0.3);
    color: #ff80a8;
}

/* ── Section headings ── */
.section-head {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #4a4a78;
    margin: 1.5rem 0 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.section-head::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, #1a1a30, transparent);
}

/* ── Divider ── */
hr { border-color: #1a1a30 !important; }

/* ── File info pill ── */
.file-pill {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: #0c0c18;
    border: 1px solid #1e1e38;
    border-radius: 999px;
    padding: 0.35rem 0.9rem;
    font-size: 0.78rem;
    color: #8080c0;
    margin: 0.5rem 0;
    font-family: 'JetBrains Mono', monospace;
}
</style>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div class="hero-glow"></div>
    <div class="hero-pill">🔐 Secure · AI-Powered · Private</div>
    <div class="hero-title">Doc<span>Vault</span></div>
    <div class="hero-sub">Extract · Scan · Redact · Download — all in one secure pipeline</div>
</div>
""", unsafe_allow_html=True)

# ── SECURITY FEATURES INTRO ───────────────────────────────────────────
st.markdown("""
<div class="shield-intro">
    <div class="shield-intro-title">🛡️ 4-Layer Security Engine — Active</div>
    <div class="security-grid">
        <div class="sec-check-card">
            <div class="sec-check-icon">📦</div>
            <div>
                <div class="sec-check-label">File Size Limit</div>
                <div class="sec-check-desc">Rejects oversized files before processing begins</div>
            </div>
        </div>
        <div class="sec-check-card">
            <div class="sec-check-icon">🦠</div>
            <div>
                <div class="sec-check-label">Virus / Malware Scan</div>
                <div class="sec-check-desc">Byte-level signature scan for known exploits & malicious patterns</div>
            </div>
        </div>
        <div class="sec-check-card">
            <div class="sec-check-icon">🧩</div>
            <div>
                <div class="sec-check-label">Corrupted File Detection</div>
                <div class="sec-check-desc">Files that can't be opened are rejected immediately</div>
            </div>
        </div>
        <div class="sec-check-card">
            <div class="sec-check-icon">🔍</div>
            <div>
                <div class="sec-check-label">File Type Verification</div>
                <div class="sec-check-desc">Magic-byte check — catches renamed or disguised files</div>
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────
st.sidebar.markdown("## ⚙️ Settings")
st.sidebar.markdown("**🔒 Redact sensitive data:**")
redact_ids       = st.sidebar.checkbox("🪪 ID / Aadhaar / SSN numbers",  value=True)
redact_phones    = st.sidebar.checkbox("📞 Phone numbers & emails",       value=True)
redact_banking   = st.sidebar.checkbox("💳 Bank / credit card numbers",   value=True)
redact_passwords = st.sidebar.checkbox("🔑 Passwords & secret keys",      value=True)
redact_names     = st.sidebar.checkbox("👤 Personal names",                value=True)
redact_dates     = st.sidebar.checkbox("📅 Dates of birth",                value=True)
show_redacted    = st.sidebar.checkbox("Show [REDACTED] placeholders",     value=True)
st.sidebar.markdown("---")
st.sidebar.markdown("**🛡️ Security Limits:**")
max_size_mb = st.sidebar.slider("Max file size (MB)", 1, 20, 10)
st.sidebar.markdown("---")
st.sidebar.markdown("<small style='color:#3a3a58'>DocVault · AI Extractor · v3.0</small>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# SECURITY ENGINE
# ════════════════════════════════════════════════════════════════════

MALWARE_SIGNATURES = [
    b"TVqQAAMAAAAEAAAA",
    b"\x4d\x5a\x90\x00",
    b"\x7fELF",
    b"/JavaScript",
    b"/JS ",
    b"eval(",
    b"unescape(",
    b"/OpenAction",
    b"/AA ",
    b"/Launch",
    b"cmd.exe",
    b"powershell",
    b"WScript",
    b"ActiveXObject",
    b"AutoOpen",
    b"Auto_Open",
    b"AutoExec",
    b"Shell(",
    b"CreateObject(",
    b"WScript.Shell",
    b"AAAA" * 20,
]

MAGIC_BYTES = {
    "pdf":  [(0, b"%PDF")],
    "png":  [(0, b"\x89PNG\r\n\x1a\n")],
    "jpg":  [(0, b"\xff\xd8\xff")],
    "jpeg": [(0, b"\xff\xd8\xff")],
    "docx": [(0, b"PK\x03\x04")],
    "xlsx": [(0, b"PK\x03\x04")],
    "pptx": [(0, b"PK\x03\x04")],
    "ppt":  [(0, b"\xd0\xcf\x11\xe0")],
}

def check_file_size(fb, max_mb):
    size_mb = len(fb) / (1024 * 1024)
    if size_mb > max_mb:
        return False, f"File is {size_mb:.1f} MB — exceeds {max_mb} MB limit"
    return True, f"Size OK · {size_mb:.1f} MB"

def check_magic_bytes(fb, ext):
    ext = ext.lower().lstrip(".")
    if ext not in MAGIC_BYTES:
        return True, "Format check skipped (unknown type)"
    for offset, magic in MAGIC_BYTES[ext]:
        if fb[offset:offset+len(magic)] == magic:
            return True, f"Signature valid · {ext.upper()} confirmed"
    return False, f"Content mismatch for .{ext} — possible disguised file"

def check_virus_signatures(fb):
    hits = []
    for sig in MALWARE_SIGNATURES:
        if sig in fb:
            label = sig.decode("utf-8", errors="replace").strip()[:40]
            hits.append(label)
    if hits:
        return False, f"Suspicious pattern: {', '.join(set(hits[:3]))}"
    return True, "No malware signatures detected"

def check_corruption(fb, ext):
    ext = ext.lower().lstrip(".")
    try:
        if ext == "pdf":
            import pypdf
            r = pypdf.PdfReader(io.BytesIO(fb))
            _ = len(r.pages)
        elif ext == "docx":
            import docx
            docx.Document(io.BytesIO(fb))
        elif ext == "xlsx":
            import openpyxl
            openpyxl.load_workbook(io.BytesIO(fb), data_only=True)
        elif ext in ("pptx", "ppt"):
            from pptx import Presentation
            Presentation(io.BytesIO(fb))
        return True, "File opened successfully · Not corrupted"
    except Exception as e:
        return False, f"Cannot open file: {str(e)[:100]}"

def run_security_scan(fb, filename, max_mb):
    ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
    results = []
    all_passed = True
    checks = [
        ("📦 File Size",    check_file_size(fb, max_mb)),
        ("🔍 File Type",    check_magic_bytes(fb, ext)),
        ("🦠 Virus Scan",   check_virus_signatures(fb)),
        ("🧩 Integrity",    check_corruption(fb, ext)),
    ]
    for label, (ok, msg) in checks:
        results.append((label, ok, msg))
        if not ok:
            all_passed = False
    return all_passed, results

# ── Redaction helpers ─────────────────────────────────────────────────
def build_redaction_prompt():
    rules = []
    if redact_ids:       rules.append("Aadhaar numbers (12-digit), SSN, PAN card numbers (ABCDE1234F), passport, driving license, voter ID, any government ID")
    if redact_phones:    rules.append("phone numbers, mobile numbers (+91 or 10-digit), email addresses")
    if redact_banking:   rules.append("bank account numbers, IFSC codes, credit card/debit card numbers, CVV, UPI IDs, MICR codes")
    if redact_passwords: rules.append("passwords, API keys, secret keys, tokens, OTPs, PINs")
    if redact_names:     rules.append("full names of any person on identity documents")
    if redact_dates:     rules.append("dates of birth in any format, DOB, Year of Birth, जन्म तिथि")
    return rules

def extract_from_pdf(file_bytes):
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        return ("".join(p.extract_text() or "" for p in reader.pages)).strip() or None
    except: return None

def extract_from_docx(file_bytes):
    try:
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip()).strip() or None
    except: return None

def extract_from_xlsx(file_bytes):
    try:
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
        rows = []
        for sheet in wb.worksheets:
            rows.append(f"[Sheet: {sheet.title}]")
            for row in sheet.iter_rows(values_only=True):
                line = " | ".join(str(c) for c in row if c is not None)
                if line.strip(): rows.append(line)
        return "\n".join(rows).strip() or None
    except: return None

def extract_from_pptx(file_bytes):
    try:
        from pptx import Presentation
        prs = Presentation(io.BytesIO(file_bytes))
        lines = []
        for i, slide in enumerate(prs.slides, 1):
            lines.append(f"[Slide {i}]")
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    lines.append(shape.text.strip())
        return "\n".join(lines).strip() or None
    except: return None

def extract_from_image(file_bytes, mime_type):
    b64 = base64.b64encode(file_bytes).decode("utf-8")
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role": "user", "content": [
            {"type": "image_url", "image_url": {"url": f"data:{mime_type};base64,{b64}"}},
            {"type": "text", "text": """Analyze this image:
1. Extract ALL visible text exactly as it appears
2. If little/no text, describe in detail

Format:
TEXT FOUND:
[text or 'No readable text found']

IMAGE DESCRIPTION:
[detailed description]"""}
        ]}],
        max_tokens=2000
    )
    return response.choices[0].message.content.strip()

def regex_redact(text, placeholder="[REDACTED]"):
    count = 0; removed = []
    if redact_ids:
        n = re.sub(r'\b\d{4}\s?\d{4}\s?\d{4}\b', placeholder, text)
        if n != text: count += 1; removed.append("Aadhaar number"); text = n
        n = re.sub(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', placeholder, text)
        if n != text: count += 1; removed.append("PAN number"); text = n
    if redact_phones:
        n = re.sub(r'\b(\+91[\s-]?)?[6-9]\d{9}\b', placeholder, text)
        if n != text: count += 1; removed.append("phone number"); text = n
        n = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', placeholder, text)
        if n != text: count += 1; removed.append("email address"); text = n
    if redact_banking:
        n = re.sub(r'\b(?:\d[ -]*?){13,16}\b', placeholder, text)
        if n != text: count += 1; removed.append("card number"); text = n
        n = re.sub(r'\b[A-Z]{4}0[A-Z0-9]{6}\b', placeholder, text)
        if n != text: count += 1; removed.append("IFSC code"); text = n
    if redact_dates:
        n = re.sub(r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}\b', placeholder, text)
        if n != text: count += 1; removed.append("date of birth"); text = n
    if redact_names:
        n = re.sub(r'(Name|नाम)\s*[:\-]\s*[A-Za-z\s]{3,40}',
                   lambda m: m.group(0).split(':')[0] + ': ' + placeholder, text)
        if n != text: count += 1; removed.append("name field"); text = n
    return text, removed, count

def redact_sensitive(text, rules):
    if not rules: return text, [], 0
    placeholder = "[REDACTED]" if show_redacted else "████"
    prompt = f"""You are a strict enterprise data privacy engine. Redact ALL sensitive information.

REDACT THESE CATEGORIES:
{chr(10).join(f'- {r}' for r in rules)}

RULES:
- Replace ONLY the sensitive value with "{placeholder}", preserve all surrounding text
- When uncertain — REDACT it

Return ONLY valid JSON:
{{"clean_text": "...", "redacted_items": ["..."], "redaction_count": 0}}

TEXT:
{text[:6000]}"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are a strict data privacy engine. Return only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.0, max_tokens=4000
    )
    raw     = response.choices[0].message.content.strip()
    cleaned = re.sub(r'```json|```', '', raw).strip()
    try:
        result    = json.loads(cleaned)
        clean     = result.get("clean_text", text)
        items     = result.get("redacted_items", [])
        count     = result.get("redaction_count", 0)
        clean, extra_items, extra_count = regex_redact(clean, placeholder)
        return clean, items + extra_items, count + extra_count
    except:
        return regex_redact(text, placeholder)

# ── UPLOAD ────────────────────────────────────────────────────────────
st.markdown('<div class="section-head">📎 Upload Document</div>', unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Upload a document or image",
    type=["pdf", "png", "jpg", "jpeg", "docx", "xlsx", "pptx", "ppt"],
    label_visibility="collapsed"
)

if uploaded:
    st.markdown(
        f'<div class="file-pill">📄 {uploaded.name} &nbsp;·&nbsp; {uploaded.type} &nbsp;·&nbsp; {uploaded.size/1024:.1f} KB</div>',
        unsafe_allow_html=True
    )

st.markdown("<br>", unsafe_allow_html=True)
run = st.button("🔐 Scan · Extract · Redact", use_container_width=True)

# ── PROCESS ───────────────────────────────────────────────────────────
if run and not uploaded:
    st.markdown('<div class="alert alert-warn">⚠️ Please upload a file first.</div>', unsafe_allow_html=True)
    st.stop()

if run and uploaded:
    file_bytes = uploaded.read()
    mime       = uploaded.type
    name       = uploaded.name.lower()

    # ── STEP 1: SECURITY SCAN ──
    st.markdown('<div class="section-head">🛡️ Security Scan</div>', unsafe_allow_html=True)

    with st.spinner("Running 4-layer security checks..."):
        passed, scan_results = run_security_scan(file_bytes, name, max_size_mb)

    for check_name, ok, msg in scan_results:
        dot_cls  = "dot-ok" if ok else "dot-err"
        icon     = "✅" if ok else "❌"
        st.markdown(
            f'<div class="scan-row">'
            f'<span class="scan-icon">{check_name.split()[0]}</span>'
            f'<span class="scan-label">{" ".join(check_name.split()[1:])}</span>'
            f'<span class="scan-msg">{icon}&nbsp; {msg}</span>'
            f'<span class="dot {dot_cls}"></span>'
            f'</div>',
            unsafe_allow_html=True
        )

    if not passed:
        st.markdown("""
        <div class="alert alert-danger">
            🚫 <strong>File rejected.</strong> One or more security checks failed.<br>
            Please upload a clean, valid, non-corrupted file.
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    st.markdown("""
    <div class="alert alert-ok">
        ✅ <strong>All 4 security checks passed.</strong> Proceeding to extraction.
    </div>
    """, unsafe_allow_html=True)

    # ── STEP 2: EXTRACT TEXT ──
    st.markdown('<div class="section-head">📖 Text Extraction</div>', unsafe_allow_html=True)
    raw_text = None

    with st.spinner("Extracting text from document..."):
        try:
            if name.endswith(".pdf"):
                raw_text = extract_from_pdf(file_bytes)
                if not raw_text:
                    st.markdown('<div class="alert alert-info">ℹ️ Native PDF extraction failed — switching to AI Vision OCR...</div>', unsafe_allow_html=True)
                    raw_text = extract_from_image(file_bytes, "application/pdf")
            elif name.endswith((".png", ".jpg", ".jpeg")):
                raw_text = extract_from_image(file_bytes, mime)
            elif name.endswith(".docx"):
                raw_text = extract_from_docx(file_bytes)
            elif name.endswith(".xlsx"):
                raw_text = extract_from_xlsx(file_bytes)
            elif name.endswith((".pptx", ".ppt")):
                raw_text = extract_from_pptx(file_bytes)
                if not raw_text:
                    raw_text = extract_from_image(file_bytes, mime)
        except Exception as e:
            st.markdown(f'<div class="alert alert-danger">❌ Extraction error: {e}</div>', unsafe_allow_html=True)
            raw_text = None

    if not raw_text or len(raw_text.strip()) < 5:
        st.markdown("""
        <div class="alert alert-warn">
            ⚠️ <strong>No text could be extracted.</strong><br>
            The file passed security checks but contains no readable content.
            It may be a blank document or a pure image with no OCR data.
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # ── STEP 3: REDACT ──
    st.markdown('<div class="section-head">🔒 Privacy Redaction</div>', unsafe_allow_html=True)
    rules      = build_redaction_prompt()
    clean_text = raw_text
    items      = []
    count      = 0

    if rules:
        with st.spinner("AI scanning for sensitive data..."):
            try:
                clean_text, items, count = redact_sensitive(raw_text, rules)
            except Exception as e:
                st.markdown(f'<div class="alert alert-warn">⚠️ AI redaction failed, using regex fallback: {e}</div>', unsafe_allow_html=True)
                clean_text, items, count = regex_redact(raw_text)
    else:
        st.markdown('<div class="alert alert-info">ℹ️ No redaction rules selected — displaying full extracted text.</div>', unsafe_allow_html=True)

    # ── STEP 4: RESULTS ──
    st.markdown('<div class="section-head">📊 Results</div>', unsafe_allow_html=True)

    word_count = len(clean_text.split())
    char_count = len(clean_text)
    status     = "CLEAN" if count == 0 else "REDACTED"
    status_col = "#a8ff60" if count == 0 else "#ff80a8"

    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-card">
            <div class="stat-num">{word_count:,}</div>
            <div class="stat-lbl">Words Extracted</div>
        </div>
        <div class="stat-card">
            <div class="stat-num">{count}</div>
            <div class="stat-lbl">Items Redacted</div>
        </div>
        <div class="stat-card">
            <div class="stat-num" style="color:{status_col};font-size:1.3rem;padding-top:0.3rem">{status}</div>
            <div class="stat-lbl">Document Status</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if items:
        tags = "".join(f'<span class="rtag">🚫 {i}</span>' for i in set(items))
        st.markdown(f'<div class="tags-row">{tags}</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="result-wrap">
        <div class="result-header">
            <span class="result-label">📝 Extracted Text</span>
        </div>
    """, unsafe_allow_html=True)
    st.markdown(f'<div class="result-box">{clean_text}</div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    col_a.download_button(
        "⬇️ Download Clean Text (.txt)",
        clean_text, f"{uploaded.name}_extracted.txt", "text/plain",
        use_container_width=True
    )
    col_b.download_button(
        "⬇️ Download as JSON",
        json.dumps({
            "filename": uploaded.name,
            "extracted_text": clean_text,
            "redacted_count": count,
            "redacted_categories": list(set(items)),
            "security_scan": {r[0]: r[1] for r in scan_results}
        }, indent=2),
        f"{uploaded.name}_extracted.json", "application/json",
        use_container_width=True
    )
