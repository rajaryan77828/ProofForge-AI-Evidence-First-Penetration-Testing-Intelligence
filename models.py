"""
ProofForge AI - Enterprise Data Models
Complies with industry reporting standards: PTES, OWASP WSTG, and NIST SP 800-115.
"""

from typing import List, Optional, Dict
from enum import Enum
from pydantic import BaseModel, Field


class SeverityLevel(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFORMATIONAL = "Informational"
    UNSPECIFIED = "Unspecified"


class EvidenceIntegrityStatus(str, Enum):
    VERIFIED_PRESENT = "Verified (Supplied in Notes)"
    UNVERIFIED_MISSING = "Flagged: Missing Evidence"
    PARTIAL = "Partial Evidence Provided"


class Finding(BaseModel):
    finding_id: str = Field(..., description="Unique finding tracking ID, e.g., SEC-001")
    title: str = Field(..., description="Vulnerability title")
    severity: SeverityLevel = Field(default=SeverityLevel.UNSPECIFIED)
    cvss_score: Optional[float] = Field(default=None, description="CVSS v3.1 Base Score (0.0 - 10.0)")
    cvss_vector: Optional[str] = Field(default=None, description="CVSS:3.1 Vector String")
    
    # Classification
    cwe_id: Optional[str] = Field(default=None, description="CWE identifier, e.g., CWE-89")
    cwe_name: Optional[str] = Field(default=None, description="CWE name/title")
    owasp_category: Optional[str] = Field(default=None, description="OWASP Top 10 category")
    wstg_id: Optional[str] = Field(default=None, description="OWASP WSTG Test ID, e.g., WSTG-INPV-05")
    
    # Assets
    affected_target: str = Field(default="Not Specified", description="Target host, IP, URL, or API endpoint")
    protocol_port: Optional[str] = Field(default=None, description="Port and protocol, e.g., 443/TCP")

    # Strict Grounded Technical Data
    description: str = Field(..., description="Vulnerability technical description")
    raw_evidence: str = Field(..., description="Exact raw reproduction steps, HTTP request/response, or logs")
    evidence_status: EvidenceIntegrityStatus = Field(default=EvidenceIntegrityStatus.VERIFIED_PRESENT)
    
    impact: str = Field(..., description="Technical impact and business risk exposure")
    remediation_short: str = Field(default="", description="Quick tactical remediation step")
    remediation_long: str = Field(..., description="Strategic architectural remediation guidance")
    references: List[str] = Field(default_factory=list, description="Defensive vendor or advisory references")


class ScopeItem(BaseModel):
    target: str
    target_type: str = "Web Application / API"
    in_scope: bool = True
    notes: Optional[str] = None


class AssessmentMetadata(BaseModel):
    project_name: str
    organization: str = "Client Organization"
    lead_assessor: str = "Senior Penetration Tester"
    peer_reviewer: str = "Principal Security Consultant"
    assessment_type: str = "Web Application & API Penetration Test"
    methodology: str = "OWASP WSTG v4.2 / PTES Standard"
    start_date: str
    end_date: str
    notes_sha256: str = Field(default="", description="Cryptographic SHA-256 hash of original assessment notes")
    scope: List[ScopeItem] = Field(default_factory=list)


class PentestReport(BaseModel):
    metadata: AssessmentMetadata
    executive_summary: str
    methodology_overview: str
    findings: List[Finding] = Field(default_factory=list)
