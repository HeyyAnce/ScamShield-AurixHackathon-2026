"""
End-to-end Scam Shield Detection Pipeline.
Orchestrates:
User message -> Rule Engine -> Dataset Reference Matching -> Gemini Analysis -> Decision Reconciliation
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
from pydantic import BaseModel, Field

from src.config import resolve_dataset_dir
from src.dataset_loader import DatasetLoader, CuratedDataset, DatasetValidationReport
from src.reference_matcher import DatasetReferenceMatcher, DatasetMatchResult
from src.rule_engine import RuleEngine, RuleAnalysisResult
from src.gemini_client import GeminiAnalyzer
from src.decision_engine import DecisionEngine, FinalDecision


class PipelineOutput(BaseModel):
    """Complete output produced by the Scam Shield pipeline."""
    # Core Verdict & Safety Advice
    verdict: str  # SCAM, SUSPICIOUS, SAFE
    scam_type: str
    explanation: str
    red_flags: List[str] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    confidence: str  # HIGH, MEDIUM, LOW

    # Execution Mode & Provenance
    is_ai: bool
    fallback_reason: Optional[str] = None
    is_dataset_informed: bool = False
    reconciliation_notes: List[str] = Field(default_factory=list)

    # Detailed Sub-Engine Signals
    rule_results: Optional[RuleAnalysisResult] = None
    dataset_matches: Optional[DatasetMatchResult] = None


_AUTO_RESOLVE = object()


class ScamShieldPipeline:
    """
    Main orchestrator for Scam Shield detection.
    Can operate in full AI mode, dataset-augmented heuristic mode, or pure offline rule mode.
    """

    def __init__(self, dataset_dir: Any = _AUTO_RESOLVE):
        if dataset_dir is _AUTO_RESOLVE:
            self.dataset_dir = resolve_dataset_dir()
        else:
            self.dataset_dir = dataset_dir
        self.dataset: Optional[CuratedDataset] = None
        self.dataset_report: Optional[DatasetValidationReport] = None
        self.matcher: Optional[DatasetReferenceMatcher] = None

        # Load Dataset if available
        if self.dataset_dir:
            loader = DatasetLoader(self.dataset_dir)
            self.dataset, self.dataset_report = loader.load()
            if self.dataset and self.dataset_report and self.dataset_report.is_valid:
                self.matcher = DatasetReferenceMatcher(self.dataset)

        # Initialize core detection engines
        self.rule_engine = RuleEngine()
        self.gemini_analyzer = GeminiAnalyzer()
        self.decision_engine = DecisionEngine()

    @property
    def is_dataset_available(self) -> bool:
        return self.matcher is not None and self.dataset is not None

    @property
    def train_records_count(self) -> int:
        return self.dataset.train_count if self.dataset else 0

    def analyze(self, text: str, api_key: Optional[str] = None, language: str = "en") -> PipelineOutput:
        """
        Runs the full detection pipeline on the provided text.
        """
        cleaned = text.strip()
        if not cleaned:
            return PipelineOutput(
                verdict="SUSPICIOUS",
                scam_type="Empty Message",
                explanation="No text was provided for analysis.",
                red_flags=["Input message was blank"],
                recommended_actions=["Please provide a message to analyze."],
                confidence="LOW",
                is_ai=False,
            )

        # 1. Rule Engine Analysis
        rule_results = self.rule_engine.analyze(cleaned)

        # 2. Dataset Reference Matching (if dataset is loaded)
        dataset_matches = DatasetMatchResult()
        matched_refs = []
        is_dataset_informed = False

        if self.matcher:
            dataset_matches = self.matcher.find_similar(cleaned, top_k=3)
            matched_refs = dataset_matches.matched_references
            if matched_refs:
                is_dataset_informed = True

        # 3. Gemini AI Analysis (if API key available)
        gemini_result = None
        if api_key:
            gemini_result = self.gemini_analyzer.analyze(
                text=cleaned,
                rule_results=rule_results,
                references=matched_refs,
                api_key=api_key,
                language=language,
            )

        # 4. Decision Engine Reconciliation
        decision: FinalDecision = self.decision_engine.reconcile(
            rule_results=rule_results,
            dataset_matches=dataset_matches,
            gemini_result=gemini_result,
        )

        return PipelineOutput(
            verdict=decision.verdict,
            scam_type=decision.scam_type,
            explanation=decision.explanation,
            red_flags=decision.red_flags,
            recommended_actions=decision.recommended_actions,
            confidence=decision.confidence,
            is_ai=decision.is_ai,
            fallback_reason=decision.fallback_reason,
            is_dataset_informed=is_dataset_informed,
            reconciliation_notes=decision.reconciliation_notes,
            rule_results=rule_results,
            dataset_matches=dataset_matches,
        )
