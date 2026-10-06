"""
ProofForge AI - Enterprise Penetration Testing Intelligence Platform
Professional Streamlit Application
"""

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

# Custom High-Tech Cybersecurity Styling
st.markdown("""
<style>
    .reportview-container {
        background: #0d1117;
    }
    .main-title {
        font-family: 'Inter', -apple-system, sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: #f0f6fc;
        letter-spacing: -0.02em;
        margin-bottom: 2px;
    }
    .badge-sub {
        font-size: 0.9rem;
        color: #58a6ff;
        font-weight: 500;
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        padding: 16px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🛡️ ProofForge AI</div>', unsafe_allow_html=True)
st.markdown('<div class="badge-sub">ENTERPRISE PENETRATION TESTING INTELLIGENCE & DETERMINISTIC EVIDENCE GROUNDING</div>', unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.header("📋 Engagement Parameters")
    project_name = st.text_input("Engagement / System Name", value="Global Payments Portal API Assessment")
    organization = st.text_input("Target Organization", value="FinTech Global Corp")
    lead_assessor = st.text_input("Lead Assessor", value="Alex Rivera, OSCP / CISSP")
    peer_reviewer = st.text_input("Peer Reviewer / QA", value="Samantha Vance, Principal Consultant")
    
    st.markdown("---")
    st.subheader("🎯 Authorized Scope")
    scope_str = st.text_area(
        "Scope Definition (1 target per line)",
        value="https://api.payments.fintechglobal.com/v2/ (Staging)\n10.240.12.0/24 (Payment Gateway Services)",
        height=90
    )

    st.markdown("---")
    st.subheader("🔒 Integrity & Security Principles")
    st.caption(
        "ProofForge AI deterministically adheres to **zero synthetic evidence generation**. "
        "Missing reproduction steps, unverified payloads, and speculative severities are flagged "
        "rather than hallucinated."
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
    st.caption("Input raw notes, burp suite snippets, and tool findings:")
    
    notes_input = st.text_area(
        "Field Notes",
        value=SAMPLE_NOTES,
        height=520,
        label_visibility="collapsed"
    )

    # Real-time SHA-256 chain of custody calculation
    current_hash = calculate_sha256(notes_input)
    st.caption(f"🔐 **Chain-of-Custody SHA-256:** `{current_hash}`")

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
        
        # Risk Metric Cards
        total_findings = len(report.findings)
        verified_count = sum(1 for f in report.findings if f.evidence_status == EvidenceIntegrityStatus.VERIFIED_PRESENT)
        unverified_count = total_findings - verified_count

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Findings", total_findings)
        m2.metric("Evidence Verified", f"{verified_count}/{total_findings}")
        m3.metric("Evidence Flags", unverified_count, delta_color="inverse")

        # Tabs for Findings and Report Preview
        tab_findings, tab_matrix, tab_export = st.tabs(["🔍 Detailed Findings", "📈 Risk Matrix", "📥 Export Deliverables"])

        with tab_findings:
            for idx, f in enumerate(report.findings, 1):
                status_icon = "🟢" if f.evidence_status == EvidenceIntegrityStatus.VERIFIED_PRESENT else "🔴"
                with st.expander(f"{f.finding_id}: {f.title} ({f.severity.value}) {status_icon}"):
                    
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
