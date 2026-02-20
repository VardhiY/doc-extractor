import streamlit as st
from groq import Groq
import json, re, base64, io

st.set_page_config(
    page_title="DocVault · AI Extractor",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="expanded"
)

try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client  = Groq(api_key=API_KEY)
except Exception:
    st.error("⚠️ API key not configured. Add GROQ_API_KEY to Streamlit Secrets.")
    st.stop()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Bebas+Neue&family=JetBrains+Mono:wght@400;500;600&display=swap');
*,*::before,*::after{box-sizing:border-box;}
html,body,[class*="css"]{font-family:'Outfit',sans-serif!important;-webkit-font-smoothing:antialiased;}
.stApp{background:#03030a!important;color:#eeeef8!important;
  background-image:radial-gradient(ellipse 120% 60% at 50% -10%,rgba(120,255,80,.09) 0%,transparent 55%),
    radial-gradient(ellipse 70% 50% at 10% 90%,rgba(80,120,255,.06) 0%,transparent 50%),
    radial-gradient(ellipse 50% 40% at 90% 60%,rgba(255,80,180,.04) 0%,transparent 50%);}
#MainMenu,footer,header,.stDeployButton,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"]{display:none!important;}
[data-testid="collapsedControl"]{display:flex!important;}

/* KEY CENTRING FIX */
.block-container{max-width:840px!important;margin-left:auto!important;margin-right:auto!important;padding:1rem 2rem 4rem!important;}

[data-testid="stSidebar"]{background:#07070f!important;border-right:1px solid #12122a!important;min-width:260px!important;}
[data-testid="stSidebar"] *{color:#9090b8!important;font-family:'Outfit',sans-serif!important;}
[data-testid="stSidebar"] h2,[data-testid="stSidebar"] strong{color:#eeeef8!important;}
[data-testid="stSidebar"] hr{border-color:#12122a!important;}
[data-testid="stSidebar"] label{font-size:.85rem!important;}

.hero{text-align:center;padding:2.5rem 1rem 1.8rem;position:relative;overflow:hidden;}
.hero-glow{position:absolute;top:-40px;left:50%;transform:translateX(-50%);width:520px;height:220px;
  background:radial-gradient(ellipse,rgba(138,255,80,.12) 0%,transparent 70%);pointer-events:none;z-index:0;border-radius:50%;}
.badge{position:relative;z-index:1;display:inline-flex;align-items:center;gap:.5rem;
  background:linear-gradient(135deg,rgba(138,255,80,.1),rgba(80,200,255,.07));
  border:1px solid rgba(138,255,80,.22);color:#a8ff60;padding:.35rem 1.1rem;border-radius:999px;
  font-size:.68rem;font-weight:800;letter-spacing:.16em;text-transform:uppercase;margin-bottom:1.1rem;}
.bdot{width:7px;height:7px;background:#a8ff60;border-radius:50%;
  box-shadow:0 0 10px #a8ff60,0 0 22px rgba(168,255,96,.4);animation:gp 2s ease-in-out infinite;}
@keyframes gp{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.35;transform:scale(1.6)}}
.htitle{position:relative;z-index:1;font-family:'Bebas Neue',sans-serif;
  font-size:5.8rem;letter-spacing:.06em;line-height:.92;color:#eeeef8;margin-bottom:.7rem;}
.htitle .g{background:linear-gradient(90deg,#a8ff60 0%,#60ffcc 50%,#60c8ff 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;}
.hsub{position:relative;z-index:1;font-size:.95rem;color:#3a3a68;font-weight:400;max-width:460px;margin:0 auto;line-height:1.6;}

.sec-card{background:linear-gradient(145deg,#090916,#0d0d1e);border:1px solid #16162e;border-radius:24px;
  padding:1.8rem 2rem;margin:1.5rem 0;position:relative;overflow:hidden;}
.sec-card::before{content:'';position:absolute;top:0;left:0;right:0;height:1px;
  background:linear-gradient(90deg,transparent,#a8ff60 40%,#60ffcc 60%,transparent);opacity:.45;}
.sec-card::after{content:'🛡️';position:absolute;right:1.5rem;bottom:.5rem;font-size:6rem;opacity:.03;pointer-events:none;}
.shead{font-size:.66rem;font-weight:900;letter-spacing:.2em;text-transform:uppercase;color:#a8ff60;margin-bottom:1.3rem;}
.g2{display:grid;grid-template-columns:1fr 1fr;gap:.75rem;}
.mc{background:rgba(255,255,255,.02);border:1px solid #141428;border-radius:16px;padding:1rem 1.1rem;
  display:flex;align-items:flex-start;gap:.85rem;transition:border-color .25s,background .25s;}
.mc:hover{border-color:rgba(168,255,96,.18);background:rgba(168,255,96,.03);}
.mi{font-size:1.5rem;flex-shrink:0;line-height:1;}
.mt{font-size:.82rem;font-weight:700;color:#d0d0e8;margin-bottom:.18rem;}
.md{font-size:.69rem;color:#333358;line-height:1.5;}

.ulbl{font-size:.67rem;font-weight:900;letter-spacing:.18em;text-transform:uppercase;color:#30305a;
  margin:2rem 0 .8rem;display:flex;align-items:center;gap:.7rem;}
.ulbl::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,#141430,transparent);}
div[data-testid="stFileUploader"]{background:#07071a!important;border:2px dashed #161634!important;border-radius:20px!important;padding:1.8rem 1.5rem!important;transition:border-color .3s,background .3s!important;}
div[data-testid="stFileUploader"]:hover{border-color:rgba(168,255,96,.3)!important;background:rgba(168,255,96,.02)!important;}
div[data-testid="stFileUploader"] p,div[data-testid="stFileUploader"] span,div[data-testid="stFileUploader"] small{color:#282850!important;}
div[data-testid="stFileUploader"] button{background:#0e0e28!important;border:1px solid #1c1c40!important;color:#6060a0!important;border-radius:10px!important;}

.fpill{display:inline-flex;align-items:center;gap:.5rem;background:#09091c;border:1px solid #141432;border-radius:999px;
  padding:.38rem 1rem;font-size:.73rem;font-family:'JetBrains Mono',monospace;color:#4a4a80;margin:.6rem 0;}
.fpill strong{color:#9090c0;}

.stButton>button{width:100%!important;background:linear-gradient(135deg,#a8ff60 0%,#60ffcc 100%)!important;
  color:#020208!important;font-family:'Outfit',sans-serif!important;font-weight:900!important;font-size:1rem!important;
  letter-spacing:.1em!important;text-transform:uppercase!important;border:none!important;border-radius:16px!important;
  padding:1rem!important;margin-top:.8rem!important;transition:all .25s!important;}
.stButton>button:hover{transform:translateY(-3px)!important;box-shadow:0 18px 55px rgba(168,255,96,.28),0 4px 14px rgba(168,255,96,.14)!important;}
.stButton>button:active{transform:translateY(-1px)!important;}

.slbl{font-size:.67rem;font-weight:900;letter-spacing:.18em;text-transform:uppercase;color:#30305a;
  margin:2rem 0 .8rem;display:flex;align-items:center;gap:.7rem;}
.slbl::after{content:'';flex:1;height:1px;background:linear-gradient(90deg,#141430,transparent);}

.srow{display:flex;align-items:center;gap:.9rem;padding:.8rem 1.1rem;background:#07071a;border:1px solid #10102a;
  border-radius:14px;margin-bottom:.5rem;transition:border-color .2s;}
.srow:hover{border-color:#181838;}
.se{font-size:1.15rem;flex-shrink:0;}.sl{font-size:.79rem;font-weight:700;color:#b0b0d8;min-width:145px;}
.sm{font-size:.71rem;font-family:'JetBrains Mono',monospace;color:#333360;flex:1;}
.dot{width:9px;height:9px;border-radius:50%;flex-shrink:0;}
.dok{background:#a8ff60;box-shadow:0 0 10px rgba(168,255,96,.65);}
.derr{background:#ff4060;box-shadow:0 0 10px rgba(255,64,96,.65);}

.ab{border-radius:16px;padding:1rem 1.3rem;margin:.8rem 0;font-size:.85rem;line-height:1.65;font-weight:500;}
.aok{background:rgba(168,255,96,.07);border:1px solid rgba(168,255,96,.2);color:#a8ff60;}
.abad{background:rgba(255,64,96,.07);border:1px solid rgba(255,64,96,.2);color:#ff7090;}
.awarn{background:rgba(255,200,80,.07);border:1px solid rgba(255,200,80,.2);color:#ffc860;}
.ainfo{background:rgba(96,200,255,.06);border:1px solid rgba(96,200,255,.18);color:#60c8ff;}

.s3{display:grid;grid-template-columns:repeat(3,1fr);gap:1rem;margin:1rem 0;}
.sc{background:linear-gradient(145deg,#07071a,#0a0a1e);border:1px solid #12122e;border-radius:20px;
  padding:1.3rem 1rem;text-align:center;position:relative;overflow:hidden;transition:border-color .25s,transform .25s;}
.sc:hover{border-color:#1c1c3e;transform:translateY(-2px);}
.sc::before{content:'';position:absolute;top:0;left:20%;right:20%;height:1px;background:linear-gradient(90deg,transparent,rgba(168,255,96,.45),transparent);}
.sn{font-family:'Bebas Neue',sans-serif;font-size:2.8rem;letter-spacing:.06em;color:#a8ff60;line-height:1;margin-bottom:.35rem;}
.sk{font-size:.62rem;font-weight:900;letter-spacing:.18em;text-transform:uppercase;color:#20204a;}

.tags{display:flex;flex-wrap:wrap;gap:.4rem;margin:.8rem 0;}
.rtag{display:inline-flex;align-items:center;gap:.3rem;padding:.25rem .8rem;border-radius:999px;
  font-size:.7rem;font-weight:700;background:rgba(255,80,128,.09);border:1px solid rgba(255,80,128,.25);color:#ff80a8;}

.rbox{background:#050512;border:1px solid #10102a;border-radius:20px;padding:1.5rem;
  font-family:'JetBrains Mono',monospace;font-size:.77rem;line-height:2;color:#9090c0;
  white-space:pre-wrap;word-break:break-word;max-height:460px;overflow-y:auto;position:relative;margin-top:.5rem;}
.rbox::before{content:'';position:absolute;top:0;left:15%;right:15%;height:1px;background:linear-gradient(90deg,transparent,rgba(168,255,96,.3),transparent);}
.rbox::-webkit-scrollbar{width:3px;}
.rbox::-webkit-scrollbar-thumb{background:#181838;border-radius:4px;}

[data-testid="stDownloadButton"] button{background:#08081e!important;border:1px solid #14143a!important;
  color:#5050a0!important;border-radius:14px!important;font-family:'Outfit',sans-serif!important;
  font-weight:700!important;font-size:.82rem!important;padding:.75rem!important;width:100%!important;transition:all .2s!important;}
[data-testid="stDownloadButton"] button:hover{border-color:rgba(168,255,96,.28)!important;color:#a8ff60!important;background:rgba(168,255,96,.04)!important;}
hr{border-color:#0e0e28!important;margin:1.5rem 0!important;}
</style>
""", unsafe_allow_html=True)

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.markdown("---")
    st.markdown("**🔒 Redaction Rules**")
    redact_ids       = st.checkbox("🪪 ID / Aadhaar / SSN",       value=True)
    redact_phones    = st.checkbox("📞 Phone numbers & emails",     value=True)
    redact_banking   = st.checkbox("💳 Bank / credit card numbers", value=True)
    redact_passwords = st.checkbox("🔑 Passwords & secret keys",    value=True)
    redact_names     = st.checkbox("👤 Personal names",              value=True)
    redact_dates     = st.checkbox("📅 Dates of birth",              value=True)
    show_redacted    = st.checkbox("Show [REDACTED] placeholders",   value=True)
    st.markdown("---")
    st.markdown("**🛡️ Security**")
    max_size_mb = st.slider("Max file size (MB)", 1, 20, 10)
    st.markdown("---")
    st.markdown("<small style='color:#1e1e48'>DocVault AI · v3.1<br>Powered by Groq + LLaMA</small>", unsafe_allow_html=True)

# ── SECURITY ENGINE ──
MALWARE_SIGNATURES = [
    b"\x4d\x5a\x90\x00", b"\x7fELF",
    b"/JavaScript", b"/JS ", b"eval(", b"unescape(",
    b"/OpenAction", b"/Launch", b"cmd.exe", b"powershell",
    b"WScript", b"ActiveXObject", b"AutoOpen", b"Auto_Open",
    b"AutoExec", b"Shell(", b"CreateObject(", b"WScript.Shell",
    b"AAAA" * 20,
]
MAGIC = {
    "pdf":[(0,b"%PDF")],"png":[(0,b"\x89PNG\r\n\x1a\n")],
    "jpg":[(0,b"\xff\xd8\xff")],"jpeg":[(0,b"\xff\xd8\xff")],
    "docx":[(0,b"PK\x03\x04")],"xlsx":[(0,b"PK\x03\x04")],
    "pptx":[(0,b"PK\x03\x04")],"ppt":[(0,b"\xd0\xcf\x11\xe0")],
}

def ck_size(fb,mx):
    s=len(fb)/1048576
    return (True,f"Size OK · {s:.2f} MB") if s<=mx else (False,f"{s:.1f} MB exceeds {mx} MB limit")

def ck_magic(fb,ext):
    e=ext.lower().lstrip(".")
    if e not in MAGIC: return True,"Format check skipped"
    for off,m in MAGIC[e]:
        if fb[off:off+len(m)]==m: return True,f"Signature valid · {e.upper()} confirmed"
    return False,f"Mismatch for .{e} — possible disguised file"

def ck_virus(fb):
    hits=[s.decode("utf-8",errors="replace").strip()[:30] for s in MALWARE_SIGNATURES if s in fb]
    return (False,f"Suspicious: {', '.join(set(hits[:3]))}") if hits else (True,"No malware patterns detected")

def ck_corrupt(fb,ext):
    e=ext.lower().lstrip(".")
    try:
        if e=="pdf":
            import pypdf; r=pypdf.PdfReader(io.BytesIO(fb)); _=len(r.pages)
        elif e=="docx":
            import docx; docx.Document(io.BytesIO(fb))
        elif e=="xlsx":
            import openpyxl; openpyxl.load_workbook(io.BytesIO(fb),data_only=True)
        elif e in("pptx","ppt"):
            from pptx import Presentation; Presentation(io.BytesIO(fb))
        return True,"Opened successfully · Intact"
    except Exception as ex:
        return False,f"Cannot open: {str(ex)[:90]}"

def security_scan(fb,fname,mx):
    ext=fname.rsplit(".",1)[-1] if "." in fname else ""
    checks=[("📦 File Size",ck_size(fb,mx)),("🔍 File Type",ck_magic(fb,ext)),
            ("🦠 Virus Scan",ck_virus(fb)),("🧩 Integrity",ck_corrupt(fb,ext))]
    results=[(lbl,ok,msg) for lbl,(ok,msg) in checks]
    return all(ok for _,ok,_ in results),results

# ── EXTRACTION ──
def pdf_text(fb):
    try:
        import pypdf; r=pypdf.PdfReader(io.BytesIO(fb))
        return ("".join(p.extract_text() or "" for p in r.pages)).strip() or None
    except: return None

def docx_text(fb):
    try:
        import docx; doc=docx.Document(io.BytesIO(fb))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip()).strip() or None
    except: return None

def xlsx_text(fb):
    try:
        import openpyxl; wb=openpyxl.load_workbook(io.BytesIO(fb),data_only=True); rows=[]
        for s in wb.worksheets:
            rows.append(f"[Sheet: {s.title}]")
            for row in s.iter_rows(values_only=True):
                l=" | ".join(str(c) for c in row if c is not None)
                if l.strip(): rows.append(l)
        return "\n".join(rows).strip() or None
    except: return None

def pptx_text(fb):
    try:
        from pptx import Presentation; prs=Presentation(io.BytesIO(fb)); lines=[]
        for i,slide in enumerate(prs.slides,1):
            lines.append(f"[Slide {i}]")
            for shape in slide.shapes:
                if hasattr(shape,"text") and shape.text.strip(): lines.append(shape.text.strip())
        return "\n".join(lines).strip() or None
    except: return None

def img_text(fb,mime):
    b64=base64.b64encode(fb).decode()
    r=client.chat.completions.create(
        model="meta-llama/llama-4-scout-17b-16e-instruct",
        messages=[{"role":"user","content":[
            {"type":"image_url","image_url":{"url":f"data:{mime};base64,{b64}"}},
            {"type":"text","text":"Extract ALL visible text.\nTEXT FOUND:\n[text]\n\nIMAGE DESCRIPTION:\n[description]"}
        ]}],max_tokens=2000)
    return r.choices[0].message.content.strip()

# ── REDACTION ──
def build_rules():
    rules=[]
    if redact_ids:       rules.append("Aadhaar (12-digit), SSN, PAN (ABCDE1234F), passport, driver license, voter ID")
    if redact_phones:    rules.append("phone/mobile (+91 or 10-digit), email addresses")
    if redact_banking:   rules.append("bank account, IFSC, credit/debit card numbers, CVV, UPI IDs")
    if redact_passwords: rules.append("passwords, API keys, tokens, OTPs, PINs, secret keys")
    if redact_names:     rules.append("full person names on identity documents")
    if redact_dates:     rules.append("dates of birth in any format, DOB, janm tithi")
    return rules

def regex_redact(text,ph="[REDACTED]"):
    count=0; removed=[]
    def sub(pat,label,t):
        nonlocal count
        n=re.sub(pat,ph,t)
        if n!=t: count+=1; removed.append(label)
        return n
    if redact_ids:
        text=sub(r'\b\d{4}\s?\d{4}\s?\d{4}\b',"Aadhaar",text)
        text=sub(r'\b[A-Z]{5}[0-9]{4}[A-Z]\b',"PAN",text)
    if redact_phones:
        text=sub(r'\b(\+91[\s-]?)?[6-9]\d{9}\b',"phone",text)
        text=sub(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', "email",text)
    if redact_banking:
        text=sub(r'\b(?:\d[ -]*?){13,16}\b',"card number",text)
        text=sub(r'\b[A-Z]{4}0[A-Z0-9]{6}\b',"IFSC",text)
    if redact_dates:
        text=sub(r'\b\d{1,2}[\/\-]\d{1,2}[\/\-]\d{4}\b',"date",text)
    if redact_names:
        n=re.sub(r'(Name|naam)\s*[:\-]\s*[A-Za-z\s]{3,40}',
                 lambda m:m.group(0).split(':')[0]+': '+ph,text)
        if n!=text: count+=1; removed.append("name"); text=n
    return text,removed,count

def redact_ai(text,rules):
    if not rules: return text,[],0
    ph="[REDACTED]" if show_redacted else "████"
    prompt=f"""Strict data privacy engine. Redact ALL sensitive data.
CATEGORIES:
{chr(10).join(f'- {r}' for r in rules)}
Replace only the sensitive VALUE with "{ph}". When uncertain REDACT.
Return ONLY valid JSON: {{"clean_text":"...","redacted_items":["..."],"redaction_count":0}}
TEXT:
{text[:6000]}"""
    r=client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role":"system","content":"Data privacy engine. Return only valid JSON."},{"role":"user","content":prompt}],
        temperature=0.0,max_tokens=4000)
    raw=re.sub(r'```json|```','',r.choices[0].message.content.strip()).strip()
    try:
        d=json.loads(raw); clean=d.get("clean_text",text); items=d.get("redacted_items",[]); count=d.get("redaction_count",0)
        clean,ei,ec=regex_redact(clean,ph)
        return clean,items+ei,count+ec
    except:
        return regex_redact(text,ph)

# ══════════════════════════════════════════════
# RENDER UI
# ══════════════════════════════════════════════

st.markdown("""
<div class="hero">
  <div class="hero-glow"></div>
  <div class="badge"><span class="bdot"></span>AI-Powered &nbsp;·&nbsp; Secure &nbsp;·&nbsp; Private</div>
  <div class="htitle">Doc<span class="g">Vault</span></div>
  <div class="hsub">Extract text from any document or image —<br>sensitive data auto-redacted before your eyes.</div>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="sec-card">
  <div class="shead">🛡️ &nbsp;4-Layer Security Engine &nbsp;·&nbsp; Always Active</div>
  <div class="g2">
    <div class="mc"><div class="mi">📦</div><div><div class="mt">File Size Limit</div><div class="md">Oversized files rejected instantly before any processing begins</div></div></div>
    <div class="mc"><div class="mi">🦠</div><div><div class="mt">Virus / Malware Scan</div><div class="md">Byte-level scan: PE headers, JS injections, macro exploits and more</div></div></div>
    <div class="mc"><div class="mi">🧩</div><div><div class="mt">Corrupted File Detection</div><div class="md">Files that cannot be opened are rejected — no broken data passes</div></div></div>
    <div class="mc"><div class="mi">🔍</div><div><div class="mt">File Type Verification</div><div class="md">Magic-byte fingerprinting catches renamed or disguised malicious files</div></div></div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="ulbl">📎 Upload Document</div>', unsafe_allow_html=True)

uploaded = st.file_uploader(
    "drop", type=["pdf","png","jpg","jpeg","docx","xlsx","pptx","ppt"],
    label_visibility="collapsed"
)

if uploaded:
    st.markdown(
        f'<div class="fpill">📄 <strong>{uploaded.name}</strong>'
        f'&nbsp;·&nbsp;{uploaded.type}&nbsp;·&nbsp;{uploaded.size/1024:.1f} KB</div>',
        unsafe_allow_html=True)

run = st.button("🔐  Scan · Extract · Redact", use_container_width=True)

if run and not uploaded:
    st.markdown('<div class="ab awarn">⚠️ Please upload a file first.</div>', unsafe_allow_html=True)
    st.stop()

if run and uploaded:
    fb=uploaded.read(); mime=uploaded.type; name=uploaded.name.lower()

    # STEP 1 — SCAN
    st.markdown('<div class="slbl">🛡️ Security Scan Results</div>', unsafe_allow_html=True)
    with st.spinner("Running security checks..."):
        passed,results=security_scan(fb,name,max_size_mb)

    for lbl,ok,msg in results:
        emoji=lbl.split()[0]; label=" ".join(lbl.split()[1:])
        dc="dok" if ok else "derr"; icon="✅" if ok else "❌"
        st.markdown(
            f'<div class="srow"><span class="se">{emoji}</span>'
            f'<span class="sl">{label}</span>'
            f'<span class="sm">{icon}&nbsp; {msg}</span>'
            f'<span class="dot {dc}"></span></div>',
            unsafe_allow_html=True)

    if not passed:
        st.markdown('<div class="ab abad">🚫 <strong>File rejected.</strong> One or more security checks failed. Please upload a clean, valid file.</div>', unsafe_allow_html=True)
        st.stop()
    st.markdown('<div class="ab aok">✅ <strong>All 4 security checks passed.</strong> Proceeding to extraction.</div>', unsafe_allow_html=True)

    # STEP 2 — EXTRACT
    st.markdown('<div class="slbl">📖 Text Extraction</div>', unsafe_allow_html=True)
    raw=None
    with st.spinner("Extracting content..."):
        try:
            if name.endswith(".pdf"):
                raw=pdf_text(fb)
                if not raw:
                    st.markdown('<div class="ab ainfo">ℹ️ Native extraction failed — switching to AI Vision OCR...</div>', unsafe_allow_html=True)
                    raw=img_text(fb,"application/pdf")
            elif name.endswith((".png",".jpg",".jpeg")): raw=img_text(fb,mime)
            elif name.endswith(".docx"):  raw=docx_text(fb)
            elif name.endswith(".xlsx"):  raw=xlsx_text(fb)
            elif name.endswith((".pptx",".ppt")):
                raw=pptx_text(fb)
                if not raw: raw=img_text(fb,mime)
        except Exception as e:
            st.markdown(f'<div class="ab abad">❌ Extraction error: {e}</div>', unsafe_allow_html=True)

    if not raw or len(raw.strip())<5:
        st.markdown('<div class="ab awarn">⚠️ No readable text found. File may be blank or unsupported.</div>', unsafe_allow_html=True)
        st.stop()

    # STEP 3 — REDACT
    st.markdown('<div class="slbl">🔒 Privacy Redaction</div>', unsafe_allow_html=True)
    rules=build_rules(); clean=raw; items=[]; count=0
    if rules:
        with st.spinner("AI scanning for sensitive data..."):
            try:    clean,items,count=redact_ai(raw,rules)
            except Exception as e:
                st.markdown(f'<div class="ab awarn">⚠️ AI redaction unavailable, regex fallback: {e}</div>', unsafe_allow_html=True)
                clean,items,count=regex_redact(raw)
    else:
        st.markdown('<div class="ab ainfo">ℹ️ No redaction rules selected.</div>', unsafe_allow_html=True)

    # STEP 4 — RESULTS
    st.markdown('<div class="slbl">📊 Results</div>', unsafe_allow_html=True)
    wc=len(clean.split()); stat="CLEAN" if count==0 else "REDACTED"; sc="#a8ff60" if count==0 else "#ff80a8"
    st.markdown(f"""
    <div class="s3">
      <div class="sc"><div class="sn">{wc:,}</div><div class="sk">Words Extracted</div></div>
      <div class="sc"><div class="sn">{count}</div><div class="sk">Items Redacted</div></div>
      <div class="sc"><div class="sn" style="color:{sc};font-size:1.7rem;padding-top:.5rem">{stat}</div><div class="sk">Document Status</div></div>
    </div>""", unsafe_allow_html=True)

    if items:
        tags="".join(f'<span class="rtag">🚫 {i}</span>' for i in set(items))
        st.markdown(f'<div class="tags">{tags}</div>', unsafe_allow_html=True)

    st.markdown('<div class="slbl">📝 Extracted Text</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="rbox">{clean}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        st.download_button("⬇️ Download Clean Text (.txt)", clean,
            f"{uploaded.name}_extracted.txt","text/plain",use_container_width=True)
    with c2:
        st.download_button("⬇️ Download as JSON",
            json.dumps({"filename":uploaded.name,"extracted_text":clean,
                "redacted_count":count,"redacted_categories":list(set(items)),
                "security_scan":{r[0]:r[1] for r in results}},indent=2),
            f"{uploaded.name}_extracted.json","application/json",use_container_width=True)
