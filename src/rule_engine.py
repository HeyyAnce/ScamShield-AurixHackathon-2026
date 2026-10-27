"""
Enhanced multi-lingual rule-based detection engine for Scam Shield.
Supports English, Hindi (Devanagari), and Hinglish (Roman script).
Distinguishes genuine threats from legitimate banking and transactional messages.
"""

import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
import pandas as pd
from pydantic import BaseModel, Field

from src.config import OFFICIAL_DOMAINS_PATH, USE_UNCHECKED_DOMAINS


class RuleAnalysisResult(BaseModel):
    """Aggregate output from rule-based heuristic analysis."""
    score: int
    net_risk_score: int  # 0 to 100
    risk_level: str  # CRITICAL, HIGH, MEDIUM, LOW
    findings: List[Dict[str, Any]]
    has_critical_indicators: bool
    has_high_risk: bool
    is_hard_negative: bool  # True if message is recognized as legitimate transactional text
    hard_negative_reasons: List[str] = Field(default_factory=list)


def load_official_domain_lists(domains_path: Optional[Path] = None) -> Tuple[Set[str], List[str]]:
    """
    Loads official domains from legit_domains.csv (defaults to data/dataset/legit_domains.csv).
    Returns (exact_domains, zone_endings). Rows marked "unchecked" are skipped
    unless USE_UNCHECKED_DOMAINS is True.
    """
    path = Path(domains_path) if domains_path else OFFICIAL_DOMAINS_PATH
    if not path.is_file():
        path = OFFICIAL_DOMAINS_PATH
    domains: Set[str] = set()
    zones: List[str] = []
    if path.exists():
        try:
            df = pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
            for _, row in df.iterrows():
                if row.get("status", "").strip().lower() != "checked" and not USE_UNCHECKED_DOMAINS:
                    continue
                dom = str(row.get("domain", "")).strip().lower()
                if not dom:
                    continue
                if str(row.get("match_rule", "")).strip() == "ends_with_zone":
                    zones.append(dom if dom.startswith(".") else "." + dom)
                else:
                    domains.add(dom)
        except Exception:
            pass

    return domains, zones


def load_official_domains(domains_path: Optional[Path] = None) -> Set[str]:
    """Exact official domains only (kept for compatibility)."""
    return load_official_domain_lists(domains_path)[0]


def is_official_host(host: str, domains: Set[str], zones: List[str]) -> bool:
    """
    True only if the host IS an official domain, is a subdomain of one, or ends with an
    official zone such as .bank.in. Never a "contains" match: sbi.co.in.fake-site.com is not official.
    """
    host = host.strip().lower().rstrip(".")
    if host in domains:
        return True
    if any(host.endswith("." + d) for d in domains):
        return True
    return any(host.endswith(z) for z in zones)


class RuleEngine:
    """Multi-lingual heuristic detection engine."""

    def __init__(self, domains_path: Optional[Path] = None):
        self.official_domains, self.official_zones = load_official_domain_lists(domains_path)

    def analyze(self, text: str) -> RuleAnalysisResult:
        """
        Runs comprehensive heuristic checks covering threats, credentials,
        malicious links, payment scams, impersonation, and hard negatives.
        """
        lower = text.lower()
        findings: List[Dict[str, Any]] = []

        # ==============================================================================
        # 1. HARD NEGATIVE (SAFE TRANSACTIONAL) CHECKS
        # ==============================================================================
        hard_neg_signals = []
        is_hard_negative = False

        # Transactional debit/credit patterns
        tx_patterns = [
            r"\b(?:ac|a/c|account)\s*(?:xx|x+|\*{2,})?\d{2,4}\s*(?:has been\s*)?(?:debited|credited)\b",
            r"\bdebited\s*(?:by|with)?\s*(?:rs\.?|inr)\s*[\d,]+(?:\.\d{2})?\b",
            r"\bcredited\s*(?:by|with)?\s*(?:rs\.?|inr)\s*[\d,]+(?:\.\d{2})?\b",
            r"\bavail(?:able)?\s*bal(?:ance)?\s*[:\-]?\s*(?:rs\.?|inr)\b",
            r"\b(?:upi\s*ref|txn\s*id|utr|rrn)\s*[:\-]?\s*[\w\d]+\b",
            r"\bखाते\s*(?:xx|x+)?\d{2,4}\s*में\s*[\d,]+(?:\.\d{2})?\s*रुपये\s*(?:ब्लॉक|क्रेडिट|डेबिट)\b",
            r"\b(quarterly savings account interest|statement for month of|e-statement)\b",
        ]
        for pat in tx_patterns:
            if re.search(pat, lower):
                hard_neg_signals.append("Standard bank transactional alert / balance notification")
                break

        # Legitimate OTP delivery (explicitly stating do not share)
        legit_otp_patterns = [
            r"\b(?:is the otp to|use otp|one time password is)\s*\d{4,8}\b",
            r"\bdo not share (?:this )?otp\b",
            r"\bkisi ke sath share na karein\b",
            r"\botp kisi ko na batayein\b",
            r"\bnever share your (?:otp|pin|password)\b",
            r"\bvalid for \d+\s*(?:mins|minutes)\b",
        ]
        otp_safety_hits = 0
        for pat in legit_otp_patterns:
            if re.search(pat, lower):
                otp_safety_hits += 1
        if otp_safety_hits >= 2 or (otp_safety_hits >= 1 and re.search(r"\bdo not share|never share\b", lower)):
            hard_neg_signals.append("Legitimate OTP delivery containing explicit safety / do-not-share warning")

        # Legitimate service / delivery confirmation
        service_patterns = [
            r"\b(?:order|package|parcel)\b.*?\b(?:has been\s*)?(?:delivered|dispatched|shipped|out for delivery)\b",
            r"\b(?:ticket|request|complaint)\s*(?:has been\s*)?resolved\b",
            r"\bappointment\s*(?:is\s*)?confirmed\b",
            r"\bservice team aapse otp nahi maangegi\b",
        ]
        for pat in service_patterns:
            if re.search(pat, lower):
                hard_neg_signals.append("Routine service appointment or delivery confirmation")
                break

        # ==============================================================================
        # 2. URGENT THREATS & PANIC INDUCERS (English, Hindi, Hinglish)
        # ==============================================================================
        threat_patterns = [
            # Electricity / Utilities
            (
                r"\b(disconnected tonight|power cutoff|electricity cut|bijli kat|bijli cut|aaj raat bijli|bijli connection band|power supply will be disconnected)\b",
                "Electricity / power disconnection threat tonight",
                "HIGH",
            ),
            (
                r"\b(bijli bill jama|bijli vibhag|electricity officer|previous month bill was not updated)\b",
                "Unpaid utility bill scare tactic",
                "MEDIUM",
            ),
            # Account / SIM Deactivation
            (
                r"\b(account suspended|account blocked|khata band|card blocked|sim block|sim band|sim deactivation|services suspended)\b",
                "Threat of bank account, card, or SIM deactivation",
                "HIGH",
            ),
            # Artificial Urgency
            (
                r"\b(immediately|within 24 hours|within 2 hrs|within 1 hour|within 30 mins|turant|aakhri mauka|final notice|last notice|aaj raat 9:30|before 9:30 pm)\b",
                "Artificial urgency / panic deadline pressure",
                "MEDIUM",
            ),
            # Severe Legal Threats / Digital Arrest
            (
                r"\b(digital arrest|arrest warrant|fir registered|cbi custody|ed interrogation|narcotics parcel|giraftari|police karyawahi|banned adult video|fedex parcel|customs clearance|skype interrogation)\b",
                "Severe threat of police arrest, drugs parcel, or Digital Arrest",
                "CRITICAL",
            ),
        ]
        urgency_hits = []
        max_urgency_sev = "LOW"
        for pattern, description, sev in threat_patterns:
            if re.search(pattern, lower):
                urgency_hits.append(description)
                if sev == "CRITICAL" or (sev == "HIGH" and max_urgency_sev != "CRITICAL"):
                    max_urgency_sev = sev
                elif sev == "MEDIUM" and max_urgency_sev == "LOW":
                    max_urgency_sev = "MEDIUM"
        if urgency_hits:
            findings.append({
                "category": "Urgent Threats & Fear Tactics",
                "icon": "⏱️",
                "details": urgency_hits,
                "severity": max_urgency_sev,
            })

        # ==============================================================================
        # 3. SENSITIVE CREDENTIAL & DATA HARVESTING
        # ==============================================================================
        credential_patterns = [
            # Active OTP demands (avoid triggering if it's a "do not share OTP" warning)
            (
                r"\b(?:apna otp|otp bheje|otp batayein|share otp|send otp|enter otp below|fill otp)\b",
                "Direct demand to share or submit One-Time Password (OTP)",
                "CRITICAL",
            ),
            (
                r"\b(?:mpin|upi pin|atm pin|cvv|netbanking password)\b",
                "Requesting confidential security PIN, CVV, or password",
                "CRITICAL",
            ),
            (
                r"\b(pan card details|aadhaar link|update kyc|kyc expired|yono kyc|kyc update|pending kyc|kyc verification|re-kyc)\b",
                "Urgent KYC or Aadhaar/PAN verification demand",
                "HIGH",
            ),
        ]
        cred_hits = []
        max_cred_sev = "LOW"
        # A safety reminder is not a request for credentials. Only mask the
        # reminder clause; a later demand must still be checked.
        credential_name = r"(?:your\s+)?(?:otp(?:s)?|upi pin(?:s)?|mpin|atm pin|pin(?:s)?|cvv|netbanking password|password(?:s)?)\b"
        credential_text = re.sub(
            r"\b(?:do not|don't|never)\s+(?:share|disclose|give)\s+" + credential_name
            + r"(?:(?:\s*,\s*(?:(?:or|and)\s+)?|\s+(?:or|and)\s+)" + credential_name + r")*",
            "", lower,
        )
        for pattern, description, sev in credential_patterns:
            if re.search(pattern, credential_text):
                cred_hits.append(description)
                if sev == "CRITICAL" or (sev == "HIGH" and max_cred_sev != "CRITICAL"):
                    max_cred_sev = sev
                elif sev == "MEDIUM" and max_cred_sev == "LOW":
                    max_cred_sev = "MEDIUM"
        if cred_hits:
            findings.append({
                "category": "Credential & KYC Demands",
                "icon": "🔑",
                "details": cred_hits,
                "severity": max_cred_sev,
            })

        # ==============================================================================
        # 4. SUSPICIOUS LINKS, DOMAINS & APK DOWNLOADS
        # ==============================================================================
        link_patterns = [
            (
                r"\b[\w\-.]+\.apk\b",
                "Direct Android Application Package (.apk) download link (Extreme malware/trojan risk)",
                "CRITICAL",
            ),
            (
                r"\b(bit\.ly|tinyurl\.com|is\.gd|t\.co|cutt\.ly|rb\.gy|shorturl\.at|goo\.gl|ow\.ly)\b",
                "Shortened / obfuscated URL hiding real destination",
                "HIGH",
            ),
            (
                r"\b(?:https?:\/\/)?\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}(?::\d+)?(?:\/\S*)?\b",
                "Suspicious raw IP address link instead of registered domain",
                "HIGH",
            ),
            (
                r"\.(xyz|top|online|click|site|work|vip|live|loan|cam|rest|space)\b",
                "High-risk top-level domain extension (.xyz, .top, .online, etc.)",
                "HIGH",
            ),
        ]
        link_hits = []
        max_link_sev = "LOW"
        for pattern, description, sev in link_patterns:
            if re.search(pattern, lower):
                link_hits.append(description)
                if sev == "CRITICAL" or (sev == "HIGH" and max_link_sev != "CRITICAL"):
                    max_link_sev = sev
                elif sev == "MEDIUM" and max_link_sev == "LOW":
                    max_link_sev = "MEDIUM"

        # Check for lookalike domains vs official domains
        # Find all domains in the text
        domain_matches = re.findall(r"\b([a-zA-Z0-9\-]+\.[a-zA-Z0-9\-.]+)\b", lower)
        for dom in domain_matches:
            if any(dom.endswith("." + ext) for ext in ["apk", "png", "jpg", "jpeg", "pdf"]):
                continue
            # Look for bank/utility names inside domain
            if re.search(r"(?:sbi|yono|hdfc|icici|kotak|pnb|electricity|bijli|trai|epfo)", dom):
                if not is_official_host(dom, self.official_domains, self.official_zones):
                    link_hits.append(f"Potential deceptive lookalike domain: '{dom}'")
                    if max_link_sev != "CRITICAL":
                        max_link_sev = "HIGH"

        if link_hits:
            findings.append({
                "category": "Suspicious Links & Downloads",
                "icon": "🔗",
                "details": link_hits,
                "severity": max_link_sev,
            })

        # ==============================================================================
        # 5. PAYMENT FRAUD, LOTTERIES & ADVANCE FEES
        # ==============================================================================
        payment_patterns = [
            (
                r"\b(kbc|lottery|lucky draw|inaam|jeete hain|won \d+|cash prize|25 lakh|maruti suzuki festival)\b",
                "Unsolicited lottery or prize winnings announcement",
                "HIGH",
            ),
            (
                r"\b(registration fee|processing fee|advance charge|tax deposit|shulk|security deposit)\b",
                "Demanding advance payment or registration fee before releasing funds",
                "HIGH",
            ),
            (
                r"\b(scan qr code to receive|enter upi pin to receive|receive money via qr|pin dalein paise pane)\b",
                "Fraudulent claim that scanning QR or entering UPI PIN receives money",
                "CRITICAL",
            ),
        ]
        pay_hits = []
        max_pay_sev = "LOW"
        for pattern, description, sev in payment_patterns:
            if re.search(pattern, lower):
                pay_hits.append(description)
                if sev == "CRITICAL" or (sev == "HIGH" and max_pay_sev != "CRITICAL"):
                    max_pay_sev = sev
                elif sev == "MEDIUM" and max_pay_sev == "LOW":
                    max_pay_sev = "MEDIUM"
        if pay_hits:
            findings.append({
                "category": "Payment Demands & Lottery Traps",
                "icon": "💸",
                "details": pay_hits,
                "severity": max_pay_sev,
            })

        # ==============================================================================
        # 6. OFFICIAL ORGANIZATION IMPERSONATION
        # ==============================================================================
        impersonation_patterns = [
            (r"\b(sbi|yono|hdfc|icici|pnb|axis bank|state bank|kotak)\b", "Bank name mentioned"),
            (
                r"\b(electricity office|bijli vibhag|power board|mahavitaran|bescom|bses|uppcl|tneb|discom)\b",
                "Power / Electricity Board mention",
            ),
            (
                r"\b(trai|telecom authority|department of telecommunications|dot|india post|customs department)\b",
                "Government department or regulatory agency mention",
            ),
            (
                r"\b(mumbai police|delhi police|cbi|cyber cell|enforcement directorate|cyber crime branch)\b",
                "Law enforcement or investigative agency mention",
            ),
        ]
        imp_hits = []
        for pattern, description in impersonation_patterns:
            if re.search(pattern, lower):
                imp_hits.append(description)
        if imp_hits:
            findings.append({
                "category": "Official Organization Mentions",
                "icon": "🏛️",
                "details": imp_hits,
                "severity": "MEDIUM",
            })

        # ==============================================================================
        # 7. RISK CALCULATION & HARD NEGATIVE RECONCILIATION
        # ==============================================================================
        gross_score = 0
        has_critical = False
        has_high = False

        for f in findings:
            sev = f["severity"]
            if sev == "CRITICAL":
                gross_score += 5
                has_critical = True
            elif sev == "HIGH":
                gross_score += 2
                has_high = True
            elif sev == "MEDIUM":
                # Official organization mention without threats is low-weight
                if f["category"] == "Official Organization Mentions":
                    gross_score += 0.5
                else:
                    gross_score += 1

        # Evaluate Hard Negative Status
        # If there are hard negative signals AND NO critical threats, dampen score!
        if hard_neg_signals and not has_critical:
            # If only medium organization mentions or harmless words were triggered
            threat_finding_categories = {
                f["category"] for f in findings if f["category"] != "Official Organization Mentions"
            }
            if not threat_finding_categories or (len(threat_finding_categories) == 1 and not has_high):
                is_hard_negative = True
                gross_score = max(0.0, gross_score - 4.0)

        # Scale gross score to 0..100
        net_risk = int(min(100, max(0, gross_score * 15)))

        if has_critical or net_risk >= 60:
            risk_level = "CRITICAL"
        elif has_high or net_risk >= 30:
            risk_level = "HIGH"
        elif net_risk >= 15:
            risk_level = "MEDIUM"
        else:
            risk_level = "LOW"

        return RuleAnalysisResult(
            score=int(gross_score),
            net_risk_score=net_risk,
            risk_level=risk_level,
            findings=findings,
            has_critical_indicators=has_critical,
            has_high_risk=has_high or has_critical,
            is_hard_negative=is_hard_negative,
            hard_negative_reasons=hard_neg_signals,
        )
