import csv
import re
from pathlib import Path
from src.dataset_loader import DatasetLoader
from src.reference_matcher import DatasetReferenceMatcher

ROOT = Path(__file__).resolve().parents[1]

def test_hindi_references_are_loaded_and_review_corpus_is_excluded():
    dataset, report = DatasetLoader(ROOT / 'data/dataset').load()
    assert report.is_valid
    assert report.total_records == 1948
    assert report.language_distribution['hi'] == 200
    assert dataset.val_count == 141 and dataset.test_count == 145
    added = dataset.df_train[dataset.df_train.source_id == 'SYN_C_CLAUDE_20261027']
    assert len(added) == 1000
    assert added.is_synthetic.all()
    matcher = DatasetReferenceMatcher(dataset)
    hi = added[added.language == 'hi'].iloc[0]
    matches = matcher.find_similar(hi.message).matched_references
    assert any(m.curated_id == hi.curated_id for m in matches)
    assert set(matcher.train_df.source_id) == set(dataset.df_train.source_id)
    assert not any(str(i).startswith('PUBLIC-') for i in matcher.train_df.curated_id)

def test_added_records_preserve_template_provenance():
    with (ROOT / 'data/dataset/import_manifest.csv').open(encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 1000
    assert len({r['message_id'] for r in rows}) == 1000
    assert all(r['template_id'] and r['source_description'] for r in rows)

def test_all_three_message_files_have_unique_text_and_ids():
    rows=[]
    for name in ('messages_english.csv','messages_hinglish.csv','messages_hindi.csv'):
        with (ROOT/'data/dataset'/name).open(encoding='utf-8') as f: rows.extend(csv.DictReader(f))
    assert len({r['message_id'] for r in rows}) == len(rows)
    assert len({re.sub(r'\s+', ' ', r['message'].casefold()).strip() for r in rows}) == len(rows)
