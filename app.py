import streamlit as st
import io
import re

st.set_page_config(
    page_title="DocVault Enterprise",
    page_icon="🔐",
    layout="wide"
)

# ─────────────────────────────────────────
# PREMIUM UI
# ─────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
}
.stApp {
    background: radial-gradient(circle at 20% 20%, #111133, #070714 60%);
    color: #f1f3ff;
}
.main .block-container {
    padding: 2rem 4rem;
    max-width: 100%;
}
.section-title {
    margin-top: 3rem;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #7f88ff;
}
.pass { color:#90ff50; font-weight:600; }
.fail { color:#ff5f7a; font-weight:600; }
.stButton>button {
    width:100%;
    background:linear-gradient(135deg,#90ff50,#40ffc8);
    color:#050510;
    font-weight:800;
    padding:1rem;
    border-radius:14px;
}
textarea {
    background:#0b0c20 !important;
    border:1px solid #20225a !important;
    color:#e0e3ff !important;
    border-radius:12px !important;
}
</style>
""", unsafe_allow_html=True)

st.title("🔐 DocVault Enterprise")
st.caption("Secure Document Validation & Extraction Platform")

# ─────────────────────────────────────────
# REDACTION CONTROLS
# ─────────────────────────────────────────
st.markdown('<div class="section-title">Redaction Controls</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    aadhaar = st.checkbox("Aadhaar Number")
    pan = st.checkbox("PAN Number")
    ssn = st.checkbox("SSN")

with col2:
    mobile = st.checkbox("Mobile Numbers")
    dob = st.checkbox("Date of Birth")

# ─────────────────────────────────────────
# FILE UPLOAD
# ─────────────────────────────────────────
st.markdown('<div class="section-title">Upload Document</div>', unsafe_allow_html=True)

uploaded = st.file_uploader(
    "Supported: PDF, DOCX, XLSX, PPTX, PPT, TXT",
    type=["pdf","docx","xlsx","pptx","ppt","txt"]
)

# ─────────────────────────────────────────
# SECURITY CONFIG
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
# TEXT EXTRACTION
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
# REDACTION ENGINE
# ─────────────────────────────────────────
def redact_text(text):
    if aadhaar:
        text = re.sub(r"\b\d{4}\s?\d{4}\s?\d{4}\b", "[REDACTED_AADHAAR]", text)
    if pan:
        text = re.sub(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", "[REDACTED_PAN]", text)
    if mobile:
        text = re.sub(r"\b[6-9]\d{9}\b", "[REDACTED_MOBILE]", text)
    if dob:
        text = re.sub(r"\b\d{2}[-/]\d{2}[-/]\d{4}\b", "[REDACTED_DOB]", text)
    if ssn:
        text = re.sub(r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED_SSN]", text)
    return text

# ─────────────────────────────────────────
# PROCESS BUTTON
# ─────────────────────────────────────────
if st.button("🔐 Secure Extract"):

    if not uploaded:
        st.warning("Upload a file first.")
        st.stop()

    file_bytes = uploaded.read()
    ext = uploaded.name.split(".")[-1].lower()

    st.markdown("## 🔍 Security Scan Results")

    magic_ok = check_magic(file_bytes, ext)
    malware_ok = check_malware(file_bytes)
    integrity_ok = check_integrity(file_bytes, ext)

    st.write("File Type Validation:", "✅" if magic_ok else "❌")
    st.write("Malware Scan:", "✅" if malware_ok else "❌")
    st.write("Integrity Check:", "✅" if integrity_ok else "❌")

    score = 100
    if not magic_ok: score -= 30
    if not malware_ok: score -= 40
    if not integrity_ok: score -= 30

    st.progress(score/100)
    st.write("Security Score:", score, "/100")

    if not (magic_ok and malware_ok and integrity_ok):
        st.error("🚫 File blocked due to failed security checks.")
        st.stop()

    st.success("✅ File passed all security layers.")

    text = extract_text(file_bytes, ext)

    if not text:
        st.warning("No readable text found.")
        st.stop()

    # Apply Redaction
    text = redact_text(text)

    st.markdown("## 📄 Extracted Output")
    st.text_area("", text, height=500)

    st.download_button(
        "⬇ Download Clean Copy",
        data=text,
        file_name="secure_extracted.txt",
        mime="text/plain"
    )
