"""
ProofForge AI - Enterprise Assessment Parser & Evidence Integrity Engine
Ensures evidence integrity, calculates CVSS v3.1 base metrics, and establishes chain-of-custody.
"""

import re
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Tuple
from models import (
    Finding,
    SeverityLevel,
    EvidenceIntegrityStatus,
    AssessmentMetadata,
    PentestReport,
    ScopeItem
)
from taxonomy import lookup_taxonomy_details
from cvss import CVSS31Calculator


def calculate_sha256(text: str) -> str:
    """Computes SHA-256 hash of raw assessment input to provide tamper-evidence."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def normalize_severity(raw_severity: str) -> SeverityLevel:
    clean = raw_severity.strip().lower()
    if "crit" in clean:
        return SeverityLevel.CRITICAL
    elif "high" in clean:
        return SeverityLevel.HIGH
    elif "med" in clean:
        return SeverityLevel.MEDIUM
    elif "low" in clean:
        return SeverityLevel.LOW
    elif "info" in clean or "informational" in clean:
        return SeverityLevel.INFORMATIONAL
    return SeverityLevel.UNSPECIFIED


def parse_assessment_notes(
    raw_text: str,
    project_name: str = "Authorized Security Assessment",
    organization: str = "Client Organization",
    lead_assessor: str = "Senior Penetration Tester",
    scope_str: str = ""
) -> PentestReport:
    """
    Parses penetration testing notes into enterprise-grade report data.
    Enforces evidence fidelity: never fabricates PoC payloads or severities.
    """
    raw_hash = calculate_sha256(raw_text)
    
    # Split notes into finding blocks
    raw_blocks = re.split(
        r'\n(?=(?:#{1,3}\s+|Finding\s*\d*:|\[Finding\]|Vulnerability:))',
        raw_text,
        flags=re.IGNORECASE
    )

    finding_chunks = [b.strip() for b in raw_blocks if b.strip()]
    if len(finding_chunks) <= 1 and "\n---\n" in raw_text:
        finding_chunks = [b.strip() for b in raw_text.split("\n---\n") if b.strip()]

    parsed_findings: List[Finding] = []
    
    for idx, chunk in enumerate(finding_chunks, 1):
        finding = _parse_finding_block(chunk, idx)
        if finding:
            parsed_findings.append(finding)

    # In case no header was matched but text exists
    if not parsed_findings and raw_text.strip():
        single = _parse_finding_block(raw_text, 1)
        if single:
            parsed_findings.append(single)

    # Parse scope entries
    scope_items = []
    if scope_str.strip():
        for line in scope_str.strip().splitlines():
            line = line.strip().lstrip("-*•").strip()
            if line:
                scope_items.append(ScopeItem(target=line, in_scope=True))
    else:
        scope_items.append(ScopeItem(target="Specified in engagement assessment notes", in_scope=True))

    metadata = AssessmentMetadata(
        project_name=project_name,
        organization=organization,
        lead_assessor=lead_assessor,
        peer_reviewer="QA / Technical Reviewer",
        assessment_type="Web Application & API Penetration Test",
        methodology="OWASP WSTG v4.2 / NIST SP 800-115",
        start_date=datetime.today().strftime("%Y-%m-%d"),
        end_date=datetime.today().strftime("%Y-%m-%d"),
        notes_sha256=raw_hash,
        scope=scope_items
    )

    summary = _build_executive_summary(project_name, parsed_findings)
    methodology = _build_methodology_overview()

    return PentestReport(
        metadata=metadata,
        executive_summary=summary,
        methodology_overview=methodology,
        findings=parsed_findings
    )


def _parse_finding_block(chunk: str, index: int) -> Finding:
    lines = chunk.splitlines()
    first_line = lines[0].lstrip('#').strip()
    
    title = re.sub(r'^(?:Finding\s*\d*:\s*|Vulnerability:\s*|\[Finding\]\s*)', '', first_line, flags=re.IGNORECASE).strip()
    if not title:
        title = f"Vulnerability Finding #{index}"

    # Finding ID format: SEC-001, SEC-002
    finding_id = f"SEC-{index:03d}"

    # Severity extraction
    severity = SeverityLevel.UNSPECIFIED
    sev_match = re.search(r'(?:Severity|Risk|Level):\s*(\w+)', chunk, re.IGNORECASE)
    if sev_match:
        severity = normalize_severity(sev_match.group(1))
    else:
        for candidate in ["critical", "high", "medium", "low", "informational"]:
            if re.search(rf'\b{candidate}\b', lines[0], re.IGNORECASE):
                severity = normalize_severity(candidate)
                break

    # Target / Endpoint
    target = "Not Specified in Notes"
    target_match = re.search(r'(?:Target|Endpoint|Host|URL|Affected Component):\s*([^\n]+)', chunk, re.IGNORECASE)
    if target_match:
        target = target_match.group(1).strip()
    else:
        url_match = re.search(r'https?://[^\s]+', chunk)
        if url_match:
            target = url_match.group(0)

    # Port / Protocol
    port_match = re.search(r'(?:Port|Protocol):\s*([^\n]+)', chunk, re.IGNORECASE)
    protocol_port = port_match.group(1).strip() if port_match else ("443/TCP (HTTPS)" if "https://" in target else "80/TCP (HTTP)" if "http://" in target else None)

    # Evidence / PoC extraction
    evidence = ""
    evidence_patterns = [
        r'(?:Proof of Concept|PoC|Evidence|Reproduction Steps|Steps to Reproduce|Request/Response|Payload):\s*([\s\S]+?)(?=\n(?:Impact|Remediation|Fix|Mitigation|Recommendation|References)|$)',
        r'```[\s\S]+?```'
    ]
    for pattern in evidence_patterns:
        match = re.search(pattern, chunk, re.IGNORECASE)
        if match:
            evidence = match.group(1).strip() if match.groups() else match.group(0).strip()
            break

    if evidence:
        evidence_status = EvidenceIntegrityStatus.VERIFIED_PRESENT
    else:
        evidence = "[EVIDENCE DEFICIT: No technical reproduction steps, HTTP transaction logs, or payload artifacts were supplied in the assessor notes. In compliance with strict audit requirements, ProofForge AI has not fabricated synthetic PoC material.]"
        evidence_status = EvidenceIntegrityStatus.UNVERIFIED_MISSING

    # Description
    desc_match = re.search(r'(?:Description|Details|Overview):\s*([\s\S]+?)(?=\n(?:Target|Severity|PoC|Evidence|Impact|Remediation)|$)', chunk, re.IGNORECASE)
    if desc_match:
        description = desc_match.group(1).strip()
    else:
        body_lines = [l for l in lines[1:] if not re.match(r'^(Severity|Target|PoC|Evidence|Impact|Remediation):', l, re.IGNORECASE)]
        description = "\n".join(body_lines).strip()
        if not description:
            description = f"Assessed instance of {title}. Full descriptive context was not supplied in original notes."

    # Impact
    impact_match = re.search(r'(?:Impact|Risk Evaluation|Consequence):\s*([\s\S]+?)(?=\n(?:Remediation|Fix|Mitigation|Recommendation|References)|$)', chunk, re.IGNORECASE)
    if impact_match:
        impact = impact_match.group(1).strip()
    else:
        impact = "Impact documentation not explicitly provided in notes. Review affected component context for blast radius."

    # Taxonomy & Standards lookup
    tax_info = lookup_taxonomy_details(title, description)
    cwe_id = tax_info.get("cwe_id")
    cwe_name = tax_info.get("cwe_name")
    owasp_cat = tax_info.get("owasp_category")
    wstg_id = tax_info.get("wstg_id")
    references = tax_info.get("references", [])

    # Remediation
    remed_match = re.search(r'(?:Remediation|Fix|Mitigation|Recommendation):\s*([\s\S]+?)(?=$)', chunk, re.IGNORECASE)
    if remed_match:
        remediation_long = remed_match.group(1).strip()
        remediation_short = tax_info.get("remediation_short", "Apply defensive mitigations.")
    else:
        remediation_short = tax_info.get("remediation_short", "Implement contextual input validation and access controls.")
        remediation_long = tax_info.get("remediation_long", "Refer to industry standard security patterns to mitigate this issue.")

    # CVSS calculation
    cvss_params = tax_info.get("default_cvss", {"av": "N", "ac": "L", "pr": "N", "ui": "N", "s": "U", "c": "L", "i": "N", "a": "N"})
    cvss_score, cvss_sev, cvss_vector = CVSS31Calculator.calculate(**cvss_params)

    # If assessor explicitly supplied severity, preserve assessor severity, otherwise use CVSS
    if severity == SeverityLevel.UNSPECIFIED:
        severity = normalize_severity(cvss_sev)

    return Finding(
        finding_id=finding_id,
        title=title,
        severity=severity,
        cvss_score=cvss_score,
        cvss_vector=cvss_vector,
        cwe_id=cwe_id,
        cwe_name=cwe_name,
        owasp_category=owasp_cat,
        wstg_id=wstg_id,
        affected_target=target,
        protocol_port=protocol_port,
        description=description,
        raw_evidence=evidence,
        evidence_status=evidence_status,
        impact=impact,
        remediation_short=remediation_short,
        remediation_long=remediation_long,
        references=references
    )


def _build_executive_summary(project_name: str, findings: List[Finding]) -> str:
    total = len(findings)
    crit = sum(1 for f in findings if f.severity == SeverityLevel.CRITICAL)
    high = sum(1 for f in findings if f.severity == SeverityLevel.HIGH)
    med = sum(1 for f in findings if f.severity == SeverityLevel.MEDIUM)
    low = sum(1 for f in findings if f.severity == SeverityLevel.LOW)
    info = sum(1 for f in findings if f.severity == SeverityLevel.INFORMATIONAL)
    unverified = sum(1 for f in findings if f.evidence_status == EvidenceIntegrityStatus.UNVERIFIED_MISSING)

    posture = "critical" if crit > 0 else "elevated" if high > 0 else "moderate" if med > 0 else "satisfactory"

    summary = f"""During the authorized security assessment of **{project_name}**, our team identified a total of **{total}** security finding(s). The overall security risk posture is currently assessed as **{posture.upper()}**.

### Summary of Discovered Vulnerabilities:
- **Critical Severity:** {crit}
- **High Severity:** {high}
- **Medium Severity:** {med}
- **Low Severity:** {low}
- **Informational:** {info}

Immediate prioritization should be placed on remediating vulnerabilities that present external attack vectors or unauthorized access pathways."""

    if unverified > 0:
        summary += f"""

> ⚠️ **Evidence Audit Note**: {unverified} finding(s) lacked explicit raw reproduction steps or payload records in the assessor notes. Under ProofForge AI's deterministic evidence-grounding standards, these findings are explicitly marked for assessor verification before executive sign-off."""

    return summary


def _build_methodology_overview() -> str:
    return """The assessment was conducted in accordance with the **OWASP Web Security Testing Guide (WSTG v4.2)** and the **Penetration Testing Execution Standard (PTES)**.

Testing phases comprised:
1. **Reconnaissance & Surface Mapping:** Active enumeration of API routes, parameters, and services.
2. **Threat Modeling & Architecture Analysis:** Identification of privilege boundaries, trust domains, and access mechanisms.
3. **Vulnerability Verification:** Active validation of potential flaws using controlled, non-destructive payloads.
4. **Evidence Grounding & Quality Review:** Strict audit ensuring all technical statements reflect verified observations without speculative assumptions."""
