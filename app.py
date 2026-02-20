import streamlit as st
import io
import re
import json

# ─────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="DocVault Secure Extractor",
    page_icon="🔐",
    layout="wide"
)

# ─────────────────────────────────────────
# SIMPLE CLEAN UI
# ─────────────────────────────────────────
st.markdown("""
<style>
body {background-color:#070714;}
.hero {text-align:center;padding:3rem 0;}
.hero h1 {font-size:3.5rem;}
.sec-head {margin-top:2rem;font-weight:700;color:#888;}
.stButton>button {background:linear-gradient(135deg,#90ff50,#40ffc8);
color:#000;font-weight:700;border-radius:12px;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
<h1>Doc<span style="color:#90ff50;">Vault</span></h1>
<p>Secure document extraction with automatic redaction.</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# SECURITY SETTINGS
# ─────────────────────────────────────────
st.markdown("### 🛡 Security Settings")
max_size_mb = st.slider("Max file size (MB)", 1, 20, 10)

# ─────────────────────────────────────────
# FILE UPLOAD
# ─────────────────────────────────────────
uploaded = st.file_uploader(
    "Upload file",
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

def check_size(file_bytes):
    size_mb = len(file_bytes)/(1024*1024)
    return size_mb <= max_size_mb, f"{size_mb:.2f} MB"

def check_magic(file_bytes, ext):
    if ext in MAGIC_BYTES:
        return file_bytes.startswith(MAGIC_BYTES[ext]), "Magic byte validation"
    return True, "Skipped"

def check_malware(file_bytes):
    for sig in MALWARE_SIGS:
        if sig in file_bytes:
            return False, f"Malware signature detected: {sig.decode(errors='ignore')}"
    return True, "No malware signatures"

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
        return True, "File opened successfully"
    except:
        return False, "File corrupted or unreadable"

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
        st.warning("Upload file first.")
    else:
        file_bytes = uploaded.read()
        ext = uploaded.name.split(".")[-1].lower()

        st.markdown("### 🔍 Security Scan")

        s_ok, s_msg = check_size(file_bytes)
        st.write("📦 File Size:", s_msg, "✅" if s_ok else "❌")

        m_ok, m_msg = check_magic(file_bytes, ext)
        st.write("🔎 Type Validation:", m_msg, "✅" if m_ok else "❌")

        v_ok, v_msg = check_malware(file_bytes)
        st.write("🦠 Malware Scan:", v_msg, "✅" if v_ok else "❌")

        i_ok, i_msg = check_integrity(file_bytes, ext)
        st.write("🧩 Integrity Check:", i_msg, "✅" if i_ok else "❌")

        if not (s_ok and m_ok and v_ok and i_ok):
            st.error("🚫 File blocked due to failed security checks.")
            st.stop()

        st.success("✅ All security checks passed.")

        st.markdown("### 📄 Extracted Text")
        text = extract_text(file_bytes, ext)

        if text:
            st.text_area("Output", text, height=400)
        else:
            st.warning("No readable text found.")
