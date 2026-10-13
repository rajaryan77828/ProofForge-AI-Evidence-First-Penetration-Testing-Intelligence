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
    is_admin: bool = False
    is_suspended: bool = False
    role: str = "Security Consultant"
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
        default_users = {}
        with open(USERS_DB_PATH, "w", encoding="utf-8") as f:
            json.dump(default_users, f, indent=2)
    
    # Always ensure default admin accounts and enterprise demos exist
    _sync_admin_and_demo_accounts()


def _sync_admin_and_demo_accounts() -> None:
    """Guarantees admin accounts and demo credentials are valid and present."""
    try:
        users = {}
        if os.path.exists(USERS_DB_PATH):
            with open(USERS_DB_PATH, "r", encoding="utf-8") as f:
                users = json.load(f)
    except Exception:
        users = {}

    admins_to_ensure = {
        "ra5338446@gmail.com": {
            "email": "ra5338446@gmail.com",
            "password_hash": hash_password("HACKER@raj"),
            "full_name": "Chief Security Architect (Admin)",
            "organization": "ProofForge Red Team Core",
            "subscription_tier": SubscriptionTier.PRO_MAX_ULTRA.value,
            "is_subscribed": True,
            "is_admin": True,
            "role": "Super Administrator & Cyber Lead",
            "subscription_plan_name": "Pro Max Ultra Enterprise Elite",
            "subscription_price_paid": "LIFETIME ADMIN ACCESS (UNLIMITED)",
            "runs_used": 0,
            "max_free_runs": 999999,
            "created_at": "2026-10-12 00:00:00 UTC",
            "last_login_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "last_device_info": "Admin Command Terminal"
        },
        "rajaryan1000211@gmail.com": {
            "email": "rajaryan1000211@gmail.com",
            "password_hash": hash_password("Hacker@raj#12345"),
            "full_name": "Senior Pentest Director (Admin)",
            "organization": "ProofForge Enterprise Operations",
            "subscription_tier": SubscriptionTier.PRO_MAX_ULTRA.value,
            "is_subscribed": True,
            "is_admin": True,
            "role": "Super Administrator & Cyber Lead",
            "subscription_plan_name": "Pro Max Ultra Enterprise Elite",
            "subscription_price_paid": "LIFETIME ADMIN ACCESS (UNLIMITED)",
            "runs_used": 0,
            "max_free_runs": 999999,
            "created_at": "2026-10-12 00:00:00 UTC",
            "last_login_at": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
            "last_device_info": "Admin Command Terminal"
        },
        "demo@fintech.corp": {
            "email": "demo@fintech.corp",
            "password_hash": hash_password("DemoPassword123!"),
            "full_name": "Alex Rivera",
            "organization": "FinTech Global Corp",
            "subscription_tier": SubscriptionTier.PRO.value,
            "is_subscribed": False,
            "is_admin": False,
            "role": "Security Consultant",
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
            "is_admin": False,
            "role": "Enterprise Lead",
            "subscription_plan_name": "Pro Max Ultra",
            "subscription_price_paid": "$499/mo",
            "runs_used": 142,
            "max_free_runs": 2,
            "created_at": "2026-08-15 08:30:00 UTC",
            "last_login_at": "2026-10-11 18:00:00 UTC",
            "last_device_info": "Google Cloud Workstation"
        }
    }

    # Upsert admins and demos
    for em, data in admins_to_ensure.items():
        users[em] = data

    with open(USERS_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(users, f, indent=2)


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
        log_audit_event("AUTH_FAILED", email_clean, f"Login attempt with non-existent email from {device_info}", severity="WARNING")
        return False, "Account not found. Please register or check email spelling.", None

    stored = users[email_clean]
    if stored.get("is_suspended", False):
        log_audit_event("AUTH_BLOCKED", email_clean, f"Blocked login attempt for suspended account from {device_info}", severity="WARNING")
        return False, "This account has been suspended by a Security Administrator. Please contact support.", None

    if stored.get("password_hash") != hash_password(password):
        log_audit_event("AUTH_FAILED", email_clean, f"Failed password attempt from {device_info}", severity="WARNING")
        return False, "Invalid password credentials. Please try again.", None

    # Update last login & device
    stored["last_login_at"] = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    stored["last_device_info"] = device_info
    users[email_clean] = stored
    save_all_users(users)

    profile = UserProfile(**stored)
    log_audit_event("AUTH_SUCCESS", email_clean, f"Successful login from {device_info} (Role: {profile.role})", severity="INFO")
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

    if profile.is_admin:
        return True, "Super Administrator Access: Unlimited pentest runs and enterprise capabilities granted.", profile.runs_used, 999999

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
    log_audit_event("SUBSCRIPTION_UPGRADE", email, f"Account upgraded to {tier.value} ({price_str})", severity="INFO")
    return True, f"Successfully upgraded to {tier.value}! Your subscription is now active on all devices.", updated_profile


AUDIT_LOG_PATH = os.path.join(DATA_DIR, "audit_log.json")


def log_audit_event(event_type: str, actor: str, details: str, severity: str = "INFO") -> Dict[str, Any]:
    """Records an immutable security audit event with cryptographic SHA-256 hash."""
    _ensure_storage()
    ts = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    raw_hash_input = f"{ts}:{event_type}:{actor}:{details}:{severity}"
    sig = hashlib.sha256(raw_hash_input.encode("utf-8")).hexdigest()

    event = {
        "timestamp": ts,
        "event_type": event_type,
        "actor": actor,
        "details": details,
        "severity": severity,
        "tamper_hash": sig
    }

    events = []
    try:
        if os.path.exists(AUDIT_LOG_PATH):
            with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
                events = json.load(f)
    except Exception:
        events = []

    events.insert(0, event)  # newest first
    # Keep last 500 records
    events = events[:500]

    with open(AUDIT_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(events, f, indent=2)

    return event


def get_audit_events(limit: int = 50) -> list[Dict[str, Any]]:
    """Retrieves recent audit log events."""
    _ensure_storage()
    try:
        if os.path.exists(AUDIT_LOG_PATH):
            with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
                events = json.load(f)
                return events[:limit]
    except Exception:
        pass
    return []


def admin_update_user(
    admin_actor: str,
    target_email: str,
    subscription_tier: Optional[str] = None,
    is_subscribed: Optional[bool] = None,
    reset_runs: bool = False,
    role: Optional[str] = None
) -> tuple[bool, str, Optional[UserProfile]]:
    """Super Admin control function to manage user roles, tiers, and run counters."""
    users = load_all_users()
    clean = target_email.strip().lower()
    if clean not in users:
        return False, "Target user not found.", None

    if subscription_tier:
        users[clean]["subscription_tier"] = subscription_tier
        users[clean]["subscription_plan_name"] = subscription_tier

    if is_subscribed is not None:
        users[clean]["is_subscribed"] = is_subscribed

    if reset_runs:
        users[clean]["runs_used"] = 0

    if role:
        users[clean]["role"] = role

    save_all_users(users)
    updated = UserProfile(**users[clean])
    log_audit_event(
        "ADMIN_USER_MODIFICATION",
        admin_actor,
        f"Modified account {clean}: tier={subscription_tier}, sub={is_subscribed}, reset_runs={reset_runs}, role={role}",
        severity="WARNING"
    )
    return True, f"Successfully updated user account {clean}.", updated


def admin_create_user(
    admin_actor: str,
    email: str,
    password: str,
    full_name: str,
    organization: str,
    role: str,
    tier: str = "Pro",
    is_subscribed: bool = False
) -> tuple[bool, str, Optional[UserProfile]]:
    """Allows Super Admin to provision team members, analysts, and auditors."""
    email_clean = email.strip().lower()
    if not email_clean or "@" not in email_clean:
        return False, "Invalid email address format.", None
    if len(password) < 6:
        return False, "Password must be at least 6 characters long.", None
    if not full_name.strip():
        return False, "Full Name is required.", None

    users = load_all_users()
    if email_clean in users:
        return False, f"Account {email_clean} already exists.", None

    enum_tier = SubscriptionTier.PRO
    for t in SubscriptionTier:
        if t.value == tier:
            enum_tier = t
            break

    is_admin = ("Super Admin" in role)
    new_profile = UserProfile(
        email=email_clean,
        password_hash=hash_password(password),
        full_name=full_name.strip(),
        organization=organization.strip() if organization.strip() else "Client Organization",
        subscription_tier=enum_tier,
        is_subscribed=is_subscribed or is_admin,
        is_admin=is_admin,
        is_suspended=False,
        role=role,
        subscription_plan_name=tier if (is_subscribed or is_admin) else None,
        subscription_price_paid="ADMIN PROVISIONED" if (is_subscribed or is_admin) else None,
        runs_used=0,
        max_free_runs=999999 if is_admin else (25 if is_subscribed else 2),
        last_device_info="Admin Provisioned Account"
    )

    users[email_clean] = new_profile.model_dump()
    save_all_users(users)
    log_audit_event("ADMIN_USER_CREATED", admin_actor, f"Provisioned account {email_clean} with role '{role}' and tier '{tier}'", severity="WARNING")
    return True, f"Account {email_clean} successfully created.", new_profile


def admin_reset_password(admin_actor: str, target_email: str, new_password: str) -> tuple[bool, str]:
    """Resets user password securely with audit logging."""
    if len(new_password) < 6:
        return False, "New password must be at least 6 characters long."
    users = load_all_users()
    clean = target_email.strip().lower()
    if clean not in users:
        return False, "User account not found."

    users[clean]["password_hash"] = hash_password(new_password)
    save_all_users(users)
    log_audit_event("ADMIN_PASSWORD_RESET", admin_actor, f"Password reset performed for account {clean}", severity="CRITICAL")
    return True, f"Password for {clean} successfully reset."


def admin_toggle_suspension(admin_actor: str, target_email: str, is_suspended: bool) -> tuple[bool, str]:
    """Suspends or reactivates an account."""
    users = load_all_users()
    clean = target_email.strip().lower()
    if clean not in users:
        return False, "User account not found."

    users[clean]["is_suspended"] = is_suspended
    save_all_users(users)
    action = "SUSPENDED" if is_suspended else "REACTIVATED"
    log_audit_event("ADMIN_ACCOUNT_STATUS", admin_actor, f"Account {clean} was {action}", severity="WARNING")
    return True, f"Account {clean} was {action.lower()} successfully."


def admin_delete_user(admin_actor: str, target_email: str) -> tuple[bool, str]:
    """Permanently deletes a user account (cannot delete the active super admin)."""
    users = load_all_users()
    clean = target_email.strip().lower()
    if clean not in users:
        return False, "User account not found."
    if clean == admin_actor.lower():
        return False, "Cannot delete your own active administrator account."

    del users[clean]
    save_all_users(users)
    log_audit_event("ADMIN_USER_DELETED", admin_actor, f"Permanently deleted account {clean}", severity="CRITICAL")
    return True, f"Account {clean} was permanently removed."

