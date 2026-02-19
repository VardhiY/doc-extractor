import streamlit as st
from groq import Groq
import json
import re
import base64
import io

# ── Page Config ───────────────────────────────────────────────────────
st.set_page_config(
    page_title="DocuVault AI · Document Intelligence",
    page_icon="🔐",
    layout="wide"
)

# ── Load API Key ──────────────────────────────────────────────────────
try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client  = Groq(api_key=API_KEY)
except Exception:
    st.error("⚠️ API key not configured. Add GROQ_API_KEY to Streamlit Secrets.")
    st.stop()

# ── CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }

#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"], [data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display: none !important; }
[data-testid="collapsedControl"] { display: flex !important; }

.stApp {
    background: #020408;
    background-image:
        radial-gradient(ellipse 80% 50% at 50% -20%, rgba(14,165,233,0.08) 0%, transparent 60%),
        radial-gradient(ellipse 60% 40% at 80% 80%, rgba(99,102,241,0.06) 0%, transparent 50%);
    color: #e2e8f0;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: #080f1a !important;
    border-right: 1px solid rgba(14,165,233,0.15) !important;
}
.sidebar-logo {
    background: linear-gradient(135deg, #0369a1, #4338ca);
    padding: 1.5rem 1.2rem; margin-bottom: 0;
}
.sidebar-logo-text { font-family:'Playfair Display',serif; font-size:1.3rem; font-weight:900; color:white; }
.sidebar-logo-sub { font-family:'IBM Plex Mono',monospace; font-size:0.6rem; color:rgba(255,255,255,0.6); letter-spacing:0.15em; text-transform:uppercase; margin-top:0.25rem; }
.sidebar-section { padding:1.2rem; border-bottom:1px solid rgba(255,255,255,0.05); }
.sidebar-section-title { font-family:'IBM Plex Mono',monospace; font-size:0.6rem; letter-spacing:0.15em; text-transform:uppercase; color:#475569; margin-bottom:0.8rem; }
.sidebar-footer { padding:1rem 1.2rem; font-family:'IBM Plex Mono',monospace; font-size:0.62rem; color:#1e293b; line-height:1.6; }

section[data-testid="stSidebar"] .stCheckbox label {
    font-family:'IBM Plex Sans',sans-serif !important;
    font-size:0.82rem !important; color:#64748b !important;
}
section[data-testid="stSidebar"] .stCheckbox label:hover { color:#e2e8f0 !important; }

/* Hero */
.hero { text-align:center; padding:3rem 1rem 1.5rem; }
.hero-eyebrow {
    display:inline-flex; align-items:center; gap:0.5rem;
    font-family:'IBM Plex Mono',monospace; font-size:0.65rem;
    letter-spacing:0.18em; text-transform:uppercase; color:#0ea5e9;
    border:1px solid rgba(14,165,233,0.3); padding:0.35rem 1rem;
    border-radius:999px; background:rgba(14,165,233,0.05); margin-bottom:1.2rem;
}
.hero-eyebrow-dot {
    width:6px; height:6px; border-radius:50%; background:#0ea5e9;
    animation: blink 2s infinite;
}
@keyframes blink { 0%,100%{opacity:1;} 50%{opacity:0.3;} }
.hero-title {
    font-family:'Playfair Display',serif;
    font-size:clamp(2.5rem,5vw,4rem); font-weight:900;
    line-height:1.05; letter-spacing:-0.03em; color:#f1f5f9;
}
.hero-title-accent {
    background:linear-gradient(135deg,#0ea5e9,#6366f1,#8b5cf6);
    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
}
.hero-sub {
    font-size:0.95rem; font-weight:300; color:#475569;
    margin-top:0.8rem; line-height:1.7;
}
.format-pills { display:flex; flex-wrap:wrap; justify-content:center; gap:0.4rem; margin:1.2rem 0 0; }
.pill { font-family:'IBM Plex Mono',monospace; font-size:0.63rem; padding:0.28rem 0.7rem; border-radius:4px; }
.p-pdf   { background:rgba(239,68,68,0.1);  border:1px solid rgba(239,68,68,0.25);  color:#f87171; }
.p-img   { background:rgba(14,165,233,0.1); border:1px solid rgba(14,165,233,0.25); color:#38bdf8; }
.p-word  { background:rgba(99,102,241,0.1); border:1px solid rgba(99,102,241,0.25); color:#818cf8; }
.p-xl    { background:rgba(34,197,94,0.1);  border:1px solid rgba(34,197,94,0.25);  color:#4ade80; }
.p-ppt   { background:rgba(251,146,60,0.1); border:1px solid rgba(251,146,60,0.25); color:#fb923c; }

/* Upload */
.upload-wrap {
    border:1.5px dashed rgba(14,165,233,0.2); border-radius:16px;
    background:rgba(14,165,233,0.02); padding:0.5rem; margin:1.5rem 0 0.8rem;
    transition:border-color 0.3s;
}
.upload-wrap:hover { border-color:rgba(14,165,233,0.45); }
div[data-testid="stFileUploader"] { background:transparent !important; border:none !important; }
div[data-testid="stFileUploadDropzone"] { background:transparent !important; border:none !important; padding:1.8rem !important; }
div[data-testid="stFileUploadDropzone"] p { color:#475569 !important; font-family:'IBM Plex Sans',sans-serif !important; }
div[data-testid="stFileUploadDropzone"] small { color:#334155 !important; }

.file-info {
    display:flex; align-items:center; gap:0.7rem;
    background:rgba(14,165,233,0.06); border:1px solid rgba(14,165,233,0.18);
    border-radius:8px; padding:0.7rem 1rem; margin-bottom:0.8rem;
}
.file-info-name { font-family:'IBM Plex Mono',monospace; font-size:0.78rem; color:#38bdf8; flex:1; }
.file-info-meta { font-family:'IBM Plex Mono',monospace; font-size:0.65rem; color:#334155; }

/* Button */
.stButton > button {
    width:100% !important;
    background:linear-gradient(135deg,#0284c7,#4f46e5) !important;
    color:white !important; font-family:'IBM Plex Sans',sans-serif !important;
    font-weight:600 !important; font-size:0.9rem !important;
    border:none !important; border-radius:10px !important;
    padding:0.85rem !important; letter-spacing:0.03em !important;
}
.stButton > button:hover {
    box-shadow:0 0 50px rgba(14,165,233,0.25) !important;
    transform:translateY(-1px) !important;
}

/* Trust badges */
.trust-row { display:flex; flex-wrap:wrap; justify-content:center; gap:1.5rem; margin-top:1.5rem; }
.trust-badge { display:flex; align-items:center; gap:0.4rem; font-family:'IBM Plex Mono',monospace; font-size:0.6rem; letter-spacing:0.06em; color:#334155; }
.trust-dot { width:4px; height:4px; border-radius:50%; background:#10b981; }

/* Divider */
.divider { height:1px; background:linear-gradient(90deg,transparent,rgba(14,165,233,0.15),rgba(99,102,241,0.15),transparent); margin:2rem 0; }

/* Stats */
.stats-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:1rem; margin:1.5rem 0; }
.stat-box {
    background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06);
    border-radius:12px; padding:1.2rem; text-align:center; position:relative; overflow:hidden;
}
.stat-box::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; }
.sb-words::before   { background:linear-gradient(90deg,#0ea5e9,#38bdf8); }
.sb-redact::before  { background:linear-gradient(90deg,#f43f5e,#fb7185); }
.sb-status::before  { background:linear-gradient(90deg,#10b981,#34d399); }
.sb-danger::before  { background:linear-gradient(90deg,#f43f5e,#fb7185); }
.stat-num { font-family:'Playfair Display',serif; font-size:1.9rem; font-weight:700; color:#f1f5f9; }
.stat-lbl { font-family:'IBM Plex Mono',monospace; font-size:0.58rem; letter-spacing:0.15em; text-transform:uppercase; color:#334155; margin-top:0.3rem; }

/* Redact tags */
.rtag { font-family:'IBM Plex Mono',monospace; font-size:0.63rem; padding:0.22rem 0.6rem; border-radius:4px; background:rgba(244,63,94,0.08); border:1px solid rgba(244,63,94,0.2); color:#fb7185; margin:0.15rem; display:inline-block; }
.rtag-row { margin:0.8rem 0; }

/* Result panel */
.result-panel {
    background:rgba(255,255,255,0.02); border:1px solid rgba(255,255,255,0.06);
    border-radius:14px; overflow:hidden; margin:1rem 0;
}
.rp-header {
    display:flex; justify-content:space-between; align-items:center;
    padding:0.9rem 1.4rem; background:rgba(255,255,255,0.02);
    border-bottom:1px solid rgba(255,255,255,0.05);
}
.rp-title { font-family:'IBM Plex Mono',monospace; font-size:0.62rem; letter-spacing:0.15em; text-transform:uppercase; color:#475569; }
.rp-meta  { font-family:'IBM Plex Mono',monospace; font-size:0.6rem; color:#1e293b; }
.rp-body {
    padding:1.4rem; font-family:'IBM Plex Mono',monospace;
    font-size:0.8rem; line-height:1.9; color:#94a3b8;
    white-space:pre-wrap; word-break:break-word;
    max-height:420px; overflow-y:auto;
}
.rp-body::-webkit-scrollbar { width:3px; }
.rp-body::-webkit-scrollbar-thumb { background:rgba(14,165,233,0.25); border-radius:2px; }

/* Download buttons */
.stDownloadButton > button {
    background:rgba(255,255,255,0.03) !important;
    border:1px solid rgba(255,255,255,0.08) !important;
    color:#64748b !important; font-family:'IBM Plex Sans',sans-serif !important;
    font-size:0.82rem !important; font-weight:500 !important;
    border-radius:8px !important; padding:0.65rem 1rem !important; width:100% !important;
}
.stDownloadButton > button:hover {
    background:rgba(14,165,233,0.06) !important;
    border-color:rgba(14,165,233,0.25) !important;
    color:#38bdf8 !important;
}

div[data-testid="stSelectbox"] > div {
    background:rgba(255,255,255,0.03) !important;
    border:1px solid rgba(255,255,255,0.08) !important;
    color:#e2e8f0 !important; border-radius:8px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div class="sidebar-logo">
    <div class="sidebar-logo-text">DocuVault AI</div>
    <div class="sidebar-logo-sub">Document Intelligence</div>
</div>
<div class="sidebar-section">
    <div class="sidebar-section-title">🛡️ Privacy Shield</div>
""", unsafe_allow_html=True)

redact_ids       = st.sidebar.checkbox("ID · Aadhaar · SSN · PAN",  value=True)
redact_phones    = st.sidebar.checkbox("Phone numbers & emails",      value=True)
redact_banking   = st.sidebar.checkbox("Bank · Cards · UPI",         value=True)
redact_passwords = st.sidebar.checkbox("Passwords · Keys · OTPs",    value=True)
redact_names     = st.sidebar.checkbox("Personal names",              value=False)
redact_dates     = st.sidebar.checkbox("Dates of birth",              value=False)
st.sidebar.markdown('</div><div class="sidebar-section"><div class="sidebar-section-title">⚙️ Output Format</div>', unsafe_allow_html=True)
show_redacted    = st.sidebar.checkbox("Show [REDACTED] tags",        value=True)
st.sidebar.markdown('</div>', unsafe_allow_html=True)
st.sidebar.markdown("""
<div class="sidebar-footer">
    DocuVault AI · v2.0<br>
    Powered by Groq · LLaMA 4 Vision<br>
    © 2025 All rights reserved
</div>
""", unsafe_allow_html=True)

# ── Hero & Upload ─────────────────────────────────────────────────────
_, col, _ = st.columns([0.5, 9, 0.5])
with col:
    st.markdown("""
    <div class="hero">
        <div style="display:flex;justify-content:center;margin-bottom:1.2rem">
            <span class="hero-eyebrow"><span class="hero-eyebrow-dot"></span>Enterprise · AI-Powered · Privacy First</span>
        </div>
        <div class="hero-title">Extract. Protect.<br><span class="hero-title-accent">Deliver.</span></div>
        <div class="hero-sub">Intelligent document extraction with automatic sensitive data redaction.<br>Built for enterprises that take privacy seriously.</div>
        <div class="format-pills">
            <span class="pill p-pdf">PDF</span>
            <span class="pill p-img">JPG · PNG</span>
            <span class="pill p-word">DOCX</span>
            <span class="pill p-xl">XLSX</span>
            <span class="pill p-ppt">PPTX</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="upload-wrap">', unsafe_allow_html=True)
    uploaded = st.file_uploader(
        "drop",
        type=["pdf","png","jpg","jpeg","docx","xlsx","pptx","ppt"],
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    if uploaded:
        size_kb = uploaded.size / 1024
        size_str = f"{size_kb:.1f} KB" if size_kb < 1024 else f"{size_kb/1024:.1f} MB"
        st.markdown(f"""
        <div class="file-info">
            <span>📎</span>
            <span class="file-info-name">{uploaded.name}</span>
            <span class="file-info-meta">{uploaded.name.split('.')[-1].upper()} &nbsp;·&nbsp; {size_str}</span>
        </div>
        """, unsafe_allow_html=True)

    run = st.button("⚡  Extract & Apply Privacy Shield", use_container_width=True)

    st.markdown("""
    <div class="trust-row">
        <span class="trust-badge"><span class="trust-dot"></span>No data stored</span>
        <span class="trust-badge"><span class="trust-dot"></span>AI + Regex dual-layer</span>
        <span class="trust-badge"><span class="trust-dot"></span>Hindi label support</span>
        <span class="trust-badge"><span class="trust-dot"></span>End-to-end secure</span>
    </div>
    """, unsafe_allow_html=True)

# ── Core Logic ────────────────────────────────────────────────────────
def build_rules():
    r = []
    if redact_ids:       r.append("Aadhaar (12-digit, XXXX XXXX XXXX), SSN, PAN (ABCDE1234F), passport, driving license, voter ID")
    if redact_phones:    r.append("phone numbers, mobile numbers (+91 or 10-digit), email addresses")
    if redact_banking:   r.append("bank account numbers, IFSC codes, credit/debit card numbers, CVV, UPI IDs")
    if redact_passwords: r.append("passwords, API keys, tokens, OTPs, PINs")
    if redact_names:     r.append("full names on identity documents after labels like 'Name:', 'नाम:'")
    if redact_dates:     r.append("dates of birth in any format, DOB, जन्म तिथि")
    return r

def pdf_text(fb):
    try:
        import pypdf; r = pypdf.PdfReader(io.BytesIO(fb))
        return "".join(p.extract_text() or "" for p in r.pages).strip()
    except: return None

def docx_text(fb):
    try:
        import docx; d = docx.Document(io.BytesIO(fb))
        return "\n".join(p.text for p in d.paragraphs if p.text.strip()).strip()
    except: return None

def xlsx_text(fb):
    try:
        import openpyxl; wb = openpyxl.load_workbook(io.BytesIO(fb), data_only=True)
        rows = []
        for s in wb.worksheets:
            rows.append(f"[Sheet: {s.title}]")
            for row in s.iter_rows(values_only=True):
                l = " | ".join(str(c) for c in row if c is not None)
                if l.strip(): rows.append(l)
        return "\n".join(rows).strip()
    except: return None

def pptx_text(fb):
    try:
        from pptx import Presentation; p = Presentation(io.BytesIO(fb))
        lines = []
        for i, s in enumerate(p.slides, 1):
            lines.append(f"[Slide {i}]")
            for sh in s.shapes:
                if hasattr(sh,"text") and sh.text.strip(): lines.append(sh.text.strip())
        return "\n".join(lines).strip()
    except: return None

def img_text(fb, mime):
    b64 = base64.b64encode(fb).decode()
    r = client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role":"user","content":[
            {"type":"image_url","image_url":{"url":f"data:{mime};base64,{b64}"}},
            {"type":"text","text":"Extract ALL text from this image exactly as it appears. Return only raw extracted text preserving formatting."}
        ]}], max_tokens=2000
    )
    return r.choices[0].message.content.strip()

def regex_redact(text, ph):
    count=0; removed=[]
    if redact_ids:
        n=re.sub(r'\b\d{4}\s?\d{4}\s?\d{4}\b',ph,text)
        if n!=text: count+=1; removed.append("Aadhaar"); text=n
        n=re.sub(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b',ph,text)
        if n!=text: count+=1; removed.append("PAN"); text=n
    if redact_phones:
        n=re.sub(r'\b(\+91[\s-]?)?[6-9]\d{9}\b',ph,text)
        if n!=text: count+=1; removed.append("phone"); text=n
        n=re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',ph,text)
        if n!=text: count+=1; removed.append("email"); text=n
    if redact_banking:
        n=re.sub(r'\b(?:\d[ -]*?){13,16}\b',ph,text)
        if n!=text: count+=1; removed.append("card number"); text=n
        n=re.sub(r'\b[A-Z]{4}0[A-Z0-9]{6}\b',ph,text)
        if n!=text: count+=1; removed.append("IFSC"); text=n
    if redact_dates:
        n=re.sub(r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}\b',ph,text)
        if n!=text: count+=1; removed.append("DOB"); text=n
    if redact_names:
        n=re.sub(r'(Name|नाम)\s*[:\-]\s*[A-Za-z\s]{3,40}', lambda m: m.group(0).split(':')[0]+': '+ph, text)
        if n!=text: count+=1; removed.append("name"); text=n
    return text, removed, count

def ai_redact(text, rules):
    ph = "[REDACTED]" if show_redacted else "████"
    if not rules: return text, [], 0
    prompt = f"""Strict enterprise privacy engine. Redact ALL sensitive data.

REDACT:
{chr(10).join(f'- {r}' for r in rules)}

RULES: Source may be Aadhaar/passport/bank doc. Replace ONLY the sensitive value with "{ph}". Keep all surrounding text. When uncertain — redact it.

Return ONLY JSON: {{"clean_text":"...","redacted_items":["..."],"redaction_count":0}}

TEXT: {text[:6000]}"""
    resp = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role":"system","content":"Strict data privacy engine. Return only valid JSON."},
            {"role":"user","content":prompt}
        ], temperature=0.0, max_tokens=4000
    )
    raw = re.sub(r'```json|```','',resp.choices[0].message.content.strip()).strip()
    try:
        res = json.loads(raw)
        clean = res.get("clean_text", text)
        items = res.get("redacted_items", [])
        count = res.get("redaction_count", 0)
        clean, ei, ec = regex_redact(clean, ph)
        return clean, items+ei, count+ec
    except:
        return regex_redact(text, ph)

# ── Process ───────────────────────────────────────────────────────────
if run and not uploaded:
    with col: st.error("Please upload a document first.")

if run and uploaded:
    with col:
        fb   = uploaded.read()
        mime = uploaded.type
        name = uploaded.name.lower()
        raw  = None

        with st.spinner("Extracting document content..."):
            try:
                if   name.endswith(".pdf"):               raw = pdf_text(fb) or img_text(fb,"application/pdf")
                elif name.endswith((".png",".jpg",".jpeg")): raw = img_text(fb, mime)
                elif name.endswith(".docx"):              raw = docx_text(fb)
                elif name.endswith(".xlsx"):              raw = xlsx_text(fb)
                elif name.endswith((".pptx",".ppt")):     raw = pptx_text(fb) or img_text(fb, mime)
            except Exception as e:
                st.error(f"Extraction error: {e}")

        if not raw or len(raw.strip()) < 5:
            st.error("Could not extract text. Please try a different file."); st.stop()

        rules = build_rules()
        clean, items, count = raw, [], 0

        if rules:
            with st.spinner("Applying Privacy Shield..."):
                try:    clean, items, count = ai_redact(raw, rules)
                except: clean, items, count = regex_redact(raw, "[REDACTED]" if show_redacted else "████")

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        wc = len(clean.split())
        is_clean = count == 0
        s_class = "stat-box sb-status" if is_clean else "stat-box sb-danger"
        s_val   = "✓ CLEAN" if is_clean else "⚠ REDACTED"

        st.markdown(f"""
        <div class="stats-grid">
            <div class="stat-box sb-words">
                <div class="stat-num">{wc:,}</div>
                <div class="stat-lbl">Words Extracted</div>
            </div>
            <div class="stat-box sb-redact">
                <div class="stat-num">{count}</div>
                <div class="stat-lbl">Items Redacted</div>
            </div>
            <div class="{s_class}">
                <div class="stat-num" style="font-size:1.3rem;padding-top:0.3rem">{s_val}</div>
                <div class="stat-lbl">Status</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if items:
            tags = "".join(f'<span class="rtag">⛔ {i}</span>' for i in set(items))
            st.markdown(f"""
            <div style="margin:0.5rem 0 1rem">
                <div style="font-family:'IBM Plex Mono',monospace;font-size:0.58rem;letter-spacing:0.15em;text-transform:uppercase;color:#1e293b;margin-bottom:0.5rem">Redacted Categories</div>
                <div class="rtag-row">{tags}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="result-panel">
            <div class="rp-header">
                <span class="rp-title">Extracted Content</span>
                <span class="rp-meta">{len(clean):,} characters</span>
            </div>
            <div class="rp-body">{clean}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        ca, cb = st.columns(2)
        ca.download_button("⬇ Download TXT", clean,
            f"{uploaded.name}_clean.txt", "text/plain", use_container_width=True)
        cb.download_button("⬇ Download JSON",
            json.dumps({"filename":uploaded.name,"text":clean,"words":wc,"redacted":count,"categories":list(set(items))},indent=2),
            f"{uploaded.name}_clean.json","application/json", use_container_width=True)
