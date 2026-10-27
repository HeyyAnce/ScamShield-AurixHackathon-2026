import pytest
from pathlib import Path
from src.config import resolve_dataset_dir
from src.dataset_loader import DatasetLoader
from src.rule_engine import RuleEngine, is_official_host, load_official_domain_lists
from src.reference_matcher import DatasetReferenceMatcher

ROOT = Path(__file__).resolve().parent.parent

def test_rule_threat_patterns():
    engine = RuleEngine()
    
    # Electricity disconnection scam
    res = engine.analyze("Dear user your electricity power will be disconnected tonight. Call 9876543210")
    assert res.has_high_risk is True
    assert res.risk_level in ["HIGH", "CRITICAL"]

    # Digital arrest threat (critical)
    res_arrest = engine.analyze("This is CBI Mumbai. A digital arrest warrant is issued against your Aadhaar.")
    assert res_arrest.has_critical_indicators is True
    assert res_arrest.risk_level == "CRITICAL"

    # Malicious APK link (critical)
    res_apk = engine.analyze("Download the update at http://example.com/sbi-app.apk now")
    assert res_apk.has_critical_indicators is True
    assert res_apk.risk_level == "CRITICAL"

def test_rule_hard_negatives():
    engine = RuleEngine()

    # Routine bank debit alert
    res_debit = engine.analyze("Dear Customer, your A/C XX4921 has been debited by Rs 1,250.00 on 22-Oct-26 at Apollo Pharmacy via UPI. Avail Bal: Rs 24,180.50.")
    assert res_debit.is_hard_negative is True
    assert res_debit.has_critical_indicators is False
    assert res_debit.net_risk_score <= 15

    # Safe OTP warning
    res_otp = engine.analyze("123456 is the OTP to login to your bank portal. Do not share this OTP with anyone.")
    assert res_otp.is_hard_negative is True
    assert res_otp.has_critical_indicators is False

def test_official_domains():
    domains, zones = load_official_domain_lists()
    assert "sbi.bank.in" in domains
    assert "sbi.co.in" in domains
    assert ".bank.in" in zones

    assert is_official_host("sbi.bank.in", domains, zones) is True
    assert is_official_host("retail.sbi.co.in", domains, zones) is True
    assert is_official_host("hdfc.bank.in", domains, zones) is True
    # Lookalike attack should not match
    assert is_official_host("sbi.co.in.fake-site.com", domains, zones) is False
    assert is_official_host("sbi-yono-update.xyz", domains, zones) is False

def test_reference_matcher():
    dataset_dir = resolve_dataset_dir()
    loader = DatasetLoader(dataset_dir)
    dataset, _ = loader.load()
    matcher = DatasetReferenceMatcher(dataset)

    # Match electricity query
    result = matcher.find_similar("Dear Consumer, Your electricity will be disconnected tonight", top_k=3)
    assert len(result.matched_references) > 0
    assert result.top_label == "SCAM"
    assert result.max_similarity > 0.15

    # Match genuine bank transaction
    res_safe = matcher.find_similar("A/C XX1234 has been debited by Rs 500 Avail Bal Rs 10000", top_k=3)
    assert len(res_safe.matched_references) > 0
    assert res_safe.top_label == "SAFE"
