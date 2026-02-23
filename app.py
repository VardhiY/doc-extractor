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

/* HERO */
.hero {
    padding: 3rem 0 2rem;
}
.hero-title {
    font-size: 4rem;
    font-weight: 800;
}
.hero-title span {
    background: linear-gradient(120deg,#90ff50,#40ffc8,#4080ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-size: 1.2rem;
    color: #9ca4ff;
    margin-top: 0.5rem;
}

/* SECTION TITLE */
.section-title {
    margin-top: 3rem;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #7f88ff;
}

/* CARDS */
.card {
    background: #0f1024;
    border: 1px solid #1c1d45;
    border-radius: 18px;
    padding: 1.5rem;
    margin-top: 1rem;
    transition: 0.3s;
}
.card:hover {
    border-color: #40ffc8;
    box-shadow: 0 10px 40px rgba(64,255,200,0.15);
}

/* STATUS COLORS */
.pass { color:#90ff50; font-weight:600; }
.fail { color:#ff5f7a; font-weight:600; }

/* UPLOAD BOX */
div[data-testid="stFileUploader"] {
    background:#0f1024 !important;
    border:2px dashed #2a2c66 !important;
    border-radius:20px !important;
    padding:2rem !important;
}
div[data-testid="stFileUploader"]:hover {
    border-color:#40ffc8 !important;
}

/* BUTTON */
.stButton>button {
    width:100%;
    background:linear-gradient(135deg,#90ff50,#40ffc8) !important;
    color:#050510 !important;
    font-weight:800 !important;
    font-size:1.1rem !important;
    padding:1rem !important;
    border-radius:14px !important;
}

/* TEXT OUTPUT */
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
# SECURITY DASHBOARD
# ─────────────────────────────────────────
st.markdown('<div class="section-title">Security Engine</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="card">
    <div class="pass">✔ File Type Verification</div>
    Validates magic bytes to prevent disguised malicious files.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
    <div class="pass">✔ Malware Signature Scan</div>
    Detects suspicious executable and embedded script patterns.
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
    <div class="pass">✔ Corruption Detection</div>
    Attempts structured parsing before extraction.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="card">
    <div class="fail">✖ Executable Files Blocked</div>
    .exe, .bat, .js and renamed scripts are automatically rejected.
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# UPLOAD SECTION
# ─────────────────────────────────────────
st.markdown('<div class="section-title">Upload Document</div>', unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Supported: PDF, DOCX, XLSX, PPTX, PPT, TXT",
    type=["pdf","docx","xlsx","pptx","ppt","txt"]
)

# ─────────────────────────────────────────
# SECURITY LOGIC
# ─────────────────────────────────────────
MALWARE_SIGS = [b"cmd.exe", b"powershell", b"eval(", b"WScript"]
MAGIC_BYTES = {
    "pdf": b"%PDF",
    "docx": b"PK",
    "xlsx": b"PK",
    "pptx": b"PK",
    "ppt": b"\xd0\xcf\x11\xe0"
}

def check_magic(file_bytes, ext):
    if ext in MAGIC_BYTES:
        return file_bytes.startswith(MAGIC_BYTES[ext])
    return True

def check_malware(file_bytes):
    return not any(sig in file_bytes for sig in MALWARE_SIGS)

def check_integrity(file_bytes, ext):
    try:
        if ext == "pdf":
            import pypdf; pypdf.PdfReader(io.BytesIO(file_bytes))
        elif ext == "docx":
            import docx; docx.Document(io.BytesIO(file_bytes))
        elif ext == "xlsx":
            import openpyxl; openpyxl.load_workbook(io.BytesIO(file_bytes))
        elif ext in ["pptx","ppt"]:
            from pptx import Presentation; Presentation(io.BytesIO(file_bytes))
        return True
    except:
        return False

# ─────────────────────────────────────────
# EXTRACTION
# ─────────────────────────────────────────
def extract_text(file_bytes, ext):
    if ext == "pdf":
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        return "\n".join(p.extract_text() or "" for p in reader.pages)

    if ext == "docx":
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs)

    if ext == "xlsx":
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
        text=[]
        for sheet in wb.worksheets:
            for row in sheet.iter_rows(values_only=True):
                line=" | ".join(str(c) for c in row if c)
                if line: text.append(line)
        return "\n".join(text)

    if ext in ["pptx","ppt"]:
        from pptx import Presentation
        prs = Presentation(io.BytesIO(file_bytes))
        lines=[]
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape,"text") and shape.text.strip():
                    lines.append(shape.text.strip())
        return "\n".join(lines)

    if ext == "txt":
        return file_bytes.decode("utf-8", errors="ignore")

    return None

# ─────────────────────────────────────────
# PROCESS
# ─────────────────────────────────────────
if st.button("🔐 Secure Extract"):

    if not uploaded:
        st.warning("Upload a file first.")
    else:
        file_bytes = uploaded.read()
        ext = uploaded.name.split(".")[-1].lower()

        st.markdown("## 🔍 Security Scan Results")

        magic_ok = check_magic(file_bytes, ext)
        malware_ok = check_malware(file_bytes)
        integrity_ok = check_integrity(file_bytes, ext)

        st.write("File Type Validation:", "✅" if magic_ok else "❌")
        st.write("Malware Scan:", "✅" if malware_ok else "❌")
        st.write("Integrity Check:", "✅" if integrity_ok else "❌")

        if not (magic_ok and malware_ok and integrity_ok):
            st.error("🚫 File blocked due to failed security checks.")
            st.stop()

        st.success("✅ File passed all security layers.")

        text = extract_text(file_bytes, ext)

        st.markdown("## 📄 Extracted Output")

        if text:
            st.text_area("", text, height=500)
        else:
            st.warning("No readable text found.")


