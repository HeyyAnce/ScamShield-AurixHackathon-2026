import pytest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

def test_imports():
    import src.config as config
    import src.dataset_loader as dataset_loader
    import src.reference_matcher as reference_matcher
    import src.rule_engine as rule_engine
    import src.gemini_client as gemini_client
    import src.decision_engine as decision_engine
    import src.image_reader as image_reader
    import src.pipeline as pipeline
    from src import (
        ScamShieldPipeline,
        PipelineOutput,
        DatasetLoader,
        CuratedDataset,
        DatasetReferenceMatcher,
        RuleEngine,
        DecisionEngine,
        GeminiAnalyzer,
    )
    import web_server
    import cloud_ui

    assert ScamShieldPipeline is not None
    assert web_server.app is not None
    assert cloud_ui.pipeline is not None
