"""
Scam Shield detection system package.
"""

from src.pipeline import ScamShieldPipeline, PipelineOutput
from src.dataset_loader import DatasetLoader, CuratedDataset
from src.reference_matcher import DatasetReferenceMatcher
from src.rule_engine import RuleEngine
from src.decision_engine import DecisionEngine
from src.gemini_client import GeminiAnalyzer

__all__ = [
    "ScamShieldPipeline",
    "PipelineOutput",
    "DatasetLoader",
    "CuratedDataset",
    "DatasetReferenceMatcher",
    "RuleEngine",
    "DecisionEngine",
    "GeminiAnalyzer",
]
