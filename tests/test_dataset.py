import csv
from pathlib import Path
import pytest
from src.config import resolve_dataset_dir
from src.dataset_loader import DatasetLoader, CuratedDataset, DatasetValidationReport

ROOT = Path(__file__).resolve().parent.parent

def test_dataset_discovery_and_loader():
    dataset_dir = resolve_dataset_dir()
    assert dataset_dir is not None
    assert dataset_dir.exists()
    assert (dataset_dir / "messages_english.csv").exists()
    assert (dataset_dir / "messages_hinglish.csv").exists()
    assert (dataset_dir / "legit_domains.csv").exists()
    assert (dataset_dir / "categories.csv").exists()
    assert (dataset_dir / "sources.csv").exists()

    loader = DatasetLoader(dataset_dir)
    dataset, report = loader.load()
    assert report.is_valid is True
    assert report.total_records == 948
    assert report.train_records == 662
    assert report.val_records == 141
    assert report.test_records == 145
    assert len(report.validation_errors) == 0

    assert dataset is not None
    assert dataset.train_count == 662
    assert dataset.val_count == 141
    assert dataset.test_count == 145

    # Check sources lookup
    src_info = dataset.get_source_info("SRC_PUB_UCI_SMSSPAM")
    assert src_info["source_name"].startswith("UCI Machine Learning Repository")
    assert "Creative Commons" in src_info["stated_license"]

def test_missing_dataset_fallback():
    non_existent = ROOT / "non_existent_dir_12345"
    loader = DatasetLoader(non_existent)
    dataset, report = loader.load()
    assert dataset is None
    assert report.is_valid is False
    assert len(report.validation_errors) > 0

def test_csv_schemas_and_integrity():
    data_dir = ROOT / "data" / "dataset"
    with open(data_dir / "messages_english.csv", "r", encoding="utf-8-sig") as f:
        en_rows = list(csv.DictReader(f))
    with open(data_dir / "messages_hinglish.csv", "r", encoding="utf-8-sig") as f:
        hg_rows = list(csv.DictReader(f))

    assert len(en_rows) == 582
    assert len(hg_rows) == 366

    all_rows = en_rows + hg_rows
    ids = [r["message_id"] for r in all_rows]
    assert len(ids) == len(set(ids)), "Message IDs must be unique"

    valid_labels = {"SCAM", "SAFE", "SUSPICIOUS"}
    valid_splits = {"train", "val", "test"}
    valid_origins = {"public", "synthetic"}

    for r in all_rows:
        assert r["label"] in valid_labels
        assert r["split"] in valid_splits
        assert r["origin"] in valid_origins
        assert len(r["message"].strip()) > 0
