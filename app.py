import streamlit as st
import io
import re

st.set_page_config(
    page_title="DocVault Enterprise",
    page_icon="🔐",
    layout="wide"
)

# ─────────────────────────────────────────
# PREMIUM FULLSCREEN UI
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}

.stApp {
    background: radial-gradient(circle at 20% 20%, #111133, #070714 60%);
    color: #f1f3ff;
}

.main .block-container {
    padding: 2rem 4rem 4rem 4rem !important;
    max-width: 100% !important;
}

.hero { padding: 3rem 0 2rem; }
.hero-title { font-size: 4rem; font-weight: 800; }
.hero-title span {
    background: linear-gradient(120deg,#90ff50,#40ffc8,#4080ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub { font-size: 1.2rem; color: #9ca4ff; margin-top: 0.5rem; }

.section-title {
    margin-top: 3rem;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #7f88ff;
}

.card {
    background: #0f1024;
    border: 1px solid #1c1d45;
    border-radius: 18px;
    padding: 1.5rem;
    margin-top: 1rem;
    transition: 0.3s;
}

.pass { color:#90ff50; font-weight:600; }
.fail { color:#ff5f7a; font-weight:600; }

div[data-testid="stFileUploader"] {
    background:#0f1024 !important;
    border:2px dashed #2a2c66 !important;
    border-radius:20px !important;
    padding:2rem !important;
}

.stButton>button {
    width:100%;
    background:linear-gradient(135deg,#90ff50,#40ffc8) !important;
    color:#050510 !important;
    font-weight:800 !important;
    font-size:1.1rem !important;
    padding:1rem !important;
    border-radius:14px !important;
}

textarea {
    background:#0b0c20 !important;
    border:1px solid #20225a !important;
    color:#e0e3ff !important;
    border-radius:12px !important;
    font-size:0.95rem !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# HERO
# ─────────────────────────────────────────
st.markdown("""
<div class="hero">
<div class="hero-title">Doc<span>Vault</span></div>
<div class="hero-sub">
Enterprise-grade secure document validation & extraction platform
</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# REDACTION CONTROLS
# ─────────────────────────────────────────
st.markdown('<div class="section-title">Redaction Controls</div>', unsafe_allow_html=True)

colA, colB, colC = st.columns(3)

with colA:
    redact_aadhaar = st.checkbox("Aadhaar Number")
    redact_pan = st.checkbox("PAN Number")
    redact_ssn = st.checkbox("SSN")

with colB:
    redact_mobile = st.checkbox("Mobile Numbers")
    redact_dob = st.checkbox("Date of Birth")

with colC:
    redact_names = st.checkbox("Personal Names")

# ─────────────────────────────────────────
# REDACTION FUNCTION
# ─────────────────────────────────────────
def redact_sensitive(text):
    redaction_count = 0

    if redact_aadhaar:
        text, n = re.subn(r'\b\d{4}\s?\d{4}\s?\d{4}\b', '[REDACTED_AADHAAR]', text)
        redaction_count += n

    if redact_pan:
        text, n = re.subn(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b', '[REDACTED_PAN]', text)
        redaction_count += n

    if redact_ssn:
        text, n = re.subn(r'\b\d{3}-\d{2}-\d{4}\b', '[REDACTED_SSN]', text)
        redaction_count += n

    if redact_mobile:
        text, n = re.subn(r'\b(\+91[\s-]?)?[6-9]\d{9}\b', '[REDACTED_PHONE]', text)
        redaction_count += n

    if redact_dob:
        text, n = re.subn(r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}\b', '[REDACTED_DOB]', text)
        redaction_count += n

    if redact_names:
        text, n = re.subn(r'(Name|नाम)\s*[:\-]\s*[A-Za-z\s]{3,40}', 'Name: [REDACTED_NAME]', text)
        redaction_count += n

    return text, redaction_count

# ─────────────────────────────────────────
# UPLOAD
# ─────────────────────────────────────────
st.markdown('<div class="section-title">Upload Document</div>', unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Supported: PDF, DOCX, XLSX, PPTX, PPT, TXT",
    type=["pdf","docx","xlsx","pptx","ppt","txt"]
)

# ─────────────────────────────────────────
# PROCESS
# ─────────────────────────────────────────
if st.button("🔐 Secure Extract"):

    if not uploaded:
        st.warning("Upload a file first.")
    else:
        file_bytes = uploaded.read()
        ext = uploaded.name.split(".")[-1].lower()

        # For simplicity, handle TXT only here (you can merge with your extraction logic)
        if ext == "txt":
            text = file_bytes.decode("utf-8", errors="ignore")
        else:
            st.error("Demo redaction works on TXT files for now.")
            st.stop()

        redacted_text, count = redact_sensitive(text)

        st.markdown("## 📄 Extracted & Redacted Output")
        st.success(f"🔒 {count} sensitive items redacted.")

        st.text_area("", redacted_text, height=500)
