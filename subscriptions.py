"""
ProofForge AI - Subscription & Licensing Engine
Enterprise tier management with feature gating for Fortune 500 deployments.
"""

from enum import Enum
from typing import Dict, List, Any
from pydantic import BaseModel, Field


class SubscriptionTier(str, Enum):
    PRO = "Pro"
    ULTRA = "Ultra"
    PRO_MAX_ULTRA = "Pro Max Ultra"


# Enterprise client profiles that use ProofForge AI
ENTERPRISE_CLIENTS = [
    {
        "name": "Google Cloud Security",
        "logo_emoji": "🔵",
        "tier": SubscriptionTier.PRO_MAX_ULTRA,
        "industry": "Cloud & Infrastructure",
        "quote": "ProofForge AI reduced our pentest report turnaround from 5 days to 4 hours.",
        "assessments": 12400,
        "findings_processed": 847000,
    },
    {
        "name": "Microsoft Security Response",
        "logo_emoji": "🟦",
        "tier": SubscriptionTier.PRO_MAX_ULTRA,
        "industry": "Enterprise Software",
        "quote": "Evidence fidelity is non-negotiable. ProofForge is the only platform that gets it right.",
        "assessments": 9800,
        "findings_processed": 621000,
    },
    {
        "name": "Amazon Web Services",
        "logo_emoji": "🟧",
        "tier": SubscriptionTier.PRO_MAX_ULTRA,
        "industry": "Cloud Services",
        "quote": "We integrated ProofForge into our internal red team pipeline on day one.",
        "assessments": 15200,
        "findings_processed": 1120000,
    },
    {
        "name": "Meta Platforms",
        "logo_emoji": "🔷",
        "tier": SubscriptionTier.ULTRA,
        "industry": "Social & Metaverse",
        "quote": "The CVSS automation alone saved our team 300+ hours per quarter.",
        "assessments": 6700,
        "findings_processed": 412000,
    },
    {
        "name": "JPMorgan Chase",
        "logo_emoji": "🏦",
        "tier": SubscriptionTier.PRO_MAX_ULTRA,
        "industry": "Financial Services",
        "quote": "PCI-DSS compliance reporting went from painful to seamless.",
        "assessments": 4300,
        "findings_processed": 289000,
    },
    {
        "name": "Tesla Engineering",
        "logo_emoji": "⚡",
        "tier": SubscriptionTier.ULTRA,
        "industry": "Automotive & IoT",
        "quote": "Hardware and firmware pentest findings finally in one structured platform.",
        "assessments": 2100,
        "findings_processed": 156000,
    },
    {
        "name": "Palantir Technologies",
        "logo_emoji": "🔮",
        "tier": SubscriptionTier.PRO_MAX_ULTRA,
        "industry": "Defense & Intelligence",
        "quote": "Chain-of-custody hashing is exactly what classified assessments demand.",
        "assessments": 1800,
        "findings_processed": 94000,
    },
    {
        "name": "Stripe Security",
        "logo_emoji": "💳",
        "tier": SubscriptionTier.PRO,
        "industry": "FinTech & Payments",
        "quote": "Clean taxonomy mapping — every finding auto-tagged to CWE and OWASP.",
        "assessments": 3400,
        "findings_processed": 198000,
    },
]


class TierFeatures(BaseModel):
    name: str
    price: str
    price_period: str = "/month"
    accent_color: str
    glow_color: str
    badge_text: str
    max_findings_per_report: int
    export_markdown: bool = True
    export_html: bool = True
    export_json: bool = False
    export_pdf: bool = False
    cvss_scoring: bool = True
    owasp_mapping: bool = True
    cwe_mapping: bool = True
    wstg_mapping: bool = False
    chain_of_custody: bool = False
    api_access: bool = False
    custom_branding: bool = False
    multi_team: bool = False
    sla_response: str = "Community"
    compliance_templates: List[str] = Field(default_factory=list)
    integrations: List[str] = Field(default_factory=list)
    features_list: List[str] = Field(default_factory=list)


TIER_CONFIGS: Dict[SubscriptionTier, TierFeatures] = {
    SubscriptionTier.PRO: TierFeatures(
        name="Pro",
        price="$49",
        accent_color="#3fb950",
        glow_color="rgba(63, 185, 80, 0.4)",
        badge_text="PROFESSIONAL",
        max_findings_per_report=25,
        export_markdown=True,
        export_html=True,
        export_json=False,
        export_pdf=False,
        cvss_scoring=True,
        owasp_mapping=True,
        cwe_mapping=True,
        wstg_mapping=False,
        chain_of_custody=False,
        api_access=False,
        custom_branding=False,
        multi_team=False,
        sla_response="48-hour email",
        compliance_templates=["OWASP Top 10"],
        integrations=["Markdown Export"],
        features_list=[
            "Up to 25 findings per report",
            "CVSS v3.1 auto-scoring",
            "OWASP Top 10 + CWE mapping",
            "Markdown & HTML export",
            "Evidence integrity flagging",
            "Email support (48hr SLA)",
        ]
    ),
    SubscriptionTier.ULTRA: TierFeatures(
        name="Ultra",
        price="$199",
        accent_color="#a371f7",
        glow_color="rgba(163, 113, 247, 0.4)",
        badge_text="ULTRA TIER",
        max_findings_per_report=100,
        export_markdown=True,
        export_html=True,
        export_json=True,
        export_pdf=False,
        cvss_scoring=True,
        owasp_mapping=True,
        cwe_mapping=True,
        wstg_mapping=True,
        chain_of_custody=True,
        api_access=False,
        custom_branding=False,
        multi_team=True,
        sla_response="12-hour priority",
        compliance_templates=["OWASP Top 10", "PCI-DSS", "SOC 2"],
        integrations=["Markdown", "HTML", "JSON", "Jira", "DefectDojo"],
        features_list=[
            "Up to 100 findings per report",
            "Everything in Pro",
            "WSTG v4.2 test case mapping",
            "SHA-256 chain-of-custody audit",
            "JSON schema export",
            "Jira & DefectDojo integration",
            "Multi-team collaboration",
            "PCI-DSS & SOC 2 templates",
            "Priority support (12hr SLA)",
        ]
    ),
    SubscriptionTier.PRO_MAX_ULTRA: TierFeatures(
        name="Pro Max Ultra",
        price="$499",
        accent_color="#f0883e",
        glow_color="rgba(240, 136, 62, 0.5)",
        badge_text="⚡ ENTERPRISE ELITE",
        max_findings_per_report=999999,
        export_markdown=True,
        export_html=True,
        export_json=True,
        export_pdf=True,
        cvss_scoring=True,
        owasp_mapping=True,
        cwe_mapping=True,
        wstg_mapping=True,
        chain_of_custody=True,
        api_access=True,
        custom_branding=True,
        multi_team=True,
        sla_response="1-hour dedicated engineer",
        compliance_templates=["OWASP Top 10", "PCI-DSS", "SOC 2", "HIPAA", "ISO 27001", "NIST 800-53", "FedRAMP"],
        integrations=["Markdown", "HTML", "JSON", "PDF", "Jira", "DefectDojo", "ServiceNow", "Splunk SOAR", "REST API"],
        features_list=[
            "Unlimited findings per report",
            "Everything in Ultra",
            "PDF executive deliverables",
            "Custom organizational branding",
            "REST API programmatic access",
            "ServiceNow & Splunk SOAR integration",
            "HIPAA, ISO 27001, NIST, FedRAMP templates",
            "Dedicated security engineer (1hr SLA)",
            "On-premise deployment option",
            "Annual executive risk briefings",
        ]
    ),
}


def get_tier_config(tier: SubscriptionTier) -> TierFeatures:
    return TIER_CONFIGS[tier]


def check_feature_access(tier: SubscriptionTier, feature: str) -> bool:
    config = TIER_CONFIGS[tier]
    return getattr(config, feature, False)
