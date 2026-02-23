# ─────────────────────────────────────────
# HERO HEADER
# ─────────────────────────────────────────
st.markdown("""
<style>
.hero {
    padding: 3rem 0 2rem;
}
.hero-title {
    font-size: 3.5rem;
    font-weight: 800;
    display: flex;
    align-items: center;
    gap: 15px;
}
.hero-title span {
    background: linear-gradient(120deg,#90ff50,#40ffc8,#4080ff);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.hero-sub {
    font-size: 1.1rem;
    color: #9ca4ff;
    margin-top: 0.5rem;
}
.security-title {
    margin-top: 2.5rem;
    font-size: 1rem;
    font-weight: 700;
    letter-spacing: 0.2em;
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
.card:hover {
    border-color: #40ffc8;
    box-shadow: 0 10px 40px rgba(64,255,200,0.15);
}
.pass { color:#90ff50; font-weight:600; }
.fail { color:#ff5f7a; font-weight:600; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <div class="hero-title">
        🔐 <span>DocVault Enterprise</span>
    </div>
    <div class="hero-sub">
        Enterprise-grade secure document validation & extraction platform
    </div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# SECURITY ENGINE CARDS
# ─────────────────────────────────────────
st.markdown('<div class="security-title">Security Engine</div>', unsafe_allow_html=True)

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
