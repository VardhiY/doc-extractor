import streamlit as st
import io
import re

st.set_page_config(
    page_title="DocVault Secure Extractor",
    page_icon="🔐",
    layout="wide"
)

# ─────────────────────────────────────────
# UI STYLE
# ─────────────────────────────────────────
st.markdown("""
<style>
body {background-color:#070714;}
.hero {text-align:center;padding:3rem 0;}
.hero h1 {font-size:3.5rem;}
.sec-head {margin-top:2.2rem;font-weight:700;color:#8a8ad8;}
.card {
    background:#0e0e1f;
    border:1px solid #1b1b3a;
    border-radius:14px;
    padding:1rem 1.2rem;
    margin-bottom:0.8rem;
}
.pass {color:#90ff50;}
.fail {color:#ff5f5f;}
.stButton>button {
    background:linear-gradient(135deg,#90ff50,#40ffc8);
    color:#000;font-weight:700;border-radius:12px;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# HERO
# ─────────────────────────────────────────
st.markdown("""
<div class="hero">
<h1>Doc<span style="color:#90ff50;">Vault</span></h1>
<p>Enterprise-grade secure document extraction & validation</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# PASSING REQUIREMENTS (BEFORE UPLOAD)
# ─────────────────────────────────────────
st.markdown("### 🛡 Security Requirements")

st.markdown("""
<div class="card pass">
✔ Supported Formats: PDF, DOCX, XLSX, PPTX, PPT, TXT
</div>

<div class="card pass">
✔ File Type Verification (Magic Byte Validation)
</div>

<div class="card pass">
✔ Malware Signature Scan
</div>

<div class="card pass">
✔ Corruption / Integrity Check
</div>

<div class="card fail">
✖ Executable files (.exe, .bat, .js) will be blocked
</div>

<div class="card fail">
✖ Disguised or renamed malicious files will be rejected
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# FILE UPLOAD
# ─────────────────────────────────────────
st.markdown("### 📎 Upload Document")

uploaded = st.file_uploader(
    "Upload your secure document",
    type=["pdf","docx","xlsx","pptx","ppt","txt"]
)

# ─────────────────────────────────────────
# SECURITY CHECKS
# ─────────────────────────────────────────
MALWARE_SIGS = [
    b"cmd.exe", b"powershell", b"eval(", b"unescape(",
    b"ActiveXObject", b"AutoOpen", b"WScript"
]

MAGIC_BYTES = {
    "pdf": b"%PDF",
    "docx": b"PK",
    "xlsx": b"PK",
    "pptx": b"PK",
    "ppt": b"\xd0\xcf\x11\xe0",
}

def check_magic(file_bytes, ext):
    if ext in MAGIC_BYTES:
        return file_bytes.startswith(MAGIC_BYTES[ext])
    return True

def check_malware(file_bytes):
    for sig in MALWARE_SIGS:
        if sig in file_bytes:
            return False
    return True

def check_integrity(file_bytes, ext):
    try:
        if ext == "pdf":
            import pypdf
            pypdf.PdfReader(io.BytesIO(file_bytes))
        elif ext == "docx":
            import docx
            docx.Document(io.BytesIO(file_bytes))
        elif ext == "xlsx":
            import openpyxl
            openpyxl.load_workbook(io.BytesIO(file_bytes))
        elif ext in ["pptx","ppt"]:
            from pptx import Presentation
            Presentation(io.BytesIO(file_bytes))
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
        return "\n".join(page.extract_text() or "" for page in reader.pages)

    elif ext == "docx":
        import docx
        doc = docx.Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs)

    elif ext == "xlsx":
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(file_bytes), data_only=True)
        text = []
        for sheet in wb.worksheets:
            for row in sheet.iter_rows(values_only=True):
                line = " | ".join(str(c) for c in row if c)
                if line:
                    text.append(line)
        return "\n".join(text)

    elif ext in ["pptx","ppt"]:
        from pptx import Presentation
        prs = Presentation(io.BytesIO(file_bytes))
        lines = []
        for slide in prs.slides:
            for shape in slide.shapes:
                if hasattr(shape,"text") and shape.text.strip():
                    lines.append(shape.text.strip())
        return "\n".join(lines)

    elif ext == "txt":
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

        st.markdown("### 🔍 Running Security Scan")

        magic_ok = check_magic(file_bytes, ext)
        malware_ok = check_malware(file_bytes)
        integrity_ok = check_integrity(file_bytes, ext)

        st.write("File Type Check:", "✅" if magic_ok else "❌")
        st.write("Malware Scan:", "✅" if malware_ok else "❌")
        st.write("Integrity Check:", "✅" if integrity_ok else "❌")

        if not (magic_ok and malware_ok and integrity_ok):
            st.error("🚫 File blocked due to security failure.")
            st.stop()

        st.success("✅ File passed all security layers.")

        st.markdown("### 📄 Extracted Text")

        text = extract_text(file_bytes, ext)

        if text:
            st.text_area("Output", text, height=400)
        else:
            st.warning("No readable text found.")
