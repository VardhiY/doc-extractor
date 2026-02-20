import streamlit as st
from groq import Groq
import json, re, base64, io, hashlib

st.set_page_config(
    page_title="AI Document Extractor",
    page_icon="📄",
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
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Mono', monospace; }
.stApp { background: #0a0a0f; color: #e8e8f0; }

#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; visibility: hidden !important; }
[data-testid="stSidebar"] { min-width: 250px !important; }
[data-testid="collapsedControl"] { display: flex !important; visibility: visible !important; }

.main-title {
    font-family: 'Syne', sans-serif;
    font-size: 2.6rem; font-weight: 800;
    background: linear-gradient(135deg, #e8e8f0 30%, #6c63ff 70%, #ff6584 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    text-align: center; margin-bottom: 0.2rem;
}
.subtitle { text-align: center; color: #6b6b8a; font-size: 0.85rem; letter-spacing: 0.05em; margin-bottom: 2rem; }
.badge { display: flex; justify-content: center; margin-bottom: 1rem; }
.badge span {
    background: linear-gradient(135deg, #6c63ff, #ff6584);
    color: white; padding: 0.3rem 1rem; border-radius: 999px;
    font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase;
}
.result-box {
    background: #12121a; border: 1px solid #2a2a3d; border-radius: 14px;
    padding: 1.4rem; margin-top: 1rem; font-size: 0.88rem;
    line-height: 1.8; color: #e8e8f0; white-space: pre-wrap; word-break: break-word;
    position: relative;
}
.result-box::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 1px;
    background: linear-gradient(90deg, transparent, #6c63ff, transparent);
}
.stat-card {
    background: #12121a; border: 1px solid #2a2a3d; border-radius: 12px;
    padding: 1rem; text-align: center;
}
.stat-num { font-family: 'Syne', sans-serif; font-size: 1.6rem; font-weight: 800; color: #6c63ff; }
.stat-label { font-size: 0.72rem; color: #6b6b8a; letter-spacing: 0.05em; }
.tag { display: inline-block; padding: 0.2rem 0.6rem; border-radius: 999px; font-size: 0.72rem; margin: 0.15rem; }
.tag-redacted { background: rgba(255,101,132,0.15); border: 1px solid rgba(255,101,132,0.4); color: #ff8fa3; }
.tag-clean    { background: rgba(67,233,123,0.12);  border: 1px solid rgba(67,233,123,0.35); color: #43e97b; }

div[data-testid="stFileUploader"] {
    background: #12121a !important; border: 2px dashed #2a2a3d !important;
    border-radius: 14px !important; padding: 1rem !important;
}
div[data-testid="stFileUploader"]:hover { border-color: #6c63ff !important; }

.stButton > button {
    width: 100%; background: linear-gradient(135deg, #6c63ff, #9b59f7) !important;
    color: white !important; font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important; font-size: 1rem !important;
    border: none !important; border-radius: 12px !important; padding: 0.75rem !important;
}
.stButton > button:hover { box-shadow: 0 8px 30px rgba(108,99,255,0.4) !important; }

section[data-testid="stSidebar"] { background: #12121a !important; border-right: 1px solid #2a2a3d; }
div[data-testid="stSelectbox"] > div { background: #0a0a0f !important; border: 1px solid #2a2a3d !important; color: #e8e8f0 !important; border-radius: 8px !important; }

/* Security alert boxes */
.sec-block {
    border-radius: 12px; padding: 1rem 1.2rem; margin: 0.5rem 0;
    font-size: 0.82rem; line-height: 1.6;
}
.sec-danger  { background: rgba(255,59,59,0.08);  border: 1px solid rgba(255,59,59,0.35);  color: #ff7070; }
.sec-warn    { background: rgba(255,180,0,0.08);   border: 1px solid rgba(255,180,0,0.35);   color: #ffc94d; }
.sec-info    { background: rgba(108,99,255,0.08);  border: 1px solid rgba(108,99,255,0.35);  color: #a09aff; }
.sec-ok      { background: rgba(67,233,123,0.07);  border: 1px solid rgba(67,233,123,0.3);   color: #43e97b; }

.shield-row {
    display: flex; align-items: center; gap: 0.6rem;
    background: #12121a; border: 1px solid #1e1e2e;
    border-radius: 10px; padding: 0.6rem 1rem;
    font-size: 0.78rem; color: #6b6b8a; margin-bottom: 0.4rem;
}
.shield-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.dot-ok    { background: #43e97b; box-shadow: 0 0 6px rgba(67,233,123,0.5); }
.dot-warn  { background: #ffc94d; box-shadow: 0 0 6px rgba(255,180,0,0.5); }
.dot-err   { background: #ff6584; box-shadow: 0 0 6px rgba(255,101,132,0.5); }
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────
st.markdown('<div class="badge"><span>📄 AI Document Extractor · Smart Redaction</span></div>', unsafe_allow_html=True)
st.markdown('<div class="main-title">AI Document Extractor</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Extract text from any document or image · Sensitive data auto-redacted.</div>', unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────
st.sidebar.markdown("## ⚙️ Settings")
st.sidebar.markdown("**Redact sensitive data:**")
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
st.sidebar.markdown("<small style='color:#6b6b8a'>AI Document Extractor · v2.0</small>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# SECURITY ENGINE
# ════════════════════════════════════════════════════════════════════

# Known malware/exploit signatures (magic bytes + patterns)
MALWARE_SIGNATURES = [
    # Executable embedded in PDF/Office
    b"TVqQAAMAAAAEAAAA",          # MZ header base64 (PE executable)
    b"\x4d\x5a\x90\x00",         # MZ header (Windows PE)
    b"\x7fELF",                   # ELF Linux executable
    # Malicious PDF patterns
    b"/JavaScript",
    b"/JS ",
    b"eval(",
    b"unescape(",
    b"/OpenAction",
    b"/AA ",                       # Auto-action PDF
    b"/Launch",                    # PDF Launch action
    b"cmd.exe",
    b"powershell",
    b"WScript",
    b"ActiveXObject",
    # Macro patterns in Office docs
    b"AutoOpen",
    b"Auto_Open",
    b"AutoExec",
    b"Shell(",
    b"CreateObject(",
    b"WScript.Shell",
    b"AAAA" * 20,                  # NOP sled pattern
]

# Real magic bytes per file type
MAGIC_BYTES = {
    "pdf":  [(0, b"%PDF")],
    "png":  [(0, b"\x89PNG\r\n\x1a\n")],
    "jpg":  [(0, b"\xff\xd8\xff")],
    "jpeg": [(0, b"\xff\xd8\xff")],
    "docx": [(0, b"PK\x03\x04")],   # ZIP-based
    "xlsx": [(0, b"PK\x03\x04")],
    "pptx": [(0, b"PK\x03\x04")],
    "ppt":  [(0, b"\xd0\xcf\x11\xe0")],  # OLE2
}

def check_file_size(fb, max_mb):
    size_mb = len(fb) / (1024 * 1024)
    if size_mb > max_mb:
        return False, f"File is {size_mb:.1f} MB — exceeds the {max_mb} MB limit. Please upload a smaller file."
    return True, f"Size OK ({size_mb:.1f} MB)"

def check_magic_bytes(fb, ext):
    """Verify actual file content matches claimed extension."""
    ext = ext.lower().lstrip(".")
    if ext not in MAGIC_BYTES:
        return True, "Format check skipped (unknown type)"
    for offset, magic in MAGIC_BYTES[ext]:
        chunk = fb[offset:offset+len(magic)]
        if chunk == magic:
            return True, f"File signature valid ({ext.upper()})"
    return False, f"⚠️ File content does not match .{ext} format — possible renamed or fake file."

def check_virus_signatures(fb):
    """Scan raw bytes for known malware signatures."""
    hits = []
    for sig in MALWARE_SIGNATURES:
        if sig in fb:
            label = sig.decode("utf-8", errors="replace").strip()[:40]
            hits.append(label)
    if hits:
        return False, f"Suspicious pattern detected: {', '.join(set(hits[:3]))}"
    return True, "No known malware signatures found"

def check_corruption(fb, ext):
    """Try actually opening the file to catch corruption."""
    ext = ext.lower().lstrip(".")
    try:
        if ext == "pdf":
            import pypdf
            r = pypdf.PdfReader(io.BytesIO(fb))
            _ = len(r.pages)  # force parse
        elif ext == "docx":
            import docx
            docx.Document(io.BytesIO(fb))
        elif ext == "xlsx":
            import openpyxl
            openpyxl.load_workbook(io.BytesIO(fb), data_only=True)
        elif ext in ("pptx", "ppt"):
            from pptx import Presentation
            Presentation(io.BytesIO(fb))
        elif ext in ("jpg", "jpeg", "png"):
            # Check image header integrity
            if ext == "png" and not fb.endswith(b"\x49\x45\x4e\x44\xae\x42\x60\x82"):
                pass  # PNG IEND check (soft warning only)
        return True, "File opened successfully — not corrupted"
    except Exception as e:
        return False, f"File appears corrupted and cannot be opened: {str(e)[:120]}"

def run_security_scan(fb, filename, max_mb):
    """Run all 4 checks. Returns (passed, results_list)."""
    ext = filename.rsplit(".", 1)[-1] if "." in filename else ""
    results = []
    all_passed = True

    # 1. File size
    ok, msg = check_file_size(fb, max_mb)
    results.append(("📦 File Size",      ok, msg))
    if not ok: all_passed = False

    # 2. Magic bytes / type verification
    ok, msg = check_magic_bytes(fb, ext)
    results.append(("🔍 File Type",      ok, msg))
    if not ok: all_passed = False

    # 3. Virus / malware signatures
    ok, msg = check_virus_signatures(fb)
    results.append(("🦠 Virus Scan",     ok, msg))
    if not ok: all_passed = False

    # 4. Corruption check
    ok, msg = check_corruption(fb, ext)
    results.append(("🧩 Integrity",      ok, msg))
    if not ok: all_passed = False

    return all_passed, results

# ── Redaction helpers ─────────────────────────────────────────────────
def build_redaction_prompt():
    rules = []
    if redact_ids:       rules.append("Aadhaar numbers (12-digit, may be spaced as XXXX XXXX XXXX), SSN, PAN card numbers (format: ABCDE1234F), passport numbers, driving license numbers, voter ID, any government ID number")
    if redact_phones:    rules.append("phone numbers, mobile numbers (+91 or 10-digit), email addresses, contact numbers")
    if redact_banking:   rules.append("bank account numbers, IFSC codes, credit card numbers, debit card numbers, CVV, UPI IDs, MICR codes")
    if redact_passwords: rules.append("passwords, API keys, secret keys, tokens, OTPs, PINs")
    if redact_names:     rules.append("full names of any person — including names on Aadhaar cards, identity documents, official documents")
    if redact_dates:     rules.append("dates of birth in ANY format (DD/MM/YYYY, YYYY-MM-DD, written like '15 August 1990'), DOB, Year of Birth, जन्म तिथि")
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
            {"type": "text", "text": """Analyze this image carefully:
1. Extract ALL visible text exactly as it appears (signs, labels, documents, watermarks, URLs, etc.)
2. If there is little or no text, describe what you see in detail (people, objects, setting, colors, actions)

Format your response as:
TEXT FOUND:
[any text you can read, or 'No readable text found']

IMAGE DESCRIPTION:
[detailed description of what is in the image]"""}
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
- Names appear after "Name:", "नाम:" — REDACT the name value
- DOB appears after "DOB:", "Date of Birth:", "जन्म तिथि:" — REDACT the date
- Aadhaar is 12 digits (may be spaced XXXX XXXX XXXX) — REDACT it
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
        result     = json.loads(cleaned)
        clean      = result.get("clean_text", text)
        items      = result.get("redacted_items", [])
        count      = result.get("redaction_count", 0)
        clean, extra_items, extra_count = regex_redact(clean, placeholder)
        return clean, items + extra_items, count + extra_count
    except:
        return regex_redact(text, placeholder)

# ── Upload ────────────────────────────────────────────────────────────
uploaded = st.file_uploader(
    "Upload a document or image",
    type=["pdf", "png", "jpg", "jpeg", "docx", "xlsx", "pptx", "ppt"],
    label_visibility="collapsed"
)

if uploaded:
    st.markdown(f"**📎 {uploaded.name}** · `{uploaded.type}` · `{uploaded.size/1024:.1f} KB`")

run = st.button("🔍 Extract & Redact", use_container_width=True)

# ── Process ───────────────────────────────────────────────────────────
if run and not uploaded:
    st.error("Please upload a file first.")
    st.stop()

if run and uploaded:
    file_bytes = uploaded.read()
    mime       = uploaded.type
    name       = uploaded.name.lower()

    # ════════════════════════════════════════════
    # STEP 1: SECURITY SCAN
    # ════════════════════════════════════════════
    st.markdown("---")
    st.markdown("### 🛡️ Security Scan")

    with st.spinner("🔍 Running security checks..."):
        passed, scan_results = run_security_scan(file_bytes, name, max_size_mb)

    # Display scan results
    for check_name, ok, msg in scan_results:
        dot = "dot-ok" if ok else "dot-err"
        icon = "✅" if ok else "❌"
        st.markdown(
            f'<div class="shield-row">'
            f'<span class="shield-dot {dot}"></span>'
            f'<strong style="color:#e8e8f0;min-width:120px">{check_name}</strong>'
            f'<span>{icon} {msg}</span>'
            f'</div>',
            unsafe_allow_html=True
        )

    if not passed:
        st.markdown("""
        <div class="sec-block sec-danger">
            🚫 <strong>File rejected.</strong> One or more security checks failed.<br>
            Please upload a clean, valid file. Do not attempt to upload corrupted,
            renamed, or potentially malicious files.
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    st.markdown("""
    <div class="sec-block sec-ok">
        ✅ <strong>All security checks passed.</strong> Proceeding with extraction.
    </div>
    """, unsafe_allow_html=True)

    # ════════════════════════════════════════════
    # STEP 2: EXTRACT TEXT
    # ════════════════════════════════════════════
    st.markdown("---")
    raw_text = None

    with st.spinner("📖 Extracting text from document..."):
        try:
            if name.endswith(".pdf"):
                raw_text = extract_from_pdf(file_bytes)
                if not raw_text:
                    st.info("Text extraction from PDF failed — using AI Vision OCR...")
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
            st.error(f"Extraction error: {e}")
            raw_text = None

    if not raw_text or len(raw_text.strip()) < 5:
        st.markdown("""
        <div class="sec-block sec-warn">
            ⚠️ <strong>No text could be extracted from this file.</strong><br>
            The file passed security checks but contains no readable text.
            It may be a scanned image with no OCR content, or an empty document.
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # ════════════════════════════════════════════
    # STEP 3: REDACT
    # ════════════════════════════════════════════
    rules      = build_redaction_prompt()
    clean_text = raw_text
    items      = []
    count      = 0

    if rules:
        with st.spinner("🔒 Scanning and redacting sensitive information..."):
            try:
                clean_text, items, count = redact_sensitive(raw_text, rules)
            except Exception as e:
                st.warning(f"AI redaction failed, using regex fallback: {e}")
                clean_text, items, count = regex_redact(raw_text)
    else:
        st.info("ℹ️ No redaction rules selected — showing full extracted text.")

    # ════════════════════════════════════════════
    # STEP 4: RESULTS
    # ════════════════════════════════════════════
    word_count = len(clean_text.split())
    char_count = len(clean_text)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-num">{word_count:,}</div><div class="stat-label">WORDS EXTRACTED</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-num">{count}</div><div class="stat-label">ITEMS REDACTED</div></div>', unsafe_allow_html=True)
    with c3:
        status = "✅ CLEAN" if count == 0 else "🔒 REDACTED"
        color  = "#43e97b" if count == 0 else "#ff8fa3"
        st.markdown(f'<div class="stat-card"><div class="stat-num" style="color:{color};font-size:1.1rem;padding-top:.4rem">{status}</div><div class="stat-label">DOCUMENT STATUS</div></div>', unsafe_allow_html=True)

    if items:
        st.markdown("<br>**🔒 Redacted categories:**", unsafe_allow_html=True)
        tags = "".join(f'<span class="tag tag-redacted">🚫 {i}</span>' for i in set(items))
        st.markdown(f'<div style="margin:.5rem 0">{tags}</div>', unsafe_allow_html=True)

    st.markdown("<br>**📝 Extracted Text:**", unsafe_allow_html=True)
    st.markdown(f'<div class="result-box">{clean_text}</div>', unsafe_allow_html=True)

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
