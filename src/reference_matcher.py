"""
Reference Matcher for Scam Shield.
Retrieves the most relevant reference examples using multilingual token
and character n-gram similarity. Strictly restricted to the train partition.
"""

import re
import math
from collections import Counter
from typing import Dict, List, Any, Optional
import pandas as pd
from pydantic import BaseModel, Field

from src.dataset_loader import CuratedDataset


class MatchedReference(BaseModel):
    """A single retrieved training reference message with provenance."""
    curated_id: str
    message: str
    assigned_label: str  # SCAM, SAFE, SUSPICIOUS
    curated_category: str
    similarity_score: float
    language: str
    is_synthetic: bool
    source_id: str
    source_name: str = "Unknown"
    license_note: str = "Unspecified"
    curated_risk_signals: Optional[str] = None


class DatasetMatchResult(BaseModel):
    """Aggregate matching result against the training partition."""
    matched_references: List[MatchedReference] = Field(default_factory=list)
    top_label: Optional[str] = None
    consensus_label: Optional[str] = None
    top_category: Optional[str] = None
    max_similarity: float = 0.0
    has_strong_match: bool = False
    synthetic_count: int = 0
    public_count: int = 0
    label_counts: Dict[str, int] = Field(default_factory=dict)


def _tokenize(text: str) -> List[str]:
    """
    Extracts word tokens and character 3-grams to support English,
    Devanagari Hindi, and romanized Hinglish transliterations.
    """
    cleaned = str(text).lower().strip()
    # Word tokens
    words = re.findall(r"\b\w+\b", cleaned, re.UNICODE)
    # Character 3-grams for subword / transliteration robustness
    char_ngrams = []
    if len(cleaned) >= 3:
        for i in range(len(cleaned) - 2):
            ngram = cleaned[i : i + 3]
            if not ngram.isspace():
                char_ngrams.append(ngram)
    return words + char_ngrams


class DatasetReferenceMatcher:
    """
    Indexes the training partition and provides fast, transparent
    similarity retrieval for user messages.
    """

    def __init__(self, dataset: CuratedDataset, min_similarity: float = 0.08):
        self.dataset = dataset
        self.min_similarity = min_similarity

        # Strictly operate on train split
        self.train_df = dataset.df_train.copy().reset_index(drop=True)
        self.num_docs = len(self.train_df)

        # Build inverted index & document token frequencies
        self.doc_token_counts: List[Counter] = []
        self.doc_lengths: List[int] = []
        self.doc_freq: Counter = Counter()

        for idx, row in self.train_df.iterrows():
            tokens = _tokenize(str(row["message"]))
            cnt = Counter(tokens)
            self.doc_token_counts.append(cnt)
            self.doc_lengths.append(len(tokens))
            for tok in cnt.keys():
                self.doc_freq[tok] += 1

        self.avg_doc_len = (
            sum(self.doc_lengths) / max(1, self.num_docs) if self.num_docs > 0 else 1.0
        )

        # Precompute IDF for BM25
        self.idf: Dict[str, float] = {}
        for tok, df in self.doc_freq.items():
            # Standard BM25 IDF formulation
            self.idf[tok] = math.log(1.0 + (self.num_docs - df + 0.5) / (df + 0.5))

    def find_similar(
        self, query_text: str, top_k: int = 3, min_similarity: Optional[float] = None
    ) -> DatasetMatchResult:
        """
        Scores the query text against all training examples and returns
        the top_k most similar reference cases with full provenance.
        """
        threshold = min_similarity if min_similarity is not None else self.min_similarity
        if self.num_docs == 0 or not query_text.strip():
            return DatasetMatchResult()

        q_tokens = _tokenize(query_text)
        q_cnt = Counter(q_tokens)
        q_len = len(q_tokens)

        if not q_tokens:
            return DatasetMatchResult()

        # BM25 parameters
        k1 = 1.5
        b = 0.75

        # Score matching documents
        scores: Dict[int, float] = {}
        for tok in q_cnt.keys():
            if tok not in self.doc_freq:
                continue
            idf_val = self.idf[tok]
            for doc_idx, doc_cnt in enumerate(self.doc_token_counts):
                if tok in doc_cnt:
                    tf = doc_cnt[tok]
                    doc_len = self.doc_lengths[doc_idx]
                    denom = tf + k1 * (1.0 - b + b * (doc_len / max(1.0, self.avg_doc_len)))
                    score = idf_val * (tf * (k1 + 1.0)) / max(0.001, denom)
                    scores[doc_idx] = scores.get(doc_idx, 0.0) + score

        if not scores:
            return DatasetMatchResult()

        # Normalize score into a pseudo-similarity ratio [0.0, 1.0]
        # Query self-score approx for normalization
        max_possible = sum(self.idf.get(t, 1.0) * (k1 + 1.0) for t in q_cnt.keys())
        norm_factor = max(1.0, max_possible)

        scored_docs = []
        for doc_idx, raw_score in scores.items():
            sim = min(1.0, raw_score / norm_factor)
            if sim >= threshold:
                scored_docs.append((doc_idx, sim))

        # Sort descending by similarity
        scored_docs.sort(key=lambda x: x[1], reverse=True)
        top_items = scored_docs[:top_k]

        matched_refs: List[MatchedReference] = []
        synth_count = 0
        pub_count = 0
        label_counter: Counter = Counter()

        for doc_idx, sim in top_items:
            row = self.train_df.iloc[doc_idx]
            source_id = str(row.get("source_id", "unknown"))
            source_info = self.dataset.get_source_info(source_id)
            is_synth = bool(row.get("is_synthetic", True))
            if is_synth:
                synth_count += 1
            else:
                pub_count += 1

            lbl = str(row.get("assigned_label", "SUSPICIOUS")).upper()
            label_counter[lbl] += 1

            matched_refs.append(
                MatchedReference(
                    curated_id=str(row.get("curated_id", "")),
                    message=str(row.get("message", "")),
                    assigned_label=lbl,
                    curated_category=str(row.get("curated_category", "unclassified")),
                    similarity_score=round(sim, 4),
                    language=str(row.get("language", "en")),
                    is_synthetic=is_synth,
                    source_id=source_id,
                    source_name=source_info.get("source_name", "Curated Reference"),
                    license_note=source_info.get("stated_license", "Unspecified"),
                    curated_risk_signals=str(row.get("curated_risk_signals", ""))
                    if pd.notna(row.get("curated_risk_signals"))
                    else None,
                )
            )

        if not matched_refs:
            return DatasetMatchResult()

        top_ref = matched_refs[0]
        max_sim = top_ref.similarity_score
        consensus = label_counter.most_common(1)[0][0] if label_counter else None

        return DatasetMatchResult(
            matched_references=matched_refs,
            top_label=top_ref.assigned_label,
            consensus_label=consensus,
            top_category=top_ref.curated_category,
            max_similarity=max_sim,
            has_strong_match=max_sim >= 0.16,
            synthetic_count=synth_count,
            public_count=pub_count,
            label_counts=dict(label_counter),
        )
