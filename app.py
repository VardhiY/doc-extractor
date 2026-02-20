import streamlit as st
from groq import Groq
import json, re, base64, io

st.set_page_config(
    page_title="DocVault · AI Extractor",
    page_icon="🔐",
    layout="wide",
)

try:
    API_KEY = st.secrets["GROQ_API_KEY"]
    client  = Groq(api_key=API_KEY)
except Exception:
    st.error("⚠️ API key not configured. Add GROQ_API_KEY to Streamlit Secrets.")
    st.stop()

# ═══════════════════════════════════════════════════════════════
# MASTER CSS (UPDATED FOR READABILITY)
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=Syne:wght@700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', sans-serif !important;
    -webkit-font-smoothing: antialiased;
}

.stApp {
    background: #06060f !important;
    color: #f0f2ff !important;
}

/* Center content */
.main .block-container {
    max-width: 880px !important;
    margin: 0 auto !important;
    padding: 0 1.8rem 5rem !important;
}

/* ─── HERO ─── */
.hero {
    text-align: center;
    padding: 3rem 1rem 2rem;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 4.8rem;
    font-weight: 800;
    line-height: 1;
    color: #ffffff;
}
.hero-title .g {
    background: linear-gradient(120deg, #90ff50 0%, #40ffc8 50%, #4080ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-size: 1.05rem;
    color: #9aa3d8;
    max-width: 520px;
    margin: 1rem auto 0;
    line-height: 1.7;
}

/* ─── SECTION HEADERS ─── */
.sec-head {
    font-size: 0.8rem;
    font-weight: 800;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #4c4c88;
    margin: 2.2rem 0 1.2rem;
}

/* ─── SECURITY CARDS ─── */
.shield-banner {
    background: #0b0b1c;
    border: 1px solid #161630;
    border-radius: 22px;
    padding: 1.8rem;
}
.shield-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}
.shield-item {
    background: #0e0e22;
    border: 1px solid #1b1b3a;
    border-radius: 16px;
    padding: 1.1rem 1.2rem;
}
.si-name {
    font-size: 0.95rem;
    font-weight: 700;
    color: #d6d8ff;
    margin-bottom: 0.4rem;
}
.si-desc {
    font-size: 0.85rem;
    color: #8e96d8;
    line-height: 1.6;
}

/* ─── REDACT CARDS ─── */
.redact-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}
.redact-card {
    background: #0c0c22;
    border: 1px solid #181840;
    border-radius: 18px;
    padding: 1.2rem;
}
.rc-name {
    font-size: 0.95rem;
    font-weight: 700;
    color: #cfd3ff;
    margin-bottom: 0.4rem;
}
.rc-desc {
    font-size: 0.85rem;
    color: #8a92d0;
    line-height: 1.6;
}

/* ─── BUTTON ─── */
.stButton > button {
    background: linear-gradient(135deg,#90ff50,#40ffc8) !important;
    color: #050510 !important;
    font-weight: 800 !important;
    border-radius: 16px !important;
    padding: 0.9rem !important;
}

/* ─── STATS ─── */
.stats {
    display: grid;
    grid-template-columns: repeat(3,1fr);
    gap: 1rem;
}
.stat-c {
    background: #0c0c22;
    border: 1px solid #1b1b3a;
    border-radius: 18px;
    padding: 1.4rem;
    text-align: center;
}
.stat-n {
    font-size: 2.2rem;
    font-weight: 800;
    color: #90ff50;
}
.stat-l {
    font-size: 0.75rem;
    letter-spacing: 0.1em;
    color: #5c5ca0;
}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# HERO
# ═══════════════════════════════════════════════════════════════
st.markdown("""
<div class="hero">
  <div class="hero-title">Doc<span class="g">Vault</span></div>
  <div class="hero-sub">
    Extract text from any document, scan for threats, and automatically
    redact sensitive information — securely and instantly.
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# SECURITY INTRO
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="sec-head">🛡️ Security Engine</div>', unsafe_allow_html=True)
st.markdown("""
<div class="shield-banner">
  <div class="shield-grid">
    <div class="shield-item">
      <div class="si-name">📦 File Size Validation</div>
      <div class="si-desc">
        Prevents oversized files from being processed to protect performance and stability.
      </div>
    </div>
    <div class="shield-item">
      <div class="si-name">🦠 Malware Detection</div>
      <div class="si-desc">
        Scans file content at byte level to detect executables, embedded scripts and exploits.
      </div>
    </div>
    <div class="shield-item">
      <div class="si-name">🧩 Corruption Detection</div>
      <div class="si-desc">
        Verifies document integrity by attempting safe structured parsing.
      </div>
    </div>
    <div class="shield-item">
      <div class="si-name">🔍 File Type Verification</div>
      <div class="si-desc">
        Validates file signature to prevent disguised or renamed malicious files.
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# SENSITIVE DATA SECTION
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="sec-head">🔒 Sensitive Data Protection</div>', unsafe_allow_html=True)
st.markdown(
    "<p style='font-size:1rem;color:#8a92d0;margin-bottom:1.5rem;'>Select which categories should be automatically redacted from your document.</p>",
    unsafe_allow_html=True
)

st.markdown("""
<div class="redact-grid">
  <div class="redact-card">
    <div class="rc-name">🪪 Aadhaar / SSN / ID</div>
    <div class="rc-desc">Government-issued identification numbers including PAN, passport and licenses.</div>
  </div>
  <div class="redact-card">
    <div class="rc-name">📞 Phone & Email</div>
    <div class="rc-desc">Mobile numbers, landlines and email addresses found in the document.</div>
  </div>
  <div class="redact-card">
    <div class="rc-name">💳 Banking Information</div>
    <div class="rc-desc">Account numbers, card numbers, IFSC codes and UPI identifiers.</div>
  </div>
  <div class="redact-card">
    <div class="rc-name">🔑 Passwords & Secrets</div>
    <div class="rc-desc">Passwords, API keys, tokens, OTPs and confidential credentials.</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════
# DEMO STATS PANEL
# ═══════════════════════════════════════════════════════════════
st.markdown('<div class="sec-head">📊 System Overview</div>', unsafe_allow_html=True)

st.markdown("""
<div class="stats">
  <div class="stat-c">
    <div class="stat-n">2,430</div>
    <div class="stat-l">Words Processed</div>
  </div>
  <div class="stat-c">
    <div class="stat-n">12</div>
    <div class="stat-l">Sensitive Items</div>
  </div>
  <div class="stat-c">
    <div class="stat-n">SECURE</div>
    <div class="stat-l">Document Status</div>
  </div>
</div>
""", unsafe_allow_html=True)
