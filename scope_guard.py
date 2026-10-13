"""
ProofForge AI - Scope & Target Authorization Engine
Prevents scanning, testing, or reporting outside of the explicitly authorized engagement scope.
Complies with Computer Fraud and Abuse Act (CFAA), UK CMA, and PTES Rules of Engagement.
"""

import ipaddress
import re
from urllib.parse import urlparse
from typing import List, Dict, Any, Tuple


def parse_scope_definition(scope_raw: str) -> List[Dict[str, Any]]:
    """
    Parses user-supplied multi-line scope definitions into structured rules.
    Supports:
    - URLs: https://api.payments.fintechglobal.com/v2/
    - FQDNs / Wildcards: *.fintechglobal.com, payments.corp.internal
    - IP addresses: 192.168.1.10
    - IPv4 CIDR blocks: 10.240.12.0/24
    """
    rules = []
    for raw_line in scope_raw.strip().splitlines():
        line = raw_line.strip()
        # Strip list markers like '- ', '• ', or '* ' (followed by space)
        line = re.sub(r'^(?:[-•]\s*|\*\s+)', '', line).strip()
        if not line or line.startswith("#"):
            continue

        # Check if URL
        if "://" in line:
            parsed = urlparse(line)
            host = parsed.hostname or line
            path = parsed.path or "/"
            rules.append({
                "type": "URL",
                "raw": line,
                "host": host.lower(),
                "path": path
            })
            continue

        # Check if CIDR
        if "/" in line:
            try:
                network = ipaddress.ip_network(line, strict=False)
                rules.append({
                    "type": "CIDR",
                    "raw": line,
                    "network": network
                })
                continue
            except ValueError:
                pass

        # Check if plain IP
        try:
            ip = ipaddress.ip_address(line)
            rules.append({
                "type": "IP",
                "raw": line,
                "ip": ip
            })
            continue
        except ValueError:
            pass

        # Treat as Domain / Hostname
        domain_pattern = line.lower()
        is_wildcard = domain_pattern.startswith("*.")
        clean_domain = domain_pattern[2:] if is_wildcard else domain_pattern
        rules.append({
            "type": "DOMAIN",
            "raw": line,
            "domain": clean_domain,
            "wildcard": is_wildcard
        })

    return rules


def verify_target_authorized(target_str: str, authorized_scope_raw: str) -> Tuple[bool, str, str]:
    """
    Evaluates whether an affected target falls inside the explicitly authorized scope.
    Returns: (is_authorized, rule_matched, audit_reason)
    """
    if not authorized_scope_raw.strip():
        # Empty scope means unconstrained engagement notes
        return True, "GLOBAL_DEFAULT", "No strict scope list supplied; engagement assumed authorized under ROE."

    clean_target = target_str.strip()
    if clean_target.lower() in ["not specified", "unspecified", "internal application"]:
        return True, "SYSTEM_DEFAULT", "Target generic or self-contained."

    # Extract host or IP from target
    if "://" in clean_target:
        parsed = urlparse(clean_target)
        host_candidate = (parsed.hostname or clean_target).lower()
    else:
        # Split off port if present (e.g. 10.240.12.5:8080)
        host_candidate = clean_target.split(":")[0].strip().lower()

    rules = parse_scope_definition(authorized_scope_raw)
    if not rules:
        return True, "UNCONSTRAINED", "Scope rules parsed empty."

    # Try matching against parsed rules
    for rule in rules:
        rtype = rule["type"]

        if rtype == "URL":
            if host_candidate == rule["host"]:
                return True, rule["raw"], f"Matches authorized endpoint URL host '{rule['host']}'."

        elif rtype == "DOMAIN":
            if rule["wildcard"]:
                if host_candidate == rule["domain"] or host_candidate.endswith("." + rule["domain"]):
                    return True, rule["raw"], f"Matches authorized wildcard domain '*.{rule['domain']}'."
            else:
                if host_candidate == rule["domain"]:
                    return True, rule["raw"], f"Matches authorized explicit domain '{rule['domain']}'."

        elif rtype == "IP":
            try:
                candidate_ip = ipaddress.ip_address(host_candidate)
                if candidate_ip == rule["ip"]:
                    return True, rule["raw"], f"Matches authorized IPv4 host '{rule['raw']}'."
            except ValueError:
                pass

        elif rtype == "CIDR":
            try:
                candidate_ip = ipaddress.ip_address(host_candidate)
                if candidate_ip in rule["network"]:
                    return True, rule["raw"], f"Target IP falls within authorized CIDR block '{rule['raw']}'."
            except ValueError:
                pass

    return False, "NONE", f"Target '{target_str}' is OUT OF SCOPE. No matching rule in authorized ROE."
