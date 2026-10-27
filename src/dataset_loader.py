"""
Dataset loader and validator for the curated Scam Shield dataset.
Strictly isolates train, validation, and test partitions to prevent data leakage.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import pandas as pd
from pydantic import BaseModel, Field

REQUIRED_COLUMNS = [
    "curated_id",
    "message",
    "assigned_label",
    "split",
    "language",
    "curated_category",
    "is_synthetic",
    "source_id",
]

VALID_LABELS = {"SCAM", "SAFE", "SUSPICIOUS"}
VALID_SPLITS = {"train", "val", "test"}
VALID_LANGUAGES = {"en", "hinglish"}
VALID_ORIGINS = {"public", "synthetic"}

# Message files in the dataset folder, and the columns they must contain.
MESSAGE_FILES = ("messages_english.csv", "messages_hinglish.csv")
FILE_COLUMNS = [
    "message_id", "message", "label", "category", "risk_signals",
    "language", "origin", "source_id", "split",
]
# File column -> name used by the rest of the app
COLUMN_RENAMES = {
    "message_id": "curated_id",
    "label": "assigned_label",
    "category": "curated_category",
    "risk_signals": "curated_risk_signals",
}


class DatasetValidationReport(BaseModel):
    """Validation report describing dataset integrity and partitioning."""
    is_valid: bool
    total_records: int = 0
    train_records: int = 0
    val_records: int = 0
    test_records: int = 0
    label_distribution: Dict[str, int] = Field(default_factory=dict)
    language_distribution: Dict[str, int] = Field(default_factory=dict)
    synthetic_ratio: float = 0.0
    public_records_count: int = 0
    synthetic_records_count: int = 0
    validation_errors: List[str] = Field(default_factory=list)
    validation_warnings: List[str] = Field(default_factory=list)


class CuratedDataset:
    """Encapsulates loaded dataset partitions and source registry."""
    def __init__(
        self,
        df_train: pd.DataFrame,
        df_val: pd.DataFrame,
        df_test: pd.DataFrame,
        sources_df: Optional[pd.DataFrame] = None,
        report: Optional[DatasetValidationReport] = None,
        dataset_path: Optional[Path] = None,
    ):
        self.df_train = df_train
        self.df_val = df_val
        self.df_test = df_test
        self.sources_df = sources_df if sources_df is not None else pd.DataFrame()
        self.report = report
        self.dataset_path = dataset_path

        # Source metadata lookup by source_id
        self._source_lookup: Dict[str, Dict[str, Any]] = {}
        if not self.sources_df.empty and "source_id" in self.sources_df.columns:
            for _, row in self.sources_df.iterrows():
                self._source_lookup[str(row["source_id"])] = row.to_dict()

    def get_source_info(self, source_id: str) -> Dict[str, Any]:
        """Returns provenance and licensing information for a given source ID."""
        return self._source_lookup.get(
            str(source_id),
            {
                "source_name": "Unknown",
                "stated_license": "Unspecified",
                "redistribution_status": "Unknown",
                "is_synthetic": True,
            },
        )

    @property
    def train_count(self) -> int:
        return len(self.df_train)

    @property
    def val_count(self) -> int:
        return len(self.df_val)

    @property
    def test_count(self) -> int:
        return len(self.df_test)


class DatasetLoader:
    """Loads and validates the curated scam detection dataset."""

    def __init__(self, dataset_dir: Optional[Path] = None):
        self.dataset_dir = dataset_dir

    def load(self) -> Tuple[Optional[CuratedDataset], DatasetValidationReport]:
        """
        Loads the English and Hinglish message files and sources.csv from the dataset folder.
        Validates columns, labels, splits, languages, duplicates and empty messages.
        Returns (CuratedDataset, DatasetValidationReport).
        """
        if not self.dataset_dir or not Path(self.dataset_dir).exists():
            report = DatasetValidationReport(
                is_valid=False,
                validation_errors=[
                    f"Dataset directory does not exist or is not specified: {self.dataset_dir}"
                ],
            )
            return None, report

        folder = Path(self.dataset_dir)
        errors: List[str] = []
        warnings: List[str] = []

        frames = []
        for name in MESSAGE_FILES:
            path = folder / name
            if not path.exists():
                errors.append(f"Required dataset file missing: {path}")
                continue
            try:
                part = pd.read_csv(path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
            except Exception as e:
                errors.append(f"Failed to read CSV at {path}: {str(e)}")
                continue
            missing = [c for c in FILE_COLUMNS if c not in part.columns]
            if missing:
                errors.append(f"Missing required columns in {name}: {missing}")
                continue
            frames.append(part)

        if errors or not frames:
            return None, DatasetValidationReport(is_valid=False, validation_errors=errors)

        df = pd.concat(frames, ignore_index=True)
        df = df.rename(columns=COLUMN_RENAMES)
        df["is_synthetic"] = df["origin"].str.lower().eq("synthetic")

        sources_df = None
        sources_path = folder / "sources.csv"
        if sources_path.exists():
            try:
                sources_df = pd.read_csv(sources_path, encoding="utf-8-sig", dtype=str, keep_default_na=False)
                if "license" in sources_df.columns and "stated_license" not in sources_df.columns:
                    sources_df = sources_df.rename(columns={"license": "stated_license"})
            except Exception:
                sources_df = None

        # Validate
        missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_cols:
            errors.append(f"Missing required columns after loading: {missing_cols}")

        empty_msg_mask = df["message"].str.strip() == ""
        if empty_msg_mask.any():
            errors.append(f"Found {int(empty_msg_mask.sum())} records with missing or empty messages.")

        invalid_labels = set(df["assigned_label"].unique()) - VALID_LABELS
        if invalid_labels:
            errors.append(f"Found unexpected labels in label: {invalid_labels}")

        invalid_splits = set(df["split"].unique()) - VALID_SPLITS
        if invalid_splits:
            errors.append(f"Found unexpected splits in split: {invalid_splits}")

        invalid_langs = set(df["language"].unique()) - VALID_LANGUAGES
        if invalid_langs:
            errors.append(f"Found unexpected languages in language: {invalid_langs}")

        invalid_origins = set(df["origin"].str.lower().unique()) - VALID_ORIGINS
        if invalid_origins:
            errors.append(f"Found unexpected values in origin: {invalid_origins}")

        if df["curated_id"].duplicated().any():
            errors.append(f"Found {int(df['curated_id'].duplicated().sum())} duplicate message_id values.")

        if df["message"].duplicated().any():
            errors.append(f"Found {int(df['message'].duplicated().sum())} duplicate message texts.")

        if errors:
            return None, DatasetValidationReport(
                is_valid=False,
                validation_errors=errors,
                validation_warnings=warnings,
            )

        # Split into partitions
        df_train = df[df["split"] == "train"].copy().reset_index(drop=True)
        df_val = df[df["split"] == "val"].copy().reset_index(drop=True)
        df_test = df[df["split"] == "test"].copy().reset_index(drop=True)

        if len(df_train) == 0:
            errors.append("Train partition is empty.")
        if len(df_val) == 0:
            warnings.append("Validation partition is empty.")
        if len(df_test) == 0:
            warnings.append("Test partition is empty.")

        # Summary statistics
        total_records = len(df)
        label_dist = df["assigned_label"].value_counts().to_dict()
        lang_dist = df["language"].value_counts().to_dict()
        synthetic_count = int(df["is_synthetic"].sum())
        public_count = total_records - synthetic_count
        synth_ratio = round(synthetic_count / total_records, 4) if total_records > 0 else 0.0

        if synth_ratio > 0.8:
            warnings.append(
                f"High synthetic data proportion ({synth_ratio * 100:.1f}%). Candidate records require provenance tracking."
            )

        report = DatasetValidationReport(
            is_valid=not errors,
            total_records=total_records,
            train_records=len(df_train),
            val_records=len(df_val),
            test_records=len(df_test),
            label_distribution=label_dist,
            language_distribution=lang_dist,
            synthetic_ratio=synth_ratio,
            public_records_count=public_count,
            synthetic_records_count=synthetic_count,
            validation_errors=errors,
            validation_warnings=warnings,
        )

        if not report.is_valid:
            return None, report

        curated_dataset = CuratedDataset(
            df_train=df_train,
            df_val=df_val,
            df_test=df_test,
            sources_df=sources_df,
            report=report,
            dataset_path=folder,
        )

        return curated_dataset, report
