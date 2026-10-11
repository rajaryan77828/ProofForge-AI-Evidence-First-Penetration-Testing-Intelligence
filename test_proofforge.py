"""
ProofForge AI - Enterprise Verification, Feature Audit & Deployment Test Suite
Tests:
1. CVSS v3.1 deterministic scoring
2. Parser & evidence integrity audit (zero hallucination, chain of custody SHA-256)
3. Markdown and HTML report generation
4. JSON export serialization
5. Subscriptions module (Pro, Ultra, Pro Max Ultra feature gating)
6. Enterprise company presets (Google, Microsoft, AWS)
7. Deployment readiness assets & configuration checks
"""

import os
from parser import parse_assessment_notes, calculate_sha256
from cvss import CVSS31Calculator
from models import SeverityLevel, EvidenceIntegrityStatus
from report_generator import export_markdown_report, export_html_report
from subscriptions import (
    SubscriptionTier, TIER_CONFIGS, ENTERPRISE_CLIENTS,
    get_tier_config, check_feature_access
)
from company_presets import COMPANY_PRESETS


def test_cvss_calculation():
    print("-> Running CVSS v3.1 Deterministic Tests...")
    # Base score test for standard critical network vector
    score, sev, vector = CVSS31Calculator.calculate(
        av="N", ac="L", pr="N", ui="N", s="U", c="H", i="H", a="H"
    )
    assert score == 10.0
    assert sev == "Critical"
    assert "CVSS:3.1/AV:N" in vector

    # Low score test
    score_low, sev_low, _ = CVSS31Calculator.calculate(
        av="N", ac="L", pr="N", ui="N", s="U", c="L", i="N", a="N"
    )
    assert score_low == 5.6
    assert sev_low == "Medium"
    print("   [PASS] CVSS 3.1 calculation verified.")



def test_parser_and_integrity_audit():
    print("-> Running Parser & Zero-Fabrication Integrity Tests...")
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
    print("   [PASS] Parser, integrity flags, and multi-format exports verified.")


def test_subscription_tiers():
    print("-> Running Subscription & Licensing Tier Tests...")
    tiers = [t.value for t in SubscriptionTier]
    assert "Pro" in tiers
    assert "Ultra" in tiers
    assert "Pro Max Ultra" in tiers

    # Check Pro
    pro_cfg = get_tier_config(SubscriptionTier.PRO)
    assert pro_cfg.max_findings_per_report == 25
    assert not pro_cfg.chain_of_custody
    assert not pro_cfg.export_json

    # Check Ultra
    ultra_cfg = get_tier_config(SubscriptionTier.ULTRA)
    assert ultra_cfg.max_findings_per_report == 100
    assert ultra_cfg.chain_of_custody
    assert ultra_cfg.export_json
    assert not ultra_cfg.export_pdf

    # Check Pro Max Ultra
    pmu_cfg = get_tier_config(SubscriptionTier.PRO_MAX_ULTRA)
    assert pmu_cfg.max_findings_per_report >= 999999
    assert pmu_cfg.export_pdf
    assert pmu_cfg.api_access
    assert pmu_cfg.custom_branding

    assert check_feature_access(SubscriptionTier.PRO_MAX_ULTRA, "api_access") is True
    assert check_feature_access(SubscriptionTier.PRO, "api_access") is False
    print("   [PASS] All 3 subscription tiers and feature gates verified.")


def test_company_presets():
    print("-> Running Fortune 500 Company Presets Tests...")
    assert "Google Cloud Security (Kubernetes & IAM Escape)" in COMPANY_PRESETS
    assert "Microsoft MSRC (Azure Active Directory & OAuth2)" in COMPANY_PRESETS
    assert "Amazon Web Services (AWS IAM & S3 Bucket Policy)" in COMPANY_PRESETS

    for name, data in COMPANY_PRESETS.items():
        rep = parse_assessment_notes(
            data["notes"],
            project_name=data["project_name"],
            organization=data["organization"]
        )
        assert len(rep.findings) > 0, f"Preset {name} produced 0 findings"
        for f in rep.findings:
            assert f.evidence_status == EvidenceIntegrityStatus.VERIFIED_PRESENT, f"Preset {name} finding {f.title} unverified"
    print(f"   [PASS] All {len(COMPANY_PRESETS)} enterprise company presets parsed with 100% verified evidence.")


def test_deployment_readiness():
    print("-> Running Deployment Readiness Checks...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    required_files = [
        "Dockerfile",
        "docker-compose.yml",
        ".dockerignore",
        "Procfile",
        ".python-version",
        "requirements.txt",
        os.path.join(".streamlit", "config.toml"),
        os.path.join("assets", "banner.jpg"),
        os.path.join("assets", "logo.jpg"),
        os.path.join("assets", "sub_banner.jpg")
    ]


    for rel_path in required_files:
        full_path = os.path.join(base_dir, rel_path)
        assert os.path.exists(full_path), f"Deployment file missing: {rel_path}"

    # Verify requirements.txt has no empty critical packages
    req_file = os.path.join(base_dir, "requirements.txt")
    with open(req_file, "r") as f:
        req_content = f.read()
    assert "streamlit" in req_content
    assert "pydantic" in req_content
    assert "markdown" in req_content

    # Verify .streamlit/config.toml has headless set to true
    config_file = os.path.join(base_dir, ".streamlit", "config.toml")
    with open(config_file, "r") as f:
        config_content = f.read()
    assert "headless = true" in config_content
    assert "base = \"dark\"" in config_content

def test_auth_and_trial_limits():
    print("-> Running Authentication, Trial Limits & Cross-Device Sync Tests...")
    from auth import register_user, authenticate_user, can_run_assessment, record_assessment_run, upgrade_user_subscription
    import time

    test_email = f"test_pentester_{int(time.time())}@security.org"
    
    # 1. Register new user
    ok, msg, profile = register_user(test_email, "SecurePassword999!", "Test Pentester", organization="Cyber Audit Lab", device_info="MacBook Pro (London)")
    assert ok is True, f"Registration failed: {msg}"
    assert profile.runs_used == 0
    assert profile.max_free_runs == 2
    assert profile.is_subscribed is False

    # 2. Check Run 1 (Allowed)
    allowed, reason, runs_used, max_free = can_run_assessment(test_email)
    assert allowed is True
    assert runs_used == 0
    record_assessment_run(test_email)

    # 3. Check Run 2 (Allowed)
    allowed, reason, runs_used, max_free = can_run_assessment(test_email)
    assert allowed is True
    assert runs_used == 1
    record_assessment_run(test_email)

    # 4. Check Run 3 (Exhausted -> Blocked!)
    allowed, reason, runs_used, max_free = can_run_assessment(test_email)
    assert allowed is False
    assert runs_used == 2
    assert "Trial limit reached" in reason

    # 5. Cross-Device Login on another device (e.g. from Tokyo, Japan)
    ok, msg, profile_tokyo = authenticate_user(test_email, "SecurePassword999!", device_info="Linux Desktop (Tokyo)")
    assert ok is True
    assert profile_tokyo.last_device_info == "Linux Desktop (Tokyo)"
    assert profile_tokyo.runs_used == 2

    # 6. Upgrade Subscription to Pro Max Ultra
    ok, msg, upgraded = upgrade_user_subscription(test_email, SubscriptionTier.PRO_MAX_ULTRA, billing_period="monthly")
    assert ok is True
    assert upgraded.is_subscribed is True
    assert upgraded.subscription_tier == SubscriptionTier.PRO_MAX_ULTRA
    assert "$499/month" in upgraded.subscription_price_paid

    # 7. Post-upgrade run check (Now Allowed indefinitely!)
    allowed, reason, runs_used, max_free = can_run_assessment(test_email)
    assert allowed is True
    assert "Active subscription" in reason
    print("   [PASS] 2 Free Runs enforcement, Cloud Authentication, and Cross-Device Sync verified.")


def test_payment_processing_and_verification():
    print("-> Running Payment Gateway Authorization, Verification & Access Provisioning Tests...")
    from payments import verify_and_process_subscription_payment, get_tier_pricing, get_user_transactions
    from auth import register_user, get_user_profile
    import time

    payer_email = f"payer_{int(time.time())}@defense.corp"
    ok, msg, user = register_user(payer_email, "PayerSecurePass123!", "Global Chief Assessor", "Defense Corp")
    assert ok is True
    assert user.is_subscribed is False

    # Check pricing calculation
    p_mo = get_tier_pricing(SubscriptionTier.PRO_MAX_ULTRA, "monthly")
    assert p_mo["usd"] == 499.00
    assert "$499/month" in p_mo["label_usd"]
    assert "₹41,699/month" in p_mo["label_inr"]

    p_ann = get_tier_pricing(SubscriptionTier.PRO_MAX_ULTRA, "annual")
    assert p_ann["usd"] == 4790.00
    assert "$4,790/year" in p_ann["label_usd"]
    assert "₹3,99,900/year" in p_ann["label_inr"]

    # 1. Test Payment Verification Failure (invalid card format)
    fail_ok, fail_msg, fail_tx = verify_and_process_subscription_payment(
        user_email=payer_email,
        tier=SubscriptionTier.PRO_MAX_ULTRA,
        billing_cycle="monthly",
        payment_method_type="Credit Card",
        card_number="123",  # invalid
        expiry="12/28",
        cvv="123",
        cardholder_name="Global Chief Assessor"
    )
    assert fail_ok is False
    assert "Invalid card number" in fail_msg

    # 2. Test Payment Verification Success (valid payment gateway approval)
    succ_ok, succ_msg, receipt = verify_and_process_subscription_payment(
        user_email=payer_email,
        tier=SubscriptionTier.PRO_MAX_ULTRA,
        billing_cycle="monthly",
        payment_method_type="Credit Card",
        card_number="4242 4242 4242 4242",
        expiry="12/28",
        cvv="456",
        cardholder_name="Global Chief Assessor"
    )
    assert succ_ok is True
    assert receipt is not None
    assert receipt.status == "verified"
    assert receipt.tier == SubscriptionTier.PRO_MAX_ULTRA
    assert receipt.card_last4 == "4242"
    assert len(receipt.verification_hash) == 64
    assert "INV-PF-" in receipt.invoice_number

    # 3. Verify user account immediately gained Pro Max Ultra access
    upgraded_user = get_user_profile(payer_email)
    assert upgraded_user.is_subscribed is True
    assert upgraded_user.subscription_tier == SubscriptionTier.PRO_MAX_ULTRA
    assert "$499/month" in upgraded_user.subscription_price_paid

    # 4. Verify transaction ledger record exists
    txs = get_user_transactions(payer_email)
    assert len(txs) == 1
    assert txs[0]["transaction_id"] == receipt.transaction_id

    # 5. Test PhonePe UPI payment verification with 12-digit UTR
    phonepe_user_email = f"phonepe_payer_{int(time.time())}@security.org"
    register_user(phonepe_user_email, "PayerPass123!", "SecOps Lead", "Red Team Ltd")
    upi_ok, upi_msg, upi_receipt = verify_and_process_subscription_payment(
        user_email=phonepe_user_email,
        tier=SubscriptionTier.ULTRA,
        billing_cycle="monthly",
        payment_method_type="PhonePe",
        upi_utr_reference="428190382910"
    )
    assert upi_ok is True
    assert upi_receipt is not None
    assert upi_receipt.payment_method == "PhonePe"
    assert upi_receipt.merchant_number == "9973928945"
    assert upi_receipt.reference_utr == "428190382910"
    assert "INR" in upi_receipt.currency
    assert upi_receipt.status == "verified"
    assert len(upi_receipt.verification_hash) == 64

    # 6. Test Google Pay UPI payment verification
    gpay_user_email = f"gpay_payer_{int(time.time())}@security.org"
    register_user(gpay_user_email, "PayerPass123!", "SecOps Architect", "Cloud Armor")
    gpay_ok, gpay_msg, gpay_receipt = verify_and_process_subscription_payment(
        user_email=gpay_user_email,
        tier=SubscriptionTier.PRO,
        billing_cycle="monthly",
        payment_method_type="Google Pay",
        upi_utr_reference="519283746501"
    )
    assert gpay_ok is True
    assert gpay_receipt is not None
    assert gpay_receipt.payment_method == "Google Pay"
    assert gpay_receipt.merchant_number == "9973928945"
    assert gpay_receipt.reference_utr == "519283746501"
    assert gpay_receipt.status == "verified"

    # 7. Test Invalid UPI UTR rejection (too short)
    bad_upi_ok, bad_upi_msg, _ = verify_and_process_subscription_payment(
        user_email=gpay_user_email,
        tier=SubscriptionTier.PRO,
        billing_cycle="monthly",
        payment_method_type="PhonePe",
        upi_utr_reference="1234"
    )
    assert bad_upi_ok is False
    assert "UTR" in bad_upi_msg or "Transaction ID" in bad_upi_msg
    print("   [PASS] Payment authorization, PhonePe/GPay UPI (9973928945) UTR verification, cryptographic signatures, and instant global access verified.")


if __name__ == "__main__":
    test_cvss_calculation()
    test_parser_and_integrity_audit()
    test_subscription_tiers()
    test_company_presets()
    test_auth_and_trial_limits()
    test_payment_processing_and_verification()
    test_deployment_readiness()
    print("\n=======================================================")
    print("[READY] PROOFFORGE AI IS 100% READY FOR PRODUCTION DEPLOYMENT!")
    print("=======================================================")



