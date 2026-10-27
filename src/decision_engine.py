"""
Decision engine for Scam Shield.
Reconciles rule heuristics, dataset reference patterns, and Gemini AI outputs.
Enforces fail-safe guardrails so neither AI nor static rules are treated as infallible.
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

from src.rule_engine import RuleAnalysisResult
from src.reference_matcher import DatasetMatchResult


class FinalDecision(BaseModel):
    """The unified, reconciled output from the detection pipeline."""
    verdict: str  # SCAM, SUSPICIOUS, SAFE
    scam_type: str
    explanation: str
    red_flags: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    confidence: str  # HIGH, MEDIUM, LOW
    is_ai: bool
    fallback_reason: Optional[str] = None
    reconciliation_notes: List[str] = Field(default_factory=list)


CATEGORY_NAMES = {
    "electricity_bill_disconnection": "Electricity Bill Disconnection Scam",
    "banking_kyc_account_block": "Bank KYC & Account Freeze Scam",
    "malicious_apk_remote_access": "Malicious APK / Trojan Malware",
    "lottery_prize_reward_scam": "Fake Lottery / Prize Winnings Scam",
    "digital_arrest_police_govt_impersonation": "Digital Arrest & Police Impersonation Threat",
    "upi_qr_payment_scam": "UPI / QR Code Payment Scam",
    "courier_parcel_customs_scam": "Courier / Customs Narcotics Threat",
    "fake_job_task_scam": "Part-Time Job / Task Investment Scam",
    "refund_cashback_fake_support_scam": "Fake Refund / Cashback Support Scam",
    "legitimate_banking_transaction": "Legitimate Bank Transaction Alert",
    "legitimate_customer_support": "Legitimate Service Communication",
    "legitimate_upi_payment": "Legitimate Payment Notification",
    "personal_conversation": "Personal Conversation",
}


def humanize_category(cat: Optional[str]) -> str:
    """Converts a snake_case taxonomy category into a clear human-readable title."""
    if not cat:
        return "Unclassified Message"
    return CATEGORY_NAMES.get(cat, cat.replace("_", " ").title())


class DecisionEngine:
    """Synthesizes rule indicators, dataset patterns, and AI predictions."""

    def reconcile(
        self,
        rule_results: RuleAnalysisResult,
        dataset_matches: DatasetMatchResult,
        gemini_result: Optional[Dict[str, Any]] = None,
    ) -> FinalDecision:
        """
        Reconciles all detection signals into a balanced final decision.
        """
        notes: List[str] = []

        # -------------------------------------------------------------------------
        # SCENARIO 1: Gemini AI is Active & Returned Valid Output
        # -------------------------------------------------------------------------
        if gemini_result and gemini_result.get("success"):
            ai_verdict = gemini_result.get("verdict", "SUSPICIOUS").upper()
            ai_type = gemini_result.get("scam_type", "Suspicious Alert")
            ai_explanation = gemini_result.get("explanation", "Please exercise caution.")
            ai_flags = list(gemini_result.get("red_flags", []))
            ai_actions = list(gemini_result.get("recommended_actions", []))
            ai_conf = gemini_result.get("confidence", "MEDIUM").upper()

            final_verdict = ai_verdict
            final_type = ai_type
            final_explanation = ai_explanation
            final_flags = ai_flags
            final_actions = ai_actions
            final_conf = ai_conf

            # GUARDRAIL 1: Critical Threat Safety Override
            # If AI says SAFE, but rules found a detected CRITICAL indicator
            # (.apk download, active OTP theft, UPI PIN inversion, Digital arrest)
            if ai_verdict == "SAFE" and rule_results.has_critical_indicators:
                final_verdict = "SCAM"
                final_type = "High-Risk Security Hazard (Safety Rule Override)"
                final_explanation = (
                    "This message contains critical security risks (such as a direct malware file, "
                    "credential demand, or arrest threat) and must be treated as dangerous."
                )
                final_flags = [
                    f"Heuristic Safety Override: Critical indicator detected ({f['category']})"
                    for f in rule_results.findings
                    if f["severity"] == "CRITICAL"
                ] + ai_flags
                final_actions = [
                    "Do NOT click any link or install any downloaded APK file.",
                    "Never share your OTP, MPIN, or bank password with anyone.",
                    "Block the sender number immediately and report to 1930 if money was lost.",
                ]
                final_conf = "HIGH"
                notes.append("Safety Guardrail: Overrode AI SAFE verdict due to detected CRITICAL heuristic.")

            # GUARDRAIL 2: Hard Negative Legitimate Alert Reconciliation
            # If AI says SCAM or SUSPICIOUS, but rules confirmed an unequivocal hard-negative
            # (routine debit alert with no links, no phone numbers, no threats) AND dataset matches SAFE
            elif (
                rule_results.is_hard_negative
                and not rule_results.has_high_risk
                and dataset_matches.consensus_label == "SAFE"
                and dataset_matches.has_strong_match
                and ai_verdict != "SAFE"
            ):
                final_verdict = "SAFE"
                final_type = humanize_category(dataset_matches.top_category)
                final_explanation = (
                    "This appears to be a standard, legitimate bank or service alert notifying you of "
                    "account activity without requesting credentials or urgent action."
                )
                final_flags = [
                    "Matches standard transactional debit/credit alert formatting",
                    "Contains no suspicious links, APK downloads, or requests for PIN/OTP",
                ]
                final_actions = [
                    "No immediate action is needed for this routine alert.",
                    "If you did not authorize this transaction, contact your bank's official 24x7 helpline.",
                    "Never share bank OTPs or PINs with anyone claiming to call from the bank.",
                ]
                final_conf = "HIGH"
                notes.append("Reconciled AI output: Legitimate transactional alert confirmed by rules & dataset.")

            # Agreement & Confidence Refinement
            else:
                agreement_count = 0
                if dataset_matches.consensus_label == ai_verdict:
                    agreement_count += 1
                if (rule_results.risk_level in ["CRITICAL", "HIGH"] and ai_verdict == "SCAM") or (
                    rule_results.risk_level == "LOW" and ai_verdict == "SAFE"
                ):
                    agreement_count += 1

                if agreement_count >= 2:
                    final_conf = "HIGH"
                    notes.append("High confidence: AI, rules, and dataset references all agree.")
                elif agreement_count == 0:
                    final_conf = "MEDIUM" if final_conf == "HIGH" else final_conf
                    notes.append("Moderate confidence: Partial divergence between AI and local heuristics.")

            return FinalDecision(
                verdict=final_verdict,
                scam_type=final_type,
                explanation=final_explanation,
                red_flags=final_flags[:3] if final_flags else ["Unusual communication pattern"],
                recommended_actions=final_actions[:3]
                if final_actions
                else ["Do not click links", "Do not share OTP"],
                confidence=final_conf,
                is_ai=True,
                reconciliation_notes=notes,
            )

        # -------------------------------------------------------------------------
        # SCENARIO 2: Gemini AI is Unavailable / Errored -> Offline Local Intelligence
        # -------------------------------------------------------------------------
        fallback_reason = "No API Key Configured"
        if gemini_result and "error_title" in gemini_result:
            fallback_reason = gemini_result["error_title"]

        flag_descriptions: List[str] = []
        for f in rule_results.findings:
            for detail in f.get("details", []):
                flag_descriptions.append(f"{f['icon']} {detail}")

        # Add dataset reference insight if available
        if dataset_matches.has_strong_match and dataset_matches.top_label:
            flag_descriptions.append(
                f"📚 Similar reference example labeled as {dataset_matches.top_label} ({humanize_category(dataset_matches.top_category)})"
            )

        # 1. Critical Threats or Direct Security Hazard (Safety Rule Override)
        if rule_results.has_critical_indicators:
            verdict = "SCAM"
            cat = dataset_matches.top_category if dataset_matches.has_strong_match else None
            scam_type = humanize_category(cat) if cat else "High-Risk Fraud Pattern (Critical Heuristic)"
            explanation = (
                "This message contains serious warning signs typical of known cyber fraud in India, "
                "such as severe threats, requests for credentials, or suspicious links."
            )
            actions = [
                "Do NOT click any link, scan QR codes, or download any APK file.",
                "Never share your OTP, MPIN, or password with anyone under any circumstance.",
                "Block the sender number immediately and report to 1930 if money was lost.",
            ]
            confidence = "HIGH"

        # 2. High Risk Rules without Safe Consensus
        elif rule_results.has_high_risk and dataset_matches.consensus_label != "SAFE":
            verdict = "SCAM"
            cat = dataset_matches.top_category if dataset_matches.has_strong_match else None
            scam_type = humanize_category(cat) if cat else "High-Risk Fraud Pattern"
            explanation = (
                "This message contains urgent threats, payment demands, or suspicious link patterns. "
                "Avoid engaging or clicking links."
            )
            actions = [
                "Do NOT click any link or call unverified numbers provided in this message.",
                "Verify independently through the official bank or service website.",
                "Never share sensitive banking credentials.",
            ]
            confidence = "HIGH" if dataset_matches.consensus_label == "SCAM" else "MEDIUM"

        # 3. Strong Dataset Reference Match
        elif dataset_matches.has_strong_match:
            if (dataset_matches.consensus_label == "SCAM"
                    and not rule_results.is_hard_negative and rule_results.net_risk_score >= 15):
                verdict = "SCAM"
                scam_type = humanize_category(dataset_matches.top_category)
                explanation = (
                    f"This message closely matches reference examples of {humanize_category(dataset_matches.top_category).lower()} "
                    "catalogued in the Scam Shield reference dataset."
                )
                actions = [
                    "Do NOT click any links, dial numbers, or download attachments from this message.",
                    "Block the sender number and report suspicious SMS to 1930.",
                ]
                confidence = "HIGH" if dataset_matches.max_similarity >= 0.22 else "MEDIUM"
            elif dataset_matches.consensus_label == "SAFE" and not rule_results.has_high_risk:
                verdict = "SAFE"
                scam_type = humanize_category(dataset_matches.top_category)
                explanation = (
                    "This message matches legitimate communication patterns with no identified fraud indicators."
                )
                actions = [
                    "Routine alert. No immediate defensive action required.",
                    "Always maintain caution and never share OTPs or banking PINs.",
                ]
                confidence = "HIGH" if dataset_matches.max_similarity >= 0.20 else "MEDIUM"
            elif dataset_matches.consensus_label == "SUSPICIOUS" and not rule_results.has_high_risk:
                verdict = "SUSPICIOUS"
                scam_type = humanize_category(dataset_matches.top_category)
                explanation = (
                    "This message matches suspicious or unsolicited communication patterns. Proceed with caution."
                )
                actions = [
                    "Verify independently using the official helpline or app.",
                    "Do not click links or share credentials.",
                ]
                confidence = "MEDIUM"
            else:
                verdict = "SUSPICIOUS"
                scam_type = humanize_category(dataset_matches.top_category)
                explanation = "This message contains ambiguous or potential warning signals. Please verify independently."
                actions = ["Verify independently through official channels.", "Never share OTP or PIN."]
                confidence = "MEDIUM"

        # 4. Moderate Similarity Dataset Match (max_similarity >= 0.08)
        elif dataset_matches.max_similarity >= 0.08 and dataset_matches.top_label:
            if dataset_matches.top_label == "SCAM" and rule_results.net_risk_score >= 10:
                verdict = "SCAM"
                scam_type = humanize_category(dataset_matches.top_category)
                explanation = (
                    f"This message matches patterns of {humanize_category(dataset_matches.top_category).lower()}."
                )
                actions = ["Do NOT click any links.", "Report to 1930 if money was lost."]
                confidence = "MEDIUM"
            elif dataset_matches.top_label == "SAFE" and rule_results.net_risk_score == 0:
                verdict = "SAFE"
                scam_type = humanize_category(dataset_matches.top_category)
                explanation = (
                    "No scam indicators were identified, and text matches standard legitimate communications."
                )
                actions = ["Routine alert. No immediate action required.", "Never share banking passwords or OTPs."]
                confidence = "MEDIUM"
            else:
                verdict = "SUSPICIOUS"
                scam_type = humanize_category(dataset_matches.top_category)
                explanation = (
                    "Similar examples were found, but they are not enough to confirm this message. Verify independently."
                )
                actions = ["Verify independently using official channels.", "Never share OTPs or passwords."]
                confidence = "MEDIUM"

        # 5. Rule Hard Negative
        elif rule_results.is_hard_negative and not rule_results.has_high_risk:
            verdict = "SAFE"
            scam_type = "Legitimate Transactional Alert"
            explanation = (
                "This appears to be a legitimate informational or transactional alert with no requests "
                "for sensitive credentials or suspicious actions."
            )
            actions = [
                "Routine transaction alert. No immediate action required.",
                "If not authorized by you, contact your bank's 24x7 helpline immediately.",
            ]
            confidence = "MEDIUM"

        # 6. Unverified Fallback
        else:
            verdict = "SUSPICIOUS"
            scam_type = "Unverified Text (Heuristic Preview)"
            explanation = (
                "No obvious scam patterns were triggered, but the message cannot be confirmed as authentic. "
                "Exercise caution when responding."
            )
            flag_descriptions = [
                "No standard threat triggers matched by built-in heuristics",
                "Full contextual intent could not be verified by offline checks",
            ]
            actions = [
                "Always verify independently through official apps rather than SMS links.",
                "Never share OTPs, PINs, or passwords with unverified contacts.",
            ]
            confidence = "LOW"

        return FinalDecision(
            verdict=verdict,
            scam_type=scam_type,
            explanation=explanation,
            red_flags=flag_descriptions[:3] if flag_descriptions else ["No obvious warning signs detected"],
            recommended_actions=actions,
            confidence=confidence,
            is_ai=False,
            fallback_reason=fallback_reason,
            reconciliation_notes=["Local decision engine executed using heuristic rules and dataset reference index."],
        )
