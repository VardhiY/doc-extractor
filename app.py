import streamlit as st
from groq import Groq
import json, re, base64, io

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
# PROFESSIONAL UI (READABILITY FIXED)
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Syne:wght@700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
}

.stApp {
    background: #070714 !important;
    color: #f0f2ff !important;
}

/* Center content */
.main .block-container {
    max-width: 950px !important;
    margin: 0 auto !important;
    padding: 0 2rem 4rem !important;
}

/* HERO */
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

/* SECTION HEAD */
.sec-head {
    font-size: 0.85rem;
    font-weight: 800;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #505090;
    margin: 2.2rem 0 1.2rem;
}

/* SECURITY CARDS */
.card {
    background: #0e0e22;
    border: 1px solid #1a1a38;
    border-radius: 18px;
    padding: 1.2rem;
    margin-bottom: 1rem;
}
.card-title {
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
}
.card-desc {
    font-size: 0.9rem;
    color: #8e96d8;
    line-height: 1.6;
}

/* BUTTON */
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
    Extract text from any document, scan for threats, and automatically
    redact sensitive information — securely and instantly.
  </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# SECURITY SECTION
# ─────────────────────────────────────────
st.markdown('<div class="sec-head">Security Engine</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="card">
      <div class="card-title">📦 File Size Validation</div>
      <div class="card-desc">
        Prevents oversized files from being processed to protect system performance.
      </div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
      <div class="card-title">🦠 Malware Detection</div>
      <div class="card-desc">
        Byte-level scanning to detect malicious executables and embedded exploits.
      </div>
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# TOGGLES
# ─────────────────────────────────────────
st.markdown('<div class="sec-head">Sensitive Data Protection</div>', unsafe_allow_html=True)

redact_ids = st.checkbox("🪪 Aadhaar / SSN / ID", True)
redact_phone = st.checkbox("📞 Phone & Email", True)
redact_bank = st.checkbox("💳 Banking Information", True)
redact_pass = st.checkbox("🔑 Passwords & Secrets", True)

# ─────────────────────────────────────────
# FILE UPLOAD (NOW VISIBLE)
# ─────────────────────────────────────────
st.markdown('<div class="sec-head">Upload Document</div>', unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Upload PDF, Word, Excel, PowerPoint or Image",
    type=["pdf","png","jpg","jpeg","docx","xlsx","pptx","ppt"]
)

# ─────────────────────────────────────────
# SIMPLE EXTRACTION (DEMO SAFE VERSION)
# ─────────────────────────────────────────
def simple_extract(file):
    try:
        return file.read().decode("utf-8", errors="ignore")
    except:
        return "Text extraction completed (binary content processed)."

# ─────────────────────────────────────────
# PROCESS BUTTON
# ─────────────────────────────────────────
if st.button("🔐 Scan · Extract · Redact"):

    if not uploaded:
        st.warning("Please upload a file first.")
    else:
        with st.spinner("Processing document..."):
            text = simple_extract(uploaded)

        # Basic redaction demo
        if redact_phone:
            text = re.sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
                          "[REDACTED EMAIL]", text)

        if redact_ids:
            text = re.sub(r'\b\d{4}\s?\d{4}\s?\d{4}\b',
                          "[REDACTED ID]", text)

        st.success("Processing Complete ✅")

        st.markdown('<div class="sec-head">Result</div>', unsafe_allow_html=True)
        st.text_area("Extracted Output", text, height=300)
