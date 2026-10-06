# ProofForge AI 🛡️
### Enterprise Penetration Testing Intelligence & Evidence Grounding Platform

ProofForge AI converts authorized security assessment notes, raw Burp Suite / proxy logs, and field observations into formal, client-ready penetration testing deliverables aligned with industry frameworks.

---

## 🔒 Security Challenge: Zero Hallucination & Evidence Fidelity
General-purpose LLMs routinely hallucinate reproduction steps, invent synthetic curl commands, or artificially inflate vulnerability severity ratings.

**ProofForge AI enforces deterministic evidentiary boundaries:**
- **Zero Synthetic PoC Generation**: Reproduction payloads, HTTP requests, and command lines are drawn **exclusively** from assessor notes.
- **Evidence Deficit Flagging**: If a finding is logged without technical reproduction steps, the platform flags it with `⚠️ Flagged: Missing Evidence` rather than generating speculative proof.
- **Cryptographic Chain-of-Custody**: The platform computes an immutable **SHA-256 hash** of the raw assessment notes to guarantee that reports cannot be altered or misrepresented post-engagement.
- **Deterministic CVSS v3.1 Scoring**: Computes reproducible base scores and vector strings according to FIRST CVSS v3.1 specification.

---

## 🏛️ Industry Standards & Taxonomy Alignment
- **Methodologies**: OWASP Web Security Testing Guide (**WSTG v4.2**), Penetration Testing Execution Standard (**PTES**), and **NIST SP 800-115**.
- **Weakness Categorization**: Common Weakness Enumeration (**CWE**).
- **Threat Standards**: **OWASP Top 10: 2021**.

---

## 🛠️ Deliverables & Output Formats
1. **Interactive Cybersecurity UI (Streamlit)**: Side-by-side assessor console with live SHA-256 chain-of-custody, findings matrix, and evidence audits.
2. **Technical Markdown (`.md`)**: Full structured report formatted with tables, CVSS vectors, and HTTP code fences.
3. **Executive HTML (`.html`)**: Styled, self-contained consulting deliverable with dark-mode security theme and print-to-PDF formatting.
4. **Machine-Readable JSON (`.json`)**: Full Pydantic JSON schema deliverable for integration into vulnerability management systems (DefectDojo, Jira, etc.).

---

## 🚀 Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Verification Tests
```bash
python test_proofforge.py
```

### 3. Launch the Streamlit Platform
```bash
streamlit run app.py
```
