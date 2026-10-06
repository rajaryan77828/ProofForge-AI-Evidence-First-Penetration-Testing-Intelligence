"""
ProofForge AI - Enterprise Verification & Test Suite
"""

from parser import parse_assessment_notes, calculate_sha256
from cvss import CVSS31Calculator
from models import SeverityLevel, EvidenceIntegrityStatus
from report_generator import export_markdown_report, export_html_report


def test_cvss_calculation():
    # Base score test for standard critical network vector
    score, sev, vector = CVSS31Calculator.calculate(
        av="N", ac="L", pr="N", ui="N", s="U", c="H", i="H", a="H"
    )
    assert score == 10.0
    assert sev == "Critical"

    assert "CVSS:3.1/AV:N" in vector


def test_parser_and_integrity_audit():
    sample_notes = """### Finding 1: SQL Injection
Severity: High
Target: https://api.corp.local/users?id=1
Description: User input in query string is executed without parameterized queries.
PoC:
GET /users?id=1%27%20OR%201=1-- HTTP/1.1
Result: Dumped table schema.
Impact: Arbitrary data extraction from primary SQL database.
Remediation: Adopt prepared statements.

### Finding 2: Unverified Information Disclosure
Severity: Low
Target: https://api.corp.local/test
Description: Missing defensive headers observed.
Impact: Low reconnaissance aid.
"""
    hash_val = calculate_sha256(sample_notes)
    assert len(hash_val) == 64

    report = parse_assessment_notes(sample_notes, project_name="Enterprise Test")
    assert len(report.findings) == 2
    assert report.metadata.notes_sha256 == hash_val

    # First finding (Verified)
    f1 = report.findings[0]
    assert f1.finding_id == "SEC-001"
    assert f1.cwe_id == "CWE-89"
    assert f1.wstg_id == "WSTG-INPV-05"
    assert f1.evidence_status == EvidenceIntegrityStatus.VERIFIED_PRESENT
    assert "Dumped table schema" in f1.raw_evidence

    # Second finding (Unverified PoC - security challenge)
    f2 = report.findings[1]
    assert f2.finding_id == "SEC-002"
    assert f2.evidence_status == EvidenceIntegrityStatus.UNVERIFIED_MISSING
    assert "EVIDENCE DEFICIT" in f2.raw_evidence

    # Report export checks
    md = export_markdown_report(report)
    assert "SEC-001" in md
    assert "Chain-of-Custody" in md
    assert "WSTG-INPV-05" in md

    html = export_html_report(report)
    assert "<!DOCTYPE html>" in html
    assert "Enterprise Test" in html

    json_str = report.model_dump_json()
    assert "SEC-001" in json_str

    print("All enterprise ProofForge AI verification tests passed successfully!")


if __name__ == "__main__":
    test_cvss_calculation()
    test_parser_and_integrity_audit()
