"""Local HTML interface. Run with python -m uvicorn web_server:app."""
import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from src.pipeline import ScamShieldPipeline
from src.image_reader import prepare_image, extract_text, ImageInputError, MAX_UPLOAD_BYTES

ROOT = Path(__file__).resolve().parent
app = FastAPI(title="Scam Shield", docs_url=None, redoc_url=None)
app.mount('/static', StaticFiles(directory=ROOT/'frontend'), name='static')


@lru_cache(maxsize=1)
def pipeline():
    return ScamShieldPipeline()


def api_key():
    key = os.getenv('GEMINI_API_KEY', '').strip()
    return key if key and not key.startswith('your_') else None


class Message(BaseModel):
    text: str = Field(min_length=1, max_length=12000)
    language: Literal['en', 'hi'] = 'en'


@app.get('/')
def home():
    return RedirectResponse('/static/index.html')


@app.get('/api/status')
def status():
    p = pipeline()
    return {'ai_available': bool(api_key()), 'dataset_available': p.is_dataset_available}


@app.post('/api/analyze')
def analyze(message: Message):
    if not message.text.strip():
        raise HTTPException(422, 'empty')
    try:
        p = pipeline()
        result = p.analyze(message.text, api_key=api_key(), language=message.language)
        return {
            **result.model_dump(exclude={'rule_results', 'dataset_matches', 'reconciliation_notes'}),
            'dataset_available': p.is_dataset_available,
            'references': [
                {'message': r.message, 'label': r.assigned_label, 'synthetic': r.is_synthetic}
                for r in (result.dataset_matches.matched_references if result.dataset_matches else [])
            ],
        }
    except Exception:
        raise HTTPException(503, 'analysis_failed') from None


@app.post('/api/extract')
async def extract(request: Request):
    # Raw bytes avoid multipart temporary files; enforce limit while streaming.
    data = bytearray()
    async for chunk in request.stream():
        if len(data) + len(chunk) > MAX_UPLOAD_BYTES:
            raise HTTPException(413, 'too_large')
        data.extend(chunk)
    try:
        png = await run_in_threadpool(prepare_image, bytes(data))
        result = await run_in_threadpool(extract_text, png, api_key())
        return {'text': result.text}
    except ImageInputError as exc:
        raise HTTPException(422, str(exc)) from None
