import pytest
from src.pipeline import ScamShieldPipeline
from src.decision_engine import DecisionEngine
from src.rule_engine import RuleAnalysisResult
from src.reference_matcher import DatasetMatchResult

def test_pipeline_offline_scam():
    pipeline = ScamShieldPipeline()
    res = pipeline.analyze(
        "Dear Consumer, Your Electricity power will be disconnected tonight at 9:30 PM from the electricity office. Call 9876543210: http://bit.ly/bijli-pay"
    )
    assert res.verdict == "SCAM"
    assert res.is_ai is False
    assert res.fallback_reason == "No API Key Configured"
    assert res.is_dataset_informed is True
    assert len(res.red_flags) > 0
    assert len(res.recommended_actions) > 0

def test_pipeline_offline_hard_negative():
    pipeline = ScamShieldPipeline()
    res = pipeline.analyze(
        "Dear Customer, your A/C XX4921 has been debited by Rs 1,250.00 on 22-Oct-26 at Apollo Pharmacy via UPI. Avail Bal: Rs 24,180.50."
    )
    assert res.verdict == "SAFE"
    assert res.is_ai is False

def test_pipeline_blank_input():
    pipeline = ScamShieldPipeline()
    res = pipeline.analyze("    ")
    assert res.verdict == "SUSPICIOUS"
    assert res.scam_type == "Empty Message"
    assert res.is_ai is False

def test_decision_engine_guardrail_override():
    engine = DecisionEngine()
    # Scenario: AI erroneously returned SAFE, but rules found CRITICAL indicator (.apk / arrest)
    fake_rules = RuleAnalysisResult(
        score=10,
        net_risk_score=90,
        risk_level="CRITICAL",
        findings=[{"category": "Malicious APK", "icon": "🔗", "details": ["Direct APK file link"], "severity": "CRITICAL"}],
        has_critical_indicators=True,
        has_high_risk=True,
        is_hard_negative=False,
    )
    fake_dataset = DatasetMatchResult()
    fake_ai = {
        "success": True,
        "verdict": "SAFE",
        "scam_type": "Benign Text",
        "explanation": "No issue found.",
        "red_flags": [],
        "recommended_actions": [],
        "confidence": "HIGH",
    }
    decision = engine.reconcile(fake_rules, fake_dataset, fake_ai)
    # Guardrail must override AI SAFE to SCAM
    assert decision.verdict == "SCAM"
    assert "Safety Rule Override" in decision.scam_type
    assert any("Safety Guardrail" in note for note in decision.reconciliation_notes)
