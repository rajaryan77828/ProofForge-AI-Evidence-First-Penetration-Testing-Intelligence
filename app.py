"""
ProofForge AI - Enterprise Penetration Testing Intelligence Platform
Professional Streamlit Application with Cyber Aesthetics & Animations
"""

import os
import base64
import streamlit as st
from datetime import datetime
from parser import parse_assessment_notes, calculate_sha256
from report_generator import export_markdown_report, export_html_report
from models import Finding, SeverityLevel, EvidenceIntegrityStatus

st.set_page_config(
    page_title="ProofForge AI | Pentest Intelligence Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Helper function to encode local images to base64
def get_base64_image(image_path: str) -> str:
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    return ""

banner_b64 = get_base64_image("assets/banner.jpg")
logo_b64 = get_base64_image("assets/logo.jpg")

# Advanced Cyberpunk & Enterprise Dark Theme with CSS Animations
st.markdown(f"""
<style>
    @keyframes pulseGlow {{
        0% {{ box-shadow: 0 0 10px rgba(56, 189, 248, 0.2); }}
        50% {{ box-shadow: 0 0 25px rgba(56, 189, 248, 0.6); }}
        100% {{ box-shadow: 0 0 10px rgba(56, 189, 248, 0.2); }}
    }}

    @keyframes scanlineAnim {{
        0% {{ transform: translateY(-100%); }}
        100% {{ transform: translateY(1000%); }}
    }}

    @keyframes fadeIn {{
        from {{ opacity: 0; transform: translateY(10px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    .hero-banner-container {{
        position: relative;
        overflow: hidden;
        border-radius: 12px;
        margin-bottom: 24px;
        border: 1px solid rgba(56, 189, 248, 0.3);
        animation: pulseGlow 4s infinite ease-in-out;
    }}

    .hero-banner-img {{
        width: 100%;
        max-height: 240px;
        object-fit: cover;
        display: block;
        filter: brightness(0.85) contrast(1.1);
    }}

    .hero-overlay {{
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(180deg, rgba(13, 17, 23, 0) 0%, rgba(13, 17, 23, 0.95) 90%);
        padding: 20px 28px;
    }}

    .hero-title {{
        font-family: 'Inter', -apple-system, sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: #ffffff;
        text-shadow: 0 2px 10px rgba(0, 0, 0, 0.8);
        margin: 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }}

    .hero-subtitle {{
        font-size: 0.95rem;
        color: #38bdf8;
        font-weight: 600;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin-top: 4px;
    }}

    .metric-card-custom {{
        background: rgba(22, 27, 34, 0.85);
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        backdrop-filter: blur(10px);
        transition: transform 0.2s ease, border-color 0.2s ease;
        animation: fadeIn 0.5s ease-out;
    }}

    .metric-card-custom:hover {{
        transform: translateY(-2px);
        border-color: #58a6ff;
    }}

    .metric-val {{
        font-size: 2rem;
        font-weight: 700;
        color: #ffffff;
    }}

    .metric-lbl {{
        font-size: 0.8rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }}

    .badge-verified {{
        background: rgba(46, 160, 67, 0.15);
        color: #3fb950;
        border: 1px solid rgba(46, 160, 67, 0.4);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }}

    .badge-unverified {{
        background: rgba(248, 81, 73, 0.15);
        color: #f85149;
        border: 1px solid rgba(248, 81, 73, 0.4);
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
    }}

    .hash-badge {{
        background-color: #161b22;
        border: 1px dashed #38bdf8;
        padding: 8px 12px;
        border-radius: 6px;
        font-family: monospace;
        font-size: 0.82rem;
        color: #79c0ff;
        word-break: break-all;
    }}
</style>
""", unsafe_allow_html=True)

# Render Animated Hero Banner
if banner_b64:
    st.markdown(f"""
    <div class="hero-banner-container">
        <img class="hero-banner-img" src="data:image/jpeg;base64,{banner_b64}" alt="ProofForge AI Banner" />
        <div class="hero-overlay">
            <div class="hero-title">
                🛡️ ProofForge AI
            </div>
            <div class="hero-subtitle">
                Enterprise Penetration Testing Intelligence & Grounded Evidence Engine
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.title("🛡️ ProofForge AI")
    st.caption("Enterprise Penetration Testing Intelligence Platform")

# Sidebar Configuration
with st.sidebar:
    if logo_b64:
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 16px;">
            <img src="data:image/jpeg;base64,{logo_b64}" style="width: 110px; height: 110px; border-radius: 50%; border: 2px solid #38bdf8; box-shadow: 0 0 15px rgba(56, 189, 248, 0.4);" />
        </div>
        """, unsafe_allow_html=True)

    st.header("📋 Engagement Settings")
    project_name = st.text_input("System / Assessment Name", value="Global Payments Portal API Assessment")
    organization = st.text_input("Target Client", value="FinTech Global Corp")
    lead_assessor = st.text_input("Lead Assessor", value="Alex Rivera, OSCP / CISSP")
    peer_reviewer = st.text_input("Peer Reviewer / QA", value="Samantha Vance, Principal Consultant")
    
    st.markdown("---")
    st.subheader("🎯 Scope Specification")
    scope_str = st.text_area(
        "Authorized Scope (1 per line)",
        value="https://api.payments.fintechglobal.com/v2/ (Staging)\n10.240.12.0/24 (Payment Gateway Services)",
        height=85
    )

    st.markdown("---")
    st.subheader("🔒 Evidence Fidelity Rule")
    st.caption(
        "ProofForge AI strictly adheres to **zero synthetic evidence generation**. "
        "Missing reproduction steps, unverified payloads, and speculative severities are flagged "
        "rather than fabricated."
    )

SAMPLE_NOTES = """### Finding 1: Blind SQL Injection on Transaction Query Parameter
Severity: High
Target: https://api.payments.fintechglobal.com/v2/transactions?ref_id=TXN-9021
Port: 443/TCP (HTTPS)
Description: The ref_id query parameter is insufficiently sanitized and directly interpolated into internal SQL query statements. Time-based blind payloads demonstrate execution delays.
Proof of Concept / Raw Evidence:
POST /v2/transactions/search HTTP/1.1
Host: api.payments.fintechglobal.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{"ref_id": "TXN-9021' OR (SELECT pg_sleep(5))--"}

Response:
HTTP/1.1 200 OK
Content-Type: application/json
X-Response-Time: 5124ms

{"status": "success", "results": []}
Impact: An authenticated user can bypass isolation barriers, execute arbitrary SQL queries against the payments database, and exfiltrate confidential ledger data.
Remediation: Enforce parameterized queries using prepared statements across all database connectors. Disable detailed stack traces.

### Finding 2: Insecure Direct Object Reference (IDOR) Exposing Customer KYC Documents
Severity: High
Target: https://api.payments.fintechglobal.com/v2/documents/download?doc_id=DOC-88210
Port: 443/TCP (HTTPS)
Description: Modifying the doc_id query parameter allows retrieval of sensitive identity documents belonging to other users without authorization validation.
Proof of Concept / Raw Evidence:
GET /v2/documents/download?doc_id=DOC-88209 HTTP/1.1
Host: api.payments.fintechglobal.com
Authorization: Bearer <Customer_B_Token>

Response:
HTTP/1.1 200 OK
Content-Type: application/pdf
Content-Disposition: attachment; filename="passport_customer_A.pdf"
[Binary PDF Content Received]
Impact: Unauthorized disclosure of Personally Identifiable Information (PII) and regulatory non-compliance with GDPR and PCI-DSS.
Remediation: Implement server-side authorization checks verifying that the requesting session identity owns the requested document record.

### Finding 3: Missing Strict-Transport-Security and Server Version Banner Leak
Severity: Low
Target: https://api.payments.fintechglobal.com/
Port: 443/TCP (HTTPS)
Description: The web server exposes exact Nginx and OpenSSL version numbers in HTTP response headers and does not supply an HSTS header.
Impact: Minor reconnaissance assistance to adversaries.
Remediation: Configure server_tokens off in Nginx configuration and add Strict-Transport-Security header.
"""

col_left, col_right = st.columns([1, 1])

with col_left:
    st.subheader("📝 Assessor Field Notes & Raw Logs")
    st.caption("Input raw tester observations, Burp request/response dumps, and notes:")
    
    notes_input = st.text_area(
        "Field Notes",
        value=SAMPLE_NOTES,
        height=480,
        label_visibility="collapsed"
    )

    current_hash = calculate_sha256(notes_input)
    st.markdown(f"""
    <div style="margin-top: 8px; margin-bottom: 16px;">
        <span style="font-size: 0.8rem; color: #8b949e; text-transform: uppercase;">🔐 Chain-of-Custody SHA-256 Digest:</span>
        <div class="hash-badge">{current_hash}</div>
    </div>
    """, unsafe_allow_html=True)

    parse_btn = st.button("⚡ Generate Structured Pentest Intelligence", type="primary", use_container_width=True)

if parse_btn or "current_report" in st.session_state:
    if parse_btn:
        with st.spinner("Analyzing observations, calculating CVSS 3.1, and auditing evidence fidelity..."):
            report = parse_assessment_notes(
                raw_text=notes_input,
                project_name=project_name,
                organization=organization,
                lead_assessor=lead_assessor,
                scope_str=scope_str
            )
            report.metadata.peer_reviewer = peer_reviewer
            st.session_state.current_report = report
    else:
        report = st.session_state.current_report

    with col_right:
        st.subheader("📊 Findings & Risk Matrix")
        
        # Risk Metric Cards with animated CSS
        total_findings = len(report.findings)
        verified_count = sum(1 for f in report.findings if f.evidence_status == EvidenceIntegrityStatus.VERIFIED_PRESENT)
        unverified_count = total_findings - verified_count

        mc1, mc2, mc3 = st.columns(3)
        with mc1:
            st.markdown(f"""
            <div class="metric-card-custom">
                <div class="metric-val">{total_findings}</div>
                <div class="metric-lbl">Total Findings</div>
            </div>
            """, unsafe_allow_html=True)
        with mc2:
            st.markdown(f"""
            <div class="metric-card-custom" style="border-color: rgba(63, 185, 80, 0.4);">
                <div class="metric-val" style="color: #3fb950;">{verified_count}</div>
                <div class="metric-lbl">Evidence Verified</div>
            </div>
            """, unsafe_allow_html=True)
        with mc3:
            flag_color = "#f85149" if unverified_count > 0 else "#8b949e"
            st.markdown(f"""
            <div class="metric-card-custom" style="border-color: {flag_color};">
                <div class="metric-val" style="color: {flag_color};">{unverified_count}</div>
                <div class="metric-lbl">Evidence Flags</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 18px;'></div>", unsafe_allow_html=True)

        # Tabs for Findings and Report Preview
        tab_findings, tab_matrix, tab_export = st.tabs(["🔍 Detailed Findings", "📈 Risk Matrix", "📥 Export Deliverables"])

        with tab_findings:
            for idx, f in enumerate(report.findings, 1):
                badge_html = f'<span class="badge-verified">Verified</span>' if f.evidence_status == EvidenceIntegrityStatus.VERIFIED_PRESENT else f'<span class="badge-unverified">Missing PoC</span>'
                with st.expander(f"{f.finding_id}: {f.title} ({f.severity.value})"):
                    
                    st.markdown(f"**Evidence Integrity:** {badge_html}", unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.markdown(f"**Target:** `{f.affected_target}`")
                        st.markdown(f"**Port / Protocol:** `{f.protocol_port or 'N/A'}`")
                        st.markdown(f"**Severity:** `{f.severity.value}`")
                    with c2:
                        st.markdown(f"**CVSS v3.1:** `{f.cvss_score:.1f}` (`{f.cvss_vector}`)")
                        st.markdown(f"**CWE:** `{f.cwe_id or 'N/A'}` ({f.cwe_name or ''})")
                        st.markdown(f"**OWASP WSTG:** `{f.wstg_id or 'N/A'}`")

                    st.markdown("#### Technical Description")
                    st.write(f.description)

                    st.markdown("#### Grounded Evidence / PoC")
                    if f.evidence_status == EvidenceIntegrityStatus.UNVERIFIED_MISSING:
                        st.warning("⚠️ Evidence Deficit: No reproduction commands or transaction logs provided in notes.")
                    st.code(f.raw_evidence, language="http")

                    st.markdown("#### Impact")
                    st.write(f.impact)

                    st.markdown("#### Remediation")
                    st.info(f"**Tactical:** {f.remediation_short}\n\n**Strategic:** {f.remediation_long}")

                    if f.references:
                        st.markdown("#### Authoritative Standards")
                        for ref in f.references:
                            st.markdown(f"- [{ref}]({ref})")

        with tab_matrix:
            st.markdown("### Executive Findings Matrix")
            matrix_data = []
            for f in report.findings:
                matrix_data.append({
                    "ID": f.finding_id,
                    "Title": f.title,
                    "Severity": f.severity.value,
                    "CVSS": f"{f.cvss_score:.1f}" if f.cvss_score else "N/A",
                    "OWASP Category": f.owasp_category or "N/A",
                    "Status": "Verified" if f.evidence_status == EvidenceIntegrityStatus.VERIFIED_PRESENT else "Flagged"
                })
            st.dataframe(matrix_data, use_container_width=True)

            st.markdown("### Methodology Overview")
            st.info(report.methodology_overview)

        with tab_export:
            st.markdown("### 📤 Client Deliverables")
            st.write("Generate executive and technical deliverable reports in standard formats.")

            md_data = export_markdown_report(report)
            html_data = export_html_report(report)
            json_data = report.model_dump_json(indent=2)

            d1, d2, d3 = st.columns(3)
            with d1:
                st.download_button(
                    label="📄 Markdown Report (.md)",
                    data=md_data,
                    file_name=f"{project_name.lower().replace(' ', '_')}_report.md",
                    mime="text/markdown",
                    use_container_width=True
                )
            with d2:
                st.download_button(
                    label="🌐 HTML Executive Deliverable (.html)",
                    data=html_data,
                    file_name=f"{project_name.lower().replace(' ', '_')}_report.html",
                    mime="text/html",
                    use_container_width=True
                )
            with d3:
                st.download_button(
                    label="💾 Raw JSON Schema (.json)",
                    data=json_data,
                    file_name=f"{project_name.lower().replace(' ', '_')}_report.json",
                    mime="application/json",
                    use_container_width=True
                )
