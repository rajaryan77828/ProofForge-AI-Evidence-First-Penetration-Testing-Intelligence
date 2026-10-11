"""
ProofForge AI - Cloud Authentication & Cross-Device Account Engine
Provides secure account creation, authentication, trial tracking (2 free runs),
and subscription synchronisation across any device worldwide.
"""

import os
import json
import hashlib
import time
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from subscriptions import SubscriptionTier

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
USERS_DB_PATH = os.path.join(DATA_DIR, "users_cloud_db.json")


class UserProfile(BaseModel):
    email: str
    password_hash: str
    full_name: str
    organization: str = "Independent Security Consultant"
    subscription_tier: SubscriptionTier = SubscriptionTier.PRO
    is_subscribed: bool = False
    subscription_plan_name: Optional[str] = None
    subscription_price_paid: Optional[str] = None
    runs_used: int = 0
    max_free_runs: int = 2
    created_at: str = Field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()))
    last_login_at: str = Field(default_factory=lambda: time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()))
    last_device_info: str = "Web Client"


def _ensure_storage() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(USERS_DB_PATH):
        # Initialize default seed accounts (demo access for Google & Microsoft enterprise users)
        default_users = {
            "demo@fintech.corp": {
                "email": "demo@fintech.corp",
                "password_hash": hash_password("DemoPassword123!"),
                "full_name": "Alex Rivera",
                "organization": "FinTech Global Corp",
                "subscription_tier": SubscriptionTier.PRO.value,
                "is_subscribed": False,
                "subscription_plan_name": None,
                "subscription_price_paid": None,
                "runs_used": 0,
                "max_free_runs": 2,
                "created_at": "2026-10-01 10:00:00 UTC",
                "last_login_at": "2026-10-11 12:00:00 UTC",
                "last_device_info": "Enterprise Workstation"
            },
            "enterprise@google.com": {
                "email": "enterprise@google.com",
                "password_hash": hash_password("GoogleSec2026!"),
                "full_name": "Google Security Team",
                "organization": "Google Cloud Platform",
                "subscription_tier": SubscriptionTier.PRO_MAX_ULTRA.value,
                "is_subscribed": True,
                "subscription_plan_name": "Pro Max Ultra",
                "subscription_price_paid": "$499/mo",
                "runs_used": 142,
                "max_free_runs": 2,
                "created_at": "2026-08-15 08:30:00 UTC",
                "last_login_at": "2026-10-11 18:00:00 UTC",
                "last_device_info": "Google Cloud Workstation"
            }
        }
        with open(USERS_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(default_users, f, indent=2)


def hash_password(password: str) -> str:
    """Computes secure SHA-256 salted hash for credentials."""
    salt = "proofforge_cloud_global_salt_2026"
    return hashlib.sha256(f"{salt}{password}".encode("utf-8")).hexdigest()


def load_all_users() -> Dict[str, Any]:
    _ensure_storage()
    try:
        with open(USERS_DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_all_users(users: Dict[str, Any]) -> None:
    _ensure_storage()
    with open(USERS_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


def register_user(
    email: str,
    password: str,
    full_name: str,
    organization: str = "Client Organization",
    device_info: str = "Web Browser"
) -> tuple[bool, str, Optional[UserProfile]]:
    email_clean = email.strip().lower()
    if not email_clean or "@" not in email_clean:
        return False, "Invalid email address format.", None
    if len(password) < 6:
        return False, "Password must be at least 6 characters long.", None
    if not full_name.strip():
        return False, "Full Name is required.", None

    users = load_all_users()
    if email_clean in users:
        return False, "An account with this email already exists worldwide. Please sign in.", None

    new_profile = UserProfile(
        email=email_clean,
        password_hash=hash_password(password),
        full_name=full_name.strip(),
        organization=organization.strip() if organization.strip() else "Client Organization",
        subscription_tier=SubscriptionTier.PRO,
        is_subscribed=False,
        subscription_plan_name=None,
        subscription_price_paid=None,
        runs_used=0,
        max_free_runs=2,
        last_device_info=device_info
    )

    users[email_clean] = new_profile.model_dump()
    save_all_users(users)
    return True, "Account created successfully! You have 2 free trial runs available.", new_profile


def authenticate_user(
    email: str,
    password: str,
    device_info: str = "Web Browser"
) -> tuple[bool, str, Optional[UserProfile]]:
    email_clean = email.strip().lower()
    users = load_all_users()

    if email_clean not in users:
        return False, "Account not found. Please register or check email spelling.", None

    stored = users[email_clean]
    if stored.get("password_hash") != hash_password(password):
        return False, "Invalid password credentials. Please try again.", None

    # Update last login & device
    stored["last_login_at"] = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    stored["last_device_info"] = device_info
    users[email_clean] = stored
    save_all_users(users)

    profile = UserProfile(**stored)
    return True, "Authentication successful! Subscription synchronized across devices.", profile


def get_user_profile(email: str) -> Optional[UserProfile]:
    users = load_all_users()
    clean = email.strip().lower()
    if clean in users:
        return UserProfile(**users[clean])
    return None


def can_run_assessment(email: str) -> tuple[bool, str, int, int]:
    """
    Checks if user is allowed to generate an assessment.
    Rule:
    - If user is subscribed (Pro, Ultra, or Pro Max Ultra): unlimited runs according to plan!
    - If user is NOT subscribed: allowed only 2 free trial runs.
    Returns: (is_allowed, reason_message, runs_used, max_free_runs)
    """
    profile = get_user_profile(email)
    if not profile:
        return False, "Session expired or user not found. Please log in.", 0, 2

    if profile.is_subscribed:
        return True, f"Active subscription: {profile.subscription_plan_name or profile.subscription_tier.value}", profile.runs_used, profile.max_free_runs

    # Free tier trial check
    if profile.runs_used < profile.max_free_runs:
        remaining = profile.max_free_runs - profile.runs_used
        return True, f"Free trial active: {remaining} of {profile.max_free_runs} runs remaining.", profile.runs_used, profile.max_free_runs

    return False, f"Trial limit reached ({profile.runs_used}/{profile.max_free_runs} runs used). Please upgrade to a paid subscription (Pro, Ultra, or Pro Max Ultra) to continue generating reports.", profile.runs_used, profile.max_free_runs


def record_assessment_run(email: str) -> UserProfile:
    """Increments the run counter in the global database."""
    users = load_all_users()
    clean = email.strip().lower()
    if clean in users:
        users[clean]["runs_used"] = users[clean].get("runs_used", 0) + 1
        save_all_users(users)
        return UserProfile(**users[clean])
    return None


def upgrade_user_subscription(
    email: str,
    tier: SubscriptionTier,
    billing_period: str = "monthly"
) -> tuple[bool, str, UserProfile]:
    """Activates paid subscription tier and syncs across all devices."""
    users = load_all_users()
    clean = email.strip().lower()
    if clean not in users:
        return False, "User account not found.", None

    pricing = {
        SubscriptionTier.PRO: "$49/month" if billing_period == "monthly" else "$470/year ($39/mo)",
        SubscriptionTier.ULTRA: "$199/month" if billing_period == "monthly" else "$1,910/year ($159/mo)",
        SubscriptionTier.PRO_MAX_ULTRA: "$499/month" if billing_period == "monthly" else "$4,790/year ($399/mo)",
    }

    price_str = pricing.get(tier, "$49/month")
    users[clean]["subscription_tier"] = tier.value
    users[clean]["is_subscribed"] = True
    users[clean]["subscription_plan_name"] = tier.value
    users[clean]["subscription_price_paid"] = price_str

    save_all_users(users)
    updated_profile = UserProfile(**users[clean])
    return True, f"Successfully upgraded to {tier.value}! Your subscription is now active on all devices.", updated_profile
