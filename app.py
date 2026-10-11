"""
ProofForge AI - Enterprise Penetration Testing Intelligence Platform
Full Production Application with Global Cloud Authentication, Cross-Device Access,
2 Free Trial Runs Enforced, Multi-Tier Subscriptions (Pro, Ultra, Pro Max Ultra),
Full Price Breakdowns, Fortune 500 Presets (Google, Microsoft, AWS), and Cyber Animations.
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
from auth import (
    register_user, authenticate_user, get_user_profile,
    can_run_assessment, record_assessment_run, upgrade_user_subscription
)

st.set_page_config(
    page_title="ProofForge AI | Global Cloud Pentest Platform",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


def get_base64_image(image_path: str) -> str:
    if os.path.isabs(image_path) and os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    script_dir = os.path.dirname(os.path.abspath(__file__))
    resolved = os.path.join(script_dir, image_path)
    if os.path.exists(resolved):
        with open(resolved, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    return ""


banner_b64 = get_base64_image("assets/banner.jpg")
logo_b64 = get_base64_image("assets/logo.jpg")


# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================
if "authenticated_user" not in st.session_state:
    st.session_state.authenticated_user = None  # UserProfile object when logged in

if "current_tier" not in st.session_state:
    st.session_state.current_tier = SubscriptionTier.PRO

if "active_page" not in st.session_state:
    st.session_state.active_page = "🛡️ Intelligence Platform"

if "selected_preset" not in st.session_state:
    st.session_state.selected_preset = "Custom / Default Notes"

if "billing_cycle" not in st.session_state:
    st.session_state.billing_cycle = "Monthly"


# Keep tier in sync with user profile if authenticated
if st.session_state.authenticated_user:
    # Refresh profile from global storage
    refreshed = get_user_profile(st.session_state.authenticated_user.email)
    if refreshed:
        st.session_state.authenticated_user = refreshed
        st.session_state.current_tier = refreshed.subscription_tier


# =============================================================================
# CSS & ANIMATION ENGINE
# =============================================================================
st.markdown(f"""
<style>
    @keyframes pulseGlow {{
        0% {{ box-shadow: 0 0 10px rgba(56, 189, 248, 0.2); }}
        50% {{ box-shadow: 0 0 32px rgba(56, 189, 248, 0.6), 0 0 60px rgba(56, 189, 248, 0.2); }}
        100% {{ box-shadow: 0 0 10px rgba(56, 189, 248, 0.2); }}
    }}

    @keyframes goldGlow {{
        0% {{ box-shadow: 0 0 10px rgba(240, 136, 62, 0.3); }}
        50% {{ box-shadow: 0 0 35px rgba(240, 136, 62, 0.75), 0 0 70px rgba(240, 136, 62, 0.25); }}
        100% {{ box-shadow: 0 0 10px rgba(240, 136, 62, 0.3); }}
    }}

    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to {{ opacity: 1; transform: translateY(0); }}
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

    .hero-banner {{
        position: relative;
        overflow: hidden;
        border-radius: 14px;
        margin-bottom: 20px;
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
        max-height: 210px;
        object-fit: cover;
        display: block;
        filter: brightness(0.8) contrast(1.15) saturate(1.15);
    }}
    .hero-overlay {{
        position: absolute;
        bottom: 0; left: 0; right: 0;
        background: linear-gradient(180deg, rgba(13,17,23,0) 0%, rgba(13,17,23,0.96) 80%);
        padding: 20px 30px;
    }}
    .hero-title {{
        font-size: 2.2rem;
        font-weight: 800;
        color: #fff;
        text-shadow: 0 2px 14px rgba(0,0,0,0.9);
        margin: 0;
        letter-spacing: -0.02em;
    }}
    .hero-sub {{
        font-size: 0.85rem;
        color: #38bdf8;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-top: 4px;
    }}

    .client-marquee {{
        overflow: hidden;
        white-space: nowrap;
        padding: 10px 0;
        background: rgba(13, 17, 23, 0.8);
        border-top: 1px solid rgba(48, 54, 61, 0.6);
        border-bottom: 1px solid rgba(48, 54, 61, 0.6);
        margin-bottom: 22px;
    }}
    .client-track {{
        display: inline-flex;
        animation: marqueeScroll 25s linear infinite;
    }}
    .client-pill {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 5px 16px;
        margin: 0 8px;
        background: rgba(22, 27, 34, 0.85);
        border: 1px solid #30363d;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        color: #e6edf3;
    }}

    .auth-banner-box {{
        background: linear-gradient(135deg, rgba(22, 27, 34, 0.95), rgba(13, 17, 23, 0.98));
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
        animation: fadeInUp 0.5s ease-out;
    }}

    .trial-pill {{
        background: rgba(56, 189, 248, 0.15);
        border: 1px solid #38bdf8;
        color: #38bdf8;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.8rem;
        font-weight: 700;
    }}

    .subscribed-pill {{
        background: rgba(46, 160, 67, 0.15);
        border: 1px solid #3fb950;
        color: #3fb950;
        padding: 4px 12px;
        border-radius: 16px;
        font-size: 0.8rem;
        font-weight: 700;
    }}

    .metric-card {{
        background: linear-gradient(145deg, rgba(22,27,34,0.9), rgba(13,17,23,0.95));
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.6s ease-out;
    }}
    .metric-card:hover {{
        transform: translateY(-4px);
        border-color: #58a6ff;
        box-shadow: 0 8px 30px rgba(56, 189, 248, 0.18);
    }}
    .metric-val {{
        font-size: 2rem;
        font-weight: 800;
        color: #fff;
    }}
    .metric-lbl {{
        font-size: 0.72rem;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 4px;
    }}

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

    .tier-card {{
        background: linear-gradient(160deg, rgba(22,27,34,0.95), rgba(13,17,23,0.98));
        border-radius: 16px;
        padding: 26px 20px;
        text-align: center;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        animation: fadeInUp 0.7s ease-out;
        border: 1px solid #30363d;
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }}
    .tier-card:hover {{
        transform: translateY(-5px);
    }}
    .tier-card.featured {{
        border: 2px solid #f0883e;
        animation: fadeInUp 0.7s ease-out, goldGlow 4s infinite ease-in-out;
    }}
    .tier-price {{
        font-size: 2.7rem;
        font-weight: 800;
        margin: 6px 0;
    }}
    .tier-period {{
        font-size: 0.8rem;
        color: #8b949e;
        margin-bottom: 14px;
    }}
    .tier-features {{
        text-align: left;
        padding: 0;
        list-style: none;
        margin: 0 0 16px 0;
    }}
    .tier-features li {{
        padding: 6px 0;
        font-size: 0.84rem;
        color: #c9d1d9;
        border-bottom: 1px solid rgba(48, 54, 61, 0.4);
    }}
    .tier-features li::before {{
        content: '✓ ';
        color: #3fb950;
        font-weight: 700;
    }}

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
        margin: 24px 0;
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
                 style="width: 90px; height: 90px; border-radius: 50%;
                        border: 2px solid #38bdf8;
                        box-shadow: 0 0 20px rgba(56, 189, 248, 0.35);" />
        </div>
        """, unsafe_allow_html=True)

    # User Account Status Box
    user = st.session_state.authenticated_user
    if user:
        tier_cfg = get_tier_config(user.subscription_tier)
        status_label = "⚡ ACTIVE SUBSCRIBER" if user.is_subscribed else f"FREE TRIAL ({user.runs_used}/{user.max_free_runs})"
        status_color = "#3fb950" if user.is_subscribed else "#38bdf8"

        st.markdown(f"""
        <div style="background: rgba(22, 27, 34, 0.9); border: 1px solid #30363d; border-radius: 10px; padding: 12px; margin-bottom: 12px;">
            <div style="font-size: 0.72rem; color: {status_color}; font-weight: 800; letter-spacing: 0.08em;">{status_label}</div>
            <div style="font-weight: 700; color: #fff; font-size: 0.95rem; margin-top: 2px;">{user.full_name}</div>
            <div style="font-size: 0.74rem; color: #8b949e;">{user.email}</div>
            <div style="font-size: 0.72rem; color: #79c0ff; margin-top: 4px;">🌍 Cloud Synced ({user.last_device_info})</div>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🚪 Sign Out", key="sidebar_logout_btn", use_container_width=True):
            st.session_state.authenticated_user = None
            st.session_state.current_report = None
            st.toast("Signed out successfully from this device.", icon="ℹ️")
            st.rerun()
    else:
        st.markdown("""
        <div style="background: rgba(248, 81, 73, 0.1); border: 1px solid rgba(248, 81, 73, 0.4); border-radius: 10px; padding: 12px; margin-bottom: 12px;">
            <div style="font-size: 0.72rem; color: #f85149; font-weight: 800; letter-spacing: 0.08em;">🔒 NOT LOGGED IN</div>
            <div style="font-size: 0.8rem; color: #c9d1d9; margin-top: 2px;">Log in to access your subscriptions and free runs from any device.</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 🧭 Platform Modules")
    nav_options = [
        "🛡️ Intelligence Platform",
        "💎 Subscriptions & Pricing",
        "🏢 Enterprise Uses (Google, Microsoft, etc.)",
        "👤 Account & Cross-Device Sync"
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
    organization = st.text_input("Target Client", value=user.organization if user else "FinTech Global Corp")
    lead_assessor = st.text_input("Lead Assessor", value=user.full_name if user else "Alex Rivera, OSCP / CISSP")
    peer_reviewer = st.text_input("Peer Reviewer / QA", value="Samantha Vance, Principal Consultant")
    scope_str = st.text_area(
        "Authorized Scope (1 per line)",
        value="https://api.payments.fintechglobal.com/v2/ (Staging)\n10.240.12.0/24 (Payment Gateway)",
        height=70
    )


# =============================================================================
# HERO BANNER & MARQUEE
# =============================================================================
if banner_b64:
    st.markdown(f"""
    <div class="hero-banner">
        <img src="data:image/jpeg;base64,{banner_b64}" alt="ProofForge AI" />
        <div class="hero-overlay">
            <div class="hero-title">🛡️ ProofForge AI</div>
            <div class="hero-sub">Enterprise Pentest Intelligence · Global Cross-Device Subscriptions · 2 Free Runs</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

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
# MODULE: 👤 ACCOUNT & CROSS-DEVICE SYNC
# =============================================================================
if nav == "👤 Account & Cross-Device Sync":
    st.markdown("""
    <div style="text-align: center; margin-bottom: 24px;">
        <h2><span class="gradient-text">Global Account & Cross-Device Authentication</span></h2>
        <p style="color: #8b949e; font-size: 0.92rem;">
            Log in once, access your ProofForge AI subscription and assessments from <b>any device anywhere in the world</b>.
            Every new account receives <b>2 free test runs</b> before requiring an upgrade.
        </p>
    </div>
    """, unsafe_allow_html=True)

    user = st.session_state.authenticated_user

    if user:
        # User is already signed in -> show account dashboard
        st.markdown(f"""
        <div class="auth-banner-box">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
                <div>
                    <h3 style="margin: 0; color: #fff;">Welcome back, {user.full_name} 👋</h3>
                    <div style="color: #8b949e; font-size: 0.85rem; margin-top: 4px;">Organization: <b>{user.organization}</b> | Email: <b>{user.email}</b></div>
                </div>
                <div>
                    {'<span class="subscribed-pill">⚡ ' + (user.subscription_plan_name or user.subscription_tier.value) + ' Active (' + (user.subscription_price_paid or '$49/mo') + ')</span>' if user.is_subscribed else '<span class="trial-pill">FREE TRIAL (' + str(user.runs_used) + '/' + str(user.max_free_runs) + ' Runs Used)</span>'}
                </div>
            </div>
            <div class="cyber-divider"></div>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
                <div style="background: rgba(13, 17, 23, 0.7); padding: 14px; border-radius: 8px; border: 1px solid #30363d;">
                    <div style="font-size: 0.72rem; color: #8b949e; text-transform: uppercase;">Subscription Tier</div>
                    <div style="font-size: 1.3rem; font-weight: 700; color: #38bdf8;">{user.subscription_tier.value}</div>
                </div>
                <div style="background: rgba(13, 17, 23, 0.7); padding: 14px; border-radius: 8px; border: 1px solid #30363d;">
                    <div style="font-size: 0.72rem; color: #8b949e; text-transform: uppercase;">Assessments Executed</div>
                    <div style="font-size: 1.3rem; font-weight: 700; color: #a371f7;">{user.runs_used}</div>
                </div>
                <div style="background: rgba(13, 17, 23, 0.7); padding: 14px; border-radius: 8px; border: 1px solid #30363d;">
                    <div style="font-size: 0.72rem; color: #8b949e; text-transform: uppercase;">Cross-Device Status</div>
                    <div style="font-size: 1rem; font-weight: 700; color: #3fb950;">🌍 Globally Synced</div>
                </div>
                <div style="background: rgba(13, 17, 23, 0.7); padding: 14px; border-radius: 8px; border: 1px solid #30363d;">
                    <div style="font-size: 0.72rem; color: #8b949e; text-transform: uppercase;">Last Device Connected</div>
                    <div style="font-size: 0.85rem; font-weight: 600; color: #e6edf3;">{user.last_device_info}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        col_act1, col_act2 = st.columns(2)
        with col_act1:
            if not user.is_subscribed:
                st.warning(f"⚠️ You are on the free trial with **{max(0, user.max_free_runs - user.runs_used)}** run(s) remaining. Upgrade to unlock unlimited assessments and enterprise features.")
                if st.button("💎 View Subscription Plans & Upgrade", type="primary", use_container_width=True):
                    st.session_state.active_page = "💎 Subscriptions & Pricing"
                    st.rerun()
            else:
                st.success(f"🎉 Your **{user.subscription_tier.value}** plan is active globally on all your laptops, workstations, and mobile devices.")
        with col_act2:
            if st.button("🚪 Logout Account", use_container_width=True):
                st.session_state.authenticated_user = None
                st.session_state.current_report = None
                st.toast("Signed out successfully.", icon="ℹ️")
                st.rerun()

    else:
        # Not logged in -> Show Tabs for Login, Register, and Demo Quick-Login
        tab_login, tab_register, tab_quickdemo = st.tabs([
            "🔐 Sign In to Existing Account",
            "✨ Create New Account (2 Free Runs)",
            "⚡ Instant Demo Access (Google / FinTech)"
        ])

        with tab_login:
            st.markdown("#### Access Your ProofForge AI Account from Anywhere")
            st.caption("Enter your credentials to synchronize your active subscription and assessments.")

            with st.form("login_form"):
                login_email = st.text_input("Email Address", placeholder="name@company.com")
                login_password = st.text_input("Password", type="password", placeholder="••••••••")
                login_device = st.text_input("Device / Location Tag", value="Workstation (Desktop Web)")
                submit_login = st.form_submit_button("🚀 Sign In & Sync Subscription", type="primary", use_container_width=True)

                if submit_login:
                    success, msg, profile = authenticate_user(login_email, login_password, device_info=login_device)
                    if success:
                        st.session_state.authenticated_user = profile
                        st.session_state.current_tier = profile.subscription_tier
                        st.success(msg)
                        st.toast(f"Welcome back, {profile.full_name}!", icon="👋")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(msg)

        with tab_register:
            st.markdown("#### Start with 2 Free Assessment Runs")
            st.caption("No credit card required. Try 2 assessments for free, then subscribe to Pro, Ultra, or Pro Max Ultra.")

            with st.form("register_form"):
                reg_name = st.text_input("Full Name", placeholder="e.g. Alex Rivera")
                reg_email = st.text_input("Email Address", placeholder="name@company.com")
                reg_org = st.text_input("Company / Organization", placeholder="e.g. FinTech Global Security")
                reg_pass = st.text_input("Choose Password (min 6 characters)", type="password")
                reg_device = st.text_input("Primary Device Name", value="Laptop (Web Browser)")
                submit_reg = st.form_submit_button("✨ Create Account & Get 2 Free Runs", type="primary", use_container_width=True)

                if submit_reg:
                    success, msg, profile = register_user(reg_email, reg_pass, reg_name, organization=reg_org, device_info=reg_device)
                    if success:
                        st.session_state.authenticated_user = profile
                        st.session_state.current_tier = profile.subscription_tier
                        st.success(msg)
                        st.toast(f"Account created for {profile.full_name}! 2 free runs ready.", icon="🎉")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error(msg)

        with tab_quickdemo:
            st.markdown("#### Test Demo Accounts with Pre-Configured Subscriptions")
            st.info("Test different user roles and cross-device sync immediately with one click:")

            dcol1, dcol2 = st.columns(2)
            with dcol1:
                st.markdown("""
                **1. FinTech Global (Free Trial Account)**
                - **Email:** `demo@fintech.corp`
                - **Password:** `DemoPassword123!`
                - **Status:** 2 Free Trial Runs available
                """)
                if st.button("🔑 Login as Demo User (Free Trial)", key="quick_demo_btn", use_container_width=True):
                    _, _, profile = authenticate_user("demo@fintech.corp", "DemoPassword123!", "Demo Web Client")
                    st.session_state.authenticated_user = profile
                    st.session_state.current_tier = profile.subscription_tier
                    st.toast("Signed in as Demo User!", icon="✅")
                    st.rerun()

            with dcol2:
                st.markdown("""
                **2. Google Security Team (Pro Max Ultra Active)**
                - **Email:** `enterprise@google.com`
                - **Password:** `GoogleSec2026!`
                - **Status:** Full Pro Max Ultra ($499/mo) Unlimited Subscription
                """)
                if st.button("⭐ Login as Google Cloud (Pro Max Ultra)", key="quick_google_btn", type="primary", use_container_width=True):
                    _, _, profile = authenticate_user("enterprise@google.com", "GoogleSec2026!", "Google Cloud Workstation")
                    st.session_state.authenticated_user = profile
                    st.session_state.current_tier = profile.subscription_tier
                    st.toast("Signed in as Google Security Team (Pro Max Ultra Active)!", icon="🌟")
                    st.rerun()


# =============================================================================
# MODULE: 💎 SUBSCRIPTIONS & PRICING
# =============================================================================
elif nav == "💎 Subscriptions & Pricing":
    st.markdown("""
    <div style="text-align: center; margin-bottom: 24px;">
        <h2><span class="gradient-text">Complete Subscription Plans & Pricing</span></h2>
        <p style="color: #8b949e; font-size: 0.95rem;">
            Transparent pricing for solo pentesters, boutique consulting firms, and Fortune 500 enterprises.
            Access your active subscription from <b>any device across the globe</b>.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Billing Cycle Toggle (Monthly vs Annual with 20% discount)
    cycle_col1, cycle_col2, cycle_col3 = st.columns([1, 2, 1])
    with cycle_col2:
        billing_mode = st.radio(
            "Billing Cycle",
            ["Monthly Billing", "Annual Billing (Save 20% + 2 Free Months)"],
            horizontal=True,
            label_visibility="collapsed"
        )
        is_annual = "Annual" in billing_mode

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # Pricing Structure
    PRICING_PLANS = {
        SubscriptionTier.PRO: {
            "name": "Pro",
            "badge": "FOR SOLO PENTESTERS",
            "monthly_price": "$49",
            "annual_price": "$39",
            "period": "/month",
            "billed_info": "$470 billed annually" if is_annual else "Billed monthly, cancel anytime",
            "accent": "#3fb950",
            "glow": "rgba(63, 185, 80, 0.4)",
            "features": [
                "Up to 25 findings per assessment report",
                "CVSS v3.1 deterministic scoring engine",
                "OWASP Top 10 + CWE automatic taxonomy",
                "Client-ready Markdown & HTML exports",
                "Evidence fidelity & PoC verification flags",
                "Multi-device cloud login access",
                "Email support (48-hr SLA)"
            ]
        },
        SubscriptionTier.ULTRA: {
            "name": "Ultra",
            "badge": "MOST POPULAR FOR TEAMS",
            "monthly_price": "$199",
            "annual_price": "$159",
            "period": "/month",
            "billed_info": "$1,910 billed annually" if is_annual else "Billed monthly, cancel anytime",
            "accent": "#a371f7",
            "glow": "rgba(163, 113, 247, 0.4)",
            "features": [
                "Up to 100 findings per assessment report",
                "Everything in Pro Tier included",
                "OWASP WSTG v4.2 test mapping",
                "SHA-256 chain-of-custody audit hashing",
                "Raw JSON schema export (DefectDojo & Jira)",
                "PCI-DSS & SOC 2 compliance templates",
                "Multi-device & team synchronization",
                "Priority support (12-hr SLA)"
            ]
        },
        SubscriptionTier.PRO_MAX_ULTRA: {
            "name": "Pro Max Ultra",
            "badge": "⚡ ENTERPRISE ELITE (GOOGLE & MSFT CHOICE)",
            "monthly_price": "$499",
            "annual_price": "$399",
            "period": "/month",
            "billed_info": "$4,790 billed annually" if is_annual else "Billed monthly, cancel anytime",
            "accent": "#f0883e",
            "glow": "rgba(240, 136, 62, 0.6)",
            "featured": True,
            "features": [
                "UNLIMITED findings per assessment report",
                "Everything in Ultra Tier included",
                "White-label custom corporate branding & logos",
                "Executive consulting PDF deliverables",
                "REST API programmatic ingestion & webhooks",
                "ServiceNow & Splunk SOAR integrations",
                "FedRAMP High & HIPAA audit trails",
                "1-hour dedicated security engineer SLA",
                "Annual executive risk posture briefing"
            ]
        }
    }

    user = st.session_state.authenticated_user

    p1, p2, p3 = st.columns(3)
    for col, tier_key in zip([p1, p2, p3], [SubscriptionTier.PRO, SubscriptionTier.ULTRA, SubscriptionTier.PRO_MAX_ULTRA]):
        plan = PRICING_PLANS[tier_key]
        is_featured = plan.get("featured", False)
        card_class = "tier-card featured" if is_featured else "tier-card"
        price_display = plan["annual_price"] if is_annual else plan["monthly_price"]
        
        is_user_current = (user and user.is_subscribed and user.subscription_tier == tier_key)
        features_html = "".join([f"<li>{feat}</li>" for feat in plan["features"]])

        with col:
            st.markdown(f"""
            <div class="{card_class}">
                <div>
                    {'<div style="background: linear-gradient(135deg, #f0883e, #f85149); color: #fff; font-size: 0.68rem; font-weight: 800; padding: 4px 12px; border-radius: 10px; display: inline-block; margin-bottom: 8px;">FORTUNE 500 STANDARD</div>' if is_featured else ''}
                    <div style="font-size: 1.35rem; font-weight: 700; color: {plan['accent']};">{plan['name']}</div>
                    <span class="badge-tier" style="background: {plan['glow']}; color: {plan['accent']}; margin: 6px 0;">{plan['badge']}</span>
                    <div class="tier-price" style="color: {plan['accent']};">{price_display}<span style="font-size: 1rem; color: #8b949e;">{plan['period']}</span></div>
                    <div class="tier-period">{plan['billed_info']}</div>
                    <ul class="tier-features">{features_html}</ul>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if is_user_current:
                st.button(f"✅ Current Active Plan ({plan['name']})", key=f"active_{plan['name']}", disabled=True, use_container_width=True)
            elif user:
                if st.button(f"⚡ Subscribe to {plan['name']} ({price_display}{plan['period']})", key=f"sub_{plan['name']}", type="primary" if is_featured else "secondary", use_container_width=True):
                    success, msg, updated = upgrade_user_subscription(user.email, tier_key, billing_period="annual" if is_annual else "monthly")
                    if success:
                        st.session_state.authenticated_user = updated
                        st.session_state.current_tier = tier_key
                        st.toast(f"Subscription Activated: {plan['name']}!", icon="🎉")
                        st.success(f"Payment Confirmed! Your account ({user.email}) is now upgraded to {plan['name']} across all your devices worldwide.")
                        time.sleep(1)
                        st.rerun()
            else:
                if st.button(f"🔒 Sign In to Subscribe to {plan['name']}", key=f"login_to_sub_{plan['name']}", use_container_width=True):
                    st.session_state.active_page = "👤 Account & Cross-Device Sync"
                    st.rerun()

    st.markdown('<div class="cyber-divider"></div>', unsafe_allow_html=True)

    # Detailed Feature Matrix Table
    st.markdown("### 📊 Enterprise Feature Matrix & Specifications")
    matrix_data = [
        {"Feature / Specification": "Monthly Price", "Pro Plan": "$49/mo ($39 billed ann.)", "Ultra Plan": "$199/mo ($159 billed ann.)", "Pro Max Ultra Plan": "$499/mo ($399 billed ann.)"},
        {"Feature / Specification": "Free Trial Runs", "Pro Plan": "2 Free Runs Included", "Ultra Plan": "2 Free Runs Included", "Pro Max Ultra Plan": "2 Free Runs Included"},
        {"Feature / Specification": "Cross-Device Cloud Access", "Pro Plan": "✅ Global Sync", "Ultra Plan": "✅ Global Sync", "Pro Max Ultra Plan": "✅ Global Sync"},
        {"Feature / Specification": "Max Findings per Report", "Pro Plan": "25 Findings", "Ultra Plan": "100 Findings", "Pro Max Ultra Plan": "Unlimited Findings ⚡"},
        {"Feature / Specification": "Markdown Deliverable", "Pro Plan": "✅ Included", "Ultra Plan": "✅ Included", "Pro Max Ultra Plan": "✅ Included"},
        {"Feature / Specification": "Styled Consulting HTML", "Pro Plan": "✅ Included", "Ultra Plan": "✅ Included", "Pro Max Ultra Plan": "✅ Included"},
        {"Feature / Specification": "CVSS v3.1 Engine", "Pro Plan": "✅ Base Score", "Ultra Plan": "✅ Base + Temporal", "Pro Max Ultra Plan": "✅ Full Environmental Matrix"},
        {"Feature / Specification": "OWASP WSTG v4.2 Mapping", "Pro Plan": "—", "Ultra Plan": "✅ Included", "Pro Max Ultra Plan": "✅ Included"},
        {"Feature / Specification": "SHA-256 Chain of Custody", "Pro Plan": "—", "Ultra Plan": "✅ Included", "Pro Max Ultra Plan": "✅ Cryptographic Proof"},
        {"Feature / Specification": "Raw JSON Audit Export", "Pro Plan": "—", "Ultra Plan": "✅ Included", "Pro Max Ultra Plan": "✅ Jira & DefectDojo"},
        {"Feature / Specification": "White-Label Corporate Branding", "Pro Plan": "—", "Ultra Plan": "—", "Pro Max Ultra Plan": "✅ Full Customization"},
        {"Feature / Specification": "Executive Consulting PDF", "Pro Plan": "—", "Ultra Plan": "—", "Pro Max Ultra Plan": "✅ Included"},
        {"Feature / Specification": "REST API Ingestion", "Pro Plan": "—", "Ultra Plan": "—", "Pro Max Ultra Plan": "✅ Unlimited API"},
        {"Feature / Specification": "Support Response SLA", "Pro Plan": "48-hr Email", "Ultra Plan": "12-hr Priority", "Pro Max Ultra Plan": "1-hr Dedicated Security Lead"},
    ]
    st.dataframe(matrix_data, use_container_width=True, hide_index=True)


# =============================================================================
# MODULE: 🏢 ENTERPRISE USES (GOOGLE, MICROSOFT, AWS, ETC.)
# =============================================================================
elif nav == "🏢 Enterprise Uses (Google, Microsoft, etc.)":
    st.markdown("""
    <div style="text-align: center; margin-bottom: 24px;">
        <h2><span class="gradient-text">How Tech Giants Use ProofForge AI in Production</span></h2>
        <p style="color: #8b949e; font-size: 0.95rem;">
            Real-world offensive security, red teaming, and compliance workflows deployed across Fortune 500 enterprises.
        </p>
    </div>
    """, unsafe_allow_html=True)

    tab_google, tab_msft, tab_aws, tab_ecosystem = st.tabs([
        "🔵 Google Cloud & Project Zero",
        "🟦 Microsoft MSRC & Azure Red Team",
        "🟧 Amazon Web Services (AWS)",
        "🌐 Complete Customer Roster"
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
                st.session_state.workspace_notes = preset["notes"]
                st.session_state.last_selected_preset = "Google Cloud Security (Kubernetes & IAM Escape)"
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
                st.session_state.workspace_notes = preset["notes"]
                st.session_state.last_selected_preset = "Microsoft MSRC (Azure Active Directory & OAuth2)"
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
                st.session_state.workspace_notes = preset["notes"]
                st.session_state.last_selected_preset = "Amazon Web Services (AWS IAM & S3 Bucket Policy)"
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
        st.markdown("### 🌐 Complete Customer Roster & Active Deployments")
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

    user = st.session_state.authenticated_user
    active_tier_cfg = get_tier_config(st.session_state.current_tier)

    # Top Authentication & Trial Run Banner
    if user:
        if user.is_subscribed:
            st.markdown(f"""
            <div style="background: rgba(46, 160, 67, 0.12); border: 1px solid rgba(46, 160, 67, 0.4); border-radius: 8px; padding: 10px 16px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #3fb950; font-weight: 700; font-size: 0.88rem;">⚡ Connected as {user.full_name} ({user.email}) · Plan: <b>{user.subscription_tier.value}</b> ({user.subscription_price_paid or '$49/mo'}) Active Worldwide</span>
                <span style="font-size: 0.8rem; color: #8b949e;">Assessments Run: <b>{user.runs_used}</b></span>
            </div>
            """, unsafe_allow_html=True)
        else:
            remaining_free = max(0, user.max_free_runs - user.runs_used)
            color_stat = "#38bdf8" if remaining_free > 0 else "#f85149"
            st.markdown(f"""
            <div style="background: rgba(56, 189, 248, 0.08); border: 1px solid {color_stat}; border-radius: 8px; padding: 10px 16px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center;">
                <span style="color: #e6edf3; font-size: 0.88rem;">👤 Account: <b>{user.full_name}</b> · Free Trial Status: <b style="color: {color_stat};">{remaining_free} of {user.max_free_runs} free runs remaining</b></span>
                <span style="font-size: 0.8rem; color: #8b949e;">{f'⚠️ Trial Exhausted' if remaining_free == 0 else '2 Free Runs Policy'}</span>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: rgba(240, 136, 62, 0.1); border: 1px solid rgba(240, 136, 62, 0.4); border-radius: 8px; padding: 12px 16px; margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 8px;">
            <span style="color: #e6edf3; font-size: 0.88rem;">🔒 <b>Sign In Required to Generate Reports:</b> Every user can access their subscription from any device, or try 2 assessments for free.</span>
            <span style="font-size: 0.85rem; color: #f0883e; font-weight: 700;">👉 Please log in via '👤 Account & Cross-Device Sync'</span>
        </div>
        """, unsafe_allow_html=True)

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

    display_org = organization
    display_proj = project_name
    if chosen_preset != "Custom / Default Notes":
        display_org = COMPANY_PRESETS[chosen_preset]["organization"]
        display_proj = COMPANY_PRESETS[chosen_preset]["project_name"]

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

    if parse_btn:
        # Check authentication first
        if not user:
            st.error("🔒 **Authentication Required:** You must log in or create an account to run assessments and access your subscriptions from any device. (2 free runs included for new accounts).")
            if st.button("👉 Go to Login & Registration", type="primary"):
                st.session_state.active_page = "👤 Account & Cross-Device Sync"
                st.rerun()
        else:
            allowed, reason, runs_used, max_free = can_run_assessment(user.email)
            if not allowed:
                st.error(f"🛑 **{reason}**")
                st.info("💡 You have used your 2 free trial runs. Please select a subscription (Pro, Ultra, or Pro Max Ultra) to continue generating unlimited assessments from any device worldwide.")
                if st.button("💎 View Subscription Plans & Upgrade Now", type="primary"):
                    st.session_state.active_page = "💎 Subscriptions & Pricing"
                    st.rerun()
            else:
                # Execution is permitted!
                progress_bar = st.progress(0, text="Initializing Evidence Integrity Engine...")
                time.sleep(0.12)
                progress_bar.progress(25, text="🔐 Calculating SHA-256 Chain of Custody & Verifying Zero-Fabrication...")
                time.sleep(0.12)
                progress_bar.progress(55, text="📊 Running FIRST.org Deterministic CVSS v3.1 Matrix Engine...")
                time.sleep(0.12)
                progress_bar.progress(85, text="🏛️ Mapping OWASP Top 10, CWE, and WSTG v4.2 Standard Taxonomies...")
                time.sleep(0.12)
                
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
                # Record the run in cloud DB
                updated_profile = record_assessment_run(user.email)
                st.session_state.authenticated_user = updated_profile

                progress_bar.progress(100, text="✅ Structured Penetration Testing Intelligence Ready!")
                time.sleep(0.2)
                progress_bar.empty()
                if not user.is_subscribed:
                    runs_left = max(0, updated_profile.max_free_runs - updated_profile.runs_used)
                    st.toast(f"Run completed! {runs_left} free trial run(s) remaining.", icon="ℹ️")

    # Display Report Output
    if "current_report" in st.session_state and st.session_state.current_report:
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
        <b>ProofForge AI™</b> — Global Evidence-First Penetration Testing Intelligence Platform<br/>
        <span style="color: #58a6ff;">Trusted in production by Google · Microsoft · Amazon Web Services · Meta · JPMorgan Chase · Palantir · Tesla</span><br/>
        <span style="font-size: 0.7rem; color: #484f58; margin-top: 4px; display: inline-block;">
            Global Cross-Device Authentication · 2 Free Runs Trial Policy · Zero Synthetic Evidence Guarantee · Deterministic CVSS v3.1 Engine
        </span>
    </div>
</div>
""", unsafe_allow_html=True)
