import streamlit as st
import time
import csv
import io
from utils.pdf_reader import extract_text_from_pdf
from utils.extractor import extract_claims
from utils.verifier import verify_claims

# ─────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────
st.set_page_config(
    page_title="TruthLens AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [data-testid="stAppViewContainer"] {
    background: #0a0a0f;
    color: #e8e8f0;
    font-family: 'DM Mono', monospace;
}
[data-testid="stAppViewContainer"] {
    background: #0a0a0f;
    background-image:
        radial-gradient(ellipse 80% 40% at 50% -10%, rgba(99,71,255,0.15) 0%, transparent 70%),
        radial-gradient(ellipse 40% 40% at 90% 80%, rgba(255,71,120,0.06) 0%, transparent 60%);
}
[data-testid="stHeader"]  { background: transparent; }
[data-testid="stSidebar"] { background: #0d0d14 !important; border-right: 1px solid rgba(255,255,255,0.06) !important; }
h1,h2,h3 { font-family: 'Syne', sans-serif !important; }

.hero { text-align: center; padding: 2.5rem 1rem 1.5rem; }
.hero-eyebrow { font-size: 0.68rem; letter-spacing: 0.28em; text-transform: uppercase; color: #6347ff; margin-bottom: 0.9rem; }
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: clamp(2.2rem, 5vw, 3.6rem); font-weight: 800; line-height: 1.05; letter-spacing: -0.02em;
    background: linear-gradient(135deg, #ffffff 30%, #a08cff 65%, #ff4778 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    margin-bottom: 0.6rem;
}
.hero-sub { font-size: 0.82rem; color: #666; letter-spacing: 0.05em; }

.step-flow { display: flex; justify-content: center; gap: 0; margin: 1.2rem 0 2rem; flex-wrap: wrap; }
.step-pill {
    font-size: 0.65rem; letter-spacing: 0.08em; text-transform: uppercase; color: #444;
    padding: 0.35rem 0.9rem; border: 1px solid rgba(255,255,255,0.06);
    display: flex; align-items: center; gap: 0.4rem;
}
.step-pill:first-child { border-radius: 20px 0 0 20px; }
.step-pill:last-child  { border-radius: 0 20px 20px 0; }
.step-pill .dot { width: 5px; height: 5px; border-radius: 50%; background: #6347ff; }
.step-arrow { color: #2a2a35; font-size: 0.7rem; display: flex; align-items: center; padding: 0 0.1rem; border: 1px solid rgba(255,255,255,0.06); border-left: none; border-right: none; }

.metric-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 0.85rem; margin: 1.25rem 0 1.25rem; }
.metric-card {
    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px; padding: 1.2rem 1rem; text-align: center;
    position: relative; overflow: hidden;
}
.metric-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px; }
.metric-card.total::before  { background: #6347ff; }
.metric-card.green::before  { background: #3dd68c; }
.metric-card.yellow::before { background: #fbbf24; }
.metric-card.red::before    { background: #f87171; }
.metric-value { font-family: 'Syne', sans-serif; font-size: 2.2rem; font-weight: 800; line-height: 1; }
.metric-label { font-size: 0.65rem; letter-spacing: 0.14em; text-transform: uppercase; color: #555; margin-top: 0.3rem; }
.metric-pct   { font-size: 0.7rem; margin-top: 0.2rem; opacity: 0.45; }
.mv-total { color: #a08cff; } .mv-green { color: #3dd68c; } .mv-yellow { color: #fbbf24; } .mv-red { color: #f87171; }

.verdict-bar-wrap { margin: 0.2rem 0 1.5rem; }
.verdict-bar-label { font-size: 0.62rem; letter-spacing: 0.1em; text-transform: uppercase; color: #333; margin-bottom: 0.4rem; }
.verdict-bar { height: 5px; border-radius: 6px; background: rgba(255,255,255,0.04); display: flex; overflow: hidden; }
.vb-green  { background: #3dd68c; }
.vb-yellow { background: #fbbf24; }
.vb-red    { background: #f87171; }

.result-card {
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.065);
    border-left: 3px solid transparent; border-radius: 12px;
    padding: 1.1rem 1.3rem; margin-bottom: 0.6rem; transition: background 0.2s;
}
.result-card:hover { background: rgba(255,255,255,0.035); }
.result-card.verified   { border-left-color: #3dd68c; }
.result-card.inaccurate { border-left-color: #fbbf24; }
.result-card.false      { border-left-color: #f87171; }
.rc-top { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; }
.claim-text { font-size: 0.86rem; line-height: 1.55; color: #ccc; flex: 1; }
.badge {
    font-size: 0.6rem; letter-spacing: 0.1em; text-transform: uppercase;
    padding: 0.2rem 0.55rem; border-radius: 20px; white-space: nowrap; font-weight: 500; flex-shrink: 0;
}
.badge-verified   { background: rgba(61,214,140,0.1);  color: #3dd68c; border: 1px solid rgba(61,214,140,0.25); }
.badge-inaccurate { background: rgba(251,191,36,0.1);  color: #fbbf24; border: 1px solid rgba(251,191,36,0.25); }
.badge-false      { background: rgba(248,113,113,0.1); color: #f87171; border: 1px solid rgba(248,113,113,0.25); }
.rc-meta { margin-top: 0.5rem; }
.correction-text { font-size: 0.75rem; color: #777; font-style: italic; line-height: 1.5; }
.corr-label { color: #a08cff; font-style: normal; margin-right: 0.25rem; }
.rc-footer {
    display: flex; align-items: center; gap: 0.85rem; margin-top: 0.5rem;
    padding-top: 0.45rem; border-top: 1px solid rgba(255,255,255,0.04); flex-wrap: wrap;
}
.source-tag { font-size: 0.67rem; color: #3a3a50; display: flex; align-items: center; gap: 0.3rem; }
.conf-tag { font-size: 0.62rem; padding: 0.12rem 0.45rem; border-radius: 10px; letter-spacing: 0.06em; text-transform: uppercase; }
.conf-high   { background: rgba(61,214,140,0.07);  color: rgba(61,214,140,0.5);  border: 1px solid rgba(61,214,140,0.15); }
.conf-medium { background: rgba(251,191,36,0.07);  color: rgba(251,191,36,0.5);  border: 1px solid rgba(251,191,36,0.15); }
.conf-low    { background: rgba(248,113,113,0.07); color: rgba(248,113,113,0.5); border: 1px solid rgba(248,113,113,0.15); }

.notice-box {
    background: rgba(99,71,255,0.06); border: 1px solid rgba(99,71,255,0.18);
    border-radius: 10px; padding: 0.8rem 1rem;
    font-size: 0.75rem; color: #777; line-height: 1.6; margin-bottom: 1.1rem;
}
.notice-box strong { color: #a08cff; }

.section-header {
    font-family: 'Syne', sans-serif; font-size: 0.72rem; font-weight: 700;
    letter-spacing: 0.18em; text-transform: uppercase; color: #3a3a55;
    margin: 1.6rem 0 0.85rem; display: flex; align-items: center; gap: 0.75rem;
}
.section-header::after { content: ''; flex: 1; height: 1px; background: rgba(255,255,255,0.05); }

.sidebar-logo {
    font-family: 'Syne', sans-serif; font-size: 1.05rem; font-weight: 800;
    background: linear-gradient(135deg, #a08cff, #ff4778);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
    margin-bottom: 1.2rem;
}
.sidebar-step { display: flex; align-items: flex-start; gap: 0.6rem; margin-bottom: 0.65rem; font-size: 0.73rem; color: #555; line-height: 1.4; }
.sidebar-step-num {
    background: rgba(99,71,255,0.12); color: #6347ff; font-size: 0.58rem; font-weight: 700;
    width: 17px; height: 17px; border-radius: 50%; display: flex; align-items: center;
    justify-content: center; flex-shrink: 0; margin-top: 1px;
}

.stFileUploader > div { background: transparent !important; }
[data-testid="stFileUploaderDropzone"] { background: rgba(99,71,255,0.03) !important; border: 1.5px dashed rgba(99,71,255,0.28) !important; border-radius: 12px !important; }
.stButton > button { background: linear-gradient(135deg, #6347ff, #8b5cf6) !important; color: white !important; border: none !important; border-radius: 8px !important; font-family: 'DM Mono', monospace !important; font-size: 0.78rem !important; letter-spacing: 0.08em !important; padding: 0.5rem 1.5rem !important; transition: opacity 0.2s !important; }
.stButton > button:hover { opacity: 0.82 !important; }
.stProgress > div > div { background: linear-gradient(90deg, #6347ff, #ff4778) !important; border-radius: 4px !important; }
[data-testid="stExpander"] { background: rgba(255,255,255,0.015) !important; border: 1px solid rgba(255,255,255,0.055) !important; border-radius: 10px !important; }
div[data-testid="stTextArea"] textarea { background: rgba(255,255,255,0.02) !important; border: 1px solid rgba(255,255,255,0.07) !important; color: #777 !important; font-family: 'DM Mono', monospace !important; font-size: 0.74rem !important; border-radius: 8px !important; }
.stDownloadButton > button { background: transparent !important; border: 1px solid rgba(99,71,255,0.35) !important; color: #8b74ff !important; border-radius: 8px !important; font-family: 'DM Mono', monospace !important; font-size: 0.75rem !important; }
.stDownloadButton > button:hover { background: rgba(99,71,255,0.07) !important; border-color: rgba(99,71,255,0.6) !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-logo">🔍 TruthLens AI</div>', unsafe_allow_html=True)

    groq_key = st.text_input(
        "Groq API Key",
        type="password",
        placeholder="gsk_...",
        help="Free key at console.groq.com — no credit card needed"
    )

    st.markdown("---")
    st.markdown("**How it works**")
    for i, s in enumerate([
        "Upload any PDF document",
        "AI extracts factual claims",
        "Web evidence is gathered",
        "AI verifies each claim",
        "View verdicts + corrections",
    ], 1):
        st.markdown(f'<div class="sidebar-step"><div class="sidebar-step-num">{i}</div><div>{s}</div></div>',
                    unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("**Best PDFs to test**")
    st.markdown("""<div style="font-size:0.7rem;color:#444;line-height:2;">
• Wikipedia economy/science articles<br>
• WHO / World Bank reports<br>
• Company annual reports (2022–23)<br>
• News articles with statistics<br>
• Research papers with data
</div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("<div style='font-size:0.62rem;color:#2a2a3a;text-align:center;'>Groq · PyMuPDF · DuckDuckGo</div>",
                unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">● AI-Powered Document Intelligence</div>
    <h1 class="hero-title">TruthLens AI</h1>
    <p class="hero-sub">Automated Claim Extraction · AI Verification · Corrected Facts</p>
</div>
<div class="step-flow">
    <div class="step-pill"><span class="dot"></span>Upload PDF</div>
    <div class="step-arrow">›</div>
    <div class="step-pill"><span class="dot"></span>Extract Claims</div>
    <div class="step-arrow">›</div>
    <div class="step-pill"><span class="dot"></span>Web Search</div>
    <div class="step-arrow">›</div>
    <div class="step-pill"><span class="dot"></span>AI Verify</div>
    <div class="step-arrow">›</div>
    <div class="step-pill"><span class="dot"></span>Results</div>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# UPLOAD
# ─────────────────────────────────────────────────────────
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    uploaded_file = st.file_uploader("Drop your PDF here", type=["pdf"], label_visibility="collapsed")

if not groq_key:
    st.markdown("""<div style="text-align:center;padding:1.2rem;color:#333;font-size:0.78rem;">
        👈 Add your free <strong style="color:#6347ff">Groq API key</strong> in the sidebar to begin
    </div>""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────
# PIPELINE
# ─────────────────────────────────────────────────────────
if uploaded_file and groq_key:

    # PDF
    st.markdown('<div class="section-header">📄 Document</div>', unsafe_allow_html=True)
    with st.spinner("Reading PDF…"):
        raw_text = extract_text_from_pdf(uploaded_file)

    col_a, col_b = st.columns([3, 1])
    with col_a:
        with st.expander(f"Preview extracted text  ({len(raw_text):,} characters)", expanded=False):
            st.text_area("", raw_text[:3000] + ("…" if len(raw_text) > 3000 else ""),
                         height=150, label_visibility="collapsed")
    with col_b:
        pages = raw_text.count("[Page ")
        st.markdown(f"""<div style="background:rgba(255,255,255,0.025);border:1px solid rgba(255,255,255,0.06);
            border-radius:10px;padding:1rem;text-align:center;margin-top:0.1rem;">
            <div style="font-family:'Syne',sans-serif;font-size:1.5rem;font-weight:800;color:#a08cff">{pages}</div>
            <div style="font-size:0.62rem;letter-spacing:0.12em;text-transform:uppercase;color:#333;margin-top:0.2rem">Pages</div>
        </div>""", unsafe_allow_html=True)

    # Claims
    st.markdown('<div class="section-header">🧠 Claim Extraction</div>', unsafe_allow_html=True)
    progress = st.progress(0, text="Extracting claims…")
    with st.spinner(""):
        claims = extract_claims(raw_text, groq_key)
        progress.progress(30, text=f"Found {len(claims)} claims — starting verification…")

    if not claims:
        st.warning("No factual claims found. Try a document with statistics, dates, or factual statements.")
        st.stop()

    type_colors = {"statistic":"#a08cff","date":"#fbbf24","financial":"#3dd68c",
                   "scientific":"#38bdf8","demographic":"#f472b6","ranking":"#fb923c","other":"#555"}
    with st.expander(f"View all {len(claims)} extracted claims", expanded=False):
        for i, c in enumerate(claims, 1):
            ctype = c.get("type", "other")
            col  = type_colors.get(ctype, "#555")
            st.markdown(
                f"`{i:02d}` {c.get('claim', c)} "
                f"<span style='font-size:0.62rem;color:{col};background:rgba(255,255,255,0.04);"
                f"padding:0.08rem 0.35rem;border-radius:8px;margin-left:0.35rem'>{ctype}</span>",
                unsafe_allow_html=True)

    # Verify
    results     = []
    live_status = st.empty()
    for i, claim_obj in enumerate(claims):
        pct     = 30 + int((i / len(claims)) * 70)
        preview = claim_obj.get("claim","")[:55]
        progress.progress(pct, text=f"[{i+1}/{len(claims)}] {preview}…")
        result  = verify_claims(claim_obj, groq_key)
        results.append(result)

        v   = sum(1 for r in results if r.get("status","").lower() == "verified")
        inc = sum(1 for r in results if r.get("status","").lower() == "inaccurate")
        f   = sum(1 for r in results if r.get("status","").lower() == "false")
        rem = len(claims) - i - 1
        live_status.markdown(
            f"<div style='font-size:0.7rem;color:#3a3a55;text-align:center;padding:0.3rem'>"
            f"✅ {v} verified &nbsp;·&nbsp; ⚠️ {inc} inaccurate &nbsp;·&nbsp; ❌ {f} false"
            f"{'&nbsp;·&nbsp; <span style=color:#2a2a40>' + str(rem) + ' remaining</span>' if rem > 0 else ''}</div>",
            unsafe_allow_html=True)

    progress.progress(100, text="✓ All claims verified")
    time.sleep(0.4)
    progress.empty()
    live_status.empty()

    # Metrics
    total      = len(results)
    verified   = sum(1 for r in results if r.get("status","").lower() == "verified")
    inaccurate = sum(1 for r in results if r.get("status","").lower() == "inaccurate")
    false_ct   = sum(1 for r in results if r.get("status","").lower() == "false")
    v_pct      = int(verified   / total * 100) if total else 0
    inc_pct    = int(inaccurate / total * 100) if total else 0
    f_pct      = int(false_ct   / total * 100) if total else 0

    st.markdown(f"""
<div class="metric-row">
    <div class="metric-card total"><div class="metric-value mv-total">{total}</div><div class="metric-label">Claims Found</div><div class="metric-pct">100%</div></div>
    <div class="metric-card green"><div class="metric-value mv-green">{verified}</div><div class="metric-label">Verified</div><div class="metric-pct">{v_pct}%</div></div>
    <div class="metric-card yellow"><div class="metric-value mv-yellow">{inaccurate}</div><div class="metric-label">Inaccurate</div><div class="metric-pct">{inc_pct}%</div></div>
    <div class="metric-card red"><div class="metric-value mv-red">{false_ct}</div><div class="metric-label">False</div><div class="metric-pct">{f_pct}%</div></div>
</div>
<div class="verdict-bar-wrap">
    <div class="verdict-bar-label">Verdict distribution</div>
    <div class="verdict-bar">
        <div class="vb-green"  style="width:{v_pct}%"></div>
        <div class="vb-yellow" style="width:{inc_pct}%"></div>
        <div class="vb-red"    style="width:{f_pct}%"></div>
    </div>
</div>""", unsafe_allow_html=True)

    # Future data notice
    future_ct = sum(1 for r in results if
        any(y in r.get("claim","") for y in ["2025","2026","2027"]) and
        r.get("status","").lower() == "inaccurate")
    if future_ct > 0:
        st.markdown(f"""<div class="notice-box">
            ℹ️ <strong>{future_ct} claims</strong> reference 2025–2027 projections.
            The AI's training data ends in early 2024, so future estimates may appear as
            <strong>Inaccurate</strong> — not because the PDF is wrong, but because the data
            doesn't exist yet. Facts from 2022–2024 are verified with high reliability.
        </div>""", unsafe_allow_html=True)

    # Results
    st.markdown('<div class="section-header">✅ Verification Results</div>', unsafe_allow_html=True)

    fc1, fc2, _ = st.columns([1, 1, 3])
    with fc1:
        filter_status = st.selectbox("Filter by status", ["All","Verified","Inaccurate","False"])
    with fc2:
        filter_conf = st.selectbox("Filter by confidence", ["All","High","Medium","Low"])

    badge_map = {"verified":"badge-verified","inaccurate":"badge-inaccurate","false":"badge-false"}
    label_map = {"verified":"✅ Verified","inaccurate":"⚠️ Inaccurate","false":"❌ False"}
    conf_map  = {"High":"conf-high","Medium":"conf-medium","Low":"conf-low"}

    shown = 0
    for r in results:
        status = r.get("status","Inaccurate").lower()
        conf   = r.get("confidence","Medium")
        if filter_status != "All" and status != filter_status.lower(): continue
        if filter_conf   != "All" and conf   != filter_conf:           continue
        shown += 1

        claim      = r.get("claim","")
        correction = r.get("corrected_fact","")
        source     = r.get("source","")
        badge_cls  = badge_map.get(status,"badge-inaccurate")
        label      = label_map.get(status, status.capitalize())
        conf_cls   = conf_map.get(conf,"conf-medium")

        corr_html = (
            '<span style="font-size:0.74rem;color:rgba(61,214,140,0.4)">✓ Consistent with available evidence</span>'
            if status == "verified"
            else f'<span class="corr-label">Corrected:</span> {correction}'
            if correction else ""
        )
        src_html  = f'<span class="source-tag">🔗 {source}</span>' if source else ""
        conf_html = f'<span class="conf-tag {conf_cls}">{conf} confidence</span>'

        st.markdown(f"""
<div class="result-card {status}">
    <div class="rc-top">
        <div class="claim-text">{claim}</div>
        <span class="badge {badge_cls}">{label}</span>
    </div>
    <div class="rc-meta"><div class="correction-text">{corr_html}</div></div>
    <div class="rc-footer">{src_html}{conf_html}</div>
</div>""", unsafe_allow_html=True)

    if shown == 0:
        st.markdown("<div style='color:#333;font-size:0.78rem;text-align:center;padding:2rem'>No results match selected filters.</div>",
                    unsafe_allow_html=True)

    # Export
    st.markdown('<div class="section-header">📥 Export</div>', unsafe_allow_html=True)
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=["claim","status","corrected_fact","source","confidence"])
    writer.writeheader()
    writer.writerows(results)

    summary_lines = [f"TruthLens AI Results\n{'='*40}",
                     f"Total: {total}  Verified: {verified}  Inaccurate: {inaccurate}  False: {false_ct}\n"]
    for r in results:
        summary_lines.append(f"[{r['status']}] {r['claim']}")
        if r.get("corrected_fact") and r["status"] != "Verified":
            summary_lines.append(f"  → {r['corrected_fact']}")
        summary_lines.append("")

    dl1, dl2, _ = st.columns([1, 1, 3])
    with dl1:
        st.download_button("⬇ Download CSV", data=buf.getvalue(),
                           file_name="truthlens_results.csv", mime="text/csv")
    with dl2:
        st.download_button("⬇ Download TXT", data="\n".join(summary_lines),
                           file_name="truthlens_results.txt", mime="text/plain")

elif uploaded_file and not groq_key:
    st.warning("👈 Please add your Groq API key in the sidebar to begin.")