# Scam Shield

Scam Shield checks a suspicious SMS, WhatsApp or email message and tells you if it looks like a scam. It explains why in plain language and says what to do next. It is built for people in India, especially parents, grandparents and first-time smartphone users.

Live app: https://scamshield-aurixhackathon-2026.streamlit.app/

## What it does

You paste the text of a message. You get one of three results:

| Result | Meaning |
| :--- | :--- |
| **Likely scam** | Strong scam signs were found. |
| **Needs verification** | Some signs are worrying, or it is unclear. Check another way before acting. |
| **No clear scam signs found** | Nothing alarming was found. This does not prove the sender is genuine. |

Along with the result you see the warning signs, numbered steps to take, and how the message was checked.

- The page can be switched between English and Hindi, and between light and dark mode.
- You can paste messages in English, Hinglish or Hindi.
- It reads the text only. It cannot tell who really sent a message, and it does not stop payments.

### Read a screenshot (beta)

Open **Upload a screenshot**, choose a PNG, JPG/JPEG or WebP image, and click **Extract text**. The image is sent to Google Gemini only when you click that button. Review and correct the text in the message box, then click **Check message** to run the normal checks.

Uploads are limited to 5 MB and 16 megapixels. Remove private details before uploading. Damaged, unreadable or empty images show an error, never a safe verdict. Without the AI service, paste or type the message instead. Extraction can miss or misread words; there is no claimed language accuracy.

## How a message is checked

1. **Rules** look for known scam signs: urgency and threats, requests for OTP or PIN, suspicious links and APK files, advance-fee and UPI tricks, and links that copy a real bank's name.
2. **Reference examples** from `data/dataset` are compared with the message.
3. **Google Gemini** reads the full message when an API key is set up.
4. **A decision step** combines all of the above into one result.

If there is no API key, or Gemini is not available, the app still works with the rules and reference examples. The result says that the AI check was not used.

## The data

The `data/dataset` folder holds the English and Hinglish example messages, a list of official bank and government websites, and the sources. Open any `.csv` file in Excel. See `data/dataset/README.txt` for details.

- Most example messages are synthetic: written for testing, with made-up names, numbers and links. The rest are real messages from public collections.
- The messages are used to find similar examples. They are not used to train a model.
- No accuracy figure is claimed for this data.
- In `legit_domains.csv`, only domains marked `checked` are used by the app.

Credits for the public messages and their licences are in `data/dataset/sources.csv`. They come from the UCI SMS Spam Collection (CC BY 4.0), the Hugging Face dataset `anmolshrivastav/scam-ham-india` (Apache-2.0) and the SmishX project (MIT).

## Run it on your computer

You need Python 3.10 or newer. These steps are for Windows PowerShell.

```powershell
git clone https://github.com/HeyyAnce/ScamShield-AurixHackathon-2026.git
cd ScamShield-AurixHackathon-2026
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The app opens at http://localhost:8501.

The Gemini key is optional. To use it, copy `.env.example` to `.env` and set `GEMINI_API_KEY`. Never commit the `.env` file.

## Put it online (Streamlit Community Cloud)

Add the key in the app's settings under **Secrets**:

```toml
GEMINI_API_KEY = "your_key_here"
```

Visitors do not need a key of their own.

## Project files

| Path | What it does |
| :--- | :--- |
| `app.py` | The page: input, results, language and theme switches. |
| `src/pipeline.py` | Runs the steps in order. |
| `src/rule_engine.py` | The rules, and the check for official links. |
| `src/dataset_loader.py` | Loads and validates the dataset. |
| `src/reference_matcher.py` | Finds similar example messages. |
| `src/gemini_client.py` | Talks to Gemini. |
| `src/decision_engine.py` | Combines everything into one result. |
| `src/config.py` | Settings and file paths. |
| `src/image_reader.py` | Validates screenshots and extracts text for review. |
| `data/dataset/` | The example messages, official websites and sources. |
| `.streamlit/config.toml` | Page theme. |
| `.env.example` | Template for the local `.env` file. |

## Privacy

When the AI check is on, the text of your message is sent to Google Gemini. Screenshot extraction also sends the selected image to Gemini. Images are processed in memory; this app does not save uploads to disk. Do not paste or upload passwords, PINs, OTPs or card numbers.

## Short hackathon demo

1. Choose **Electricity cut-off**, then **Check message**. Explain the warning signs and the three checks shown under the result.
2. Choose **Real bank alert**. Explain that no clear scam signs does not prove who sent it.
3. Enter an unclear message to show **Needs verification**. Results can vary when AI is used.
4. Upload a clear screenshot, extract the text, correct it if needed, and run the check.
5. Switch to Hindi and dark mode. Explain that offline explanations may remain in English.

The 948 dataset messages are reference examples, mostly synthetic. Only the 662 train messages are searched. This is a hackathon prototype, not a trained fraud model, sender verification service, or guarantee of protection.

If the live app is missing reference examples, confirm that `data/dataset` is deployed and that any `SCAM_SHIELD_DATASET_DIR` override points to real files. The detector cache follows dataset changes and expires after five minutes. Failed dataset loading is shown with a warning after analysis. After a deployment, reload the page; if an old process persists, reboot the app from Streamlit Community Cloud.

## If you have been scammed

- National Cybercrime Helpline: call **1930** straight away.
- Report online: https://cybercrime.gov.in
- Report a fraud call or message (Chakshu): https://sancharsaathi.gov.in
- Help with a complaint about your bank: RBI contact centre, toll-free **14448**.

Scam Shield is a project made for a hackathon. It is not connected to any bank, police body or government department, and none of them has checked or approved its results.

## Turquoise web frontend

The HTML/CSS/JavaScript frontend is in `frontend/`; `web_server.py` provides the Python API. The Streamlit entrypoint `app.py` serves the same frontend through `cloud_ui.py` on the existing public URL.

Install `web_requirements.txt`, set `GEMINI_API_KEY` in your environment or local `.env`, then run `python -m uvicorn web_server:app --host 127.0.0.1 --port 8765`. Open http://127.0.0.1:8765. Keep `.env` out of Git.

Includes Home, Safety Guide, Help, About/Privacy, light/dark turquoise themes, message analysis and reviewed screenshot extraction. Result labels map SCAM to Scam, SUSPICIOUS to Likely scam, and SAFE to Safe; no result verifies the sender or guarantees safety.

English/Hindi switching is available across the web interface and requests AI explanations in the selected language. Offline explanations and reference messages may remain in their original language. Current limit: feedback downloads a draft and does not send to an inbox. The public Streamlit deployment uses `cloud_ui.py` and the existing server-side Gemini secret; no API key is exposed to the browser. Feedback delivery is not connected. Set the server environment variable `SCAM_SHIELD_LEGACY_UI=1` only for an intentional rollback to the original UI. The FastAPI entrypoint remains available for standalone local use.
