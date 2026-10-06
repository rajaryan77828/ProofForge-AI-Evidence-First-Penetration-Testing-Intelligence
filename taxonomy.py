"""
ProofForge AI - Enterprise Taxonomy & Standards Database
Comprehensive mappings across OWASP Top 10 (2021), CWE, and OWASP WSTG v4.2.
Provides baseline CVSS v3.1 vectors for standard vulnerability classifications.
"""

from typing import Dict, Any, Tuple, Optional

# Structured vulnerability taxonomy database
TAXONOMY_DATABASE = {
    "sql injection": {
        "cwe_id": "CWE-89",
        "cwe_name": "Improper Neutralization of Special Elements used in an SQL Command ('SQL Injection')",
        "owasp_category": "A03:2021-Injection",
        "wstg_id": "WSTG-INPV-05",
        "default_cvss": {"av": "N", "ac": "L", "pr": "N", "ui": "N", "s": "U", "c": "H", "i": "H", "a": "L"},
        "remediation_short": "Utilize parameterized queries / prepared statements for all database queries.",
        "remediation_long": "Ensure all SQL operations utilize parameterized database access layers (e.g., PDO with prepared statements in PHP, PreparedStatement in Java, or ORMs like SQLAlchemy/Hibernate). Disable detailed database error disclosure to HTTP clients.",
        "references": [
            "https://owasp.org/www-project-web-security-testing-guide/v42/4-Web_Application_Security_Testing/07-Input_Validation_Testing/05-Testing_for_SQL_Injection",
            "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html",
            "https://cwe.mitre.org/data/definitions/89.html"
        ]
    },
    "sqli": {
        "alias_of": "sql injection"
    },
    "cross-site scripting": {
        "cwe_id": "CWE-79",
        "cwe_name": "Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')",
        "owasp_category": "A03:2021-Injection",
        "wstg_id": "WSTG-INPV-01",
        "default_cvss": {"av": "N", "ac": "L", "pr": "N", "ui": "R", "s": "C", "c": "L", "i": "L", "a": "N"},
        "remediation_short": "Context-aware output encoding and strict Content Security Policy (CSP).",
        "remediation_long": "Implement context-aware HTML entity encoding on all reflected or stored untrusted data before rendering it in the DOM. Deploy a defense-in-depth Content Security Policy (CSP) header restricting script execution.",
        "references": [
            "https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html",
            "https://cwe.mitre.org/data/definitions/79.html"
        ]
    },
    "xss": {
        "alias_of": "cross-site scripting"
    },
    "command injection": {
        "cwe_id": "CWE-78",
        "cwe_name": "Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')",
        "owasp_category": "A03:2021-Injection",
        "wstg_id": "WSTG-INPV-12",
        "default_cvss": {"av": "N", "ac": "L", "pr": "L", "ui": "N", "s": "U", "c": "H", "i": "H", "a": "H"},
        "remediation_short": "Avoid invoking shell interpreters; use native language runtime APIs.",
        "remediation_long": "Refactor application logic to use native programmatic APIs instead of spawning system shells or invoking external executables. If external execution is required, strictly whitelist inputs and pass arguments as an isolated array without shell expansion.",
        "references": [
            "https://cwe.mitre.org/data/definitions/78.html",
            "https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html"
        ]
    },
    "idor": {
        "cwe_id": "CWE-639",
        "cwe_name": "Authorization Bypass Through User-Controlled Key",
        "owasp_category": "A01:2021-Broken Access Control",
        "wstg_id": "WSTG-ATHZ-04",
        "default_cvss": {"av": "N", "ac": "L", "pr": "L", "ui": "N", "s": "U", "c": "H", "i": "L", "a": "N"},
        "remediation_short": "Enforce server-side record ownership checks on all parameterized queries.",
        "remediation_long": "Implement centralized, mandatory access control enforcement verifying whether the authenticated user or tenant identity is authorized to access the requested resource identifier before query execution.",
        "references": [
            "https://cheatsheetseries.owasp.org/cheatsheets/Insecure_Direct_Object_Reference_Prevention_Cheat_Sheet.html",
            "https://cwe.mitre.org/data/definitions/639.html"
        ]
    },
    "broken access control": {
        "cwe_id": "CWE-284",
        "cwe_name": "Improper Access Control",
        "owasp_category": "A01:2021-Broken Access Control",
        "wstg_id": "WSTG-ATHZ-02",
        "default_cvss": {"av": "N", "ac": "L", "pr": "L", "ui": "N", "s": "U", "c": "H", "i": "H", "a": "N"},
        "remediation_short": "Enforce role-based access control (RBAC) at the server layer.",
        "remediation_long": "Deny by default. Verify user authorization on every privileged endpoint on the server side rather than relying on client-side routing controls.",
        "references": [
            "https://owasp.org/Top10/A01_2021-Broken_Access_Control/",
            "https://cwe.mitre.org/data/definitions/284.html"
        ]
    },
    "ssrf": {
        "cwe_id": "CWE-918",
        "cwe_name": "Server-Side Request Forgery (SSRF)",
        "owasp_category": "A10:2021-Server-Side Request Forgery (SSRF)",
        "wstg_id": "WSTG-INPV-19",
        "default_cvss": {"av": "N", "ac": "L", "pr": "N", "ui": "N", "s": "C", "c": "H", "i": "N", "a": "N"},
        "remediation_short": "Enforce strict target domain whitelisting and block internal network subnets.",
        "remediation_long": "Disable unnecessary URI schemes (e.g. file://, gopher://). Implement positive whitelisting of outbound hostnames and validate DNS resolution results to explicitly reject RFC 1918 private subnets and cloud metadata endpoints (169.254.169.254).",
        "references": [
            "https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html",
            "https://cwe.mitre.org/data/definitions/918.html"
        ]
    },
    "authentication bypass": {
        "cwe_id": "CWE-287",
        "cwe_name": "Improper Authentication",
        "owasp_category": "A07:2021-Identification and Authentication Failures",
        "wstg_id": "WSTG-ATHN-01",
        "default_cvss": {"av": "N", "ac": "L", "pr": "N", "ui": "N", "s": "U", "c": "H", "i": "H", "a": "H"},
        "remediation_short": "Ensure cryptographic verification of identity tokens and session assertions.",
        "remediation_long": "Validate session identifiers, JWT signatures, and authentication credentials strictly on the backend. Never trust client-supplied authentication state flags.",
        "references": [
            "https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html",
            "https://cwe.mitre.org/data/definitions/287.html"
        ]
    },
    "csrf": {
        "cwe_id": "CWE-352",
        "cwe_name": "Cross-Site Request Forgery (CSRF)",
        "owasp_category": "A01:2021-Broken Access Control",
        "wstg_id": "WSTG-SESS-05",
        "default_cvss": {"av": "N", "ac": "L", "pr": "N", "ui": "R", "s": "U", "c": "N", "i": "H", "a": "N"},
        "remediation_short": "Use anti-CSRF tokens and SameSite cookie attributes.",
        "remediation_long": "Enforce cryptographic, unpredictably generated anti-CSRF tokens tied to the user session for all state-changing HTTP requests. Set SameSite=Lax or SameSite=Strict on all authentication cookies.",
        "references": [
            "https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html",
            "https://cwe.mitre.org/data/definitions/352.html"
        ]
    },
    "cors": {
        "cwe_id": "CWE-942",
        "cwe_name": "Permissive Cross-Domain Policy with Untrusted Domains",
        "owasp_category": "A01:2021-Broken Access Control",
        "wstg_id": "WSTG-CLNT-07",
        "default_cvss": {"av": "N", "ac": "L", "pr": "N", "ui": "R", "s": "U", "c": "H", "i": "N", "a": "N"},
        "remediation_short": "Restrict Access-Control-Allow-Origin headers to trusted origin domains.",
        "remediation_long": "Avoid dynamically reflecting the HTTP Origin request header in Access-Control-Allow-Origin with Access-Control-Allow-Credentials: true. Maintain a strict whitelist of legitimate client domains.",
        "references": [
            "https://cwe.mitre.org/data/definitions/942.html"
        ]
    },
    "hardcoded secret": {
        "cwe_id": "CWE-798",
        "cwe_name": "Use of Hard-coded Credentials",
        "owasp_category": "A07:2021-Identification and Authentication Failures",
        "wstg_id": "WSTG-CONF-04",
        "default_cvss": {"av": "N", "ac": "L", "pr": "N", "ui": "N", "s": "U", "c": "H", "i": "H", "a": "N"},
        "remediation_short": "Revoke exposed keys and store secrets in a secure vault.",
        "remediation_long": "Immediately revoke and rotate compromised credentials. Implement automated secret scanning in CI/CD pipelines and externalize secrets to dedicated vault services (e.g., AWS Secrets Manager, HashiCorp Vault).",
        "references": [
            "https://cwe.mitre.org/data/definitions/798.html"
        ]
    },
    "server version banner disclosure": {
        "cwe_id": "CWE-200",
        "cwe_name": "Exposure of Sensitive Information to an Unauthorized Actor",
        "owasp_category": "A05:2021-Security Misconfiguration",
        "wstg_id": "WSTG-INFO-02",
        "default_cvss": {"av": "N", "ac": "L", "pr": "N", "ui": "N", "s": "U", "c": "L", "i": "N", "a": "N"},
        "remediation_short": "Suppress detailed server banner headers in reverse proxy / web server configuration.",
        "remediation_long": "Disable detailed server technology version banners across web servers, gateways, and reverse proxies (e.g. ServerTokens Prod in Apache, server_tokens off in Nginx) to reduce reconnaissance footprint.",
        "references": [
            "https://cwe.mitre.org/data/definitions/200.html"
        ]
    }
}


def lookup_taxonomy_details(title: str, text_context: str = "") -> Dict[str, Any]:
    """
    Looks up standard vulnerability taxonomy details across OWASP, CWE, and WSTG.
    Returns matched metadata dictionary.
    """
    search_space = f"{title} {text_context}".lower()

    for key, data in TAXONOMY_DATABASE.items():
        if "alias_of" in data:
            real_key = data["alias_of"]
            if key in search_space:
                return TAXONOMY_DATABASE[real_key]
        else:
            if key in search_space:
                return data

    # Default fallback
    return {
        "cwe_id": None,
        "cwe_name": None,
        "owasp_category": "Uncategorized / Engagement Specific",
        "wstg_id": None,
        "default_cvss": {"av": "N", "ac": "L", "pr": "N", "ui": "N", "s": "U", "c": "L", "i": "N", "a": "N"},
        "remediation_short": "Follow standard defensive programming practices and validate all inputs.",
        "remediation_long": "Implement defense-in-depth mitigations in accordance with organizational security policies and industry baselines.",
        "references": []
    }
