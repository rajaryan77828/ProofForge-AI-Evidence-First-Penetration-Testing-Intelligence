"""
ProofForge AI - CVSS v3.1 Deterministic Calculator
Complies with FIRST.org CVSS v3.1 specification.
Deterministic scoring based exclusively on provided metrics, preventing score inflation.
"""

from typing import Dict, Tuple, Optional
import math


def round_up(val: float) -> float:
    """CVSS v3.1 round up function (round to 1 decimal place with ceiling for ties)."""
    return round(math.ceil(val * 10) / 10, 1)


class CVSS31Calculator:
    # Metric weights according to FIRST CVSS v3.1 Specification
    AV = {"N": 0.85, "A": 0.62, "L": 0.55, "P": 0.2}
    AC = {"L": 0.77, "H": 0.44}
    PR_UNCHANGED = {"N": 0.85, "L": 0.62, "H": 0.27}
    PR_CHANGED = {"N": 0.85, "L": 0.68, "H": 0.50}
    UI = {"N": 0.85, "R": 0.62}
    C = {"H": 0.56, "L": 0.22, "N": 0.0}
    I = {"H": 0.56, "L": 0.22, "N": 0.0}
    A = {"H": 0.56, "L": 0.22, "N": 0.0}

    @classmethod
    def calculate(
        cls,
        av: str = "N",
        ac: str = "L",
        pr: str = "N",
        ui: str = "N",
        s: str = "U",
        c: str = "H",
        i: str = "H",
        a: str = "H"
    ) -> Tuple[float, str, str]:
        """
        Calculates CVSS 3.1 Base Score, Severity Rating, and Vector String.
        Returns: (score, severity_string, vector_string)
        """
        # ISS (Impact Sub-Score)
        iss = 1 - ((1 - cls.C[c]) * (1 - cls.I[i]) * (1 - cls.A[a]))
        
        # Impact
        if s == "U":
            impact = 7.52 * iss
            pr_val = cls.PR_UNCHANGED[pr]
        else:
            impact = 7.52 * (iss - 0.029) - 3.25 * ((iss - 0.02) ** 15)
            pr_val = cls.PR_CHANGED[pr]

        # Exploitability
        exploitability = 8.22 * cls.AV[av] * cls.AC[ac] * pr_val * cls.UI[ui]

        # Base Score
        if impact <= 0:
            base_score = 0.0
        elif s == "U":
            base_score = round_up(min(impact + exploitability, 10.0))
        else:
            base_score = round_up(min(1.08 * (impact + exploitability), 10.0))

        # Severity rating
        if base_score == 0.0:
            sev = "None"
        elif 0.1 <= base_score <= 3.9:
            sev = "Low"
        elif 4.0 <= base_score <= 6.9:
            sev = "Medium"
        elif 7.0 <= base_score <= 8.9:
            sev = "High"
        else:
            sev = "Critical"

        vector = f"CVSS:3.1/AV:{av}/AC:{ac}/PR:{pr}/UI:{ui}/S:{s}/C:{c}/I:{i}/A:{a}"
        return base_score, sev, vector
