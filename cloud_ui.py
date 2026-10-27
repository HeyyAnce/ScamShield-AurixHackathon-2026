"""Serve the shared HTML frontend through Streamlit Community Cloud."""
import base64
import os
from pathlib import Path
import tempfile

import streamlit as st
import streamlit.components.v1 as components

from src.pipeline import ScamShieldPipeline
from src.image_reader import prepare_image, extract_text, ImageInputError, MAX_UPLOAD_BYTES

ROOT = Path(__file__).resolve().parent


@st.cache_resource
def component():
    # Generated assets live outside the repository; never include secrets or data.
    destination = Path(tempfile.mkdtemp(prefix="scam-shield-ui-"))
    for source in (ROOT / "frontend").iterdir():
        if source.suffix not in {".html", ".css", ".js"}:
            continue
        text = source.read_text(encoding="utf-8").replace('/static/', './')
        if source.suffix == '.html':
            text = text.replace('<head>', '<head><script src="./cloud-bridge.js" defer></script>', 1)
        (destination / source.name).write_text(text, encoding="utf-8")
    return components.declare_component("scam_shield_web", path=str(destination))


@st.cache_resource
def pipeline():
    return ScamShieldPipeline()


def api_key():
    try:
        key = str(st.secrets.get('GEMINI_API_KEY', '')).strip()
    except (FileNotFoundError, st.errors.StreamlitSecretNotFoundError):
        key = ''
    key = key or os.getenv('GEMINI_API_KEY', '').strip()
    return key if key and not key.startswith('your_') else None


def handle_request(request, detector, key):
    """Validate untrusted component input before calling the existing pipeline."""
    request_id = request.get('id')
    if not isinstance(request_id, str) or len(request_id) > 100:
        return {'id': '', 'status': 422, 'body': {'detail': 'invalid_request'}}
    response = {'id': request_id, 'status': 200}
    try:
        path = request.get('path')
        payload = request.get('payload')
        if path == '/api/analyze':
            if not isinstance(payload, dict):
                raise ValueError('invalid_message')
            text, language = payload.get('text'), payload.get('language')
            if not isinstance(text, str) or not text.strip() or len(text) > 12000 or language not in ('en', 'hi'):
                raise ValueError('invalid_message')
            result = detector.analyze(text, api_key=key, language=language)
            response['body'] = {
                **result.model_dump(exclude={'rule_results', 'dataset_matches', 'reconciliation_notes'}),
                'dataset_available': detector.is_dataset_available,
                'references': [
                    {'message': item.message, 'label': item.assigned_label, 'synthetic': item.is_synthetic}
                    for item in (result.dataset_matches.matched_references if result.dataset_matches else [])
                ],
            }
        elif path == '/api/extract':
            if not isinstance(payload, str) or len(payload) > ((MAX_UPLOAD_BYTES + 2) // 3) * 4:
                raise ValueError('invalid_image')
            raw = base64.b64decode(payload, validate=True)
            if len(raw) > MAX_UPLOAD_BYTES:
                raise ValueError('too_large')
            response['body'] = {'text': extract_text(prepare_image(raw), key).text}
        else:
            raise ValueError('invalid_request')
    except (ValueError, ImageInputError):
        response.update(status=422, body={'detail': 'invalid_input'})
    except Exception:
        response.update(status=503, body={'detail': 'analysis_unavailable'})
    return response


def main():
    st.set_page_config(page_title='Scam Shield', page_icon='🛡️', layout='wide', initial_sidebar_state='collapsed')
    st.markdown('''<style>
    [data-testid="stHeader"], [data-testid="stToolbar"], footer {display:none;}
    .stMainBlockContainer {max-width:100%;padding:0;}
    [data-testid="stVerticalBlock"] {gap:0;}
    .stApp {background:#f1f8f7;}
    iframe[title="cloud_ui.scam_shield_web"] {display:block;width:100%;border:0;}
    </style>''', unsafe_allow_html=True)
    response = st.session_state.get('web_response')
    request = component()(response=response, key='scam_shield_frontend', default=None)
    if isinstance(request, dict) and request.get('id') != st.session_state.get('web_last_request'):
        st.session_state.web_last_request = request.get('id')
        # Session-local response only. No global cache of submitted messages.
        st.session_state.web_response = handle_request(request, pipeline(), api_key())
        st.rerun()
