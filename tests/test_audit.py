import os
import re
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parent.parent

def test_html_links():
    frontend = ROOT / "frontend"
    for html_file in frontend.glob("*.html"):
        content = html_file.read_text(encoding="utf-8")
        hrefs = re.findall(r'href=["\']([^"\']+)["\']', content)
        srcs = re.findall(r'src=["\']([^"\']+)["\']', content)
        for src in srcs:
            clean = src.split("?")[0]
            if clean.startswith("/static/"):
                asset = frontend / clean.replace("/static/", "")
                assert asset.exists(), f"Asset {src} in {html_file.name} does not exist"
        for href in hrefs:
            clean = href.split("?")[0].split("#")[0]
            if clean.startswith("/static/"):
                asset = frontend / clean.replace("/static/", "")
                assert asset.exists(), f"Link {href} in {html_file.name} does not exist"

def test_no_outdated_github_urls():
    for f in (ROOT / "frontend").glob("*.*"):
        text = f.read_text(encoding="utf-8")
        assert "HeyyAnce/scam-shield" not in text, f"Outdated repo URL in {f.name}"
