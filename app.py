import streamlit as st
import io
import re
import os
import base64

# ── MUST BE FIRST STREAMLIT CALL ──
st.set_page_config(page_title="DocVault Enterprise", page_icon="🔐", layout="wide")

# ── GROQ CLIENT (after set_page_config) ──
api_key = os.environ.get("GROQ_API_KEY", "")
groq_client = None
if api_key:
    from groq import Groq
    groq_client = Groq(api_key=api_key)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
.stApp { background: radial-gradient(circle at 20% 20%, #111133, #070714 60%); color: #f1f3ff; }
.main .block-container { padding: 2rem 4rem 4rem 4rem !important; max-width: 100% !important; }
.section-title { margin-top: 3rem; font-size: 1rem; font-weight: 700; letter-spacing: 0.15em; text-transform: uppercase; color: #7f88ff; }
.card { background: #0f1024; border: 1px solid #1c1d45; border-radius: 18px; padding: 1.5rem; margin-top: 1rem; }
.pass { color:#90ff50; font-weight:600; }
.info { color:#7f88ff; font-weight:600; }
textarea { background:#0b0c20 !important; border:1px solid #20225a !important; color:#e0e3ff !important; border-radius:12px !important; }
</style>
""", unsafe_allow_html=True)

st.title("🔐 DocVault Enterprise")

# SECURITY DASHBOARD
st.markdown('<div class="section-title">Security Engine</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="card"><div class="pass">✔ File Type Verification</div>Validates magic bytes to prevent disguised malicious files.</div>', unsafe_allow_html=True)
    st.markdown('<div class="card"><div class="pass">✔ Malware Signature Scan</div>Detects suspicious executable and embedded script patterns.</div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="card"><div class="pass">✔ Corruption Detection</div>Attempts structured parsing before extraction.</div>', unsafe_allow_html=True)
    ocr_label = "Groq Vision AI" if groq_client else "Tesseract OCR"
    st.markdown(f'<div class="card"><div class="info">🔍 Image OCR via {ocr_label}</div>Extracts text from PNG, JPG, JPEG, BMP, TIFF images.</div>', unsafe_allow_html=True)

# REDACTION CONTROLS
st.markdown('<div class="section-title">Redaction Controls</div>', unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
with c1:
    redact_aadhaar = st.checkbox("Aadhaar Number")
    redact_pan     = st.checkbox("PAN Number")
    redact_ssn     = st.checkbox("SSN")
with c2:
    redact_mobile  = st.checkbox("Mobile Numbers")
    redact_dob     = st.checkbox("Date of Birth")
with c3:
    redact_names   = st.checkbox("Personal Names")

# UPLOAD
st.markdown('<div class="section-title">Upload Document</div>', unsafe_allow_html=True)
uploaded = st.file_uploader(
    "Supported: PDF, DOCX, XLSX, PPTX, PPT, TXT, PNG, JPG, JPEG, BMP, TIFF",
    type=["pdf","docx","xlsx","pptx","ppt","txt","png","jpg","jpeg","bmp","tiff"]
)

IMAGE_EXTS   = {"png","jpg","jpeg","bmp","tiff"}
MALWARE_SIGS = [b"cmd.exe", b"powershell", b"eval(", b"WScript"]
MAGIC_BYTES  = {
    "pdf":  b"%PDF",  "docx": b"PK",
    "xlsx": b"PK",    "pptx": b"PK",
    "ppt":  b"\xd0\xcf\x11\xe0",
    "png":  b"\x89PNG",
    "jpg":  b"\xff\xd8\xff",
    "jpeg": b"\xff\xd8\xff",
    "bmp":  b"BM",
}

def check_magic(fb, ext):
    return fb.startswith(MAGIC_BYTES[ext]) if ext in MAGIC_BYTES else True

def check_malware(fb):
    return not any(s in fb for s in MALWARE_SIGS)

def check_integrity(fb, ext):
    try:
        if ext == "pdf":
            import pypdf; pypdf.PdfReader(io.BytesIO(fb))
        elif ext == "docx":
            import docx; docx.Document(io.BytesIO(fb))
        elif ext == "xlsx":
            import openpyxl; openpyxl.load_workbook(io.BytesIO(fb))
        elif ext in ("pptx","ppt"):
            from pptx import Presentation; Presentation(io.BytesIO(fb))
        elif ext in IMAGE_EXTS:
            from PIL import Image
            Image.open(io.BytesIO(fb)).verify()
        return True
    except:
        return False

def ocr_image(fb):
    from PIL import Image

    # ── Groq Vision (fast + accurate) ──
    if groq_client:
        try:
            img = Image.open(io.BytesIO(fb)).convert("RGB")
            w, h = img.size
            if max(w, h) > 1200:
                scale = 1200 / max(w, h)
                img = img.resize((int(w*scale), int(h*scale)), Image.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=85)
            b64 = base64.b64encode(buf.getvalue()).decode()
            resp = groq_client.chat.completions.create(
                model="meta-llama/llama-4-scout-17b-16e-instruct",
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                        {"type": "text", "text": "Extract ALL text from this image exactly as it appears. Include names, numbers, dates, addresses. Output only the raw extracted text, nothing else."}
                    ]
                }],
                max_tokens=1000,
                temperature=0.0
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            st.warning(f"Groq Vision failed, falling back to Tesseract: {e}")

    # ── Tesseract fallback ──
    from PIL import ImageEnhance, ImageOps
    import pytesseract
    img = Image.open(io.BytesIO(fb))
    w, h = img.size
    if max(w, h) > 1600:
        scale = 1600 / max(w, h)
        img = img.resize((int(w*scale), int(h*scale)), Image.LANCZOS)
    img = img.convert("L")
    img = ImageOps.autocontrast(img)
    img = img.point(lambda x: 0 if x < 140 else 255, '1').convert("L")
    return pytesseract.image_to_string(img, lang="eng", config="--oem 3 --psm 4").strip()

def extract_text(fb, ext):
    if ext in IMAGE_EXTS:
        return ocr_image(fb)

    if ext == "pdf":
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(fb))
        text = "\n".join(p.extract_text() or "" for p in reader.pages)
        if not text.strip():
            try:
                import fitz
                import pytesseract
                from PIL import Image
                doc = fitz.open(stream=fb, filetype="pdf")
                pages = []
                for i, page in enumerate(doc):
                    pix = page.get_pixmap(dpi=150)
                    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples).convert("L")
                    pages.append(pytesseract.image_to_string(img, config="--oem 3 --psm 4"))
                text = "\n".join(pages)
            except Exception as e:
                st.warning(f"Scanned PDF OCR error: {e}")
        return text

    if ext == "docx":
        import docx
        return "\n".join(p.text for p in docx.Document(io.BytesIO(fb)).paragraphs)

    if ext == "xlsx":
        import openpyxl
        wb = openpyxl.load_workbook(io.BytesIO(fb), data_only=True)
        rows = []
        for ws in wb.worksheets:
            for row in ws.iter_rows(values_only=True):
                line = " | ".join(str(c) for c in row if c)
                if line: rows.append(line)
        return "\n".join(rows)

    if ext in ("pptx","ppt"):
        from pptx import Presentation
        lines = []
        for slide in Presentation(io.BytesIO(fb)).slides:
            for shape in slide.shapes:
                if hasattr(shape,"text") and shape.text.strip():
                    lines.append(shape.text.strip())
        return "\n".join(lines)

    if ext == "txt":
        return fb.decode("utf-8", errors="ignore")

    return None

def redact(text):
    count = 0
    rules = []
    if redact_aadhaar: rules.append((r'\b\d{4}\s?\d{4}\s?\d{4}\b','[REDACTED_AADHAAR]'))
    if redact_pan:     rules.append((r'\b[A-Z]{5}[0-9]{4}[A-Z]\b','[REDACTED_PAN]'))
    if redact_ssn:     rules.append((r'\b\d{3}-\d{2}-\d{4}\b','[REDACTED_SSN]'))
    if redact_mobile:  rules.append((r'\b(\+91[\s-]?)?[6-9]\d{9}\b','[REDACTED_PHONE]'))
    if redact_dob:     rules.append((r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}\b','[REDACTED_DOB]'))
    if redact_names:   rules.append((r'(Name|नाम)\s*[:\-]\s*[A-Za-z\s]{3,40}','Name: [REDACTED_NAME]'))
    for pattern, replacement in rules:
        text, n = re.subn(pattern, replacement, text)
        count += n
    return text, count

# PROCESS
if st.button("🔐 Secure Extract"):
    if not uploaded:
        st.warning("Upload a file first.")
    else:
        fb  = uploaded.read()
        ext = uploaded.name.split(".")[-1].lower()

        st.markdown("## 🔍 Security Scan Results")
        m_ok = check_magic(fb, ext)
        w_ok = check_malware(fb)
        i_ok = check_integrity(fb, ext)
        st.write("File Type Validation:", "✅" if m_ok else "❌")
        st.write("Malware Scan:",         "✅" if w_ok else "❌")
        st.write("Integrity Check:",      "✅" if i_ok else "❌")

        if not (m_ok and w_ok and i_ok):
            st.error("🚫 File blocked due to failed security checks.")
            st.stop()

        st.success("✅ File passed all security layers.")

        if ext in IMAGE_EXTS:
            st.info(f"🔍 Image detected — extracting text with {ocr_label}...")

        with st.spinner("Extracting text..."):
            try:
                text = extract_text(fb, ext)
            except Exception as e:
                st.error(f"Extraction error: {e}")
                st.stop()

        if not text or not text.strip():
            st.warning("No readable text found in this file.")
            st.stop()

        redacted_text, redaction_count = redact(text)
        st.markdown("## 📄 Extracted Output")
        if redaction_count > 0:
            st.success(f"🔒 {redaction_count} sensitive items redacted.")
        st.text_area("", redacted_text, height=500)
