import streamlit as st
from groq import Groq
import os, io, re, urllib.request
import streamlit.components.v1 as components

st.set_page_config(page_title="InfographAI", page_icon="🎨", layout="wide")

api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    try: api_key = st.secrets["GROQ_API_KEY"]
    except: pass
if not api_key:
    st.error("⚠️ GROQ_API_KEY missing.")
    st.stop()

client = Groq(api_key=api_key)

# ══════════════════════════════════════════════════════════
# STYLING — LEXIS AI architecture, green palette
# ══════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; }

/* ══ BASE ══ */
.stApp {
    background: #f0f7f2 !important;
    color: #1a2e22 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 15px !important;
}

/* Soft green gradient mesh */
.stApp::before {
    content: '';
    position: fixed; inset: 0;
    background:
        radial-gradient(ellipse 1000px 700px at 20%   0%,  rgba(167,243,208,0.55) 0%, transparent 60%),
        radial-gradient(ellipse  800px 600px at 85%  10%,  rgba(186,254,222,0.42) 0%, transparent 60%),
        radial-gradient(ellipse  700px 600px at 10%  90%,  rgba(167,243,208,0.35) 0%, transparent 60%),
        radial-gradient(ellipse  900px 500px at 90%  95%,  rgba(199,254,215,0.28) 0%, transparent 60%),
        radial-gradient(ellipse  500px 400px at 50%  50%,  rgba(212,254,226,0.20) 0%, transparent 55%);
    pointer-events: none; z-index: 0;
}

.block-container {
    padding-top: 0 !important;
    padding-bottom: 3rem !important;
    max-width: 1260px !important;
    position: relative; z-index: 1;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: #a7f3d0; border-radius: 10px; }

/* ══ NAV ══ */
.ig-nav {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1.1rem 0;
    border-bottom: 1px solid rgba(0,0,0,0.06);
    background: rgba(240,247,242,0.75);
    backdrop-filter: blur(12px);
    margin-bottom: 0;
}
.ig-logo-wrap { display: flex; align-items: center; gap: 0.5rem; }
.ig-logo-icon {
    width: 30px; height: 30px;
    background: linear-gradient(135deg, #10b981, #34d399);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.88rem;
    box-shadow: 0 3px 10px rgba(16,185,129,0.35);
}
.ig-logo-text {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 1.05rem; font-weight: 800; color: #1a2e22; letter-spacing: -0.2px;
}
.ig-logo-text span {
    background: linear-gradient(90deg, #10b981, #34d399);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.ig-nav-badge {
    font-family: 'DM Mono', monospace;
    font-size: 0.62rem; letter-spacing: 0.18em; text-transform: uppercase;
    color: #4a7c5e; border: 1px solid rgba(16,185,129,0.2);
    background: rgba(255,255,255,0.8);
    padding: 0.28rem 0.9rem; border-radius: 100px;
}
.ig-status {
    display: flex; align-items: center; gap: 0.4rem;
    font-size: 0.78rem; font-weight: 500; color: #4a7c5e;
}
.ig-status-dot {
    width: 7px; height: 7px; background: #10b981; border-radius: 50%;
    box-shadow: 0 0 7px rgba(16,185,129,0.6); animation: sDot 2.5s ease-in-out infinite;
}
@keyframes sDot { 0%,100%{opacity:1;} 50%{opacity:0.35;} }

/* nav format pills */
.ig-nav-pills { display: flex; align-items: center; gap: 0.35rem; }
.ig-pill {
    font-family: 'DM Mono', monospace;
    font-size: 0.6rem; letter-spacing: 0.1em; text-transform: uppercase;
    color: #4a7c5e; border: 1px solid rgba(16,185,129,0.18);
    background: rgba(255,255,255,0.7);
    padding: 0.22rem 0.65rem; border-radius: 100px;
    font-weight: 600;
}

/* ══ HERO ══ */
.ig-hero { text-align: center; padding: 2.8rem 0 2.2rem; }
.ig-hero-tag {
    display: inline-flex; align-items: center; gap: 0.4rem;
    background: rgba(255,255,255,0.85); border: 1px solid rgba(16,185,129,0.22);
    border-radius: 100px; padding: 0.3rem 0.95rem;
    font-size: 0.76rem; font-weight: 600; color: #0d7c57;
    margin-bottom: 1.2rem; box-shadow: 0 2px 10px rgba(16,185,129,0.1);
}
.ig-hero-tag::before {
    content: ''; width: 6px; height: 6px;
    background: linear-gradient(135deg, #10b981, #34d399);
    border-radius: 50%; flex-shrink: 0; animation: tagPulse 2.2s ease-in-out infinite;
}
@keyframes tagPulse { 0%,100%{opacity:1;transform:scale(1);} 50%{opacity:0.4;transform:scale(0.8);} }
.ig-h1 {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: clamp(2.2rem, 4.5vw, 3.5rem); font-weight: 800;
    line-height: 1.1; letter-spacing: -1px; color: #0f1f16; margin-bottom: 0;
}
.ig-h1-accent {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: clamp(2.2rem, 4.5vw, 3.5rem); font-weight: 800;
    line-height: 1.1; letter-spacing: -1px;
    background: linear-gradient(90deg, #10b981, #34d399, #6ee7b7);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text; display: block; margin-bottom: 0.9rem;
}
.ig-hero-sub {
    font-size: 0.97rem; color: #4a7c5e;
    max-width: 450px; margin: 0 auto; line-height: 1.7;
}

/* ══ CARD ══ */
.ig-card {
    background: rgba(255,255,255,0.82);
    border: 1px solid rgba(255,255,255,0.9);
    border-radius: 16px; padding: 1.5rem 1.5rem 1rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 24px rgba(16,185,129,0.07), 0 1px 4px rgba(0,0,0,0.04);
    backdrop-filter: blur(12px);
}

/* ══ SECTION LABEL ══ */
.ig-sec-label {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.68rem; font-weight: 700; letter-spacing: 0.1em;
    text-transform: uppercase; color: #4a7c5e;
    margin-bottom: 0.9rem; display: flex; align-items: center; gap: 0.5rem;
}
.ig-sec-label::after { content:''; flex:1; height:1px; background:rgba(16,185,129,0.15); }

/* ══ TABS ══ */
div[data-baseweb="tab-list"] {
    background: #f0fdf4 !important; border-radius: 10px !important;
    padding: 4px !important; border: 1px solid rgba(16,185,129,0.18) !important;
    gap: 2px !important; margin-bottom: 1rem !important; width: fit-content !important;
}
div[data-baseweb="tab"] {
    border-radius: 7px !important; color: #6b9e80 !important;
    font-weight: 600 !important; font-family: 'DM Sans', sans-serif !important;
    font-size: 0.88rem !important; padding: 0.4rem 1rem !important; transition: all 0.18s !important;
}
div[aria-selected="true"] {
    background: linear-gradient(135deg, #10b981, #34d399) !important;
    color: white !important; box-shadow: 0 2px 10px rgba(16,185,129,0.32) !important;
}
div[data-baseweb="tab-panel"] { background: transparent !important; padding: 0 !important; }

/* ══ INPUTS ══ */
textarea, .stTextInput input {
    background: #ffffff !important; border: 1.5px solid rgba(16,185,129,0.2) !important;
    border-radius: 10px !important; color: #1a2e22 !important;
    font-family: 'DM Sans', sans-serif !important; font-size: 0.95rem !important;
    padding: 0.85rem 1rem !important; line-height: 1.6 !important;
    transition: all 0.2s !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) inset !important;
}
textarea:focus, .stTextInput input:focus {
    border-color: #10b981 !important;
    box-shadow: 0 0 0 3px rgba(16,185,129,0.1) !important; outline: none !important;
}
textarea::placeholder, .stTextInput input::placeholder { color: #a0c4b0 !important; }

/* ══ SELECT ══ */
div[data-testid="stSelectbox"] label { display: none !important; }
div[data-baseweb="select"] > div {
    background: #ffffff !important; border: 1.5px solid rgba(16,185,129,0.2) !important;
    border-radius: 10px !important; color: #1a2e22 !important;
}
div[data-baseweb="select"] > div:focus-within {
    border-color: #10b981 !important;
    box-shadow: 0 0 0 3px rgba(16,185,129,0.1) !important;
}
[data-baseweb="popover"] > div {
    background: #ffffff !important; border: 1px solid rgba(16,185,129,0.18) !important;
    border-radius: 10px !important;
}
[role="option"]:hover { background: rgba(16,185,129,0.08) !important; }

/* ══ FILE UPLOADER ══ */
[data-testid="stFileUploader"] section {
    background: rgba(240,253,244,0.7) !important;
    border: 2px dashed rgba(16,185,129,0.28) !important;
    border-radius: 12px !important; transition: all 0.2s !important;
}
[data-testid="stFileUploader"] section:hover {
    border-color: rgba(16,185,129,0.55) !important;
    background: rgba(240,253,244,0.9) !important;
}
[data-testid="stFileUploader"] section p { color: #6b9e80 !important; }

/* ══ PRIMARY BUTTON ══ */
.stButton > button {
    width: 100% !important;
    background: linear-gradient(135deg, #10b981, #059669) !important;
    border: none !important; border-radius: 11px !important; color: #fff !important;
    font-family: 'Plus Jakarta Sans', sans-serif !important; font-weight: 700 !important;
    font-size: 1rem !important; padding: 0.85rem 1.5rem !important;
    margin-top: 0.5rem !important; transition: all 0.2s !important;
    box-shadow: 0 4px 15px rgba(16,185,129,0.35) !important;
}
.stButton > button:hover {
    opacity: 0.9 !important; transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(16,185,129,0.45) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ══ DOWNLOAD BUTTON ══ */
.stDownloadButton > button {
    background: #ffffff !important; border: 1.5px solid rgba(16,185,129,0.25) !important;
    color: #0d7c57 !important; font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important; border-radius: 9px !important;
    padding: 0.48rem 1rem !important; font-size: 0.85rem !important;
    margin-top: 0 !important; transition: all 0.18s !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05) !important;
}
.stDownloadButton > button:hover {
    border-color: #10b981 !important; color: #059669 !important;
    background: #f0fdf4 !important;
}

/* ══ SECURITY BADGES ══ */
.sec-badge-row {
    display: flex; align-items: center; justify-content: space-between;
    background: #f8fffe; border: 1px solid rgba(16,185,129,0.12);
    border-radius: 10px; padding: 0.65rem 1rem; margin-bottom: 0.42rem;
    transition: background 0.15s;
}
.sec-badge-row:hover { background: #f0fdf4; }
.sec-badge-label { font-size: 0.88rem; font-weight: 600; color: #1a2e22; }
.sec-badge-pass {
    display: inline-flex; align-items: center; gap: 0.28rem;
    font-size: 0.74rem; font-weight: 700; color: #059669;
    background: rgba(16,185,129,0.12); border: 1px solid rgba(16,185,129,0.28);
    border-radius: 6px; padding: 0.15rem 0.5rem;
}
.sec-badge-fail {
    display: inline-flex; align-items: center; gap: 0.28rem;
    font-size: 0.74rem; font-weight: 700; color: #dc2626;
    background: rgba(220,38,38,0.09); border: 1px solid rgba(220,38,38,0.22);
    border-radius: 6px; padding: 0.15rem 0.5rem;
}
.sec-badge-warn {
    display: inline-flex; align-items: center; gap: 0.28rem;
    font-size: 0.74rem; font-weight: 700; color: #b45309;
    background: rgba(245,158,11,0.10); border: 1px solid rgba(245,158,11,0.25);
    border-radius: 6px; padding: 0.15rem 0.5rem;
}

/* ══ SCORE DISPLAY ══ */
.score-row {
    display: flex; align-items: center; gap: 1.4rem;
    background: #f0fdf4; border: 1px solid rgba(16,185,129,0.18);
    border-radius: 12px; padding: 0.9rem 1.1rem; margin-top: 0.5rem;
}
.score-num {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 2rem; font-weight: 800; line-height: 1;
}
.score-lbl { font-size: 0.6rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #6b9e80; margin-bottom: 0.12rem; }
.score-bar-bg { height: 7px; background: rgba(16,185,129,0.12); border-radius: 100px; overflow: hidden; flex: 1; }
.score-bar-fill { height: 100%; border-radius: 100px; }

/* ══ CANVAS PANEL ══ */
.canvas-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 1.1rem 1.4rem;
    background: rgba(255,255,255,0.88);
    border: 1px solid rgba(16,185,129,0.15);
    border-radius: 16px 16px 0 0;
    box-shadow: 0 2px 8px rgba(16,185,129,0.06);
}
.canvas-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 0.95rem; font-weight: 700; color: #0f1f16;
    display: flex; align-items: center; gap: 0.5rem;
}
.canvas-body {
    border: 1px solid rgba(16,185,129,0.12); border-top: none;
    border-radius: 0 0 16px 16px; overflow: hidden;
    box-shadow: 0 4px 20px rgba(16,185,129,0.07);
}

/* ══ CANVAS BADGE ══ */
.cbadge-ready {
    display: inline-flex; align-items: center; gap: 0.35rem;
    font-size: 0.76rem; font-weight: 700; color: #059669;
    background: rgba(16,185,129,0.1); border: 1px solid rgba(16,185,129,0.25);
    border-radius: 100px; padding: 0.25rem 0.75rem;
}
.cbadge-wait {
    display: inline-flex; align-items: center; gap: 0.35rem;
    font-size: 0.76rem; font-weight: 700; color: #b45309;
    background: rgba(245,158,11,0.08); border: 1px solid rgba(245,158,11,0.22);
    border-radius: 100px; padding: 0.25rem 0.75rem;
}
.cbadge-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }

/* ══ EMPTY STATE ══ */
.empty-state {
    min-height: 560px; background: #f8fffc;
    display: flex; align-items: center; justify-content: center;
    position: relative; overflow: hidden;
}
.empty-grid {
    position: absolute; inset: 0; pointer-events: none;
    background-image:
        linear-gradient(rgba(16,185,129,0.06) 1px, transparent 1px),
        linear-gradient(90deg, rgba(16,185,129,0.06) 1px, transparent 1px);
    background-size: 38px 38px;
}
.empty-inner { position: relative; z-index: 1; text-align: center; padding: 2rem; }
.empty-emoji { font-size: 3.8rem; display: block; margin-bottom: 1.1rem; animation: float 3s ease-in-out infinite; }
@keyframes float { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)} }
.empty-h { font-family:'Plus Jakarta Sans',sans-serif; font-size:1.45rem; font-weight:800; color:#c8e6d4; margin-bottom:0.4rem; }
.empty-p { font-size:0.9rem; color:#c0deca; line-height:1.7; }
.steps { display:flex; gap:0.8rem; margin-top:1.8rem; justify-content:center; flex-wrap:wrap; }
.step {
    background: rgba(255,255,255,0.85); border: 1px solid rgba(16,185,129,0.15);
    border-radius: 10px; padding: 0.85rem 1.1rem; text-align: center;
    box-shadow: 0 2px 8px rgba(16,185,129,0.07);
}
.step-n { font-size:0.65rem; color:#10b981; font-weight:700; font-family:'DM Mono',monospace; letter-spacing:0.1em; margin-bottom:0.25rem; }
.step-t { font-size:0.85rem; color:#1a2e22; font-weight:700; font-family:'Plus Jakarta Sans',sans-serif; }

/* ══ SIDEBAR SC CARDS ══ */
.sc {
    background: rgba(255,255,255,0.85); border: 1px solid rgba(255,255,255,0.9);
    border-radius: 14px; padding: 1.1rem 1.15rem; margin-bottom: 0.85rem;
    box-shadow: 0 3px 16px rgba(16,185,129,0.07), 0 1px 3px rgba(0,0,0,0.04);
    backdrop-filter: blur(10px);
}
.sc-ttl {
    font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.72rem;
    font-weight: 700; letter-spacing: 0.08em; text-transform: uppercase;
    color: #4a7c5e; margin-bottom: 0.85rem; display:flex; align-items:center; gap:0.45rem;
}
.sc-ttl::after { content:''; flex:1; height:1px; background:rgba(16,185,129,0.14); }

/* loaded chars badge */
.chars-badge {
    display: inline-flex; align-items: center; gap: 0.35rem;
    font-family: 'DM Mono', monospace; font-size: 0.72rem; font-weight: 600;
    color: #059669; background: rgba(16,185,129,0.09);
    border: 1px solid rgba(16,185,129,0.22); border-radius: 7px;
    padding: 0.25rem 0.65rem; margin-top: 0.5rem;
}

/* ══ ALERTS ══ */
.stAlert { background:rgba(16,185,129,0.07) !important; border:1px solid rgba(16,185,129,0.2) !important; border-radius:10px !important; }
.stSpinner > div { border-top-color: #10b981 !important; }
div[data-testid="stHorizontalBlock"] > div[data-testid="column"] { background:transparent !important; }

/* ══ EXPORT HINT ══ */
.export-hint {
    font-size:0.84rem; color:#6b9e80; line-height:1.9; margin-top:0.8rem;
    font-family:'DM Sans',sans-serif;
}
.export-hint strong { color:#1a2e22; font-weight:600; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# SECURITY HELPERS — malware, file size info, integrity
# ══════════════════════════════════════════════════════════
MALWARE_SIGS = [b"cmd.exe", b"powershell", b"eval(", b"WScript", b"<script", b"javascript:", b"vbscript:"]

def check_malware(fb):
    return not any(sig.lower() in fb.lower() for sig in MALWARE_SIGS)

def check_integrity(fb, ext):
    try:
        if ext == "pdf":
            import pypdf; pypdf.PdfReader(io.BytesIO(fb))
        elif ext == "docx":
            import docx; docx.Document(io.BytesIO(fb))
        return True
    except: return False

def format_size(b):
    if b < 1024:       return f"{b} B"
    elif b < 1048576:  return f"{b/1024:.1f} KB"
    else:              return f"{b/1048576:.1f} MB"

def render_security_scan(fb, ext):
    malware_ok   = check_malware(fb)
    integrity_ok = check_integrity(fb, ext)
    size_str     = format_size(len(fb))

    def badge(ok, label_ok="✓ Pass", label_fail="✗ Fail"):
        return f'<span class="sec-badge-pass">{label_ok}</span>' if ok else f'<span class="sec-badge-fail">{label_fail}</span>'

    score = 100
    if not malware_ok:   score -= 40
    if not integrity_ok: score -= 30

    color    = "#059669" if score == 100 else ("#b45309" if score >= 60 else "#dc2626")
    bar_grad = "linear-gradient(90deg,#10b981,#34d399)" if score == 100 else ("linear-gradient(90deg,#f59e0b,#fbbf24)" if score >= 60 else "linear-gradient(90deg,#ef4444,#f87171)")

    html = f"""
<div class="ig-sec-label" style="margin-top:1.1rem;">Security Scan Results</div>
<div class="sec-badge-row">
  <span class="sec-badge-label">🛡️ Malware Signature Scan</span>{badge(malware_ok)}
</div>
<div class="sec-badge-row">
  <span class="sec-badge-label">✅ File Integrity Check</span>{badge(integrity_ok)}
</div>
<div class="sec-badge-row">
  <span class="sec-badge-label">📦 File Size</span>
  <span class="sec-badge-warn">{size_str} · No limit</span>
</div>
<div class="score-row">
  <div>
    <div class="score-lbl">Security Score</div>
    <div class="score-num" style="color:{color};">{score}</div>
    <div style="font-size:0.62rem;color:#a0c4b0;font-family:'DM Mono',monospace;">/ 100</div>
  </div>
  <div style="flex:1;">
    <div class="score-lbl" style="margin-bottom:0.3rem;">Scan Confidence</div>
    <div class="score-bar-bg">
      <div class="score-bar-fill" style="width:{score}%;background:{bar_grad};"></div>
    </div>
    <div style="font-size:0.7rem;color:{color};font-family:'DM Mono',monospace;margin-top:0.28rem;font-weight:600;">{score}% clean</div>
  </div>
</div>"""
    return html, malware_ok, integrity_ok


# ══════════════════════════════════════════════════════════
# EXTRACTION HELPERS
# ══════════════════════════════════════════════════════════
def extract_pdf(fb):
    import pypdf
    return "\n".join(p.extract_text() or "" for p in pypdf.PdfReader(io.BytesIO(fb)).pages).strip()

def extract_docx(fb):
    import docx
    return "\n".join(p.text for p in docx.Document(io.BytesIO(fb)).paragraphs).strip()

def fetch_url(url):
    req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=15) as r:
        html = r.read().decode('utf-8', errors='ignore')
    txt = re.sub(r'<style[^>]*>.*?</style>','',html,flags=re.DOTALL)
    txt = re.sub(r'<script[^>]*>.*?</script>','',txt,flags=re.DOTALL)
    return re.sub(r'\s+',' ', re.sub(r'<[^>]+>',' ',txt)).strip()

def call_groq(system, user, max_tokens=4000, temp=0.35):
    r = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role":"system","content":system},{"role":"user","content":user}],
        temperature=temp, max_tokens=max_tokens
    )
    return r.choices[0].message.content.strip()


# ══════════════════════════════════════════════════════════
# INFOGRAPHIC CONFIG
# ══════════════════════════════════════════════════════════
TYPES = {
    "auto":       "🤖  AI Decides Best Format",
    "summary":    "📋  Key Points & Insights",
    "timeline":   "⏱  Timeline & Events",
    "stats":      "📊  Stats & Data Visualization",
    "comparison": "⚖  Comparison & Analysis",
    "process":    "🔄  Process Flow & Steps",
    "report":     "📑  Full Report Dashboard",
}
THEMES = {
    "Emerald & Green":      "#071c12 dark bg, #10b981 emerald, #34d399 mint, white text",
    "Teal & Cyan":          "#0a2535 dark bg, #00bcd4 teal, #26c6da cyan, white text",
    "Dark Indigo & Purple": "#0a0f1e dark bg, #6366f1 indigo, #8b5cf6 purple, #e0e7ff text",
    "Sunset Orange & Red":  "#1a0800 dark bg, #f97316 orange, #ef4444 red, #fef3c7 text",
    "Clean White & Blue":   "#f8faff white bg, #1e3a5f navy, #3b82f6 blue, #dbeafe accents",
    "Warm Cream":           "#faf7f2 cream bg, #292524 dark, #dc6e2e terracotta, #f59e0b amber",
    "Black & Gold":         "#080608 black bg, #f59e0b gold, #fbbf24 bright gold, white text",
}

SYS = """You are a world-class infographic designer. Create Canva/Piktochart quality visual infographics.
Return ONLY complete HTML starting with <!DOCTYPE html>. No markdown, no fences.
All CSS in <style>. Import Google Fonts. Width 900px centered. MUST include SVG charts."""

def build_prompt(text, itype, title, theme):
    type_map = {
        "auto":       "Choose best layout. Mix stat circles, donut charts, key insight cards.",
        "summary":    "KEY POINTS: colored header, 5-8 numbered cards in 2-col grid with emoji icons, highlight stat.",
        "timeline":   "TIMELINE: bold header, vertical alternating events, year badges, connecting dots.",
        "stats":      "STATS DASHBOARD: hero numbers row, SVG donut charts, CSS bar charts, percentage rings.",
        "comparison": "COMPARISON: two-column VS layout, checkmark rows, VS badge divider, summary banner.",
        "process":    "PROCESS FLOW: numbered steps, arrow connectors, icon per step, color progression.",
        "report":     "FULL REPORT: hero header, 4 KPI cards, 2-3 content sections with charts, footer.",
    }
    t = f'Title: "{title}"' if title.strip() else "Auto-generate a compelling title."
    return f"""Create a stunning professional infographic.
TYPE: {type_map.get(itype, type_map['auto'])}
{t}
THEME: {theme}
REQUIREMENTS:
- 900px wide, margin:0 auto
- SVG donut rings (stroke-dasharray), CSS bar charts, stat circles
- Emoji icons throughout, fadeInUp CSS animations
- Cards with box-shadow, bold numbers 2.5rem+
- Google Fonts, professional spacing
- "Generated by InfographAI" footer
SVG DONUT EXAMPLE: <svg width="130" height="130" viewBox="0 0 130 130">
  <circle cx="65" cy="65" r="54" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="14"/>
  <circle cx="65" cy="65" r="54" fill="none" stroke="#10b981" stroke-width="14"
    stroke-dasharray="237 339" stroke-dashoffset="-85" stroke-linecap="round"/>
  <text x="65" y="70" text-anchor="middle" font-size="22" font-weight="800" fill="white">70%</text>
</svg>
DOCUMENT: {text[:5000]}
Return ONLY complete HTML."""


# ══════════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════════
for k,v in [("doc_text",""),("html_out",""),("generated",False)]:
    if k not in st.session_state: st.session_state[k] = v


# ══════════════════════════════════════════════════════════
# NAV
# ══════════════════════════════════════════════════════════
st.markdown("""
<div class="ig-nav">
  <div class="ig-logo-wrap">
    <div class="ig-logo-icon">🎨</div>
    <div class="ig-logo-text">Infograph<span>AI</span></div>
  </div>
  <div class="ig-nav-pills">
    <span class="ig-pill">PDF</span>
    <span class="ig-pill">DOCX</span>
    <span class="ig-pill">TEXT</span>
    <span class="ig-pill">URL</span>
    <span class="ig-pill">7 FORMATS</span>
    <span class="ig-pill">7 THEMES</span>
  </div>
  <div class="ig-status"><div class="ig-status-dot"></div>AI Online</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# HERO
# ══════════════════════════════════════════════════════════
st.markdown("""
<div class="ig-hero">
  <div class="ig-hero-tag">AI-Powered Infographic Generator</div>
  <h1 class="ig-h1">Transform Documents</h1>
  <span class="ig-h1-accent">into Visual Infographics</span>
  <p class="ig-hero-sub">Paste text, upload PDF or DOCX, or drop a URL — InfographAI turns your content into stunning, shareable visuals.</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# LAYOUT — left panel + right canvas
# ══════════════════════════════════════════════════════════
lcol, rcol = st.columns([1, 2.2], gap="large")

# ══════════════════════════════════════════════════════════
# LEFT — Input + Config + Security + Export
# ══════════════════════════════════════════════════════════
with lcol:

    # ── INPUT CARD ──
    st.markdown('<div class="ig-card">', unsafe_allow_html=True)
    st.markdown('<div class="ig-sec-label">Document Input</div>', unsafe_allow_html=True)

    t1, t2, t3, t4 = st.tabs(["📝 Text", "📄 PDF", "📃 DOCX", "🔗 URL"])

    with t1:
        txt = st.text_area("", height=180,
            placeholder="Paste your document, report, article or any text here…",
            label_visibility="collapsed", key="itxt")
        if st.button("Load Text →", key="btxt"):
            if txt.strip():
                st.session_state.doc_text = txt.strip()
                st.success(f"✅ Loaded {len(txt):,} characters")
            else:
                st.warning("Please enter some text first.")

    with t2:
        pf = st.file_uploader("", type=["pdf"], label_visibility="collapsed", key="ipdf")
        if st.button("Extract & Scan PDF →", key="bpdf"):
            if pf:
                fb = pf.read()
                scan_html, malware_ok, integrity_ok = render_security_scan(fb, "pdf")
                st.markdown(scan_html, unsafe_allow_html=True)
                if malware_ok and integrity_ok:
                    try:
                        st.session_state.doc_text = extract_pdf(fb)
                        st.success(f"✅ Extracted {len(st.session_state.doc_text):,} chars — no size limit")
                    except Exception as e:
                        st.error(f"Extraction failed: {e}")
                else:
                    st.error("🚫 File blocked by security scan.")
            else:
                st.warning("Upload a PDF first.")

    with t3:
        df = st.file_uploader("", type=["docx"], label_visibility="collapsed", key="idocx")
        if st.button("Extract & Scan DOCX →", key="bdocx"):
            if df:
                fb = df.read()
                scan_html, malware_ok, integrity_ok = render_security_scan(fb, "docx")
                st.markdown(scan_html, unsafe_allow_html=True)
                if malware_ok and integrity_ok:
                    try:
                        st.session_state.doc_text = extract_docx(fb)
                        st.success(f"✅ Extracted {len(st.session_state.doc_text):,} chars — no size limit")
                    except Exception as e:
                        st.error(f"Extraction failed: {e}")
                else:
                    st.error("🚫 File blocked by security scan.")
            else:
                st.warning("Upload a DOCX first.")

    with t4:
        ui = st.text_input("", placeholder="https://example.com/article…",
                           label_visibility="collapsed", key="iurl")
        if st.button("Fetch URL →", key="burl"):
            if ui.startswith("http"):
                with st.spinner("Fetching page content…"):
                    try:
                        t = fetch_url(ui)
                        if len(t) < 100:
                            st.error("Not enough readable content found.")
                        else:
                            st.session_state.doc_text = t[:8000]
                            st.success(f"✅ Fetched {len(st.session_state.doc_text):,} chars")
                    except Exception as e:
                        st.error(f"Failed: {e}")
            else:
                st.warning("Enter a valid URL starting with https://")

    if st.session_state.doc_text:
        st.markdown(f'<div class="chars-badge">✓ &nbsp;{len(st.session_state.doc_text):,} chars loaded</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)  # close ig-card

    # ── CONFIG CARD ──
    st.markdown('<div class="ig-card">', unsafe_allow_html=True)
    st.markdown('<div class="ig-sec-label">Configuration</div>', unsafe_allow_html=True)

    st.markdown('<p style="font-family:\'DM Mono\',monospace;font-size:0.68rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:#4a7c5e;margin-bottom:0.4rem;">Infographic Format</p>', unsafe_allow_html=True)
    itype = st.selectbox("fmt", list(TYPES.keys()), format_func=lambda k: TYPES[k],
                         label_visibility="collapsed", key="itype")

    st.markdown('<p style="font-family:\'DM Mono\',monospace;font-size:0.68rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:#4a7c5e;margin:0.8rem 0 0.4rem;">Color Theme</p>', unsafe_allow_html=True)
    theme = st.selectbox("thm", list(THEMES.keys()), label_visibility="collapsed", key="itheme")

    st.markdown('<p style="font-family:\'DM Mono\',monospace;font-size:0.68rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:#4a7c5e;margin:0.8rem 0 0.4rem;">Custom Title (optional)</p>', unsafe_allow_html=True)
    ctitle = st.text_input("", placeholder="Leave blank — AI will auto-generate…",
                           label_visibility="collapsed", key="ictitle")

    st.markdown("<div style='height:0.3rem'></div>", unsafe_allow_html=True)
    gen = st.button("✨  Generate Infographic", key="bgen")
    st.markdown('</div>', unsafe_allow_html=True)

    # ── EXPORT CARD ──
    if st.session_state.generated:
        st.markdown('<div class="ig-card">', unsafe_allow_html=True)
        st.markdown('<div class="ig-sec-label">Export</div>', unsafe_allow_html=True)
        st.download_button("⬇  Download HTML File",
            data=st.session_state.html_out.encode(),
            file_name="infographic.html", mime="text/html")
        st.markdown("""
<div class="export-hint">
  <strong>Save as PNG:</strong><br>
  Open in Chrome → Ctrl+P<br>
  → Save as PDF, or screenshot
</div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── RIGHT SIDEBAR INFO ──


# ══════════════════════════════════════════════════════════
# RIGHT — Canvas
# ══════════════════════════════════════════════════════════
with rcol:
    ready = st.session_state.generated and st.session_state.html_out
    if ready:
        badge_html = '<span class="cbadge-ready"><span class="cbadge-dot" style="background:#10b981;"></span>Infographic Ready</span>'
    else:
        badge_html = '<span class="cbadge-wait"><span class="cbadge-dot" style="background:#f59e0b;"></span>Awaiting Input</span>'

    st.markdown(f"""
<div class="canvas-header">
  <div class="canvas-title">🖼 Output Canvas</div>
  {badge_html}
</div>
<div class="canvas-body">
""", unsafe_allow_html=True)

    if not ready:
        st.markdown("""
<div class="empty-state">
  <div class="empty-grid"></div>
  <div class="empty-inner">
    <span class="empty-emoji">🎨</span>
    <div class="empty-h">Your infographic appears here</div>
    <div class="empty-p">Load a document, choose format and theme,<br>then hit Generate.</div>
    <div class="steps">
      <div class="step"><div class="step-n">STEP 1</div><div class="step-t">Load Doc</div></div>
      <div class="step"><div class="step-n">STEP 2</div><div class="step-t">Configure</div></div>
      <div class="step"><div class="step-n">STEP 3</div><div class="step-t">Generate ✨</div></div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)
    else:
        components.html(st.session_state.html_out, height=980, scrolling=True)

    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════
# GENERATE
# ══════════════════════════════════════════════════════════
if gen:
    if not st.session_state.doc_text.strip():
        st.error("⚠️ Please load a document first (Text, PDF, DOCX or URL).")
    else:
        theme_desc = THEMES.get(theme, list(THEMES.values())[0])
        prompt = build_prompt(st.session_state.doc_text, itype, ctitle, theme_desc)
        with st.spinner("✨ Generating your infographic with charts and visuals…"):
            try:
                raw = call_groq(SYS, prompt, max_tokens=4000, temp=0.38)
                raw = re.sub(r'^```html\s*','',raw.strip())
                raw = re.sub(r'^```\s*','',raw.strip())
                raw = re.sub(r'```\s*$','',raw.strip())
                if not raw.strip().startswith('<!'):
                    for tag in ['<!DOCTYPE','<html']:
                        idx = raw.find(tag)
                        if idx != -1: raw = raw[idx:]; break
                st.session_state.html_out = raw
                st.session_state.generated = True
                st.rerun()
            except Exception as e:
                st.error(f"Generation failed: {e}")
