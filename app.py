import streamlit as st
from groq import Groq
import json
import re
import base64
import io

st.set_page_config(page_title="DocAI Extractor", page_icon="✨", layout="centered")

try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client  = Groq(api_key=API_KEY)
except:
    st.error("Add GROQ_API_KEY to Streamlit Secrets.")
    st.stop()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

* { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }

#MainMenu, footer, header, .stDeployButton,
[data-testid="stToolbar"],[data-testid="stDecoration"],
[data-testid="stStatusWidget"] { display:none !important; }
[data-testid="collapsedControl"] { display:flex !important; }

/* ── BACKGROUND ── */
.stApp {
    background: #0d0d1a;
    background-image:
        radial-gradient(circle at 15% 20%, rgba(255,0,128,0.12) 0%, transparent 40%),
        radial-gradient(circle at 85% 10%, rgba(100,0,255,0.15) 0%, transparent 35%),
        radial-gradient(circle at 50% 80%, rgba(0,200,255,0.08) 0%, transparent 45%),
        radial-gradient(circle at 90% 70%, rgba(255,150,0,0.07) 0%, transparent 35%);
    min-height: 100vh;
}

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
    background: rgba(15,10,30,0.95) !important;
    border-right: 1px solid rgba(255,255,255,0.06) !important;
    backdrop-filter: blur(20px);
}
section[data-testid="stSidebar"] .stCheckbox label {
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.85rem !important; color: #888 !important; font-weight: 500 !important;
}
section[data-testid="stSidebar"] .stCheckbox label:hover { color: #fff !important; }
section[data-testid="stSidebar"] .stMarkdown h2 {
    font-size: 0.65rem !important; letter-spacing: 0.2em !important;
    text-transform: uppercase !important; color: #444 !important; margin-bottom: 0.8rem !important;
}

/* ── HERO ── */
.hero-wrap { padding: 2.5rem 0 1rem; text-align: center; }

.logo-badge {
    display: inline-flex; align-items: center; gap: 0.5rem;
    background: linear-gradient(135deg, rgba(255,0,128,0.15), rgba(100,0,255,0.15));
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 50px; padding: 0.4rem 1.2rem;
    font-size: 0.7rem; letter-spacing: 0.15em; text-transform: uppercase;
    color: rgba(255,255,255,0.6); margin-bottom: 1.5rem;
    backdrop-filter: blur(10px);
}
.live-dot {
    width: 7px; height: 7px; border-radius: 50%;
    background: #00ff88; box-shadow: 0 0 8px #00ff88;
    animation: livepulse 1.5s infinite;
}
@keyframes livepulse { 0%,100%{transform:scale(1);opacity:1;} 50%{transform:scale(1.4);opacity:0.5;} }

.main-title {
    font-size: clamp(2.8rem, 7vw, 5rem);
    font-weight: 700; line-height: 1.05;
    letter-spacing: -0.03em;
    margin-bottom: 0.5rem;
}
.word-1 { color: #ff2d78; }
.word-2 { color: #ffffff; }
.word-3 {
    background: linear-gradient(90deg, #7c3aed, #06b6d4, #7c3aed);
    background-size: 200% auto;
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    animation: shimmer 3s linear infinite;
}
@keyframes shimmer { 0%{background-position:0%} 100%{background-position:200%} }

.hero-desc {
    color: rgba(255,255,255,0.35); font-size: 1rem;
    font-weight: 400; line-height: 1.6; margin: 0.8rem 0 1.5rem;
}

/* ── FORMAT CHIPS ── */
.chips { display: flex; flex-wrap: wrap; justify-content: center; gap: 0.5rem; margin-bottom: 2rem; }
.chip {
    font-family: 'Space Mono', monospace;
    font-size: 0.62rem; font-weight: 700; letter-spacing: 0.08em;
    padding: 0.3rem 0.75rem; border-radius: 6px;
    border: 1px solid; text-transform: uppercase;
}
.c1 { color: #ff6b6b; border-color: rgba(255,107,107,0.4); background: rgba(255,107,107,0.08); }
.c2 { color: #4ecdc4; border-color: rgba(78,205,196,0.4); background: rgba(78,205,196,0.08); }
.c3 { color: #a78bfa; border-color: rgba(167,139,250,0.4); background: rgba(167,139,250,0.08); }
.c4 { color: #34d399; border-color: rgba(52,211,153,0.4); background: rgba(52,211,153,0.08); }
.c5 { color: #fb923c; border-color: rgba(251,146,60,0.4);  background: rgba(251,146,60,0.08);  }

/* ── UPLOAD CARD ── */
.upload-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.03), rgba(255,255,255,0.01));
    border: 1.5px dashed rgba(255,255,255,0.12);
    border-radius: 20px; padding: 0.8rem; margin-bottom: 1rem;
    transition: border-color 0.3s, background 0.3s;
    position: relative; overflow: hidden;
}
.upload-card::before {
    content: ''; position: absolute; inset: 0; border-radius: 20px;
    background: linear-gradient(135deg, rgba(255,0,128,0.03), rgba(100,0,255,0.03));
    pointer-events: none;
}
.upload-card:hover { border-color: rgba(255,0,128,0.4); background: rgba(255,0,128,0.03); }

div[data-testid="stFileUploader"] { background: transparent !important; border: none !important; }
div[data-testid="stFileUploadDropzone"] {
    background: transparent !important; border: none !important;
    padding: 2rem 1rem !important;
}
div[data-testid="stFileUploadDropzone"] p {
    color: rgba(255,255,255,0.3) !important;
    font-family: 'Space Grotesk', sans-serif !important; font-size: 0.9rem !important;
}
div[data-testid="stFileUploadDropzone"] small { color: rgba(255,255,255,0.15) !important; }

/* ── FILE INFO ── */
.file-info {
    display: flex; align-items: center; gap: 0.8rem;
    background: linear-gradient(135deg, rgba(255,0,128,0.08), rgba(100,0,255,0.08));
    border: 1px solid rgba(255,255,255,0.08); border-radius: 12px;
    padding: 0.75rem 1.1rem; margin-bottom: 0.8rem;
}
.file-name { font-family: 'Space Mono', monospace; font-size: 0.78rem; color: #ff79c6; flex: 1; }
.file-size { font-family: 'Space Mono', monospace; font-size: 0.65rem; color: rgba(255,255,255,0.2); }

/* ── BUTTON ── */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #ff2d78, #7c3aed, #06b6d4) !important;
    background-size: 200% auto !important;
    color: white !important; font-family: 'Space Grotesk', sans-serif !important;
    font-weight: 700 !important; font-size: 1rem !important;
    border: none !important; border-radius: 14px !important;
    padding: 0.9rem !important; letter-spacing: 0.02em !important;
    transition: all 0.4s ease !important;
    box-shadow: 0 4px 30px rgba(255,45,120,0.25) !important;
}
.stButton > button:hover {
    background-position: right center !important;
    box-shadow: 0 8px 50px rgba(255,45,120,0.4), 0 0 80px rgba(124,58,237,0.2) !important;
    transform: translateY(-2px) !important;
}

/* ── DIVIDER ── */
.rainbow-divider {
    height: 2px; border-radius: 2px; margin: 2rem 0;
    background: linear-gradient(90deg, #ff2d78, #7c3aed, #06b6d4, #34d399, #fb923c, #ff2d78);
    background-size: 200% auto;
    animation: rainbow 4s linear infinite;
}
@keyframes rainbow { 0%{background-position:0%} 100%{background-position:200%} }

/* ── STATS ── */
.stats-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.8rem; margin: 1.2rem 0; }
.stat-card {
    border-radius: 16px; padding: 1.2rem 0.8rem; text-align: center;
    position: relative; overflow: hidden;
}
.stat-card::before {
    content: ''; position: absolute; inset: 0; border-radius: 16px;
    opacity: 0.12;
}
.sc-1 { background: rgba(255,45,120,0.08); border: 1px solid rgba(255,45,120,0.2); }
.sc-1::before { background: linear-gradient(135deg,#ff2d78,transparent); }
.sc-2 { background: rgba(124,58,237,0.08); border: 1px solid rgba(124,58,237,0.2); }
.sc-2::before { background: linear-gradient(135deg,#7c3aed,transparent); }
.sc-3g { background: rgba(52,211,153,0.08); border: 1px solid rgba(52,211,153,0.2); }
.sc-3g::before { background: linear-gradient(135deg,#34d399,transparent); }
.sc-3r { background: rgba(251,146,60,0.08); border: 1px solid rgba(251,146,60,0.2); }
.sc-3r::before { background: linear-gradient(135deg,#fb923c,transparent); }

.stat-num {
    font-size: 2rem; font-weight: 700; line-height: 1;
    font-family: 'Space Mono', monospace;
}
.sc-1 .stat-num { color: #ff2d78; }
.sc-2 .stat-num { color: #a78bfa; }
.sc-3g .stat-num { color: #34d399; font-size: 1.1rem; padding-top: 0.4rem; }
.sc-3r .stat-num { color: #fb923c; font-size: 1.1rem; padding-top: 0.4rem; }
.stat-lbl { font-size: 0.6rem; letter-spacing: 0.15em; text-transform: uppercase; color: rgba(255,255,255,0.25); margin-top: 0.4rem; }

/* ── REDACT TAGS ── */
.rtags { display: flex; flex-wrap: wrap; gap: 0.4rem; margin: 0.8rem 0 1.2rem; }
.rtag {
    font-family: 'Space Mono', monospace; font-size: 0.63rem;
    padding: 0.25rem 0.65rem; border-radius: 6px;
    background: rgba(255,45,120,0.1); border: 1px solid rgba(255,45,120,0.25); color: #ff79c6;
}

/* ── RESULT BOX ── */
.result-wrap {
    border-radius: 20px; overflow: hidden; margin: 0.8rem 0;
    border: 1px solid rgba(255,255,255,0.07);
    background: rgba(255,255,255,0.02);
}
.result-header {
    display: flex; justify-content: space-between; align-items: center;
    padding: 1rem 1.4rem;
    background: linear-gradient(135deg, rgba(255,45,120,0.06), rgba(124,58,237,0.06));
    border-bottom: 1px solid rgba(255,255,255,0.05);
}
.result-header-title {
    font-size: 0.65rem; letter-spacing: 0.15em; text-transform: uppercase;
    color: rgba(255,255,255,0.3); font-family: 'Space Mono', monospace;
}
.result-header-badge {
    font-family: 'Space Mono', monospace; font-size: 0.6rem;
    color: #06b6d4; background: rgba(6,182,212,0.1);
    border: 1px solid rgba(6,182,212,0.2);
    padding: 0.15rem 0.6rem; border-radius: 999px;
}
.result-body {
    padding: 1.4rem; font-family: 'Space Mono', monospace;
    font-size: 0.78rem; line-height: 1.9; color: rgba(255,255,255,0.55);
    white-space: pre-wrap; word-break: break-word;
    max-height: 380px; overflow-y: auto;
}
.result-body::-webkit-scrollbar { width: 3px; }
.result-body::-webkit-scrollbar-thumb { background: rgba(255,45,120,0.3); border-radius: 2px; }

/* ── DOWNLOAD BUTTONS ── */
.stDownloadButton > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: rgba(255,255,255,0.4) !important;
    font-family: 'Space Grotesk', sans-serif !important;
    font-size: 0.82rem !important; font-weight: 500 !important;
    border-radius: 10px !important; padding: 0.65rem 1rem !important; width: 100% !important;
    transition: all 0.2s !important;
}
.stDownloadButton > button:hover {
    background: rgba(255,45,120,0.08) !important;
    border-color: rgba(255,45,120,0.3) !important;
    color: #ff79c6 !important;
}

/* ── TRUST ROW ── */
.trust-row {
    display: flex; flex-wrap: wrap; justify-content: center;
    gap: 1.2rem; margin-top: 1.2rem;
}
.trust-item {
    font-size: 0.63rem; letter-spacing: 0.08em; color: rgba(255,255,255,0.18);
    display: flex; align-items: center; gap: 0.35rem;
}
.trust-dot { width: 4px; height: 4px; border-radius: 50%; background: #34d399; }

div[data-testid="stSelectbox"] > div {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #e2e8f0 !important; border-radius: 10px !important;
}
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ───────────────────────────────────────────────────────────
st.sidebar.markdown("## 🛡️ Privacy Shield")
redact_ids       = st.sidebar.checkbox("🪪 Aadhaar · SSN · PAN · ID",   value=True)
redact_phones    = st.sidebar.checkbox("📞 Phones & Emails",             value=True)
redact_banking   = st.sidebar.checkbox("💳 Bank · Cards · UPI",          value=True)
redact_passwords = st.sidebar.checkbox("🔑 Passwords · Keys · OTPs",     value=True)
redact_names     = st.sidebar.checkbox("👤 Personal Names",               value=False)
redact_dates     = st.sidebar.checkbox("📅 Dates of Birth",               value=False)
st.sidebar.markdown("---")
st.sidebar.markdown("## ⚙️ Output")
show_redacted    = st.sidebar.checkbox("Show [REDACTED] tags",            value=True)
st.sidebar.markdown("---")
st.sidebar.markdown("<small style='color:#333;font-family:Space Mono'>DocAI Extractor · v2.0<br>Powered by Groq + LLaMA 4</small>", unsafe_allow_html=True)

# ── HERO ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-wrap">
    <div style="display:flex;justify-content:center;margin-bottom:1.2rem">
        <span class="logo-badge"><span class="live-dot"></span>AI-Powered Document Intelligence</span>
    </div>
    <div class="main-title">
        <span class="word-1">Extract.</span>
        <span class="word-2"> Shield.</span><br>
        <span class="word-3">Deliver.</span>
    </div>
    <div class="hero-desc">Drop any document. Get clean text instantly.<br>Sensitive data auto-redacted with military-grade AI.</div>
    <div class="chips">
        <span class="chip c1">PDF</span>
        <span class="chip c2">JPG · PNG</span>
        <span class="chip c3">DOCX</span>
        <span class="chip c4">XLSX</span>
        <span class="chip c5">PPTX</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ── UPLOAD ────────────────────────────────────────────────────────────
st.markdown('<div class="upload-card">', unsafe_allow_html=True)
uploaded = st.file_uploader("drop", type=["pdf","png","jpg","jpeg","docx","xlsx","pptx","ppt"], label_visibility="collapsed")
st.markdown('</div>', unsafe_allow_html=True)

if uploaded:
    sz = uploaded.size/1024
    st.markdown(f"""
    <div class="file-info">
        <span style="font-size:1.3rem">📎</span>
        <span class="file-name">{uploaded.name}</span>
        <span class="file-size">{uploaded.name.split('.')[-1].upper()} · {"%.1f KB" % sz if sz<1024 else "%.1f MB" % (sz/1024)}</span>
    </div>""", unsafe_allow_html=True)

run = st.button("✨  Extract & Apply Privacy Shield", use_container_width=True)

st.markdown("""
<div class="trust-row">
    <span class="trust-item"><span class="trust-dot"></span>No data stored</span>
    <span class="trust-item"><span class="trust-dot"></span>AI + Regex dual-layer</span>
    <span class="trust-item"><span class="trust-dot"></span>Hindi label support</span>
    <span class="trust-item"><span class="trust-dot"></span>100% secure</span>
</div>
""", unsafe_allow_html=True)

# ── LOGIC ─────────────────────────────────────────────────────────────
def build_rules():
    r=[]
    if redact_ids:       r.append("Aadhaar (12-digit, XXXX XXXX XXXX), SSN, PAN (ABCDE1234F), passport, driving license, voter ID")
    if redact_phones:    r.append("phone numbers (+91 or 10-digit), email addresses")
    if redact_banking:   r.append("bank account numbers, IFSC codes, credit/debit card numbers, CVV, UPI IDs")
    if redact_passwords: r.append("passwords, API keys, tokens, OTPs, PINs")
    if redact_names:     r.append("full names on identity documents after 'Name:', 'नाम:'")
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
        import openpyxl; wb=openpyxl.load_workbook(io.BytesIO(fb),data_only=True)
        rows=[]
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
            {"type":"text","text":"Extract ALL text from this image exactly as it appears. Return only raw text."}
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
    prompt=f"""Strict privacy engine. Redact ALL sensitive data.
REDACT: {chr(10).join(f'- {r}' for r in rules)}
RULES: Replace ONLY the sensitive value with "{ph}". Keep all surrounding text. When uncertain — redact it.
Return ONLY JSON: {{"clean_text":"...","redacted_items":["..."],"redaction_count":0}}
TEXT: {text[:6000]}"""
    resp=client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role":"system","content":"Strict data privacy engine. Return only valid JSON."},
                  {"role":"user","content":prompt}],
        temperature=0.0,max_tokens=4000)
    raw=re.sub(r'```json|```','',resp.choices[0].message.content.strip()).strip()
    try:
        res=json.loads(raw)
        clean=res.get("clean_text",text); items=res.get("redacted_items",[]); count=res.get("redaction_count",0)
        clean,ei,ec=regex_redact(clean,ph)
        return clean,items+ei,count+ec
    except: return regex_redact(text,ph)

# ── RUN ───────────────────────────────────────────────────────────────
if run and not uploaded:
    st.error("Please upload a document first.")

if run and uploaded:
    fb=uploaded.read(); mime=uploaded.type; name=uploaded.name.lower(); raw=None

    with st.spinner("✨ Extracting content..."):
        try:
            if   name.endswith(".pdf"):                  raw=pdf_text(fb) or img_text(fb,"application/pdf")
            elif name.endswith((".png",".jpg",".jpeg")): raw=img_text(fb,mime)
            elif name.endswith(".docx"):                 raw=docx_text(fb)
            elif name.endswith(".xlsx"):                 raw=xlsx_text(fb)
            elif name.endswith((".pptx",".ppt")):        raw=pptx_text(fb) or img_text(fb,mime)
        except Exception as e: st.error(f"Error: {e}")

    if not raw or len(raw.strip())<5:
        st.error("Could not extract text from this file."); st.stop()

    rules=build_rules(); clean,items,count=raw,[],0
    if rules:
        with st.spinner("🛡️ Applying Privacy Shield..."):
            try:    clean,items,count=ai_redact(raw,rules)
            except: clean,items,count=regex_redact(raw,"[REDACTED]" if show_redacted else "████")

    st.markdown('<div class="rainbow-divider"></div>', unsafe_allow_html=True)

    wc=len(clean.split()); is_clean=count==0
    s_cls="sc-3g" if is_clean else "sc-3r"
    s_val="✓ CLEAN" if is_clean else "⚠ FLAGGED"

    st.markdown(f"""
    <div class="stats-row">
        <div class="stat-card sc-1">
            <div class="stat-num">{wc:,}</div>
            <div class="stat-lbl">Words</div>
        </div>
        <div class="stat-card sc-2">
            <div class="stat-num">{count}</div>
            <div class="stat-lbl">Redacted</div>
        </div>
        <div class="stat-card {s_cls}">
            <div class="stat-num">{s_val}</div>
            <div class="stat-lbl">Status</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if items:
        tags="".join(f'<span class="rtag">⛔ {i}</span>' for i in set(items))
        st.markdown(f'<div class="rtags">{tags}</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="result-wrap">
        <div class="result-header">
            <span class="result-header-title">📄 Extracted Content</span>
            <span class="result-header-badge">{len(clean):,} chars</span>
        </div>
        <div class="result-body">{clean}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    ca,cb=st.columns(2)
    ca.download_button("⬇ Download TXT", clean, f"{uploaded.name}_clean.txt","text/plain", use_container_width=True)
    cb.download_button("⬇ Download JSON",
        json.dumps({"filename":uploaded.name,"text":clean,"words":wc,"redacted":count,"categories":list(set(items))},indent=2),
        f"{uploaded.name}_clean.json","application/json", use_container_width=True)
