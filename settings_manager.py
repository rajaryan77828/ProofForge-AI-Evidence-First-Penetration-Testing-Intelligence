"""
ProofForge AI - Enterprise System Settings & API Management Engine
Provides persistent configuration for authentication policies, appearance,
security headers, CORS, webhook alerts, REST API keys, and maintenance controls.
"""

import os
import json
import time
import uuid
import hashlib
from typing import Dict, Any, List, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
SETTINGS_FILE_PATH = os.path.join(DATA_DIR, "system_settings.json")


DEFAULT_SYSTEM_SETTINGS: Dict[str, Any] = {
    "general": {
        "app_name": "ProofForge AI™",
        "app_tagline": "Evidence-First Penetration Testing Intelligence",
        "platform_version": "2.4.0 (Enterprise Hardened)",
        "organization_name": "ProofForge Enterprise Security Operations",
        "contact_support_email": "security-support@proofforge.corp",
        "default_timezone": "UTC",
        "documentation_url": "https://github.com/proofforge/proofforge-ai/docs",
        "changelog_version": "v2.4 - Added Scope Guard, Super Admin Center & Dynamic UPI Settler"
    },
    "appearance": {
        "color_theme": "Cyber Neon Dark (#0d1117 / #38bdf8)",
        "accent_color": "#38bdf8",
        "pulse_glow_enabled": True,
        "radar_scanlines_enabled": True,
        "client_marquee_enabled": True
    },
    "security": {
        "min_password_length": 8,
        "require_special_characters": True,
        "session_inactivity_timeout_minutes": 60,
        "max_failed_login_attempts": 5,
        "brute_force_lockout_duration_minutes": 15,
        "enforce_strict_cfaa_scope_guard": True,
        "cors_allowed_origins": [
            "http://localhost:8501",
            "http://127.0.0.1:8501",
            "http://192.168.7.91:8501"
        ],
        "content_security_policy": "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: https:;"
    },
    "notifications": {
        "in_app_toasts_enabled": True,
        "critical_finding_webhook_enabled": True,
        "webhook_url": "https://hooks.slack.com/services/PF/SEC/ALERT",
        "webhook_secret_signature": "whsec_pf_live_2026_superkey",
        "min_alert_severity": "High",
        "alert_notification_email": "ra5338446@gmail.com"
    },
    "api_and_integrations": {
        "rest_api_ingestion_enabled": True,
        "default_rate_limit_rpm": 120,
        "active_api_keys": [
            {
                "key_id": "PF-KEY-GOOGLE-901",
                "name": "Google Cloud Security Automation",
                "prefix": "pf_live_goog_",
                "key_hash": hashlib.sha256("pf_live_goog_token_2026".encode()).hexdigest(),
                "role": "Super Admin & API Ingest",
                "created_at": "2026-10-01 10:00:00 UTC",
                "last_used_at": "2026-10-12 14:00:00 UTC",
                "status": "Active"
            },
            {
                "key_id": "PF-KEY-MSFT-402",
                "name": "Microsoft MSRC SOAR Integration",
                "prefix": "pf_live_msft_",
                "key_hash": hashlib.sha256("pf_live_msft_token_2026".encode()).hexdigest(),
                "role": "Security Analyst",
                "created_at": "2026-10-05 12:00:00 UTC",
                "last_used_at": "2026-10-11 18:30:00 UTC",
                "status": "Active"
            }
        ]
    },
    "maintenance": {
        "maintenance_mode": False,
        "maintenance_message": "ProofForge AI is undergoing scheduled cryptographic database migration.",
        "auto_backup_enabled": True,
        "last_backup_timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "docker_container_ready": True
    }
}


def _ensure_settings_storage() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(SETTINGS_FILE_PATH):
        with open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_SYSTEM_SETTINGS, f, indent=2)


def load_system_settings() -> Dict[str, Any]:
    """Loads current persistent system settings."""
    _ensure_settings_storage()
    try:
        with open(SETTINGS_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_SYSTEM_SETTINGS.copy()


def save_system_settings(settings: Dict[str, Any]) -> bool:
    """Commits system settings to persistent storage."""
    _ensure_settings_storage()
    try:
        with open(SETTINGS_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception:
        return False


def update_setting_section(section: str, updates: Dict[str, Any]) -> bool:
    """Updates a specific section of system settings."""
    settings = load_system_settings()
    if section in settings:
        settings[section].update(updates)
    else:
        settings[section] = updates
    return save_system_settings(settings)


def create_new_api_key(name: str, role: str) -> Dict[str, Any]:
    """Generates a secure API key with prefix and SHA-256 hash."""
    settings = load_system_settings()
    raw_secret = f"pf_live_{uuid.uuid4().hex[:16]}"
    key_id = f"PF-KEY-{uuid.uuid4().hex[:6].upper()}"
    ts = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())

    key_record = {
        "key_id": key_id,
        "name": name.strip(),
        "prefix": raw_secret[:12] + "...",
        "key_hash": hashlib.sha256(raw_secret.encode()).hexdigest(),
        "role": role,
        "created_at": ts,
        "last_used_at": "Never",
        "status": "Active"
    }

    if "api_and_integrations" not in settings:
        settings["api_and_integrations"] = {}
    if "active_api_keys" not in settings["api_and_integrations"]:
        settings["api_and_integrations"]["active_api_keys"] = []

    settings["api_and_integrations"]["active_api_keys"].append(key_record)
    save_system_settings(settings)

    # Return dict containing the plaintext key ONCE so the user can copy it
    key_record["plaintext_key"] = raw_secret
    return key_record


def revoke_api_key(key_id: str) -> bool:
    """Revokes an API key by key ID."""
    settings = load_system_settings()
    keys = settings.get("api_and_integrations", {}).get("active_api_keys", [])
    updated = False
    for k in keys:
        if k["key_id"] == key_id:
            k["status"] = "Revoked"
            updated = True
            break
    if updated:
        save_system_settings(settings)
    return updated


def create_system_backup_archive() -> Dict[str, Any]:
    """Creates a complete snapshot of users, transactions, settings, and audit logs."""
    _ensure_settings_storage()
    backup_data = {
        "backup_id": f"PF-BACKUP-{int(time.time())}",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
        "settings": load_system_settings()
    }
    
    # Load users
    users_path = os.path.join(DATA_DIR, "users_cloud_db.json")
    if os.path.exists(users_path):
        try:
            with open(users_path, "r", encoding="utf-8") as f:
                backup_data["users"] = json.load(f)
        except Exception:
            backup_data["users"] = {}

    # Load payments
    payments_path = os.path.join(DATA_DIR, "payments_ledger.json")
    if os.path.exists(payments_path):
        try:
            with open(payments_path, "r", encoding="utf-8") as f:
                backup_data["payments"] = json.load(f)
        except Exception:
            backup_data["payments"] = []

    # Load audit log
    audit_path = os.path.join(DATA_DIR, "audit_log.json")
    if os.path.exists(audit_path):
        try:
            with open(audit_path, "r", encoding="utf-8") as f:
                backup_data["audit_logs"] = json.load(f)
        except Exception:
            backup_data["audit_logs"] = []

    backup_json = json.dumps(backup_data, indent=2)
    backup_hash = hashlib.sha256(backup_json.encode()).hexdigest()
    backup_data["backup_integrity_sha256"] = backup_hash

    return backup_data
