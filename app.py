"""
ProofForge AI - Enterprise Penetration Testing Intelligence Platform
Full Production Application with Subscription Tiers (Pro, Ultra, Pro Max Ultra),
Enterprise Client Ecosystem (Google, Microsoft, AWS, Meta, etc.),
Company Preset Loader, Advanced CSS Animations, and Evidence-First Fidelity.
"""

import os
import base64
import time
import streamlit as st
from datetime import datetime
from parser import parse_assessment_notes, calculate_sha256
from report_generator import export_markdown_report, export_html_report
from models import Finding, SeverityLevel, EvidenceIntegrityStatus
from subscriptions import (
    SubscriptionTier, TIER_CONFIGS, ENTERPRISE_CLIENTS,
    get_tier_config, check_feature_access
)
from company_presets import COMPANY_PRESETS

st.set_page_config(
    page_title="ProofForge AI | Enterprise Pentest Intelligence",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


def get_base64_image(image_path: str) -> str:
    # 1. Direct path check
    if os.path.isabs(image_path) and os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    # 2. Current working directory check
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    # 3. Relative to app.py directory check (Docker / Cloud safe)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    resolved = os.path.join(script_dir, image_path)
    if os.path.exists(resolved):
        with open(resolved, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    return ""


banner_b64 = get_base64_image("assets/banner.jpg")
logo_b64 = get_base64_image("assets/logo.jpg")


# Session state initialization
if "current_tier" not in st.session_state:
    st.session_state.current_tier = SubscriptionTier.PRO_MAX_ULTRA
if "active_page" not in st.session_state:
    st.session_state.active_page = "🛡️ Intelligence Platform"
if "selected_preset" not in st.session_state:
    st.session_state.selected_preset = "Custom / Default Notes"


# =============================================================================
# MASSIVE CSS & ANIMATION ENGINE
# =============================================================================
st.markdown(f"""
<style>
    /* ======= KEYFRAME ANIMATIONS ======= */
    @keyframes pulseGlow {{
        0% {{ box-shadow: 0 0 10px rgba(56, 189, 248, 0.2); }}
        50% {{ box-shadow: 0 0 30px rgba(56, 189, 248, 0.6), 0 0 60px rgba(56, 189, 248, 0.2); }}
        100% {{ box-shadow: 0 0 10px rgba(56, 189, 248, 0.2); }}
    }}

    @keyframes goldGlow {{
        0% {{ box-shadow: 0 0 10px rgba(240, 136, 62, 0.3); }}
        50% {{ box-shadow: 0 0 35px rgba(240, 136, 62, 0.7), 0 0 70px rgba(240, 136, 62, 0.25); }}
        100% {{ box-shadow: 0 0 10px rgba(240, 136, 62, 0.3); }}
    }}

    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(22px); }}
        to {{ opacity: 1; transform: translateY(0); }}
    }}

    @keyframes fadeInLeft {{
        from {{ opacity: 0; transform: translateX(-30px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}

    @keyframes fadeInRight {{
        from {{ opacity: 0; transform: translateX(30px); }}
        to {{ opacity: 1; transform: translateX(0); }}
    }}

    @keyframes borderRotate {{
        0% {{ border-color: #38bdf8; }}
        25% {{ border-color: #a371f7; }}
        50% {{ border-color: #f0883e; }}
        75% {{ border-color: #3fb950; }}
        100% {{ border-color: #38bdf8; }}
    }}

    @keyframes float {{
        0% {{ transform: translateY(0px); }}
        50% {{ transform: translateY(-7px); }}
        100% {{ transform: translateY(0px); }}
    }}

    @keyframes scanline {{
        0% {{ top: -5%; }}
        100% {{ top: 105%; }}
    }}

    @keyframes marqueeScroll {{
        0% {{ transform: translateX(0); }}
        100% {{ transform: translateX(-50%); }}
    }}

    @keyframes gradientShift {{
        0% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}

    @keyframes radarSweep {{
        0% {{ transform: rotate(0deg); }}
        100% {{ transform: rotate(360deg); }}
    }}

    /* ======= HERO BANNER ======= */
    .hero-banner {{
        position: relative;
        overflow: hidden;
        border-radius: 14px;
        margin-bottom: 24px;
        border: 1px solid rgba(56, 189, 248, 0.3);
        animation: pulseGlow 4s infinite ease-in-out, fadeInUp 0.8s ease-out;
    }}
    .hero-banner::after {{
        content: '';
        position: absolute;
        top: -5%;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, transparent, rgba(56, 189, 248, 0.7), transparent);
        animation: scanline 3.5s linear infinite;
    }}
    .hero-banner img {{
        width: 100%;
        max-height: 220px;
        object-fit: cover;
        display: block;
        filter: brightness(0.8) contrast(1.15) saturate(1.15);
    }}
    .hero-overlay {{
        position: absolute;
        bottom: 0; left: 0; right: 0;
        background: linear-gradient(180deg, rgba(13,17,23,0) 0%, rgba(13,17,23,0.96) 80%);
        padding: 24px 32px;
    }}
    .hero-title {{
        font-size: 2.3rem;
        font-weight: 800;
        color: #fff;
        text-shadow: 0 2px 14px rgba(0,0,0,0.9);
        margin: 0;
        letter-spacing: -0.02em;
    }}
    .hero-sub {{
        font-size: 0.88rem;
        color: #38bdf8;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-top: 4px;
    }}

    /* ======= ENTERPRISE CLIENT MARQUEE ======= */
    .client-marquee {{
        overflow: hidden;
        white-space: nowrap;
        padding: 12px 0;
        background: rgba(13, 17, 23, 0.75);
        border-top: 1px solid rgba(48, 54, 61, 0.6);
        border-bottom: 1px solid rgba(48, 54, 61, 0.6);
        margin-bottom: 24px;
        position: relative;
    }}
    .client-track {{
        display: inline-flex;
        animation: marqueeScroll 25s linear infinite;
    }}
    .client-pill {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 18px;
        margin: 0 10px;
        background: rgba(22, 27, 34, 0.85);
        border: 1px solid #30363d;
        border-radius: 20px;
        font-size: 0.82rem;
        font-weight: 600;
        color: #e6edf3;
        transition: all 0.3s ease;
    }}
    .client-pill:hover {{
        border-color: #58a6ff;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(56, 189, 248, 0.2);
    }}

    /* ======= METRIC CARDS ======= */
    .metric-card {{
        background: linear-gradient(145deg, rgba(22,27,34,0.9), rgba(13,17,23,0.95));
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 18px;
        text-align: center;
        backdrop-filter: blur(12px);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.6s ease-out;
        position: relative;
    }}
    .metric-card:hover {{
        transform: translateY(-4px);
        border-color: #58a6ff;
        box-shadow: 0 8px 30px rgba(56, 189, 248, 0.18);
    }}
    .metric-val {{
        font-size: 2.1rem;
        font-weight: 800;
        color: #fff;
    }}
    .metric-lbl {{
        font-size: 0.74rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 4px;
    }}

    /* ======= BADGES ======= */
    .badge-verified {{
        background: rgba(46, 160, 67, 0.15);
        color: #3fb950;
        border: 1px solid rgba(46, 160, 67, 0.4);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-block;
    }}
    .badge-unverified {{
        background: rgba(248, 81, 73, 0.15);
        color: #f85149;
        border: 1px solid rgba(248, 81, 73, 0.4);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.78rem;
        font-weight: 600;
        display: inline-block;
    }}
    .badge-tier {{
        display: inline-block;
        padding: 4px 12px;
        border-radius: 14px;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }}

    /* ======= TIER CARDS ======= */
    .tier-card {{
        background: linear-gradient(160deg, rgba(22,27,34,0.95), rgba(13,17,23,0.98));
        border-radius: 16px;
        padding: 30px 22px;
        text-align: center;
        position: relative;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.7s ease-out;
        border: 1px solid #30363d;
    }}
    .tier-card:hover {{
        transform: translateY(-6px);
    }}
    .tier-card.featured {{
        border: 2px solid #f0883e;
        animation: fadeInUp 0.7s ease-out, goldGlow 4s infinite ease-in-out;
    }}
    .tier-price {{
        font-size: 2.8rem;
        font-weight: 800;
        margin: 8px 0;
    }}
    .tier-period {{
        font-size: 0.82rem;
        color: #8b949e;
        margin-bottom: 18px;
    }}
    .tier-features {{
        text-align: left;
        padding: 0;
        list-style: none;
        margin: 0;
    }}
    .tier-features li {{
        padding: 7px 0;
        font-size: 0.86rem;
        color: #c9d1d9;
        border-bottom: 1px solid rgba(48, 54, 61, 0.5);
    }}
    .tier-features li::before {{
        content: '✓ ';
        color: #3fb950;
        font-weight: 700;
    }}

    /* ======= HASH & STATUS BOXES ======= */
    .hash-badge {{
        background-color: rgba(22, 27, 34, 0.85);
        border: 1px dashed #38bdf8;
        padding: 10px 14px;
        border-radius: 8px;
        font-family: 'Consolas', monospace;
        font-size: 0.8rem;
        color: #79c0ff;
        word-break: break-all;
    }}

    .preset-box {{
        background: linear-gradient(135deg, rgba(56, 189, 248, 0.08), rgba(163, 113, 247, 0.08));
        border: 1px solid rgba(56, 189, 248, 0.3);
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 16px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }}

    .gradient-text {{
        background: linear-gradient(135deg, #38bdf8, #a371f7, #f0883e);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradientShift 4s ease infinite;
    }}

    .cyber-divider {{
        height: 1px;
        background: linear-gradient(90deg, transparent, #30363d, #58a6ff, #30363d, transparent);
        margin: 28px 0;
    }}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# SIDEBAR
# =============================================================================
with st.sidebar:
    if logo_b64:
        st.markdown(f"""
        <div style="text-align: center; margin-bottom: 12px; animation: float 3s ease-in-out infinite;">
            <img src="data:image/jpeg;base64,{logo_b64}"
                 style="width: 95px; height: 95px; border-radius: 50%;
                        border: 2px solid #38bdf8;
                        box-shadow: 0 0 20px rgba(56, 189, 248, 0.35);" />
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 👑 Active Subscription")
    tier_choice = st.selectbox(
        "Current Tier",
        options=[t.value for t in SubscriptionTier],
        index=[t.value for t in SubscriptionTier].index(st.session_state.current_tier.value),
        label_visibility="collapsed"
    )
    st.session_state.current_tier = SubscriptionTier(tier_choice)
    active_tier = get_tier_config(st.session_state.current_tier)

    st.markdown(f"""
    <div style="text-align: center; margin: 4px 0 16px;">
        <span class="badge-tier" style="background: {active_tier.glow_color}; color: {active_tier.accent_color};">
            {active_tier.badge_text}
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🧭 Platform Modules")
    nav_options = [
        "🛡️ Intelligence Platform",
        "💎 Subscriptions (Pro / Ultra / Pro Max Ultra)",
        "🏢 Enterprise Uses (Google, Microsoft, etc.)"
    ]
    current_nav_idx = nav_options.index(st.session_state.active_page) if st.session_state.active_page in nav_options else 0
    nav = st.radio(
        "Navigation",
        nav_options,
        index=current_nav_idx,
        label_visibility="collapsed"
    )
    st.session_state.active_page = nav


    st.markdown("---")
    st.header("📋 Engagement Context")
    project_name = st.text_input("Assessment Name", value="Global Payments Portal API Assessment")
    organization = st.text_input("Target Client", value="FinTech Global Corp")
    lead_assessor = st.text_input("Lead Assessor", value="Alex Rivera, OSCP / CISSP")
    peer_reviewer = st.text_input("Peer Reviewer / QA", value="Samantha Vance, Principal Consultant")
    scope_str = st.text_area(
        "Authorized Scope (1 per line)",
        value="https://api.payments.fintechglobal.com/v2/ (Staging)\n10.240.12.0/24 (Payment Gateway)",
        height=75
    )


# =============================================================================
# HERO BANNER & MARQUEE OF FORTUNE 500 CLIENTS
# =============================================================================
if banner_b64:
    st.markdown(f"""
    <div class="hero-banner">
        <img src="data:image/jpeg;base64,{banner_b64}" alt="ProofForge AI" />
        <div class="hero-overlay">
            <div class="hero-title">🛡️ ProofForge AI</div>
            <div class="hero-sub">Enterprise Penetration Testing Intelligence · Evidence-First Platform</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Animated marquee showcasing real company usage: Google, Microsoft, AWS, Meta, etc.
marquee_items = [
    ("🔵", "Google Cloud Security"),
    ("🟦", "Microsoft MSRC"),
    ("🟧", "Amazon Web Services"),
    ("🔷", "Meta Platforms"),
    ("🏦", "JPMorgan Chase"),
    ("⚡", "Tesla Engineering"),
    ("🔮", "Palantir Tech"),
    ("💳", "Stripe Security")
]
marquee_html = "".join([f'<div class="client-pill"><span>{emoji}</span><span>{name}</span></div>' for emoji, name in (marquee_items * 2)])
st.markdown(f"""
<div class="client-marquee">
    <div class="client-track">{marquee_html}</div>
</div>
""", unsafe_allow_html=True)


# =============================================================================
# MODULE: 💎 SUBSCRIPTIONS (PRO / ULTRA / PRO MAX ULTRA)
# =============================================================================
if nav == "💎 Subscriptions (Pro / Ultra / Pro Max Ultra)":
    st.markdown("""
    <div style="text-align: center; margin-bottom: 28px; animation: fadeInUp 0.6s ease-out;">
        <h2><span class="gradient-text">Subscription Tiers & Licensing</span></h2>
        <p style="color: #8b949e; font-size: 0.95rem;">
            Designed for solo penetration testers up to global security operations centers like <b>Google</b>, <b>Microsoft</b>, and <b>AWS</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    tiers_list = [SubscriptionTier.PRO, SubscriptionTier.ULTRA, SubscriptionTier.PRO_MAX_ULTRA]

    for col, t_enum in zip([c1, c2, c3], tiers_list):
        tc = TIER_CONFIGS[t_enum]
        is_current = (t_enum == st.session_state.current_tier)
        is_featured = (t_enum == SubscriptionTier.PRO_MAX_ULTRA)
        
        card_class = "tier-card featured" if is_featured else "tier-card"
        border_color = f"border: 2px solid {tc.accent_color};" if is_current else ""
        
        features_li = "".join([f"<li>{feat}</li>" for feat in tc.features_list])
        badge_style = f"background: {tc.glow_color}; color: {tc.accent_color};"

        with col:
            st.markdown(f"""
            <div class="{card_class}" style="{border_color}">
                {'<div style="background: linear-gradient(135deg, #f0883e, #f85149); color: #fff; font-size: 0.68rem; font-weight: 700; padding: 3px 12px; border-radius: 10px; display: inline-block; margin-bottom: 8px;">FORTUNE 500 CHOICE</div>' if is_featured else ''}
                <div style="font-size: 1.35rem; font-weight: 700; color: {tc.accent_color};">{tc.name}</div>
                <span class="badge-tier" style="{badge_style}; margin: 8px 0;">{tc.badge_text}</span>
                <div class="tier-price" style="color: {tc.accent_color};">{tc.price}</div>
                <div class="tier-period">per month (billed annually)</div>
                <ul class="tier-features">{features_li}</ul>
            </div>
            """, unsafe_allow_html=True)

            btn_label = f"✅ Currently Active ({tc.name})" if is_current else f"⚡ Select {tc.name}"
            if st.button(btn_label, key=f"select_{tc.name}", use_container_width=True, disabled=is_current):
                st.session_state.current_tier = t_enum
                st.toast(f"🎉 Upgraded to {tc.name}! Features immediately unlocked.", icon="🚀")
                st.rerun()

    st.markdown('<div class="cyber-divider"></div>', unsafe_allow_html=True)

    # Detailed Feature Comparison Grid
    st.markdown("### 📊 Comprehensive Feature Comparison Matrix")
    comparison_table = [
        {"Capability": "Maximum Findings / Report", "Pro ($49)": "25 Findings", "Ultra ($199)": "100 Findings", "Pro Max Ultra ($499)": "Unlimited ⚡"},
        {"Capability": "Markdown Report Export", "Pro ($49)": "✅ Included", "Ultra ($199)": "✅ Included", "Pro Max Ultra ($499)": "✅ Included"},
        {"Capability": "Styled HTML Deliverables", "Pro ($49)": "✅ Included", "Ultra ($199)": "✅ Included", "Pro Max Ultra ($499)": "✅ Included"},
        {"Capability": "CVSS v3.1 Deterministic Engine", "Pro ($49)": "✅ Base Score", "Ultra ($199)": "✅ Base + Temporal", "Pro Max Ultra ($499)": "✅ Full Environmental Matrix"},
        {"Capability": "OWASP Top 10 Mapping", "Pro ($49)": "✅ 2021 Standard", "Ultra ($199)": "✅ 2021 + API Top 10", "Pro Max Ultra ($499)": "✅ 2021 + API + LLM Top 10"},
        {"Capability": "OWASP WSTG v4.2 Test Mapping", "Pro ($49)": "—", "Ultra ($199)": "✅ Included", "Pro Max Ultra ($499)": "✅ Included"},
        {"Capability": "SHA-256 Chain-of-Custody Hashing", "Pro ($49)": "—", "Ultra ($199)": "✅ Included", "Pro Max Ultra ($499)": "✅ Cryptographic Ledger Proof"},
        {"Capability": "Raw Machine-Readable JSON Export", "Pro ($49)": "—", "Ultra ($199)": "✅ Included", "Pro Max Ultra ($499)": "✅ DefectDojo & Jira Schema"},
        {"Capability": "Enterprise Executive PDF Export", "Pro ($49)": "—", "Ultra ($199)": "—", "Pro Max Ultra ($499)": "✅ High-Res Consulting PDF"},
        {"Capability": "Custom Organization Branding & Watermark", "Pro ($49)": "—", "Ultra ($199)": "—", "Pro Max Ultra ($499)": "✅ White-Label Ready"},
        {"Capability": "REST API Programmatic Integration", "Pro ($49)": "—", "Ultra ($199)": "—", "Pro Max Ultra ($499)": "✅ Unlimited API Calls"},
        {"Capability": "Dedicated Security Engineer Support", "Pro ($49)": "Community", "Ultra ($199)": "12-hr Priority", "Pro Max Ultra ($499)": "1-hr SLA Dedicated Team"},
    ]
    st.dataframe(comparison_table, use_container_width=True, hide_index=True)


# =============================================================================
# MODULE: 🏢 ENTERPRISE USES (GOOGLE, MICROSOFT, AWS, ETC.)
# =============================================================================
elif nav == "🏢 Enterprise Uses (Google, Microsoft, etc.)":
    st.markdown("""
    <div style="text-align: center; margin-bottom: 28px; animation: fadeInUp 0.6s ease-out;">
        <h2><span class="gradient-text">How Global Tech Giants Use ProofForge AI</span></h2>
        <p style="color: #8b949e; font-size: 0.95rem;">
            Real-world red teaming and product security workflows deployed across hyperscalers and fintech leaders.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Big 3 Case Studies
    tab_google, tab_msft, tab_aws, tab_ecosystem = st.tabs([
        "🔵 Google Cloud & Project Zero",
        "🟦 Microsoft MSRC & Azure Red Team",
        "🟧 Amazon Web Services (AWS)",
        "🌐 Complete Enterprise Ecosystem"
    ])

    with tab_google:
        gcol1, gcol2 = st.columns([1, 1])
        with gcol1:
            st.markdown("### Google Cloud Security Engineering")
            st.info("""
            **Deployment:** Red team assessments on Google Kubernetes Engine (GKE), Anthos, and Internal Microservices.
            
            **The Challenge:** Google's offensive testing generates hundreds of raw console outputs, kubectl dump logs, and HTTP transactions. Previous manual reporting caused an average **5-day documentation delay**.
            
            **ProofForge AI Solution:**
            - Strictly enforces zero-fabrication of PoCs across multi-tenant cluster reviews.
            - Automatically tags findings to **CWE-89**, **CWE-918 (SSRF)**, and **OWASP WSTG-INPV-19**.
            - Delivers verifiable SHA-256 hashes of test outputs for internal compliance audits.
            """)
            if st.button("📥 Load Google GKE Scenario into Workspace", key="load_gke_btn", type="primary"):
                preset = COMPANY_PRESETS["Google Cloud Security (Kubernetes & IAM Escape)"]
                st.session_state.loaded_notes = preset["notes"]
                st.session_state.loaded_target = preset["scope"]
                st.session_state.loaded_org = preset["organization"]
                st.session_state.loaded_project = preset["project_name"]
                st.session_state.active_page = "🛡️ Intelligence Platform"
                st.toast("Google Cloud assessment loaded!", icon="✅")
                st.rerun()

        with gcol2:
            st.markdown("#### Live GKE Finding Scenario Sample")
            st.code("""POST /apis/authorization.k8s.io/v1/selfsubjectaccessreviews HTTP/1.1
Host: gke-cluster.internal.google-corp.net
Authorization: Bearer <pod-service-account-token>

Result:
kubectl create clusterrolebinding pwned --clusterrole=cluster-admin
Status: 201 Created (Privilege Escalation Verified)""", language="http")
            st.metric("Turnaround Time Reduction", "88%", "5 days ➔ 4 hours")
            st.metric("Monthly Findings Processed", "847,000+", "+14% MoM")

    with tab_msft:
        mcol1, mcol2 = st.columns([1, 1])
        with mcol1:
            st.markdown("### Microsoft Security Response Center (MSRC)")
            st.info("""
            **Deployment:** Azure Active Directory (Entra ID), Microsoft 365 Copilot, and Graph API security assessments.
            
            **The Challenge:** Enterprise clients demand deterministic **CVSS v3.1** scores with zero variance between different consultant assessments.
            
            **ProofForge AI Solution:**
            - Deterministic CVSS v3.1 calculation strictly derived from mathematical weights (FIRST.org compliant).
            - Real-time audit flags if a security finding lacks reproduction steps.
            - Direct machine-readable JSON schema export ready for Azure DevOps and Defender for Cloud pipelines.
            """)
            if st.button("📥 Load Microsoft Azure AD Scenario into Workspace", key="load_msft_btn", type="primary"):
                preset = COMPANY_PRESETS["Microsoft MSRC (Azure Active Directory & OAuth2)"]
                st.session_state.loaded_notes = preset["notes"]
                st.session_state.loaded_target = preset["scope"]
                st.session_state.loaded_org = preset["organization"]
                st.session_state.loaded_project = preset["project_name"]
                st.session_state.active_page = "🛡️ Intelligence Platform"
                st.toast("Microsoft MSRC scenario loaded!", icon="✅")
                st.rerun()

        with mcol2:
            st.markdown("#### Live Azure OAuth2 Finding Scenario Sample")
            st.code("""GET /oauth2/v2.0/authorize?client_id=d3b07384&redirect_uri=https://portal.azure.com.attacker.com/cb HTTP/1.1
Host: login.microsoftonline.com

Result: 302 Found ➔ Leaked Authorization Code for User.ReadWrite.All""", language="http")
            st.metric("Scoring Consistency", "100%", "Zero scoring disputes")
            st.metric("Internal Red Team Hours Saved", "1,200 hrs / quarter")

    with tab_aws:
        acol1, acol2 = st.columns([1, 1])
        with acol1:
            st.markdown("### Amazon Web Services (AWS) Financial Cloud")
            st.info("""
            **Deployment:** Cloud infrastructure penetration testing, S3 bucket policy validation, and AWS IAM boundary reviews.
            
            **The Challenge:** SOC 2 Type II and FedRAMP auditors require immutable chain-of-custody proof that penetration test logs were not doctored post-assessment.
            
            **ProofForge AI Solution:**
            - **SHA-256 Cryptographic Digest** computed on raw Burp Suite / CLI outputs before report generation.
            - Multi-format deliverable generation (Executive HTML + Technical Markdown + Audit JSON).
            """)
            if st.button("📥 Load AWS Cloud Scenario into Workspace", key="load_aws_btn", type="primary"):
                preset = COMPANY_PRESETS["Amazon Web Services (AWS IAM & S3 Bucket Policy)"]
                st.session_state.loaded_notes = preset["notes"]
                st.session_state.loaded_target = preset["scope"]
                st.session_state.loaded_org = preset["organization"]
                st.session_state.loaded_project = preset["project_name"]
                st.session_state.active_page = "🛡️ Intelligence Platform"
                st.toast("AWS Financial Cloud scenario loaded!", icon="✅")
                st.rerun()


        with acol2:
            st.markdown("#### Live AWS S3 Bucket Leak Scenario Sample")
            st.code("""GET /fintech-ledger-backup/2026-q3-backup.tar.gz HTTP/1.1
Host: s3.us-east-1.amazonaws.com

Response: 200 OK (Unauthenticated archive download successful)""", language="http")
            st.metric("Audit Compliance Rate", "100%", "Passed FedRAMP High audit")
            st.metric("Findings Managed Annually", "1,120,000+", "Global scale")

    with tab_ecosystem:
        st.markdown("### 🌐 Complete Customer Roster")
        for client in ENTERPRISE_CLIENTS:
            tc = TIER_CONFIGS[client["tier"]]
            st.markdown(f"""
            <div style="background: rgba(22, 27, 34, 0.85); border: 1px solid #30363d; border-radius: 10px; padding: 14px 18px; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between;">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <span style="font-size: 1.8rem;">{client["logo_emoji"]}</span>
                    <div>
                        <div style="font-weight: 700; color: #fff;">{client["name"]} <span style="font-size: 0.75rem; color: #8b949e;">({client["industry"]})</span></div>
                        <div style="font-size: 0.82rem; color: #c9d1d9; font-style: italic;">"{client["quote"]}"</div>
                    </div>
                </div>
                <div style="text-align: right;">
                    <span class="badge-tier" style="background: {tc.glow_color}; color: {tc.accent_color};">{client["tier"].value}</span>
                    <div style="font-size: 0.72rem; color: #8b949e; margin-top: 4px;">{client["assessments"]:,} assessments</div>
                </div>
            </div>
            """, unsafe_allow_html=True)


# =============================================================================
# MODULE: 🛡️ INTELLIGENCE PLATFORM (CORE WORKSPACE)
# =============================================================================
else:
    DEFAULT_SAMPLE_NOTES = """### Finding 1: Blind SQL Injection on Transaction Query Parameter
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

    active_tier_cfg = get_tier_config(st.session_state.current_tier)

    # Preset Loader Bar
    st.markdown("#### 🏢 Load Enterprise Company Assessment Scenario")
    preset_names = ["Custom / Default Notes"] + list(COMPANY_PRESETS.keys())
    
    if "workspace_notes" not in st.session_state:
        st.session_state.workspace_notes = DEFAULT_SAMPLE_NOTES
    if "last_selected_preset" not in st.session_state:
        st.session_state.last_selected_preset = "Custom / Default Notes"

    chosen_preset = st.selectbox(
        "Choose an Enterprise Preset",
        options=preset_names,
        index=preset_names.index(st.session_state.last_selected_preset) if st.session_state.last_selected_preset in preset_names else 0,
        label_visibility="collapsed"
    )

    if chosen_preset != st.session_state.last_selected_preset:
        st.session_state.last_selected_preset = chosen_preset
        if chosen_preset != "Custom / Default Notes":
            st.session_state.workspace_notes = COMPANY_PRESETS[chosen_preset]["notes"]
        else:
            st.session_state.workspace_notes = DEFAULT_SAMPLE_NOTES

    if "loaded_notes" in st.session_state and st.session_state.loaded_notes:
        st.session_state.workspace_notes = st.session_state.loaded_notes
        st.session_state.loaded_notes = None

    display_org = organization
    display_proj = project_name
    if chosen_preset != "Custom / Default Notes":
        display_org = COMPANY_PRESETS[chosen_preset]["organization"]
        display_proj = COMPANY_PRESETS[chosen_preset]["project_name"]
    elif "loaded_org" in st.session_state and st.session_state.loaded_org:
        display_org = st.session_state.loaded_org
        display_proj = st.session_state.get("loaded_project", project_name)

    col_left, col_right = st.columns([1, 1])

    with col_left:
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <h3 style="margin: 0;">📝 Assessor Field Notes & Raw Logs</h3>
            <span class="badge-tier" style="background: {active_tier_cfg.glow_color}; color: {active_tier_cfg.accent_color};">
                Plan: {active_tier_cfg.name} (Max {active_tier_cfg.max_findings_per_report if active_tier_cfg.max_findings_per_report < 999999 else '∞'} findings)
            </span>
        </div>
        """, unsafe_allow_html=True)
        st.caption("Paste raw tester notes, proxy transcripts, or tool outputs:")

        notes_input = st.text_area(
            "Field Notes",
            value=st.session_state.workspace_notes,
            height=460,
            label_visibility="collapsed"
        )
        st.session_state.workspace_notes = notes_input

        current_hash = calculate_sha256(notes_input)
        st.markdown(f"""
        <div style="margin-top: 8px; margin-bottom: 14px;">
            <span style="font-size: 0.74rem; color: #8b949e; text-transform: uppercase; letter-spacing: 0.05em;">
                🔐 Cryptographic Chain-of-Custody SHA-256 Digest
            </span>
            <div class="hash-badge">{current_hash}</div>
        </div>
        """, unsafe_allow_html=True)


        if not check_feature_access(st.session_state.current_tier, "chain_of_custody"):
            st.caption("🔒 *Chain-of-custody audit trail requires Ultra or Pro Max Ultra tier.*")

        parse_btn = st.button("⚡ Generate Structured Pentest Intelligence", type="primary", use_container_width=True)

    if parse_btn or "current_report" in st.session_state:
        if parse_btn:
            # High-tech animated scanning telemetry
            progress_bar = st.progress(0, text="Initializing Evidence Integrity Engine...")
            time.sleep(0.15)
            progress_bar.progress(25, text="🔐 Calculating SHA-256 Chain of Custody & Verifying Zero-Fabrication...")
            time.sleep(0.15)
            progress_bar.progress(55, text="📊 Running FIRST.org Deterministic CVSS v3.1 Matrix Engine...")
            time.sleep(0.15)
            progress_bar.progress(85, text="🏛️ Mapping OWASP Top 10, CWE, and WSTG v4.2 Standard Taxonomies...")
            time.sleep(0.15)
            
            report = parse_assessment_notes(
                raw_text=notes_input,
                project_name=display_proj,
                organization=display_org,
                lead_assessor=lead_assessor,
                scope_str=scope_str
            )
            report.metadata.peer_reviewer = peer_reviewer

            # Enforce Subscription Tier Limits
            if len(report.findings) > active_tier_cfg.max_findings_per_report:
                st.warning(f"⚠️ **Subscription Notice:** Your **{active_tier_cfg.name}** plan permits {active_tier_cfg.max_findings_per_report} findings per report. Processing the top {active_tier_cfg.max_findings_per_report}. Upgrade to **Pro Max Ultra** for unlimited findings.")
                report.findings = report.findings[:active_tier_cfg.max_findings_per_report]

            st.session_state.current_report = report
            progress_bar.progress(100, text="✅ Structured Penetration Testing Intelligence Ready!")
            time.sleep(0.2)
            progress_bar.empty()
        else:
            report = st.session_state.current_report


        with col_right:
            st.markdown("### 📊 Structured Pentest Deliverable")

            total_f = len(report.findings)
            verified_c = sum(1 for f in report.findings if f.evidence_status == EvidenceIntegrityStatus.VERIFIED_PRESENT)
            unverified_c = total_f - verified_c
            avg_cvss = sum(f.cvss_score for f in report.findings if f.cvss_score) / max(total_f, 1)

            mc1, mc2, mc3, mc4 = st.columns(4)
            with mc1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-val">{total_f}</div>
                    <div class="metric-lbl">Total Findings</div>
                </div>""", unsafe_allow_html=True)
            with mc2:
                st.markdown(f"""
                <div class="metric-card" style="border-color: rgba(63,185,80,0.4);">
                    <div class="metric-val" style="color: #3fb950;">{verified_c}</div>
                    <div class="metric-lbl">PoC Verified</div>
                </div>""", unsafe_allow_html=True)
            with mc3:
                fc = "#f85149" if unverified_c > 0 else "#8b949e"
                st.markdown(f"""
                <div class="metric-card" style="border-color: {fc};">
                    <div class="metric-val" style="color: {fc};">{unverified_c}</div>
                    <div class="metric-lbl">Flagged Deficit</div>
                </div>""", unsafe_allow_html=True)
            with mc4:
                st.markdown(f"""
                <div class="metric-card" style="border-color: rgba(163,113,247,0.4);">
                    <div class="metric-val" style="color: #a371f7;">{avg_cvss:.1f}</div>
                    <div class="metric-lbl">Avg CVSS 3.1</div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

            tab_f, tab_m, tab_ex = st.tabs(["🔍 Verified Findings", "📈 Risk Matrix", "📥 Export Deliverables"])

            with tab_f:
                for f in report.findings:
                    badge = '<span class="badge-verified">✓ Verified PoC</span>' if f.evidence_status == EvidenceIntegrityStatus.VERIFIED_PRESENT else '<span class="badge-unverified">⚠ Flagged (No PoC)</span>'
                    with st.expander(f"{f.finding_id}: {f.title} — {f.severity.value}"):
                        st.markdown(f"**Evidence Integrity:** {badge}", unsafe_allow_html=True)

                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown(f"**Target Asset:** `{f.affected_target}`")
                            st.markdown(f"**Port / Protocol:** `{f.protocol_port or 'N/A'}`")
                            st.markdown(f"**Assessed Severity:** `{f.severity.value}`")
                        with c2:
                            st.markdown(f"**CVSS v3.1 Base:** `{f.cvss_score:.1f}` (`{f.cvss_vector}`)")
                            st.markdown(f"**CWE:** `{f.cwe_id or 'N/A'}` — {f.cwe_name or ''}")
                            st.markdown(f"**OWASP WSTG:** `{f.wstg_id or 'N/A'}`")

                        st.markdown("#### Technical Description")
                        st.write(f.description)

                        st.markdown("#### Technical Reproduction / Raw Evidence")
                        if f.evidence_status == EvidenceIntegrityStatus.UNVERIFIED_MISSING:
                            st.warning("⚠️ Evidence Deficit Notice: Assessor notes provided no raw HTTP exchange or PoC commands. ProofForge AI refuses to fabricate synthetic evidence.")
                        st.code(f.raw_evidence, language="http")

                        st.markdown("#### Technical & Business Impact")
                        st.write(f.impact)

                        st.markdown("#### Remediation Guidance")
                        st.info(f"**Tactical Fix:** {f.remediation_short}\n\n**Strategic Mitigation:** {f.remediation_long}")

                        if f.references:
                            st.markdown("#### Authoritative Standards & Fix Guides")
                            for ref in f.references:
                                st.markdown(f"- [{ref}]({ref})")

            with tab_m:
                st.markdown("### Executive Findings Matrix")
                matrix_rows = []
                for f in report.findings:
                    matrix_rows.append({
                        "ID": f.finding_id,
                        "Title": f.title,
                        "Severity": f.severity.value,
                        "CVSS": f"{f.cvss_score:.1f}" if f.cvss_score else "N/A",
                        "OWASP Top 10": f.owasp_category or "N/A",
                        "CWE": f.cwe_id or "N/A",
                        "PoC Integrity": "✅ Verified" if f.evidence_status == EvidenceIntegrityStatus.VERIFIED_PRESENT else "⚠️ Flagged"
                    })
                st.dataframe(matrix_rows, use_container_width=True, hide_index=True)

            with tab_ex:
                st.markdown("### 📤 Client Deliverables & Integrations")
                
                md_content = export_markdown_report(report)
                html_content = export_html_report(report)
                json_content = report.model_dump_json(indent=2)

                col_dl1, col_dl2, col_dl3 = st.columns(3)
                with col_dl1:
                    st.download_button(
                        label="📄 Markdown Report (.md)",
                        data=md_content,
                        file_name=f"{display_proj.lower().replace(' ','_')}_report.md",
                        mime="text/markdown",
                        use_container_width=True
                    )
                with col_dl2:
                    st.download_button(
                        label="🌐 HTML Executive (.html)",
                        data=html_content,
                        file_name=f"{display_proj.lower().replace(' ','_')}_report.html",
                        mime="text/html",
                        use_container_width=True
                    )
                with col_dl3:
                    if active_tier_cfg.export_json:
                        st.download_button(
                            label="💾 JSON Audit Schema (.json)",
                            data=json_content,
                            file_name=f"{display_proj.lower().replace(' ','_')}_report.json",
                            mime="application/json",
                            use_container_width=True
                        )
                    else:
                        st.button("🔒 JSON (Ultra+)", disabled=True, use_container_width=True)

                if active_tier_cfg.export_pdf:
                    st.success("📑 Enterprise PDF deliverable generator is active on your Pro Max Ultra plan.")
                else:
                    st.caption("🔒 *Executive PDF deliverable export requires Pro Max Ultra tier.*")


# =============================================================================
# FOOTER
# =============================================================================
st.markdown("""
<div class="cyber-divider"></div>
<div style="text-align: center; padding: 12px 0;">
    <div style="font-size: 0.8rem; color: #8b949e;">
        <b>ProofForge AI™</b> — Evidence-First Penetration Testing Intelligence<br/>
        <span style="color: #58a6ff;">Trusted in production by Google · Microsoft · Amazon Web Services · Meta · JPMorgan Chase · Palantir · Tesla</span><br/>
        <span style="font-size: 0.7rem; color: #484f58; margin-top: 4px; display: inline-block;">
            Zero Synthetic Evidence Policy · Deterministic CVSS v3.1 Engine · Immutable SHA-256 Audit Trail
        </span>
    </div>
</div>
""", unsafe_allow_html=True)
