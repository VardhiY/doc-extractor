import streamlit as st
from groq import Groq
import json, re, io

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="DocVault · AI Extractor",
    page_icon="🔐",
    layout="wide",
)

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("⚠️ Add GROQ_API_KEY to Streamlit Secrets.")
    st.stop()

# ─────────────────────────────────────────
# PROFESSIONAL UI
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
}

.stApp {
    background: #070714 !important;
    color: #f0f2ff !important;
}

.main .block-container {
    max-width: 950px !important;
    margin: 0 auto !important;
    padding: 0 2rem 4rem !important;
}

.hero {
    text-align: center;
    padding: 3rem 0 2rem;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 4.5rem;
    font-weight: 800;
}
.hero-title .g {
    background: linear-gradient(120deg,#90ff50,#40ffc8,#4080ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-size: 1.05rem;
    color: #9aa3d8;
    max-width: 600px;
    margin: 1rem auto 0;
    line-height: 1.7;
}

.sec-head {
    font-size: 0.85rem;
    font-weight: 800;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #505090;
    margin: 2.2rem 0 1.2rem;
}

.stButton > button {
    background: linear-gradient(135deg,#90ff50,#40ffc8) !important;
    color: #050510 !important;
    font-weight: 800 !important;
    border-radius: 14px !important;
    padding: 0.8rem !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# HERO
# ─────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-title">Doc<span class="g">Vault</span></div>
  <div class="hero-sub">
    Extract text from any document and automatically redact sensitive information — securely and instantly.
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# REDACTION OPTIONS
# ─────────────────────────────────────────
st.markdown('<div class="sec-head">Sensitive Data Protection</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    redact_ids = st.checkbox("🪪 Aadhaar / SSN / ID", True)
    redact_phone = st.checkbox("📞 Phone & Email", True)

with col2:
    redact_bank = st.checkbox("💳 Banking Information", True)
    redact_pass = st.checkbox("🔑 Passwords & Secrets", True)

# ─────────────────────────────────────────
# FILE UPLOAD
# ─────────────────────────────────────────
st.markdown('<div class="sec-head">Upload Document</div>', unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Upload PDF, Word, Excel, PowerPoint or TXT file",
    type=["pdf","docx","xlsx","pptx","ppt","txt"]
)

# ─────────────────────────────────────────
# EXTRACTION FUNCTIONS
# ─────────────────────────────────────────
def extract_pdf(file_bytes):
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except:
        return None

def extract_docx(file_bytes):
    try:
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except:
        return None

def extract_xlsx(file_bytes):
    try:
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
        lines = []
        for sheet in wb.worksheets:
            lines.append(f"[Sheet: {sheet.title}]")
            for row in sheet.iter_rows(values_only=True):
                row_data = " | ".join(str(cell) for cell in row if cell)
                if row_data:
                    lines.append(row_data)
        return "\n".join(lines)
    except:
        return None

def extract_pptx(file_bytes):
    try:
        from pptx import Presentation
        prs = Presentation(io.BytesIO(file_bytes))
        lines = []
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape, "text") and shape.text.strip():
                    lines.append(shape.text.strip())
        return "\n".join(lines)
    except:
        return None

# ─────────────────────────────────────────
# REDACTION FUNCTION
# ─────────────────────────────────────────
def redact_text(text):
    if redact_phone:
        text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
                      "[REDACTED EMAIL]", text)
        text = re.sub(r'\b(\+91[\s-]?)?[6-9]\d{9}\b',
                      "[REDACTED PHONE]", text)

    if redact_ids:
        text = re.sub(r'\b\d{4}\s?\d{4}\s?\d{4}\b',
                      "[REDACTED ID]", text)

    if redact_bank:
        text = re.sub(r'\b(?:\d[ -]*?){13,16}\b',
                      "[REDACTED CARD]", text)

    if redact_pass:
        text = re.sub(r'(?i)(password\s*[:=]\s*\S+)',
                      "[REDACTED PASSWORD]", text)

    return text

# ─────────────────────────────────────────
# PROCESS BUTTON
# ─────────────────────────────────────────
if st.button("🔐 Scan · Extract · Redact"):

    if not uploaded:
        st.warning("Please upload a file first.")
    else:
        file_bytes = uploaded.read()
        name = uploaded.name.lower()

        with st.spinner("Extracting document..."):

            text = None

            if name.endswith(".pdf"):
                text = extract_pdf(file_bytes)

            elif name.endswith(".docx"):
                text = extract_docx(file_bytes)

            elif name.endswith(".xlsx"):
                text = extract_xlsx(file_bytes)

            elif name.endswith((".pptx",".ppt")):
                text = extract_pptx(file_bytes)

            elif name.endswith(".txt"):
                text = file_bytes.decode("utf-8", errors="ignore")

        if not text:
            st.error("Unable to extract readable text from this file.")
        else:
            redacted = redact_text(text)

            st.success("Processing Complete ✅")

            st.markdown('<div class="sec-head">Result</div>', unsafe_allow_html=True)
            st.text_area("Extracted Output", redacted, height=400)
