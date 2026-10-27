"""Offline regression checks: no real credentials or external requests required."""
import os
from io import BytesIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase, main
from unittest.mock import patch

os.environ['GEMINI_API_KEY'] = ''

from PIL import Image
from fastapi.testclient import TestClient
from src import config
from src.dataset_loader import DatasetLoader
from src.pipeline import ScamShieldPipeline
from src.image_reader import prepare_image, ImageInputError, MAX_UPLOAD_BYTES
from src.gemini_client import GeminiAnalyzer
import web_server
import cloud_ui


class ConfigTests(TestCase):
    def test_missing_override_uses_bundle(self):
        with patch.dict(os.environ, {'SCAM_SHIELD_DATASET_DIR': 'missing-folder'}):
            self.assertEqual(config.resolve_dataset_dir(), config.DATASET_DIR.resolve())

    def test_relative_path_is_project_relative(self):
        with patch.dict(os.environ, {'SCAM_SHIELD_DATASET_DIR': 'data/dataset'}):
            self.assertEqual(config.resolve_dataset_dir(), config.DATASET_DIR.resolve())

    def test_partial_override_is_not_selected(self):
        with TemporaryDirectory() as folder:
            Path(folder, 'messages_english.csv').touch()
            with patch.dict(os.environ, {'SCAM_SHIELD_DATASET_DIR': folder}):
                self.assertEqual(config.resolve_dataset_dir(), config.DATASET_DIR.resolve())

    def test_complete_override_is_selected(self):
        with TemporaryDirectory() as folder:
            for name in ('messages_english.csv', 'messages_hinglish.csv'):
                Path(folder, name).touch()
            with patch.dict(os.environ, {'SCAM_SHIELD_DATASET_DIR': folder}):
                self.assertEqual(config.resolve_dataset_dir(), Path(folder).resolve())

    def test_no_bundle_no_override(self):
        with TemporaryDirectory() as folder, patch.object(config, 'DATASET_DIR', Path(folder)), patch.dict(os.environ, {'SCAM_SHIELD_DATASET_DIR': ''}):
            self.assertIsNone(config.resolve_dataset_dir())


class PipelineTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.detector = ScamShieldPipeline(config.DATASET_DIR)

    def test_dataset_and_split(self):
        self.assertTrue(self.detector.is_dataset_available)
        self.assertEqual(self.detector.dataset_report.total_records, 948)
        self.assertEqual(self.detector.matcher.num_docs, 662)
        ids = set(self.detector.matcher.train_df.curated_id)
        self.assertFalse(ids & set(self.detector.dataset.df_test.curated_id))
        self.assertFalse(ids & set(self.detector.dataset.df_val.curated_id))

    def test_no_key_fallback(self):
        result = self.detector.analyze('Share OTP immediately to update KYC at bit.ly/test')
        self.assertFalse(result.is_ai)
        self.assertEqual(result.verdict, 'SCAM')

    def test_missing_dataset_fallback(self):
        detector = ScamShieldPipeline(dataset_dir=None)
        self.assertFalse(detector.is_dataset_available)
        self.assertEqual(detector.analyze('Share OTP immediately').verdict, 'SCAM')

    def test_missing_csv_is_invalid(self):
        with TemporaryDirectory() as folder:
            dataset, report = DatasetLoader(Path(folder)).load()
            self.assertIsNone(dataset)
            self.assertFalse(report.is_valid)

    def test_empty_train_never_returns_usable_dataset(self):
        import pandas as pd
        with TemporaryDirectory() as folder:
            for name in ('messages_english.csv', 'messages_hinglish.csv'):
                frame = pd.read_csv(config.DATASET_DIR / name, keep_default_na=False)
                frame['split'] = 'test'
                frame.to_csv(Path(folder, name), index=False)
            dataset, report = DatasetLoader(Path(folder)).load()
            self.assertIsNone(dataset)
            self.assertFalse(report.is_valid)


class ImageTests(TestCase):
    def test_invalid_bytes(self):
        with self.assertRaises(ImageInputError):
            prepare_image(b'not an image')

    def test_size_limit(self):
        with self.assertRaisesRegex(ImageInputError, 'too_large'):
            prepare_image(b'x' * (MAX_UPLOAD_BYTES + 1))

    def test_valid_png(self):
        buffer = BytesIO()
        Image.new('RGB', (20, 20), 'white').save(buffer, format='PNG')
        self.assertTrue(prepare_image(buffer.getvalue()).startswith(b'\x89PNG'))

    def test_unsupported_format(self):
        buffer = BytesIO()
        Image.new('RGB', (20, 20)).save(buffer, format='BMP')
        with self.assertRaisesRegex(ImageInputError, 'wrong_format'):
            prepare_image(buffer.getvalue())


class ApiTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(web_server.app)

    def test_pages_and_status(self):
        for page in ('index', 'safety', 'help', 'about'):
            self.assertEqual(self.client.get('/static/' + page + '.html').status_code, 200)
        self.assertEqual(self.client.get('/api/status').json(), {'ai_available': False, 'dataset_available': True})

    def test_reject_bad_text(self):
        for payload in ({'text': ''}, {'text': '   '}, {'text': 'x' * 12001}, {'text': 'hello', 'language': 'xx'}):
            self.assertEqual(self.client.post('/api/analyze', json=payload).status_code, 422)

    def test_analysis(self):
        result = self.client.post('/api/analyze', json={'text': 'Share OTP immediately', 'language': 'hi'})
        self.assertEqual(result.status_code, 200)
        self.assertFalse(result.json()['is_ai'])

    def test_bad_image(self):
        self.assertEqual(self.client.post('/api/extract', content=b'bad').status_code, 422)

    def test_streamlit_bridge_validation(self):
        detector = web_server.pipeline()
        for request in ({'id': 5}, {'id': 'a', 'path': '/api/analyze', 'payload': {'text': ''}}, {'id': 'b', 'path': '/api/extract', 'payload': '!!!'}):
            self.assertEqual(cloud_ui.handle_request(request, detector, None)['status'], 422)

    def test_streamlit_bridge_analysis(self):
        result = cloud_ui.handle_request({'id': 'test', 'path': '/api/analyze', 'payload': {'text': 'Share OTP now', 'language': 'en'}}, web_server.pipeline(), None)
        self.assertEqual(result['status'], 200)
        self.assertFalse(result['body']['is_ai'])


class GeminiTests(TestCase):
    def test_invalid_json_shapes_fall_back_and_close_client(self):
        rules = web_server.pipeline().rule_engine.analyze('hello')
        for body in ('[]', '{"verdict":"SAFE"}', '{"verdict":null}', 'not json'):
            with self.subTest(body=body), patch('google.genai.Client') as constructor:
                client = constructor.return_value
                client.models.generate_content.return_value.text = body
                result = GeminiAnalyzer().analyze('hello', rules, api_key='test-placeholder')
                self.assertEqual(result['error_type'], 'JSON_PARSE_ERROR')
                client.close.assert_called_once()

    def test_valid_ai_response_and_close(self):
        rules = web_server.pipeline().rule_engine.analyze('hello')
        with patch('google.genai.Client') as constructor:
            client = constructor.return_value
            client.models.generate_content.return_value.text = '{"verdict":"SUSPICIOUS","scam_type":"Unverified","explanation":"Verify independently","red_flags":[],"recommended_actions":["Verify"],"confidence":"LOW"}'
            result = GeminiAnalyzer().analyze('hello', rules, api_key='test-placeholder')
            self.assertTrue(result['success'])
            client.close.assert_called_once()


if __name__ == '__main__':
    main()


class DomainFallbackTests(TestCase):
    def test_alternate_messages_keep_bundled_domains(self):
        import shutil
        with TemporaryDirectory() as folder:
            for name in ("messages_english.csv", "messages_hinglish.csv", "sources.csv"):
                shutil.copy(config.DATASET_DIR / name, Path(folder) / name)
            detector = ScamShieldPipeline(Path(folder))
            self.assertIn("sbi.co.in", detector.rule_engine.official_domains)
            self.assertFalse(detector.rule_engine.analyze("Visit https://sbi.co.in for your statement").has_high_risk)
