import streamlit as st
from groq import Groq
import json
import re
import base64
import io

# ── Page Config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="REDACT · Document Intelligence",
    page_icon="▣",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ── Load API Key ──────────────────────────────────────────────────────
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client  = Groq(api_key=API_KEY)
except Exception:
    st.error("⚠️ API key not configured.")
    st.info("Add to Streamlit Secrets:\n\n`GROQ_API_KEY = \"gsk_your_key_here\"`")
    st.stop()

# ─────────────────────────────────────────────────────────────────────
# CSS — Cream & Ink Brutalist Editorial Theme
# ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Libre+Baskerville:ital,wght@0,400;0,700;1,400&family=Space+Mono:wght@400;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --cream:      #f5f0e8;
  --cream2:     #ede8dc;
  --ink:        #1a1710;
  --ink2:       #2e2b22;
  --ink3:       #4a4535;
  --red:        #c0392b;
  --red-pale:   rgba(192,57,43,0.08);
  --red-border: rgba(192,57,43,0.25);
  --green:      #1a6b3c;
  --green-pale: rgba(26,107,60,0.08);
  --amber:      #b5620a;
  --border:     #c8c0a8;
  --border2:    #a89e88;
  --shadow:     4px 4px 0px #1a1710;
  --radius:     0px;
}

html, body, [class*="css"] {
  font-family: 'Space Grotesk', sans-serif !important;
  background: var(--cream) !important;
  color: var(--ink) !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"],
[data-testid="collapsedControl"] { display: none !important; }

/* ── Layout ── */
.main .block-container {
  max-width: 780px !important;
  padding: 0 2rem 5rem !important;
  margin: 0 auto !important;
}

/* ── Background ── */
.stApp {
  background: var(--cream) !important;
  background-image:
    repeating-linear-gradient(
      0deg,
      transparent,
      transparent 39px,
      rgba(26,23,16,0.06) 39px,
      rgba(26,23,16,0.06) 40px
    ) !important;
}

/* ── Top rule ── */
[data-testid="stAppViewContainer"] > section > div:first-child::before {
  content: '';
  display: block; width: 100%; height: 4px;
  background: var(--ink);
  position: fixed; top: 0; left: 0; z-index: 999;
}

/* ── Hero ── */
.hero {
  padding: 3rem 0 2rem;
  border-bottom: 2px solid var(--ink);
  margin-bottom: 2rem;
  position: relative;
}
.hero-tag {
  font-family: 'Space Mono', monospace;
  font-size: 0.6rem; letter-spacing: 0.25em; text-transform: uppercase;
  color: var(--ink3); margin-bottom: 0.8rem;
  display: flex; align-items: center; gap: 0.6rem;
}
.hero-tag::before {
  content: '▣'; color: var(--red); font-size: 0.7rem;
}
.hero-title {
  font-family: 'Libre Baskerville', serif;
  font-size: clamp(3rem, 9vw, 6rem);
  font-weight: 700; line-height: 0.95;
  color: var(--ink); letter-spacing: -0.02em;
  margin-bottom: 0.6rem;
}
.hero-title span {
  font-style: italic; color: var(--red);
}
.hero-rule {
  width: 60px; height: 3px; background: var(--red); margin: 1rem 0;
}
.hero-sub {
  font-family: 'Space Grotesk', sans-serif;
  font-size: 0.95rem; font-weight: 400; color: var(--ink3);
  max-width: 480px; line-height: 1.7;
}
.hero-version {
  position: absolute; top: 3rem; right: 0;
  font-family: 'Space Mono', monospace; font-size: 0.6rem;
  color: var(--border2); letter-spacing: 0.1em;
  text-transform: uppercase;
  border: 1px solid var(--border); padding: 0.3rem 0.6rem;
}

/* ── Stat strip ── */
.stat-strip {
  display: grid; grid-template-columns: 1fr 1fr 1fr;
  border: 2px solid var(--ink); margin: 1.5rem 0;
  background: var(--cream);
}
.stat-item {
  padding: 1.2rem 1rem; text-align: center;
  border-right: 2px solid var(--ink);
  position: relative;
}
.stat-item:last-child { border-right: none; }
.stat-val {
  font-family: 'Libre Baskerville', serif;
  font-size: 2.2rem; font-weight: 700; line-height: 1;
  color: var(--ink);
}
.stat-val.red   { color: var(--red); }
.stat-val.green { color: var(--green); }
.stat-val.amber { color: var(--amber); }
.stat-lbl {
  font-family: 'Space Mono', monospace;
  font-size: 0.55rem; color: var(--ink3);
  letter-spacing: 0.18em; text-transform: uppercase; margin-top: 0.3rem;
}

/* ── Upload zone ── */
div[data-testid="stFileUploader"] {
  background: var(--cream2) !important;
  border: 2px dashed var(--border2) !important;
  border-radius: 0 !important;
  padding: 2rem !important;
  transition: border-color 0.2s, background 0.2s !important;
}
div[data-testid="stFileUploader"]:hover {
  border-color: var(--ink) !important;
  background: var(--cream) !important;
}
div[data-testid="stFileUploader"] label {
  color: var(--ink3) !important;
  font-family: 'Space Mono', monospace !important;
  font-size: 0.78rem !important;
}

/* ── File info pill ── */
.file-info {
  background: var(--ink); color: var(--cream);
  padding: 0.6rem 1rem; margin: 0.6rem 0;
  font-family: 'Space Mono', monospace; font-size: 0.72rem;
  display: flex; align-items: center; gap: 0.75rem;
  border: none;
}
.file-info .fi-name { font-weight: 700; color: #fff; }
.file-info .fi-meta { color: #aaa; }

/* ── Primary button ── */
.stButton > button {
  background: var(--ink) !important;
  color: var(--cream) !important;
  font-family: 'Libre Baskerville', serif !important;
  font-size: 1.05rem !important; font-weight: 700 !important;
  font-style: italic !important;
  border: 2px solid var(--ink) !important;
  border-radius: 0 !important; padding: 0.85rem 2rem !important;
  width: 100% !important; letter-spacing: 0.03em !important;
  box-shadow: var(--shadow) !important;
  transition: all 0.15s ease !important;
}
.stButton > button:hover {
  background: var(--red) !important;
  border-color: var(--red) !important;
  box-shadow: 4px 4px 0px var(--red-border) !important;
  transform: translate(-1px, -1px) !important;
}
.stButton > button:active {
  transform: translate(2px, 2px) !important;
  box-shadow: 2px 2px 0px var(--ink) !important;
}

/* ── Download button ── */
.stDownloadButton > button {
  background: var(--cream) !important;
  color: var(--ink) !important;
  font-family: 'Space Mono', monospace !important;
  font-size: 0.72rem !important;
  border: 2px solid var(--ink) !important;
  border-radius: 0 !important; padding: 0.65rem 1rem !important;
  box-shadow: 3px 3px 0px var(--border2) !important;
  transition: all 0.15s ease !important;
}
.stDownloadButton > button:hover {
  background: var(--ink) !important;
  color: var(--cream) !important;
  transform: translate(-1px, -1px) !important;
  box-shadow: 4px 4px 0px var(--ink3) !important;
}

/* ── Checkboxes in sidebar ── */
.stCheckbox label {
  font-family: 'Space Mono', monospace !important;
  font-size: 0.75rem !important; color: var(--ink) !important;
}
.stCheckbox [data-testid="stCheckbox"] input:checked + div {
  background: var(--ink) !important;
  border-color: var(--ink) !important;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
  background: var(--ink) !important;
  border-right: 3px solid var(--ink) !important;
}
section[data-testid="stSidebar"] * { color: var(--cream) !important; }
section[data-testid="stSidebar"] .stCheckbox label { color: var(--cream) !important; font-size: 0.72rem !important; }
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 { color: #fff !important; }
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.15) !important; }
.sb-section-title {
  font-family: 'Space Mono', monospace !important;
  font-size: 0.58rem !important; letter-spacing: 0.2em !important;
  text-transform: uppercase !important; color: rgba(245,240,232,0.45) !important;
  margin: 1rem 0 0.4rem !important; display: block !important;
}
.sidebar-brand {
  font-family: 'Libre Baskerville', serif;
  font-size: 1.3rem; font-weight: 700; font-style: italic;
  color: #fff; letter-spacing: -0.01em;
  border-bottom: 1px solid rgba(255,255,255,0.15);
  padding-bottom: 0.75rem; margin-bottom: 1rem;
}
.sidebar-brand span { color: var(--red); }

/* ── Result box ── */
.result-wrap {
  margin-top: 1.5rem;
}
.result-label {
  font-family: 'Space Mono', monospace; font-size: 0.6rem;
  letter-spacing: 0.2em; text-transform: uppercase; color: var(--ink3);
  margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;
}
.result-label::after { content: ''; flex: 1; height: 1px; background: var(--border); }
.result-box {
  background: var(--cream2);
  border: 2px solid var(--ink);
  padding: 1.5rem;
  font-family: 'Space Mono', monospace; font-size: 0.78rem;
  line-height: 1.9; color: var(--ink2);
  white-space: pre-wrap; word-break: break-word;
  max-height: 480px; overflow-y: auto;
  box-shadow: var(--shadow);
  position: relative;
}
.result-box::-webkit-scrollbar { width: 6px; }
.result-box::-webkit-scrollbar-track { background: var(--cream); }
.result-box::-webkit-scrollbar-thumb { background: var(--border2); }

/* ── Redaction tags ── */
.tags-row { display: flex; flex-wrap: wrap; gap: 0.35rem; margin: 0.75rem 0 1rem; }
.tag-item {
  font-family: 'Space Mono', monospace; font-size: 0.65rem;
  padding: 0.22rem 0.65rem;
  border: 1.5px solid;
}
.tag-bad  { border-color: var(--red);   color: var(--red);   background: var(--red-pale); }
.tag-good { border-color: var(--green); color: var(--green); background: var(--green-pale); }

/* ── Section divider ── */
.section-rule {
  border: none; border-top: 2px solid var(--ink);
  margin: 2rem 0;
}
.section-heading {
  font-family: 'Libre Baskerville', serif;
  font-size: 1.2rem; font-weight: 700; font-style: italic;
  color: var(--ink); margin-bottom: 1rem;
  display: flex; align-items: center; gap: 0.6rem;
}
.section-heading::before { content: '§'; color: var(--red); font-style: normal; }

/* ── Warn / info banners ── */
.banner {
  font-family: 'Space Mono', monospace; font-size: 0.72rem;
  padding: 0.7rem 1rem; margin: 0.5rem 0;
  border: 1.5px solid; display: flex; align-items: flex-start; gap: 0.6rem;
}
.banner.warn  { border-color: var(--amber); color: var(--amber); background: rgba(181,98,10,0.06); }
.banner.error { border-color: var(--red);   color: var(--red);   background: var(--red-pale); }
.banner.info  { border-color: var(--ink3);  color: var(--ink3);  background: rgba(26,23,16,0.04); }

/* ── Spinner ── */
.stSpinner > div { border-top-color: var(--ink) !important; }

/* ── Selectbox ── */
div[data-testid="stSelectbox"] > div > div {
  background: var(--cream2) !important;
  border: 2px solid var(--border) !important;
  border-radius: 0 !important; color: var(--ink) !important;
  font-family: 'Space Mono', monospace !important; font-size: 0.76rem !important;
}

/* ── Code ── */
.stCodeBlock pre {
  background: var(--cream2) !important;
  border: 2px solid var(--border) !important;
  border-radius: 0 !important;
  font-family: 'Space Mono', monospace !important;
}

/* ── Progress bar ── */
.stProgress > div > div > div { background: var(--ink) !important; }
.stProgress > div > div { background: var(--border) !important; }

/* ── Popover ── */
[data-baseweb="popover"] {
  background: var(--cream) !important;
  border: 2px solid var(--ink) !important;
  border-radius: 0 !important;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">RE<span>▣</span>DACT</div>', unsafe_allow_html=True)
    st.markdown('<span class="sb-section-title">Redaction Rules</span>', unsafe_allow_html=True)
    redact_ids       = st.checkbox("▣  ID / Aadhaar / SSN / PAN",     value=True)
    redact_phones    = st.checkbox("▣  Phone numbers & emails",         value=True)
    redact_banking   = st.checkbox("▣  Bank / card numbers / IFSC",     value=True)
    redact_passwords = st.checkbox("▣  Passwords / keys / OTPs",        value=True)
    redact_names     = st.checkbox("▣  Personal names",                  value=False)
    redact_dates     = st.checkbox("▣  Dates of birth",                  value=False)
    st.markdown("---")
    st.markdown('<span class="sb-section-title">Output</span>', unsafe_allow_html=True)
    show_redacted = st.checkbox("▣  Show [REDACTED] labels",            value=True)
    st.markdown("---")
    st.markdown("""<div style="font-family:'Space Mono',monospace;font-size:0.58rem;
    color:rgba(245,240,232,0.35);line-height:1.8">
    REDACT · v1.1<br>Powered by Groq AI<br>LLaMA 3.1 · Vision AI
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-tag">Document Intelligence · Privacy Engine</div>
  <div class="hero-title">RE<span>DACT</span></div>
  <div class="hero-rule"></div>
  <div class="hero-sub">
    Extract text from any document or image. Sensitive data is automatically identified and redacted using AI — protecting privacy before you share.
  </div>
  <div class="hero-version">v1.1 · Groq AI</div>
</div>
""", unsafe_allow_html=True)

# ── Supported formats strip ───────────────────────────────────────────
st.markdown("""<div style="display:flex;gap:0.4rem;margin-bottom:2rem;flex-wrap:wrap">
""" + "".join(
    f'<span style="font-family:Space Mono,monospace;font-size:0.6rem;letter-spacing:0.1em;'
    f'padding:0.2rem 0.6rem;border:1.5px solid #c8c0a8;color:#4a4535">{f}</span>'
    for f in ["PDF", "PNG", "JPG", "JPEG", "DOCX", "XLSX", "PPTX", "PPT"]
) + "</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────
# LOGIC (unchanged from original)
# ─────────────────────────────────────────────────────────────────────
def build_redaction_prompt():
    rules = []
    if redact_ids:       rules.append("Aadhaar numbers (12-digit, may be spaced as XXXX XXXX XXXX), SSN, PAN card numbers (format: ABCDE1234F), passport numbers, driving license numbers, voter ID, any government ID number")
    if redact_phones:    rules.append("phone numbers, mobile numbers (+91 or 10-digit), email addresses, contact numbers")
    if redact_banking:   rules.append("bank account numbers, IFSC codes, credit card numbers, debit card numbers, CVV, UPI IDs, MICR codes")
    if redact_passwords: rules.append("passwords, API keys, secret keys, tokens, OTPs, PINs")
    if redact_names:     rules.append("full names of any person — INCLUDING names on Aadhaar cards, identity documents, official documents")
    if redact_dates:     rules.append("dates of birth in ANY format (DD/MM/YYYY, YYYY-MM-DD, written like '15 August 1990'), DOB, Year of Birth")
    return rules

def extract_from_pdf(file_bytes):
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        return "".join(page.extract_text() or "" for page in reader.pages).strip()
    except ImportError:
        return None

def extract_from_docx(file_bytes):
    try:
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip()).strip()
    except ImportError:
        return None

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
        return "\n".join(rows).strip()
    except ImportError:
        return None

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
        return "\n".join(lines).strip()
    except ImportError:
        return None

def extract_from_image(file_bytes, mime_type):
    b64 = base64.b64encode(file_bytes).decode("utf-8")
    response = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role":"user","content":[
            {"type":"image_url","image_url":{"url":f"data:{mime_type};base64,{b64}"}},
            {"type":"text","text":"Extract ALL text from this image exactly as it appears. Return only the raw extracted text, preserve formatting and line breaks."}
        ]}],
        max_tokens=2000
    )
    return response.choices[0].message.content.strip()

def regex_redact(text, placeholder="[REDACTED]"):
    count = 0; removed = []
    if redact_ids:
        new = re.sub(r'\b\d{4}\s?\d{4}\s?\d{4}\b', placeholder, text)
        if new != text: count += 1; removed.append("Aadhaar number"); text = new
        new = re.sub(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', placeholder, text)
        if new != text: count += 1; removed.append("PAN number"); text = new
    if redact_phones:
        new = re.sub(r'\b(\+91[\s-]?)?[6-9]\d{9}\b', placeholder, text)
        if new != text: count += 1; removed.append("phone number"); text = new
        new = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', placeholder, text)
        if new != text: count += 1; removed.append("email address"); text = new
    if redact_banking:
        new = re.sub(r'\b(?:\d[ -]*?){13,16}\b', placeholder, text)
        if new != text: count += 1; removed.append("card number"); text = new
        new = re.sub(r'\b[A-Z]{4}0[A-Z0-9]{6}\b', placeholder, text)
        if new != text: count += 1; removed.append("IFSC code"); text = new
    if redact_dates:
        new = re.sub(r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}\b', placeholder, text)
        if new != text: count += 1; removed.append("date of birth"); text = new
    if redact_names:
        new = re.sub(r'(Name|नाम)\s*[:\-]\s*[A-Za-z\s]{3,40}',
                     lambda m: m.group(0).split(':')[0]+': '+placeholder, text)
        if new != text: count += 1; removed.append("name field"); text = new
    return text, removed, count

def redact_sensitive(text, rules):
    if not rules: return text, [], 0
    placeholder = "[REDACTED]" if show_redacted else "████"
    prompt = f"""You are a strict data privacy and redaction engine.

SENSITIVE CATEGORIES:
{chr(10).join(f'- {r}' for r in rules)}

RULES:
- Replace ONLY the sensitive value with "{placeholder}", keep surrounding text
- MUST redact every single instance — missing one is a privacy violation
- When in doubt — REDACT it

Return JSON only:
{{"clean_text":"...","redacted_items":["name: ...","DOB: ..."],"redaction_count":0}}

TEXT:
{text[:6000]}"""
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role":"system","content":"Strict data privacy engine. Return only valid JSON. No extra text."},
            {"role":"user","content":prompt}
        ],
        temperature=0.0, max_tokens=4000
    )
    raw     = response.choices[0].message.content.strip()
    cleaned = re.sub(r'```json|```','',raw).strip()
    try:
        result     = json.loads(cleaned)
        clean      = result.get("clean_text", text)
        items      = result.get("redacted_items", [])
        count      = result.get("redaction_count", 0)
        clean, ex, ec = regex_redact(clean, placeholder)
        return clean, items + ex, count + ec
    except:
        return regex_redact(text, placeholder)


# ─────────────────────────────────────────────────────────────────────
# UPLOAD ZONE
# ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-heading">Upload Document</div>', unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Drop your file here",
    type=["pdf","png","jpg","jpeg","docx","xlsx","pptx","ppt"],
    label_visibility="collapsed"
)

if uploaded:
    size_kb = uploaded.size / 1024
    size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.2f} MB"
    st.markdown(f"""<div class="file-info">
      <span>▣</span>
      <span class="fi-name">{uploaded.name}</span>
      <span class="fi-meta">{uploaded.type}</span>
      <span class="fi-meta">{size_str}</span>
    </div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
run = st.button("▣  Extract & Redact Document", use_container_width=True)


# ─────────────────────────────────────────────────────────────────────
# PROCESS
# ─────────────────────────────────────────────────────────────────────
if run and not uploaded:
    st.markdown('<div class="banner error">▣ No file uploaded. Please select a document first.</div>', unsafe_allow_html=True)

if run and uploaded:
    file_bytes = uploaded.read()
    mime       = uploaded.type
    name       = uploaded.name.lower()
    raw_text   = None

    # Step 1 — Extract
    with st.spinner("Extracting text from document..."):
        try:
            if name.endswith(".pdf"):
                raw_text = extract_from_pdf(file_bytes)
                if not raw_text:
                    st.markdown('<div class="banner warn">▣ PDF text layer empty — using AI vision.</div>', unsafe_allow_html=True)
                    raw_text = extract_from_image(file_bytes, "application/pdf")
            elif name.endswith((".png",".jpg",".jpeg")):
                raw_text = extract_from_image(file_bytes, mime)
            elif name.endswith(".docx"):
                raw_text = extract_from_docx(file_bytes)
            elif name.endswith(".xlsx"):
                raw_text = extract_from_xlsx(file_bytes)
            elif name.endswith((".pptx",".ppt")):
                raw_text = extract_from_pptx(file_bytes)
                if not raw_text:
                    st.markdown('<div class="banner warn">▣ PPT text empty — using AI vision.</div>', unsafe_allow_html=True)
                    raw_text = extract_from_image(file_bytes, mime)
        except Exception as e:
            st.markdown(f'<div class="banner error">▣ Extraction error: {e}</div>', unsafe_allow_html=True)
            raw_text = None

    if not raw_text or len(raw_text.strip()) < 5:
        st.markdown('<div class="banner error">▣ Could not extract any text. Try a different file or format.</div>', unsafe_allow_html=True)
        st.stop()

    # Step 2 — Redact
    rules      = build_redaction_prompt()
    clean_text = raw_text
    items      = []
    count      = 0

    if rules:
        with st.spinner("Scanning for sensitive data..."):
            try:
                clean_text, items, count = redact_sensitive(raw_text, rules)
            except Exception as e:
                st.markdown(f'<div class="banner warn">▣ AI redaction failed, regex fallback used: {e}</div>', unsafe_allow_html=True)
                clean_text, items, count = regex_redact(raw_text)
    else:
        st.markdown('<div class="banner info">▣ No redaction rules active — displaying full text.</div>', unsafe_allow_html=True)

    # ── Results ───────────────────────────────────────────────────────
    st.markdown('<hr class="section-rule">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Results</div>', unsafe_allow_html=True)

    # Stat strip
    word_count = len(clean_text.split())
    status_val = "CLEAN" if count == 0 else f"{count}"
    status_cls = "green" if count == 0 else "red"
    st.markdown(f"""<div class="stat-strip">
      <div class="stat-item">
        <div class="stat-val">{word_count:,}</div>
        <div class="stat-lbl">Words Extracted</div>
      </div>
      <div class="stat-item">
        <div class="stat-val {status_cls}">{status_val}</div>
        <div class="stat-lbl">Items Redacted</div>
      </div>
      <div class="stat-item">
        <div class="stat-val" style="font-size:1rem;padding-top:0.6rem;color:var(--{'green' if count==0 else 'red'})">
          {'✓ SAFE' if count == 0 else '▣ SCRUBBED'}
        </div>
        <div class="stat-lbl">Document Status</div>
      </div>
    </div>""", unsafe_allow_html=True)

    # Redacted category tags
    if items:
        st.markdown('<div class="section-heading" style="font-size:1rem;margin-top:0.5rem">Redacted Categories</div>', unsafe_allow_html=True)
        tags = "".join(f'<span class="tag-item tag-bad">▣ {i}</span>' for i in sorted(set(items)))
        st.markdown(f'<div class="tags-row">{tags}</div>', unsafe_allow_html=True)

    # Extracted text output
    st.markdown('<div class="result-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="result-label">Extracted & Redacted Text</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="result-box">{clean_text}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Downloads
    st.markdown('<hr class="section-rule">', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Export</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns(2)
    col_a.download_button(
        "▣  Download as .txt",
        clean_text,
        f"{uploaded.name}_redacted.txt",
        "text/plain",
        use_container_width=True
    )
    col_b.download_button(
        "▣  Download as .json",
        json.dumps({
            "filename": uploaded.name,
            "extracted_text": clean_text,
            "redacted_count": count,
            "redacted_categories": sorted(set(items))
        }, indent=2),
        f"{uploaded.name}_redacted.json",
        "application/json",
        use_container_width=True
    )
