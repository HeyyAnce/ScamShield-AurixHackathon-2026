# ScamShield | AURIX 2026

**Check a suspicious message before you act.**

ScamShield helps people in India examine SMS, WhatsApp and email text for scam warning signs. It combines rules, reference examples and Google Gemini to explain a result and suggest next steps in plain language.

[Open the live app](https://scamshield-aurixhackathon-2026.streamlit.app/) · [GitHub repository](https://github.com/HeyyAnce/ScamShield-AurixHackathon-2026)

## What you can do

- Paste a message in English, Hindi or Hinglish.
- See a verdict, reasons, suggested actions and which checks were used.
- Switch between English and Hindi, and light and dark themes.
- Try example messages before checking your own.
- Upload a screenshot, review the extracted text and then analyze it.
- Explore Home, Safety Guide, Help and About/Privacy pages.

| Result | How to interpret it |
| --- | --- |
| **Scam** | Strong scam indicators were found. |
| **Likely scam** | The message looks suspicious and needs independent verification. |
| **Safe** | No clear scam signs were found; this does **not** prove the sender is genuine. |

ScamShield is a second opinion. It does not authenticate senders, block payments or guarantee protection.

## How it works

```text
Message text / reviewed screenshot text
                  |
           Python pipeline
                  |
      +-----------+------------+
      |           |            |
 Warning rules  Reference   Gemini analysis
                matching   (when available)
      |           |            |
      +-----------+------------+
                  |
           Decision engine
                  |
     Verdict + reasons + next steps
```

1. **Rules** detect patterns such as threats, urgency, OTP/PIN requests, suspicious links, APK downloads and payment tricks.
2. **Reference matching** retrieves similar messages using lexical similarity. It does not train a model.
3. **Gemini** analyzes the message when a valid server-side API key and service access are available.
4. **The decision engine** reconciles the signals into a result.

If Gemini is unavailable, text analysis falls back to rules and reference examples. The interface indicates when AI was not used. Screenshot extraction requires Gemini and is a separate step before message analysis.

## Technology

| Layer | Technology |
| --- | --- |
| Interface | HTML, CSS, JavaScript; English/Hindi translations |
| Analysis | Python rules, reference retrieval and decision logic |
| AI | Google Gen AI SDK; configured model: `gemini-3.5-flash-lite` |
| Local web server | FastAPI and Uvicorn |
| Public deployment | Streamlit Community Cloud with a custom frontend component |
| Reference data | CSV files included in the repository |
| Image processing | Pillow validation and Gemini text extraction |

The public app starts from `app.py` and serves the frontend through `cloud_ui.py`. Local FastAPI mode starts from `web_server.py`. Both use the shared Python analysis pipeline.

## Run locally on Windows

Install Git and Python. The team's working environment uses Python 3.14. Commands below run directly through the virtual environment, so PowerShell script activation is unnecessary.

### 1. Get the project and install dependencies

```powershell
git clone https://github.com/HeyyAnce/ScamShield-AurixHackathon-2026.git
Set-Location ScamShield-AurixHackathon-2026
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --index-url https://pypi.org/simple --timeout 120 -r web_requirements.txt
```

### 2. Configure optional AI access

Create a `.env` file in the project root containing:

```dotenv
GEMINI_API_KEY="your_actual_key_here"
```

Use your own key and keep it private. `.env` and `.venv` must remain excluded from Git. No dataset path override is needed: the project loads `data/dataset` by default. Restart the server after changing environment settings.

### 3. Start the web app

```powershell
.\.venv\Scripts\python.exe -m uvicorn web_server:app --host 127.0.0.1 --port 8766
```

Open **http://127.0.0.1:8766**. Keep the terminal open; press **Ctrl+C** to stop.

### Alternatively: test the Streamlit deployment mode

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.port 8501
```

Open **http://localhost:8501**.

## Deploy with Streamlit Community Cloud

Select repository `HeyyAnce/ScamShield-AurixHackathon-2026`, branch `main`, and entry point `app.py`. Add the key under the app's Secrets settings:

```toml
GEMINI_API_KEY = "your_actual_key_here"
```

Visitors do not need their own API keys. The key stays on the server. Dependencies are installed from `requirements.txt`; the FastAPI server is only needed for standalone web mode.

## Project structure

```text
frontend/                 HTML, styles, scripts and translations
app.py                    Streamlit entry point
cloud_ui.py               Frontend-to-Python bridge for Streamlit
web_server.py             FastAPI server and API routes
src/
  config.py               Model, timeouts and dataset settings
  pipeline.py             Analysis orchestration
  rule_engine.py          Warning-sign rules
  dataset_loader.py       CSV loading and validation
  reference_matcher.py    Similar-message retrieval
  gemini_client.py        Gemini message analysis
  decision_engine.py      Signal reconciliation
  image_reader.py         Image validation and text extraction
data/dataset/             Reference messages, domains and source records
requirements.txt          Streamlit and analysis dependencies
web_requirements.txt      Additional standalone web dependencies
```

Local API routes: `GET /api/status`, `POST /api/analyze`, `POST /api/extract`. The status endpoint reports key configuration and dataset availability; a successful **AI analysis** result is needed to confirm an actual AI request worked.

## Reference data and attribution

The active collection contains **1948 messages**: 982 English, 766 Hinglish and 200 Hindi. 1722 are synthetic and 226 are marked public-origin. Only the **1662 training-split messages** are searched; this app does not train Gemini. The original 141 validation and 145 test records are unchanged. Added synthetic examples are reference material, not independent evidence of accuracy.

An additional public spam/ham collection is stored in `data/review/` for label review. It is excluded from retrieval: spam is not equivalent to scam, and ham does not prove safety. See `data/review/README.md` for provenance and licensing.

Source and licence records are maintained in `data/dataset/sources.csv`, with collection notes in `data/dataset/README.txt`. Public sources include the UCI SMS Spam Collection, `anmolshrivastav/scam-ham-india` and SmishX. Preserve their attribution when using or distributing the data.

No measured accuracy figure is claimed. Synthetic examples and reference matches are not proof that an unseen message is fraudulent or legitimate.

## Privacy and limitations

- With AI enabled, submitted message text is sent to Google Gemini. Screenshot extraction sends the selected image to Gemini.
- Images are processed in memory rather than intentionally saved as uploaded files. The Streamlit session retains the latest request/result for interaction.
- Do not submit passwords, PINs, OTPs, card numbers or unnecessary personal information.
- Screenshots are limited to 5 MB and 16 megapixels. Review extracted text because OCR can make mistakes.
- Offline explanations and reference messages may remain in their original language.
- Feedback currently downloads a draft; it is **not delivered to an inbox**.
- Results can vary, and false positives and false negatives are possible.
- This prototype is not an official bank, police or government service.

## Quick demo and verification

1. Try the KYC alert or Prize money example and explain the warning signs.
2. Try Bank reminder and explain why a Safe label is not sender verification.
3. Switch to Hindi and analyze another message.
4. Extract text from a non-sensitive screenshot, review it and run analysis.
5. Confirm the result shows whether AI and reference examples were used.

Before presenting, test the deployed URL on another device and save a 60–90 second demo video locally as an internet-outage backup.

## Team Ideaforge

**IILM University, Greater Noida · AURIX 2026**

- Aditya Raj Dixit
- Rudraksh Singh
- Somya Singh
- Himanshi Bisht
- Piyush Raj

## AI tools disclosure

Google Gemini powers runtime message analysis and screenshot text extraction. ChatGPT/Codex assisted with code generation, debugging, interface design, documentation and deployment guidance. The project uses a hosted model; the team did not train a custom fraud-detection model. Model configuration is recorded in `src/config.py`.

## Configuration and audit notes

Only the project-root `.env` is loaded. Existing environment variables take
precedence; Streamlit Secrets take precedence for the public app's API key.
The optional `SCAM_SHIELD_DATASET_DIR` selects an alternate message collection.
Relative paths are resolved from the project root. Missing or incomplete folders
fall back to `data/dataset`; malformed CSV contents are reported as unavailable.
An alternate `legit_domains.csv` is used when present; otherwise rules retain the bundled official-domain list.
Restart the server after changing data or configuration because detectors are cached.

`SCAM_SHIELD_LEGACY_UI=1` intentionally selects the alternate built-in Streamlit
interface. It is retained for compatibility; normal deployment uses the HTML frontend.
Some rule-based overrides can still produce English explanations even with Hindi selected.
The confidence label is heuristic, not a calibrated probability.

Install development dependencies and run both test suites:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest tests -q
```

See `CHANGELOG.md` for the cleanup summary and remaining limitations.

To test, commit and push a release from the connected repository, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\release.ps1
```

This script stops on failed tests or a diverged remote and never force-pushes. Streamlit redeploys the connected main branch; verify the live site after the push.
