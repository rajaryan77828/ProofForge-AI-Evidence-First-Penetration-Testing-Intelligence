"""
ProofForge AI - Enterprise Report Generator
Produces formal penetration testing reports in Markdown and executive-styled HTML.
"""

import os
import base64
from models import PentestReport, SeverityLevel, EvidenceIntegrityStatus

try:
    import markdown
except ImportError:
    markdown = None


def _get_base64_asset(filename: str) -> str:
    path = os.path.join(os.path.dirname(__file__), "assets", filename)
    if os.path.exists(path):
        with open(path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    return ""



def export_markdown_report(report: PentestReport) -> str:
    """Generates an enterprise-standard penetration testing report in Markdown."""
    m = report.metadata
    md = []

    # Title & Metadata
    md.append(f"# Technical Penetration Testing Assessment Report")
    md.append(f"### Engagement: {m.project_name}")
    md.append("")
    md.append("| Assessment Parameter | Detail |")
    md.append("|---|---|")
    md.append(f"| **Target Organization** | {m.organization} |")
    md.append(f"| **Lead Assessor** | {m.lead_assessor} |")
    md.append(f"| **Peer Reviewer / QA** | {m.peer_reviewer} |")
    md.append(f"| **Assessment Methodology** | {m.methodology} |")
    md.append(f"| **Assessment Period** | {m.start_date} to {m.end_date} |")
    md.append(f"| **Chain-of-Custody (SHA-256)** | `{m.notes_sha256[:16]}...{m.notes_sha256[-8:]}` |")
    md.append("\n---\n")

    # Scope
    md.append("## 1. Assessment Scope")
    md.append("| Target Asset | Type | In-Scope Status |")
    md.append("|---|---|---|")
    for s in m.scope:
        md.append(f"| `{s.target}` | {s.target_type} | {'✅ Authorized' if s.in_scope else '❌ Out of Scope'} |")
    md.append("\n---\n")

    # Executive Summary
    md.append("## 2. Executive Summary")
    md.append(report.executive_summary)
    md.append("\n---\n")

    # Methodology
    md.append("## 3. Assessment Methodology")
    md.append(report.methodology_overview)
    md.append("\n---\n")

    # Findings Matrix Table
    md.append("## 4. Vulnerability Findings Matrix")
    md.append("| ID | Finding Title | Severity | CVSS v3.1 | OWASP Top 10 | CWE | Evidence Status |")
    md.append("|---|---|---|---|---|---|---|")
    for f in report.findings:
        cwe_str = f.cwe_id if f.cwe_id else "N/A"
        cvss_str = f"{f.cvss_score:.1f}" if f.cvss_score is not None else "N/A"
        status_icon = "✅ Verified" if f.evidence_status == EvidenceIntegrityStatus.VERIFIED_PRESENT else "⚠️ Deficit Flagged"
        md.append(f"| **{f.finding_id}** | {f.title} | **{f.severity.value}** | {cvss_str} | {f.owasp_category or 'N/A'} | {cwe_str} | {status_icon} |")
    md.append("\n---\n")

    # Detailed Findings
    md.append("## 5. Detailed Technical Findings & Remediation\n")
    for f in report.findings:
        md.append(f"### {f.finding_id}: {f.title}")
        md.append(f"- **Severity:** `{f.severity.value}`")
        if f.cvss_score:
            md.append(f"- **CVSS v3.1 Score:** `{f.cvss_score:.1f}` (`{f.cvss_vector}`)")
        md.append(f"- **Target Asset:** `{f.affected_target}` ({f.protocol_port or 'N/A'})")
        if f.owasp_category:
            md.append(f"- **OWASP Category:** {f.owasp_category}")
        if f.wstg_id:
            md.append(f"- **OWASP WSTG Test:** `{f.wstg_id}`")
        if f.cwe_id:
            md.append(f"- **CWE:** [{f.cwe_id}] {f.cwe_name or ''}")

        md.append("\n#### Technical Description")
        md.append(f.description)

        md.append("\n#### Technical Evidence & Reproduction Steps")
        if f.evidence_status == EvidenceIntegrityStatus.UNVERIFIED_MISSING:
            md.append("> ⚠️ **Assessor Evidence Notice**: ProofForge AI did not detect reproduction commands or raw logs in tester notes. No synthetic PoC was generated.")
        md.append("```http")
        md.append(f.raw_evidence)
        md.append("```")

        md.append("\n#### Technical & Business Impact")
        md.append(f.impact)

        md.append("\n#### Tactical Remediation")
        md.append(f"{f.remediation_short}")

        md.append("\n#### Strategic Architecture Guidance")
        md.append(f"{f.remediation_long}")

        if f.references:
            md.append("\n#### Authoritative References")
            for ref in f.references:
                md.append(f"- [{ref}]({ref})")

        md.append("\n---\n")

    return "\n".join(md)


def export_html_report(report: PentestReport) -> str:
    """Renders high-grade styled HTML report suitable for client deliverables or PDF printing."""
    md_content = export_markdown_report(report)
    
    banner_b64 = _get_base64_asset("banner.jpg")
    logo_b64 = _get_base64_asset("logo.jpg")

    banner_html = ""
    if banner_b64:
        banner_html = f'<img src="data:image/jpeg;base64,{banner_b64}" style="width: 100%; max-height: 220px; object-fit: cover; border-radius: 8px; margin-bottom: 24px; border: 1px solid var(--border-color);" alt="Assessment Banner" />'

    logo_html = ""
    if logo_b64:
        logo_html = f'<img src="data:image/jpeg;base64,{logo_b64}" style="width: 50px; height: 50px; border-radius: 50%; vertical-align: middle; margin-right: 12px; border: 1px solid var(--accent-blue);" alt="Logo" />'

    if markdown:
        html_body = markdown.markdown(md_content, extensions=['tables', 'fenced_code'])
    else:
        html_body = f"<pre style='white-space: pre-wrap; font-family: inherit;'>{md_content}</pre>"


    # Professional Cybersecurity Consulting CSS
    styled_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Penetration Test Report - {report.metadata.project_name}</title>
    <style>
        :root {{
            --bg-color: #0d1117;
            --surface-color: #161b22;
            --border-color: #30363d;
            --text-primary: #e6edf3;
            --text-secondary: #8b949e;
            --accent-blue: #58a6ff;
            --accent-red: #f85149;
            --accent-orange: #d29922;
            --accent-green: #3fb950;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-primary);
            line-height: 1.65;
            margin: 0;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 1040px;
            margin: 0 auto;
            background-color: var(--surface-color);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 56px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        }}
        h1, h2, h3, h4 {{
            color: #ffffff;
            font-weight: 600;
        }}
        h1 {{
            font-size: 2.2rem;
            margin-top: 0;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 16px;
        }}
        h2 {{
            font-size: 1.5rem;
            margin-top: 40px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 8px;
            color: var(--accent-blue);
        }}
        h3 {{
            font-size: 1.25rem;
            margin-top: 32px;
            color: #f0f6fc;
        }}
        h4 {{
            font-size: 1rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: var(--text-secondary);
            margin-top: 20px;
            margin-bottom: 8px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 24px 0;
            font-size: 0.95rem;
        }}
        th, td {{
            border: 1px solid var(--border-color);
            padding: 12px 16px;
            text-align: left;
        }}
        th {{
            background-color: #21262d;
            color: #ffffff;
            font-weight: 600;
        }}
        tr:nth-child(even) {{
            background-color: #0d1117;
        }}
        code {{
            background-color: #21262d;
            color: #79c0ff;
            padding: 3px 6px;
            border-radius: 4px;
            font-family: "Consolas", "Courier New", monospace;
            font-size: 0.88em;
        }}
        pre {{
            background-color: #0b0e14;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 16px;
            overflow-x: auto;
        }}
        pre code {{
            background-color: transparent;
            color: #38bdf8;
            padding: 0;
        }}
        blockquote {{
            border-left: 4px solid var(--accent-orange);
            background-color: rgba(210, 153, 34, 0.1);
            color: #e3b341;
            padding: 12px 18px;
            margin: 16px 0;
            border-radius: 0 6px 6px 0;
        }}
        hr {{
            border: none;
            border-top: 1px solid var(--border-color);
            margin: 40px 0;
        }}
        a {{
            color: var(--accent-blue);
            text-decoration: none;
        }}
        a:hover {{
            text-decoration: underline;
        }}
        @media print {{
            body {{
                background-color: #fff;
                color: #000;
                padding: 0;
            }}
            .container {{
                border: none;
                box-shadow: none;
                padding: 0;
                background-color: #fff;
            }}
            pre {{
                background-color: #f6f8fa;
                border: 1px solid #d0d7de;
            }}
            pre code {{
                color: #24292f;
            }}
            th {{
                background-color: #f6f8fa;
                color: #000;
            }}
            th, td {{
                border-color: #d0d7de;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        {banner_html}
        {html_body}
    </div>
</body>
</html>"""
    return styled_html
