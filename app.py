"""
Scam Shield - redesigned front end (Streamlit).

Presentation only: every verdict, flag, step and status comes from
ScamShieldPipeline.analyze(). Nothing is scored or invented here.
"""

import os
import html
import hashlib
from pathlib import Path
from typing import Optional

import streamlit as st
from dotenv import load_dotenv

from src.pipeline import ScamShieldPipeline, PipelineOutput
from src.image_reader import prepare_image, extract_text, ImageInputError

load_dotenv(override=True)

# Keep the original UI available as an explicit server-side rollback option.
if os.getenv("SCAM_SHIELD_LEGACY_UI") != "1":
    from cloud_ui import main as render_web_frontend
    render_web_frontend()
    st.stop()

# Reference examples come from a mostly synthetic, not-yet-reviewed dataset.
# Set to False to hide them from users until the data is approved for display.
SHOW_REFERENCE_EXAMPLES = True

SAMPLE_MESSAGES = {
    "Electricity cut-off": (
        "Dear Consumer, Your Electricity power will be disconnected tonight at 9:30 PM from "
        "the electricity office because your previous month bill was not updated. Please immediately "
        "contact our electricity officer Rahul Sharma at 9876543210 or update bill through link: "
        "http://bit.ly/bijli-bill-pay"
    ),
    "Bank KYC app": (
        "Dear Customer, Your SBI YONO account has been suspended due to pending KYC verification. "
        "Please click the link below to download our KYC update app and prevent account freeze: "
        "http://sbi-yono-update.xyz/app.apk. Do not ignore."
    ),
    "KBC lottery": (
        "Badhai ho! Aapka number KBC WhatsApp lucky draw me chuna gaya hai aur aapne jeete hain "
        "₹25,00,000 cash prize. Apne inaam ki rashi pane ke liye turant WhatsApp karein Rana Pratap Singh "
        "ko 9123456789 par aur registration fee ₹2,500 jama karein."
    ),
    "Digital arrest": (
        "URGENT NOTICE: This is Inspector Ajay Kumar from Mumbai Cyber Crime Branch. A FedEx parcel sent "
        "to Taiwan under your Aadhaar details contains 5 fake passports and 140 grams of narcotics. "
        "An FIR has been registered. You must connect on Skype immediately for interrogation under "
        "Digital Arrest warrant to avoid arrest."
    ),
    "Real bank alert": (
        "Dear Customer, your A/C XX4921 has been debited by Rs 1,250.00 on 22-Oct-26 at Apollo Pharmacy "
        "via UPI. Avail Bal: Rs 24,180.50. If not done by you, call 1800-11-2211 or SMS NO to 567676 - State Bank of India"
    ),
}

SAMPLE_BUTTON_MAPPING = [
    ("sample_electricity", "Electricity cut-off"),
    ("sample_kyc", "Bank KYC app"),
    ("sample_kbc", "KBC lottery"),
    ("sample_arrest", "Digital arrest"),
    ("sample_bank", "Real bank alert"),
]

STRINGS = {
    "en": {
        "page_title": "Scam Shield: check a suspicious message",
        "brand_name": "Scam Shield",
        "lost_money_call": "Lost money? Call 1930",
        "phone_call_bar": "Lost money? Call 1930",
        "dark_mode": "Dark mode",
        "language_label": "Language",

        # Intro
        "intro_heading": "Got a message that feels wrong? Check it before you act.",
        "intro_p1": "Paste the SMS, WhatsApp or email text below. We will tell you if it looks like a scam and what to do next.",
        "intro_p2": "संदेश यहाँ पेस्ट करें। हम बताएँगे कि यह स्कैम तो नहीं।",

        # Input
        "input_label": "Paste the message here",
        "input_placeholder": "Example: Dear customer, your electricity will be cut tonight. Call 98xxxxxx10 to pay the pending bill.",
        "privacy_note": "Do not paste passwords, PINs or OTPs.",
        "check_button": "Check message",
        "clear_button": "Clear",

        # Examples
        "try_example": "Try an example message",
        "sample_electricity": "Electricity cut-off",
        "sample_kyc": "Bank KYC app",
        "sample_kbc": "KBC lottery",
        "sample_arrest": "Digital arrest",
        "sample_bank": "Real bank alert",

        # Progress / State notices
        "spinner_text": "Reading the message. This can take a few seconds.",
        "empty_title": "Nothing to check yet",
        "empty_body": 'Paste a message in the box above, or open "Try an example message".',
        "error_title": "We could not check this message",
        "error_body": 'This is not a safe or unsafe result. Press "Check message" to try again. If it keeps failing, do not trust the message until you have verified it another way.',
        "backup_used_title": "Backup check used",

        # Verdicts
        "verdict_scam_title": "Likely scam",
        "verdict_scam_lead": "Do not reply, click or pay.",
        "verdict_scam_flags": "Why it looks like a scam",

        "verdict_warn_title": "Needs verification",
        "verdict_warn_lead": "Don't act on this yet. Check it another way first.",
        "verdict_warn_flags": "What looks concerning",

        "verdict_safe_title": "No clear scam signs found",
        "verdict_safe_lead": "This does not prove the sender is genuine.",
        "verdict_safe_flags": "What we noticed",

        # Confidence & Sections
        "confidence_label": "How sure we are",
        "confidence_high": "High",
        "confidence_medium": "Medium",
        "confidence_low": "Low",

        "what_to_do_now": "What to do now",
        "backend_english_note": "नीचे दिया गया विवरण अंग्रेज़ी में है।",

        # How we checked this strip
        "how_checked_heading": "How we checked this",
        "badge_ai_title": "AI analysis",
        "badge_ai_sub": "Gemini AI read the message",
        "badge_ai_off_title": "AI check not used this time",
        "badge_ai_off_sub": "Offline backup check",
        "badge_rules_title": "Warning-sign rules",
        "badge_rules_sub": "Checked for known scam patterns",
        "badge_dataset_title": "Known scam examples",
        "badge_dataset_sub": "Compared with similar messages in our reference collection",
        "check_summary_full": "AI analyzed the message and cross-checked against warning-sign rules and our reference collection of known scam examples.",
        "check_summary_ai_rules": "AI analyzed the message and cross-checked against warning-sign rules.",
        "check_summary_rules_refs": "The offline backup check cross-checked the message against warning-sign rules and our reference collection of known scam examples.",
        "check_summary_rules_only": "The offline backup check analyzed the message against warning-sign rules only.",
        "rule_patterns_label": "Patterns found:",
        "no_patterns_found": "No known warning-sign pattern matched. That does not prove the message is genuine.",

        # Expanders
        "refs_expander": "Similar example messages we compared",
        "refs_note": "These are examples from our reference collection, not proof about your message. Many are written for testing.",
        "ref_synthetic": "Written for testing",
        "ref_real": "Real message from a public collection",

        # Right Rail
        "rail_heading": "Already lost money or shared an OTP?",
        "rail_p1": "Act quickly. Reporting early gives the bank a better chance to hold the transfer.",
        "rail_call": "Call 1930",
        "rail_cybercrime": "File a complaint: ",
        "rail_sanchar": "Report a fraud call or message (Chakshu): ",
        "rail_rbi": "Bank complaint not resolved: RBI helpline ",
        "rail_privacy_heading": "Your privacy",
        "rail_privacy_body": "The message text is checked as you submit it. When the AI check is on, it is sent to Google Gemini. Do not paste passwords, PINs or OTPs.",
        "rail_about_heading": "About Scam Shield",
        "rail_about_p1": "A free helper for families in India to spot scam messages in English, Hindi and Hinglish.",
        "rail_about_p2": "It reads the text of a message only. It cannot confirm who sent it, and no bank, police body or government department has checked or endorsed a result. Treat it as a second opinion, not a guarantee.",
    },
    "hi": {
        "page_title": "Scam Shield: संदिग्ध संदेश की जाँच करें",
        "brand_name": "Scam Shield",
        "lost_money_call": "पैसे डूब गए? 1930 पर कॉल करें",
        "phone_call_bar": "पैसे डूब गए? 1930 पर कॉल करें",
        "dark_mode": "डार्क मोड",
        "language_label": "भाषा",

        # Intro
        "intro_heading": "कोई ऐसा संदेश मिला जो सही नहीं लग रहा? कुछ करने से पहले जाँच लें।",
        "intro_p1": "नीचे SMS, WhatsApp या ईमेल का संदेश पेस्ट करें। हम बताएँगे कि यह स्कैम लग रहा है या नहीं, और आगे क्या करना है।",
        "intro_p2": "संदेश यहाँ पेस्ट करें। हम बताएँगे कि यह स्कैम तो नहीं।",

        # Input
        "input_label": "संदेश यहाँ पेस्ट करें",
        "input_placeholder": "उदाहरण: Dear customer, your electricity will be cut tonight. Call 98xxxxxx10 to pay the pending bill.",
        "privacy_note": "पासवर्ड, PIN या OTP यहाँ पेस्ट न करें।",
        "check_button": "संदेश जाँचें",
        "clear_button": "हटाएँ",

        # Examples
        "try_example": "उदाहरण संदेश आज़माएँ",
        "sample_electricity": "बिजली बिल फ्रॉड",
        "sample_kyc": "बैंक KYC ऐप",
        "sample_kbc": "KBC लॉटरी",
        "sample_arrest": "डिजिटल अरेस्ट",
        "sample_bank": "असली बैंक अलर्ट",

        # Progress / State notices
        "spinner_text": "संदेश पढ़ा जा रहा है। इसमें कुछ सेकंड लग सकते हैं।",
        "empty_title": "अभी जाँचने के लिए कुछ नहीं है",
        "empty_body": 'ऊपर दिए गए बॉक्स में कोई संदेश पेस्ट करें, या "उदाहरण संदेश आज़माएँ" खोलें।',
        "error_title": "हम इस संदेश की जाँच नहीं कर सके",
        "error_body": 'यह सुरक्षित या असुरक्षित का फ़ैसला नहीं है। दोबारा कोशिश करने के लिए "संदेश जाँचें" दबाएँ। अगर बार-बार ऐसा हो, तो जब तक किसी अन्य तरीके से पुष्टि न हो जाए, संदेश पर भरोसा न करें।',
        "backup_used_title": "बैकअप जाँच का इस्तेमाल हुआ",

        # Verdicts
        "verdict_scam_title": "स्कैम होने की पूरी संभावना",
        "verdict_scam_lead": "कोई जवाब न दें, लिंक पर क्लिक न करें और पैसे न भेजें।",
        "verdict_scam_flags": "यह स्कैम क्यों लग रहा है",

        "verdict_warn_title": "जाँच-पड़ताल की ज़रूरत है",
        "verdict_warn_lead": "जल्दबाज़ी में कुछ न करें। पहले किसी और तरीके से पता करें।",
        "verdict_warn_flags": "इसमें क्या चिंताजनक है",

        "verdict_safe_title": "स्कैम का कोई साफ़ संकेत नहीं मिला",
        "verdict_safe_lead": "यह साबित नहीं करता कि संदेश भेजने वाला पूरी तरह असली है।",
        "verdict_safe_flags": "हमने क्या पाया",

        # Confidence & Sections
        "confidence_label": "हम कितने आश्वस्त हैं",
        "confidence_high": "ज़्यादा",
        "confidence_medium": "मध्यम",
        "confidence_low": "कम",

        "what_to_do_now": "अब क्या करें",
        "backend_english_note": "नीचे दिया गया विवरण अंग्रेज़ी में है।",

        # How we checked this strip
        "how_checked_heading": "हमने यह कैसे जांचा",
        "badge_ai_title": "AI जांच",
        "badge_ai_sub": "Gemini AI ने संदेश पढ़ा",
        "badge_ai_off_title": "इस बार AI जांच का उपयोग नहीं हुआ",
        "badge_ai_off_sub": "ऑफ़लाइन बैकअप जांच",
        "badge_rules_title": "खतरे के संकेतों की जांच",
        "badge_rules_sub": "पहचाने गए स्कैम पैटर्न की पड़ताल",
        "badge_dataset_title": "जाने-पहचाने स्कैम के उदाहरण",
        "badge_dataset_sub": "संदर्भ संग्रह के मिलते-जुलते संदेशों से तुलना",
        "check_summary_full": "AI ने संदेश का विश्लेषण किया और खतरे के नियमों व संदर्भ संग्रह के जाने-पहचाने स्कैम उदाहरणों से क्रॉस-चेक किया।",
        "check_summary_ai_rules": "AI ने संदेश का विश्लेषण किया और खतरे के नियमों से क्रॉस-चेक किया।",
        "check_summary_rules_refs": "ऑफ़लाइन बैकअप जांच द्वारा संदेश को खतरे के नियमों और जाने-पहचाने स्कैम उदाहरणों के संदर्भ संग्रह से क्रॉस-चेक किया गया।",
        "check_summary_rules_only": "ऑफ़लाइन बैकअप जांच द्वारा केवल खतरे के नियमों के आधार पर संदेश का विश्लेषण किया गया।",
        "rule_patterns_label": "मिले संकेत:",
        "no_patterns_found": "नियमों को कोई जाना-पहचाना ख़तरे का संकेत नहीं मिला। इसका मतलब यह नहीं कि संदेश पूरी तरह असली है।",

        # Expanders
        "refs_expander": "मिलते-जुलते उदाहरण जिनकी हमने तुलना की",
        "refs_note": "ये हमारे संदर्भ संग्रह के उदाहरण हैं, आपके संदेश का कोई पक्का सबूत नहीं। इनमें से कई सिर्फ़ टेस्टिंग के लिए लिखे गए हैं।",
        "ref_synthetic": "टेस्टिंग के लिए लिखा गया",
        "ref_real": "सार्वजनिक संग्रह का असली संदेश",

        # Right Rail
        "rail_heading": "क्या पैसे कट गए या OTP शेयर कर दिया?",
        "rail_p1": "तुरंत कदम उठाएँ। जितनी जल्दी शिकायत करेंगे, बैंक के पास पैसे रोकने का उतना ही बेहतर मौका होगा।",
        "rail_call": "1930 पर कॉल करें",
        "rail_cybercrime": "ऑनलाइन शिकायत दर्ज करें: ",
        "rail_sanchar": "फ़्रॉड कॉल या मैसेज की रिपोर्ट करें (चक्षु): ",
        "rail_rbi": "बैंक में शिकायत का हल न मिले तो RBI हेल्पलाइन ",
        "rail_privacy_heading": "आपकी गोपनीयता",
        "rail_privacy_body": "संदेश सबमिट करते ही उसकी जाँच होती है। जब AI जाँच चालू होती है, तो यह Google Gemini को भेजा जाता है। पासवर्ड, PIN या OTP यहाँ पेस्ट न करें।",
        "rail_about_heading": "Scam Shield के बारे में",
        "rail_about_p1": "भारत में परिवारों के लिए English, Hindi और Hinglish संदेशों में स्कैम पहचानने वाला एक मुफ़्त मददगार।",
        "rail_about_p2": "यह केवल संदेश का टेक्स्ट पढ़ता है। यह पुष्टि नहीं कर सकता कि संदेश किसने भेजा, और किसी भी बैंक, पुलिस या सरकारी विभाग ने इस परिणाम की पुष्टि नहीं की है। इसे केवल एक सलाह समझें, कोई पक्की गारंटी नहीं।",
    },
}

ICONS = {
    "SCAM": '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><polygon points="8.5,2.5 15.5,2.5 21.5,8.5 21.5,15.5 15.5,21.5 8.5,21.5 2.5,15.5 2.5,8.5"/><path d="M9 9l6 6M15 9l-6 6"/></svg>',
    "SUSPICIOUS": '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 3L22 20H2L12 3z"/><path d="M12 10v4.5M12 17.2v.1"/></svg>',
    "SAFE": '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><circle cx="12" cy="12" r="9.5"/><path d="M7.5 12.5l3 3 6-6.5"/></svg>',
}

SHIELD_LOGO = (
    '<svg viewBox="0 0 32 32" width="30" height="30" aria-hidden="true">'
    '<path d="M16 2.5l11 4v8.2c0 7-4.6 12.2-11 14.8C9.6 26.9 5 21.7 5 14.7V6.5l11-4z" fill="var(--brand)"/>'
    '<path d="M10.8 15.6l3.7 3.7 7-7.6" fill="none" stroke="#fff" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/>'
    '</svg>'
)

esc = html.escape


def t(key: str) -> str:
    lang = st.session_state.get("lang", "en")
    return STRINGS.get(lang, STRINGS["en"]).get(key, STRINGS["en"].get(key, key))


def get_css(theme: str, lang: str) -> str:
    is_dark = (theme == "dark")
    is_hi = (lang == "hi")

    # Dark palette meets WCAG AA contrast (>= 4.5:1 for body, >= 3:1 for large text)
    if is_dark:
        colors = """
  --bg:#0F172A; --surface:#1E293B; --ink:#F8FAFC; --muted:#94A3B8; --line:#334155;
  --brand:#3B82F6; --brand-soft:#1E294D; --brand-link:#60A5FA;
  --stamp-bg:rgba(15,23,42,0.85);
  --scam:#F87171; --scam-tint:#2A1215; --scam-edge:#7F1D1D;
  --warn:#FBBF24; --warn-tint:#271C07; --warn-edge:#78350F;
  --safe:#34D399; --safe-tint:#0A2318; --safe-edge:#065F46;
  --note-info-bg:#1E294D; --note-info-border:#3B4E82;
  --note-err-bg:#261E26; --note-err-border:#523C4D;
  --textarea-border:#475569; --btn-sec-border:#475569;
  --badge-active-dot:#34D399;
        """
    else:
        colors = """
  --bg:#F4F6F8; --surface:#FFFFFF; --ink:#172033; --muted:#46526A; --line:#CBD3DE;
  --brand:#1D2F6F; --brand-soft:#E6EAF6; --brand-link:#1D2F6F;
  --stamp-bg:rgba(255,255,255,0.65);
  --scam:#A5180E; --scam-tint:#FDECEA; --scam-edge:#F0B8B2;
  --warn:#7A4400; --warn-tint:#FFF3D6; --warn-edge:#E8C46A;
  --safe:#13663A; --safe-tint:#E6F4EB; --safe-edge:#A9D5B8;
  --note-info-bg:var(--brand-soft); --note-info-border:#B9C3E6;
  --note-err-bg:#EEF0F4; --note-err-border:#9AA6BF;
  --textarea-border:#7C889C; --btn-sec-border:#9AA6BF;
  --badge-active-dot:#16A34A;
        """

    # Add ~0.1 to line-height for Hindi (Devanagari)
    lh_body = "1.65" if is_hi else "1.55"
    lh_heading = "1.22" if is_hi else "1.12"
    lh_card = "1.65" if is_hi else "1.55"

    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible+Next:wght@400;500;700;800&family=Noto+Sans+Devanagari:wght@400;600;700&display=swap');

:root {{
{colors}
  --lh-body: {lh_body};
  --lh-heading: {lh_heading};
  --lh-card: {lh_card};
}}

html, body, [class*="css"], .stApp, button, textarea, input {{
  font-family:'Atkinson Hyperlegible Next','Noto Sans Devanagari',-apple-system,'Segoe UI',sans-serif !important;
}}

/* Base app container */
.stApp, [data-testid="stAppViewContainer"] {{
  background:var(--bg) !important;
  color:var(--ink) !important;
}}
[data-testid="stHeader"], #MainMenu, footer, [data-testid="stToolbar"] {{ display:none !important; }}
.block-container {{
  max-width:1240px !important;
  padding:1.1rem 1.4rem 3.5rem !important;
  background:transparent !important;
}}

::selection {{
  background:var(--brand-soft) !important;
  color:var(--ink) !important;
}}

/* Top bar container */
.st-key-topbar_container {{
  padding-bottom:.75rem;
  border-bottom:1px solid var(--line);
  margin-bottom:.4rem;
}}
.brand {{
  display:flex;
  align-items:center;
  gap:.55rem;
  font-weight:800;
  font-size:1.25rem;
  color:var(--brand);
  letter-spacing:-.01em;
}}
.sos-wrap {{
  display:flex;
  justify-content:flex-end;
  align-items:center;
}}
.sos {{
  display:inline-block;
  font-weight:700;
  font-size:.92rem;
  color:var(--scam);
  text-decoration:none;
  border:2px solid var(--scam);
  border-radius:999px;
  padding:.32rem .85rem;
  white-space:nowrap;
  background:var(--surface);
  text-align:center;
}}
.sos:hover {{ background:var(--scam-tint); }}

/* Top bar widgets (Toggle & Radio) */
.st-key-topbar_container [data-testid="stToggle"] {{
  margin:0 !important;
}}
.st-key-topbar_container [data-testid="stToggle"] label p {{
  font-size:.92rem !important;
  font-weight:700 !important;
  color:var(--ink) !important;
  margin:0 !important;
}}
.st-key-topbar_container [data-testid="stRadio"] {{
  margin:0 !important;
}}
.st-key-topbar_container [data-testid="stRadio"] > div {{
  gap:.3rem !important;
  flex-direction:row !important;
}}
.st-key-topbar_container [data-testid="stRadio"] div[role="radiogroup"] label {{
  font-size:.92rem !important;
  font-weight:700 !important;
  color:var(--ink) !important;
  cursor:pointer;
  margin:0 !important;
  padding:.15rem .4rem !important;
  border-radius:6px;
}}
.st-key-topbar_container [data-testid="stRadio"] div[role="radiogroup"] label:has(input:checked) {{
  background:var(--brand-soft);
  color:var(--brand) !important;
}}

/* Keyboard focus visibility on all controls */
button:focus-visible, a:focus-visible, input:focus-visible, textarea:focus-visible,
summary:focus-visible, [tabindex]:focus-visible,
[data-testid="stToggle"] label:focus-within,
[data-testid="stRadio"] label:focus-within {{
  outline:3px solid var(--brand) !important;
  outline-offset:2px !important;
  border-radius:6px !important;
}}

/* Intro */
.intro {{ padding:1rem 0 .9rem; }}
.intro h1 {{
  font-size:clamp(1.6rem,4.5vw,2.4rem);
  line-height:var(--lh-heading);
  font-weight:800;
  letter-spacing:-.025em;
  margin:0 0 .5rem;
  color:var(--ink);
  max-width:26ch;
}}
.intro p {{
  font-size:1.05rem;
  line-height:var(--lh-body);
  color:var(--muted);
  margin:0 0 .25rem;
  max-width:58ch;
}}
.intro .hi {{ font-size:1rem; }}

/* Input */
[data-testid="stTextArea"] label p {{
  font-size:1.05rem !important;
  font-weight:700 !important;
  color:var(--ink) !important;
}}
[data-testid="stTextArea"] textarea {{
  font-size:1.05rem !important;
  line-height:var(--lh-body) !important;
  color:var(--ink) !important;
  background:var(--surface) !important;
  border:2px solid var(--textarea-border) !important;
  border-radius:12px !important;
  padding:.85rem !important;
}}
[data-testid="stTextArea"] textarea:focus {{
  border-color:var(--brand) !important;
  box-shadow:0 0 0 4px rgba(59,130,246,.28) !important;
}}
[data-testid="stTextArea"] textarea::placeholder {{
  color:var(--muted) !important;
}}
.privacy {{
  font-size:.9rem;
  color:var(--muted);
  line-height:var(--lh-body);
  margin:.25rem 0 .85rem;
}}

/* Buttons */
.stButton > button, [data-testid="stBaseButton-primary"], [data-testid="stBaseButton-secondary"] {{
  min-height:3rem;
  font-size:1.05rem !important;
  font-weight:700 !important;
  border-radius:12px !important;
  width:100%;
}}
.stButton > button[kind="primary"], [data-testid="stBaseButton-primary"] {{
  background:var(--brand) !important;
  color:#fff !important;
  border:2px solid var(--brand) !important;
}}
.stButton > button[kind="primary"]:hover:not(:disabled), [data-testid="stBaseButton-primary"]:hover:not(:disabled) {{
  filter:brightness(1.12);
}}
.stButton > button[kind="primary"]:disabled, [data-testid="stBaseButton-primary"]:disabled {{
  background:{'#334155' if is_dark else '#8E98BC'} !important;
  border-color:{'#334155' if is_dark else '#8E98BC'} !important;
  color:{'#64748B' if is_dark else '#FFFFFF'} !important;
}}
.stButton > button[kind="secondary"], [data-testid="stBaseButton-secondary"] {{
  background:var(--surface) !important;
  color:var(--ink) !important;
  border:2px solid var(--btn-sec-border) !important;
}}
.stButton > button[kind="secondary"]:hover:not(:disabled), [data-testid="stBaseButton-secondary"]:hover:not(:disabled) {{
  background:var(--brand-soft) !important;
  border-color:var(--brand) !important;
  color:var(--ink) !important;
}}

/* Underlined Clear Button */
.st-key-clear button {{
  min-height:2.6rem !important;
  background:transparent !important;
  border:2px solid transparent !important;
  text-decoration:underline !important;
  color:var(--muted) !important;
}}
.st-key-clear button:hover {{
  color:var(--ink) !important;
}}
.st-key-clear button p {{
  font-size:1rem !important;
  color:inherit !important;
}}

/* Expanders */
[data-testid="stExpander"] {{
  background:var(--surface) !important;
  border:1px solid var(--line) !important;
  border-radius:12px;
}}
[data-testid="stExpander"] summary {{
  font-size:1rem;
  font-weight:700;
  color:var(--ink) !important;
}}
[data-testid="stExpander"] summary p {{
  font-size:1rem !important;
  font-weight:700 !important;
  color:var(--ink) !important;
}}
[data-testid="stExpander"] summary svg {{
  fill:var(--ink) !important;
  stroke:var(--ink) !important;
  color:var(--ink) !important;
}}
[data-testid="stExpanderDetails"] {{
  background:var(--surface) !important;
  color:var(--ink) !important;
}}

/* Spinner */
[data-testid="stSpinner"] {{
  color:var(--ink) !important;
}}

/* Notices */
.note {{
  border-radius:12px;
  padding:.8rem 1rem;
  font-size:1rem;
  line-height:var(--lh-body);
  margin:.9rem 0;
  border:1px solid;
}}
.note b {{ display:block; margin-bottom:.15rem; }}
.note-info {{
  background:var(--note-info-bg);
  border-color:var(--note-info-border);
  color:var(--ink);
}}
.note-error {{
  background:var(--note-err-bg);
  border-color:var(--note-err-border);
  color:var(--ink);
}}

/* ==========================================================================
   COMPACT VERDICT CARD & RESULT LAYOUT
   ========================================================================== */
.verdict {{
  border-radius:14px;
  padding:1rem 1.15rem;
  margin:1.1rem 0 .75rem;
  border:1px solid var(--edge);
  background:var(--tint);
  color:var(--ink);
}}
.v-scam {{ --tone:var(--scam); --tint:var(--scam-tint); --edge:var(--scam-edge); }}
.v-warn {{ --tone:var(--warn); --tint:var(--warn-tint); --edge:var(--warn-edge); }}
.v-safe {{ --tone:var(--safe); --tint:var(--safe-tint); --edge:var(--safe-edge); }}

/* Verdict Header Row */
.v-header {{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:.75rem;
  flex-wrap:wrap;
  margin-bottom:.45rem;
}}
.v-stamp-group {{
  display:flex;
  align-items:center;
  gap:.75rem;
  flex-wrap:wrap;
  flex:1 1 auto;
}}
.stamp {{
  display:inline-flex;
  align-items:center;
  gap:.45rem;
  color:var(--tone);
  background:var(--stamp-bg);
  border:3.5px double var(--tone);
  border-radius:8px;
  padding:.26rem .75rem .26rem .55rem;
  font-weight:800;
  font-size:1.22rem;
  line-height:1.1;
  letter-spacing:-.01em;
  transform:rotate(-1.5deg);
  animation:thud .38s cubic-bezier(.2,1.5,.4,1) both;
  white-space:nowrap;
}}
@keyframes thud {{
  from {{ transform:rotate(-1.5deg) scale(1.28); opacity:0; }}
  to {{ transform:rotate(-1.5deg) scale(1); opacity:1; }}
}}
@media (prefers-reduced-motion:reduce) {{ .stamp {{ animation:none; }} }}

.v-headline {{
  display:flex;
  flex-direction:column;
  gap:.1rem;
}}
.v-type {{
  font-size:1.08rem;
  font-weight:800;
  color:var(--ink);
  line-height:1.25;
}}
.v-lead {{
  font-size:.96rem;
  font-weight:700;
  color:var(--tone);
  line-height:1.35;
}}

.v-conf-pill {{
  display:inline-flex;
  align-items:center;
  gap:.3rem;
  font-size:.84rem;
  font-weight:600;
  padding:.22rem .65rem;
  border-radius:999px;
  background:var(--surface);
  border:1px solid var(--line);
  color:var(--muted);
  white-space:nowrap;
}}
.v-conf-pill b {{
  color:var(--ink);
  font-weight:700;
}}

.v-explain {{
  font-size:1rem;
  line-height:var(--lh-card);
  margin:.45rem 0 .75rem;
  max-width:70ch;
  color:var(--ink);
}}

/* Two columns side-by-side on desktop */
.v-grid {{
  display:grid;
  grid-template-columns:1fr 1fr;
  gap:1rem;
  margin-top:.5rem;
}}
.v-grid.single-col {{
  grid-template-columns:1fr;
}}
.v-col {{
  min-width:0;
}}
.v-sec-title {{
  font-size:1.08rem;
  font-weight:800;
  margin:0 0 .35rem;
  color:var(--ink);
  letter-spacing:-.01em;
  line-height:var(--lh-heading);
}}

.flags, .steps {{ margin:0; padding:0; list-style:none; }}
.flags li {{
  position:relative;
  padding:.35rem 0 .35rem 1.35rem;
  border-bottom:1px solid var(--line);
  font-size:.98rem;
  line-height:var(--lh-body);
  overflow-wrap:anywhere;
  color:var(--ink);
}}
.flags li:last-child {{
  border-bottom:none;
}}
.flags li::before {{
  content:"";
  position:absolute;
  left:.1rem;
  top:.68rem;
  width:.55rem;
  height:.55rem;
  background:var(--mark,var(--scam));
  clip-path:polygon(0 0,100% 0,100% 100%,50% 75%,0 100%);
}}
.flags.f-safe li::before {{ --mark:var(--safe); clip-path:circle(50%); }}
.flags.f-warn li::before {{ --mark:var(--warn); }}

.steps {{ counter-reset:s; }}
.steps li {{
  counter-increment:s;
  display:flex;
  gap:.6rem;
  align-items:flex-start;
  padding:.35rem 0;
  border-bottom:1px solid var(--line);
  font-size:.98rem;
  line-height:var(--lh-body);
  overflow-wrap:anywhere;
  color:var(--ink);
  background:transparent;
  border-radius:0;
  margin-bottom:0;
}}
.steps li:last-child {{
  border-bottom:none;
}}
.steps li::before {{
  content:counter(s);
  flex:none;
  width:1.4rem;
  height:1.4rem;
  border-radius:50%;
  background:var(--brand);
  color:#fff;
  font-weight:800;
  display:grid;
  place-items:center;
  font-size:.8rem;
  margin-top:.1rem;
}}

/* "How we checked this" strip */
.check-strip {{
  margin-top:.85rem;
  padding-top:.75rem;
  border-top:1px solid var(--edge);
}}
.check-strip-header {{
  display:flex;
  align-items:baseline;
  justify-content:space-between;
  gap:.75rem;
  flex-wrap:wrap;
  margin-bottom:.5rem;
}}
.check-strip h4 {{
  font-size:1.05rem;
  font-weight:800;
  margin:0;
  color:var(--ink);
  letter-spacing:-.01em;
  line-height:var(--lh-heading);
}}
.badge-row {{
  display:flex;
  gap:.5rem;
  flex-wrap:wrap;
  align-items:stretch;
}}
.check-badge {{
  display:inline-flex;
  align-items:center;
  gap:.45rem;
  background:var(--surface);
  border:1px solid var(--line);
  border-radius:8px;
  padding:.35rem .6rem;
  flex:1 1 auto;
  min-width:140px;
}}
.badge-dot {{
  width:8px;
  height:8px;
  border-radius:50%;
  background:var(--badge-active-dot);
  flex-shrink:0;
}}
.badge-dot.dot-neutral {{
  background:var(--muted);
}}
.badge-text {{
  display:flex;
  flex-direction:column;
}}
.badge-text strong {{
  font-size:.86rem;
  color:var(--ink);
  line-height:1.2;
}}
.badge-text small {{
  font-size:.76rem;
  color:var(--muted);
  line-height:1.25;
}}
.check-summary {{
  font-size:.9rem;
  color:var(--muted);
  margin:.5rem 0 .4rem;
  line-height:var(--lh-body);
}}
.rule-chips {{
  display:flex;
  align-items:flex-start;
  gap:.35rem;
  flex-wrap:wrap;
  margin-top:.3rem;
}}
.chips-label {{
  font-size:.85rem;
  font-weight:700;
  color:var(--ink);
  margin-top:.15rem;
}}
.rule-chip {{
  display:inline-block;
  font-size:.82rem;
  padding:.18rem .48rem;
  background:var(--surface);
  border:1px solid var(--line);
  border-radius:6px;
  color:var(--ink);
  line-height:1.35;
}}
.rule-chip strong {{
  color:var(--ink);
}}
.no-patterns {{
  font-size:.86rem;
  color:var(--muted);
  margin:.25rem 0;
  font-style:italic;
}}
.compact-note {{
  font-size:.84rem;
  color:var(--muted);
  line-height:1.35;
  margin:.25rem 0;
}}
.compact-note.note-en-hint {{
  font-style:italic;
}}
.compact-note b {{
  color:var(--ink);
}}

.detail {{ font-size:1rem; line-height:var(--lh-body); color:var(--ink); }}
.detail p {{ margin:.2rem 0 .7rem; color:var(--ink); }}
.ref {{ border-left:4px solid var(--line); padding:.2rem 0 .2rem .9rem; margin:.85rem 0; }}
.ref q {{
  display:block;
  font-size:.96rem;
  color:var(--muted);
  margin:.25rem 0;
  overflow-wrap:anywhere;
  quotes:"\\201C" "\\201D";
}}
.ref small {{ color:var(--muted); font-size:.85rem; }}

/* Right rail */
.rail {{
  background:var(--surface);
  border:1px solid var(--line);
  border-radius:16px;
  padding:1.25rem 1.15rem;
  margin-top:1rem;
  color:var(--ink);
}}
.rail h2 {{
  font-size:1.15rem;
  font-weight:800;
  margin:0 0 .35rem;
  letter-spacing:-.01em;
  color:var(--ink);
  line-height:var(--lh-heading);
}}
.rail h3 {{
  font-size:1rem;
  font-weight:800;
  margin:1.1rem 0 .25rem;
  padding-top:1rem;
  border-top:1px solid var(--line);
  color:var(--ink);
  line-height:var(--lh-heading);
}}
.rail p {{
  font-size:.95rem;
  line-height:var(--lh-body);
  color:var(--muted);
  margin:.2rem 0 .45rem;
}}
.rail ul {{ list-style:none; padding:0; margin:.25rem 0 0; }}
.rail li {{
  padding:.4rem 0;
  font-size:.95rem;
  line-height:var(--lh-body);
  overflow-wrap:anywhere;
  color:var(--ink);
}}
.rail a {{
  color:var(--brand-link);
  font-weight:700;
}}
.rail a.call {{
  display:block;
  text-align:center;
  background:#DC2626;
  color:#fff !important;
  font-size:1.25rem;
  font-weight:800;
  border-radius:12px;
  padding:.7rem;
  text-decoration:none;
  margin:.6rem 0 .7rem;
}}
.rail a.call:hover {{
  filter:brightness(1.1);
}}

/* Phone call bar */
.callbar {{ display:none; }}

@media (max-width:760px) {{
  .sos, .sos-wrap {{ display:none !important; }}
  .st-key-topbar_container [data-testid="column"]:has(.sos-wrap) {{ display:none !important; }}

  /* Top bar layout on phone */
  .st-key-topbar_container > [data-testid="stHorizontalBlock"] {{
    flex-direction:column !important;
    gap:.5rem !important;
  }}
  .st-key-topbar_container > [data-testid="stHorizontalBlock"] > [data-testid="column"] {{
    width:100% !important;
    flex:1 1 100% !important;
  }}
  .st-key-topbar_container [data-testid="column"] > [data-testid="stHorizontalBlock"] {{
    display:flex !important;
    flex-direction:row !important;
    flex-wrap:nowrap !important;
    align-items:center !important;
    justify-content:flex-start !important;
    gap:.75rem !important;
  }}
  .st-key-topbar_container [data-testid="column"] > [data-testid="stHorizontalBlock"] > [data-testid="column"] {{
    width:auto !important;
    flex:0 0 auto !important;
  }}

  /* Mobile compact result */
  .v-header {{
    flex-direction:column;
    align-items:flex-start;
    gap:.4rem;
  }}
  .v-conf-pill {{
    margin-top:.2rem;
  }}
  .v-grid {{
    grid-template-columns:1fr !important;
    gap:.8rem;
  }}
  .badge-row {{
    flex-direction:column;
  }}
  .check-badge {{
    width:100%;
    min-width:0;
  }}

  .block-container {{
    padding:1rem 1rem calc(5.5rem + env(safe-area-inset-bottom, 0px)) !important;
  }}

  .callbar {{
    display:flex;
    position:fixed;
    left:0;
    right:0;
    bottom:0;
    z-index:999;
    justify-content:center;
    align-items:center;
    gap:.6rem;
    background:#DC2626;
    color:#fff !important;
    font-weight:800;
    font-size:1.15rem;
    text-decoration:none;
    padding:.9rem 1rem calc(.9rem + env(safe-area-inset-bottom, 0px));
    box-shadow:0 -2px 10px rgba(0,0,0,0.25);
  }}
}}
</style>
"""


def get_pipeline() -> ScamShieldPipeline:
    # Adding or updating dataset files must replace a cached detector.
    folder = Path(os.getenv("SCAM_SHIELD_DATASET_DIR") or Path(__file__).parent / "data" / "dataset")
    signature = tuple(
        (name, (folder / name).stat().st_mtime_ns, (folder / name).stat().st_size)
        for name in ("messages_english.csv", "messages_hinglish.csv", "sources.csv", "legit_domains.csv")
        if (folder / name).is_file()
    )
    return _cached_pipeline(str(folder.resolve()), signature)


@st.cache_resource(ttl=300, max_entries=2)
def _cached_pipeline(folder: str, signature: tuple) -> ScamShieldPipeline:
    return ScamShieldPipeline(dataset_dir=Path(folder))


def get_gemini_api_key() -> Optional[str]:
    """Server-side key lookup: Streamlit secrets first, then environment / .env."""
    try:
        if "GEMINI_API_KEY" in st.secrets:
            key = str(st.secrets["GEMINI_API_KEY"]).strip()
            if key and key != "your_gemini_api_key_here":
                return key
    except Exception:
        pass
    key = (os.getenv("GEMINI_API_KEY") or "").strip()
    if key and key != "your_gemini_api_key_here":
        return key
    return None


# ---- state & callbacks -----------------------------------------------------

def _init_state():
    s = st.session_state

    # 1. Language state
    qp_lang = st.query_params.get("lang")
    if qp_lang in ("en", "hi") and "lang" in s and s["lang"] != qp_lang:
        s["lang"] = qp_lang
        s["lang_radio"] = "हिन्दी" if qp_lang == "hi" else "English"
        s.result, s.error, s.empty, s.pending = None, False, False, False
    elif "lang" not in s:
        s["lang"] = "hi" if qp_lang == "hi" else "en"

    if "lang_radio" not in s:
        s["lang_radio"] = "हिन्दी" if s["lang"] == "hi" else "English"
    st.query_params["lang"] = s["lang"]

    # 2. Theme state
    qp_theme = st.query_params.get("theme")
    if qp_theme in ("light", "dark") and "theme" in s and s["theme"] != qp_theme:
        s["theme"] = qp_theme
        s["theme_toggle"] = (qp_theme == "dark")
    elif "theme" not in s:
        s["theme"] = "dark" if qp_theme == "dark" else "light"

    if "theme_toggle" not in s:
        s["theme_toggle"] = (s["theme"] == "dark")
    st.query_params["theme"] = s["theme"]

    # Message and execution states
    s.setdefault("message_input", "")
    s.setdefault("result", None)
    s.setdefault("error", False)
    s.setdefault("empty", False)
    s.setdefault("pending", False)


def on_lang_change():
    s = st.session_state
    new_choice = s.get("lang_radio", "English")
    new_lang = "hi" if new_choice == "हिन्दी" else "en"
    if s.get("lang") != new_lang:
        s["lang"] = new_lang
        st.query_params["lang"] = new_lang
        # Clear shown result when language changes so an English result is never shown under Hindi labels
        s.result, s.error, s.empty, s.pending = None, False, False, False


def on_theme_change():
    s = st.session_state
    is_dark = s.get("theme_toggle", False)
    new_theme = "dark" if is_dark else "light"
    s["theme"] = new_theme
    st.query_params["theme"] = new_theme


def on_check():
    s = st.session_state
    s.result, s.error = None, False
    if not s.message_input.strip():
        s.empty, s.pending = True, False
    else:
        s.empty, s.pending = False, True


def on_text_change():
    st.session_state.result = None
    st.session_state.error = False
    st.session_state.empty = False


def render_screenshot_input():
    s = st.session_state
    hi = s.lang == "hi"
    def label(en, hindi):
        return hindi if hi else en
    with st.expander(label("Upload a screenshot (beta)", "स्क्रीनशॉट अपलोड करें (बीटा)")):
        st.caption(label(
            "PNG, JPG or WebP, up to 5 MB. Crop out private details first. Clicking Extract text sends this image to Google Gemini. Review every word before checking; text extraction can make mistakes.",
            "PNG, JPG या WebP, अधिकतम 5 MB। पहले निजी जानकारी हटा दें। टेक्स्ट निकालें दबाने पर तस्वीर Google Gemini को भेजी जाएगी। जाँच से पहले हर शब्द पढ़ें; टेक्स्ट निकालने में गलतियाँ हो सकती हैं।"))
        upload = st.file_uploader(label("Choose screenshot", "स्क्रीनशॉट चुनें"),
                                  type=["png", "jpg", "jpeg", "webp"], key="screenshot", max_upload_size=5)
        data = upload.getvalue() if upload else None
        digest = hashlib.sha256(data).hexdigest() if data else None
        if digest != s.get("upload_digest"):
            s.upload_digest = digest
            s.ocr_error = None
            s.ocr_ready = False
            s.result, s.error, s.empty, s.pending = None, False, False, False
            if s.get("input_from_image"):
                s.message_input = ""
                s.input_from_image = False
        errors = {
            "too_large": label("Image is too large. Use up to 5 MB and 16 megapixels.", "तस्वीर बहुत बड़ी है। अधिकतम 5 MB और 16 मेगापिक्सेल की तस्वीर चुनें।"),
            "wrong_format": label("Use a PNG, JPG or WebP image.", "PNG, JPG या WebP तस्वीर चुनें।"),
            "damaged": label("This image cannot be opened. Try another image or type the message.", "यह तस्वीर खुल नहीं रही। दूसरी तस्वीर चुनें या संदेश टाइप करें।"),
            "blurry": label("The message is not clear enough to read safely. Upload a clearer screenshot or type it.", "संदेश साफ़ नहीं पढ़ा जा रहा। साफ़ स्क्रीनशॉट चुनें या संदेश टाइप करें।"),
            "no_text": label("No readable message was found. Try another screenshot or type the message.", "पढ़ने योग्य संदेश नहीं मिला। दूसरा स्क्रीनशॉट चुनें या संदेश टाइप करें।"),
            "failed": label("Text extraction failed. Try again, upload another image, or type the message.", "टेक्स्ट नहीं निकाला जा सका। फिर कोशिश करें, दूसरी तस्वीर चुनें या संदेश टाइप करें।"),
            "unavailable": label("Screenshot reading is unavailable without the AI service. You can still paste or type a message below.", "AI सेवा के बिना स्क्रीनशॉट पढ़ना उपलब्ध नहीं है। नीचे संदेश पेस्ट या टाइप कर सकते हैं।"),
        }
        key = get_gemini_api_key()
        if not key:
            st.info(errors["unavailable"])
        if data:
            try:
                png = prepare_image(data)
                st.image(png, caption=label("Screenshot preview", "स्क्रीनशॉट का पूर्वावलोकन"), width=380)
                if st.button(label("Extract text", "टेक्स्ट निकालें"), disabled=not key or s.pending):
                    s.result, s.error, s.empty, s.pending = None, False, False, False
                    s.ocr_ready, s.ocr_error = False, None
                    if s.get("input_from_image"):
                        s.message_input = ""
                    with st.spinner(label("Reading screenshot…", "स्क्रीनशॉट पढ़ रहे हैं…")):
                        result = extract_text(png, key)
                    s.message_input = result.text.strip()
                    s.input_from_image = True
                    s.ocr_ready = True
            except ImageInputError as exc:
                s.ocr_error = str(exc)
            if s.get("ocr_error"):
                st.error(errors.get(s.ocr_error, errors["failed"]))
            if s.get("ocr_ready"):
                st.info(label("Review and edit the text below, then click Check message. No scam check has run yet.",
                              "नीचे टेक्स्ट पढ़ें और सुधारें, फिर संदेश जाँचें दबाएँ। अभी स्कैम की जाँच नहीं हुई है।"))


def on_clear():
    s = st.session_state
    s.message_input = ""
    s.input_from_image = False
    s.ocr_ready = False
    s.result, s.error, s.empty, s.pending = None, False, False, False


def on_sample(name: str):
    s = st.session_state
    s.message_input = SAMPLE_MESSAGES[name]
    s.input_from_image = False
    s.ocr_ready = False
    s.result, s.error, s.empty, s.pending = None, False, False, False


# ---- rendering -------------------------------------------------------------

def clean_list(items) -> list:
    return [str(i).strip() for i in (items or []) if str(i).strip()]


def get_check_summary(out: PipelineOutput) -> str:
    """Truthful plain-language summary of how the message was checked."""
    if out.is_ai and out.is_dataset_informed:
        return t("check_summary_full")
    if out.is_ai:
        return t("check_summary_ai_rules")
    if out.is_dataset_informed:
        return t("check_summary_rules_refs")
    return t("check_summary_rules_only")


def render_result(out: PipelineOutput):
    if not get_pipeline().is_dataset_available:
        st.warning("Reference examples could not be loaded. This check used the remaining available checks."
                   if st.session_state.lang == "en" else
                   "उदाहरण लोड नहीं हुए। यह परिणाम बाकी उपलब्ध जाँचों पर आधारित है।")
    key = str(out.verdict).upper().strip()
    if key not in ("SCAM", "SUSPICIOUS", "SAFE"):
        key = "SUSPICIOUS"

    verdict_info = {
        "SCAM": {
            "cls": "v-scam",
            "title": t("verdict_scam_title"),
            "lead": t("verdict_scam_lead"),
            "flags": t("verdict_scam_flags"),
        },
        "SUSPICIOUS": {
            "cls": "v-warn",
            "title": t("verdict_warn_title"),
            "lead": t("verdict_warn_lead"),
            "flags": t("verdict_warn_flags"),
        },
        "SAFE": {
            "cls": "v-safe",
            "title": t("verdict_safe_title"),
            "lead": t("verdict_safe_lead"),
            "flags": t("verdict_safe_flags"),
        },
    }[key]

    conf_map = {
        "HIGH": t("confidence_high"),
        "MEDIUM": t("confidence_medium"),
        "LOW": t("confidence_low"),
    }
    conf = conf_map.get(str(out.confidence).upper().strip())
    pill_html = (
        f'<div class="v-conf-pill">{esc(t("confidence_label"))}: <b>{esc(conf)}</b></div>'
        if conf else ""
    )

    # Flags and Actions
    flags = clean_list(out.red_flags)
    actions = clean_list(out.recommended_actions)

    flags_html = ""
    if flags:
        fcls = {"SAFE": "f-safe", "SUSPICIOUS": "f-warn"}.get(key, "")
        items = "".join(f"<li>{esc(f)}</li>" for f in flags)
        flags_html = f'<div class="v-col"><h3 class="v-sec-title">{esc(verdict_info["flags"])}</h3><ul class="flags {fcls}">{items}</ul></div>'

    steps_html = ""
    if actions:
        items = "".join(f"<li><span>{esc(a)}</span></li>" for a in actions)
        steps_html = f'<div class="v-col"><h3 class="v-sec-title">{esc(t("what_to_do_now"))}</h3><ol class="steps">{items}</ol></div>'

    grid_cls = ""
    if not flags or not actions:
        grid_cls = "single-col"

    # Badges for "How we checked this"
    if out.is_ai:
        ai_badge = (
            f'<div class="check-badge">'
            f'<span class="badge-dot"></span>'
            f'<div class="badge-text"><strong>{esc(t("badge_ai_title"))}</strong>'
            f'<small>{esc(t("badge_ai_sub"))}</small></div></div>'
        )
    else:
        ai_badge = (
            f'<div class="check-badge badge-neutral">'
            f'<span class="badge-dot dot-neutral"></span>'
            f'<div class="badge-text"><strong>{esc(t("badge_ai_off_title"))}</strong>'
            f'<small>{esc(t("badge_ai_off_sub"))}</small></div></div>'
        )

    rules_badge = (
        f'<div class="check-badge">'
        f'<span class="badge-dot"></span>'
        f'<div class="badge-text"><strong>{esc(t("badge_rules_title"))}</strong>'
        f'<small>{esc(t("badge_rules_sub"))}</small></div></div>'
    )

    dataset_badge = ""
    if out.is_dataset_informed:
        dataset_badge = (
            f'<div class="check-badge">'
            f'<span class="badge-dot"></span>'
            f'<div class="badge-text"><strong>{esc(t("badge_dataset_title"))}</strong>'
            f'<small>{esc(t("badge_dataset_sub"))}</small></div></div>'
        )

    # Patterns found
    findings = out.rule_results.findings if out.rule_results else []
    if findings:
        chips = []
        for f in findings:
            details = ", ".join(esc(str(d)) for d in f.get("details", []))
            cat = esc(str(f.get("category", "")))
            chips.append(f'<span class="rule-chip"><strong>{cat}</strong>: {details}</span>')
        patterns_html = (
            f'<div class="rule-chips"><span class="chips-label">{esc(t("rule_patterns_label"))}</span>'
            + "".join(chips)
            + '</div>'
        )
    else:
        patterns_html = f'<p class="no-patterns">{esc(t("no_patterns_found"))}</p>'

    current_lang = st.session_state.get("lang", "en")
    lang_hint_html = ""
    if current_lang == "hi" and not out.is_ai:
        lang_hint_html = f'<span class="compact-note note-en-hint">{esc(t("backend_english_note"))}</span>'

    backup_note_html = ""
    if not out.is_ai and out.fallback_reason:
        backup_note_html = f'<p class="compact-note"><b>{esc(t("backup_used_title"))}:</b> {esc(str(out.fallback_reason))}</p>'

    summary_sentence = get_check_summary(out)

    card_html = (
        f'<section class="verdict {verdict_info["cls"]}" role="status" aria-live="polite">'
        f'<div class="v-header">'
        f'  <div class="v-stamp-group">'
        f'    <div class="stamp">{ICONS[key]}<span>{esc(verdict_info["title"])}</span></div>'
        f'    <div class="v-headline">'
        f'      <span class="v-type">{esc(str(out.scam_type))}</span>'
        f'      <span class="v-lead">{esc(verdict_info["lead"])}</span>'
        f'    </div>'
        f'  </div>'
        f'  {pill_html}'
        f'</div>'
        f'<p class="v-explain">{esc(str(out.explanation))}</p>'
        + (f'<div class="v-grid {grid_cls}">{flags_html}{steps_html}</div>' if (flags_html or steps_html) else '')
        + f'<div class="check-strip">'
        f'  <div class="check-strip-header">'
        f'    <h4>{esc(t("how_checked_heading"))}</h4>'
        f'    {lang_hint_html}'
        f'  </div>'
        f'  <div class="badge-row">{ai_badge}{rules_badge}{dataset_badge}</div>'
        f'  <p class="check-summary">{esc(summary_sentence)}</p>'
        f'  {backup_note_html}'
        f'  {patterns_html}'
        f'</div>'
        f'</section>'
    )

    st.markdown(card_html, unsafe_allow_html=True)

    # Reference examples expander (below the strip, collapsed by default)
    refs = out.dataset_matches.matched_references if out.dataset_matches else []
    if SHOW_REFERENCE_EXAMPLES and refs:
        with st.expander(t("refs_expander")):
            st.markdown(f'<div class="detail"><p>{esc(t("refs_note"))}</p></div>', unsafe_allow_html=True)
            for r in refs:
                origin = t("ref_synthetic") if r.is_synthetic else t("ref_real")
                label = esc(str(r.assigned_label).title())
                cat = esc(str(r.curated_category).replace("_", " ").capitalize())
                st.markdown(
                    f'<div class="detail ref"><b>{label}</b>, {cat}<q>{esc(str(r.message))}</q>'
                    f'<small>{origin}</small></div>',
                    unsafe_allow_html=True,
                )


def render_rail() -> str:
    return (
        f'<aside class="rail"><h2>{esc(t("rail_heading"))}</h2>'
        f'<p>{esc(t("rail_p1"))}</p>'
        f'<a class="call" href="tel:1930">{esc(t("rail_call"))}</a>'
        '<ul>'
        f'<li>{esc(t("rail_cybercrime"))}<a href="https://cybercrime.gov.in" target="_blank" rel="noopener noreferrer">cybercrime.gov.in</a></li>'
        f'<li>{esc(t("rail_sanchar"))}<a href="https://sancharsaathi.gov.in" target="_blank" rel="noopener noreferrer">sancharsaathi.gov.in</a></li>'
        f'<li>{esc(t("rail_rbi"))}<a href="tel:14448">14448</a></li>'
        '</ul>'
        f'<h3>{esc(t("rail_privacy_heading"))}</h3>'
        f'<p>{esc(t("rail_privacy_body"))}</p>'
        f'<h3>{esc(t("rail_about_heading"))}</h3>'
        f'<p>{esc(t("rail_about_p1"))}</p>'
        f'<p>{esc(t("rail_about_p2"))}</p>'
        '</aside>'
    )


def render_app():
    _init_state()
    s = st.session_state

    st.set_page_config(
        page_title=t("page_title"),
        page_icon="🛡️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(get_css(s.theme, s.lang), unsafe_allow_html=True)

    # Top Bar: Brand on Left, Theme Toggle + Language Toggle + SOS button on Right
    with st.container(key="topbar_container"):
        top_left, top_right = st.columns([1, 1], vertical_alignment="center")
        with top_left:
            st.markdown(
                f'<div class="brand">{SHIELD_LOGO}<span>{esc(t("brand_name"))}</span></div>',
                unsafe_allow_html=True,
            )
        with top_right:
            c_theme, c_lang, c_sos = st.columns([1.1, 1.4, 1.6], vertical_alignment="center")
            with c_theme:
                st.toggle(
                    t("dark_mode"),
                    value=(s.theme == "dark"),
                    key="theme_toggle",
                    on_change=on_theme_change,
                )
            with c_lang:
                st.radio(
                    t("language_label"),
                    options=["English", "हिन्दी"],
                    index=0 if s.lang == "en" else 1,
                    horizontal=True,
                    key="lang_radio",
                    on_change=on_lang_change,
                    label_visibility="collapsed",
                )
            with c_sos:
                st.markdown(
                    f'<div class="sos-wrap"><a class="sos" href="tel:1930">{esc(t("lost_money_call"))}</a></div>',
                    unsafe_allow_html=True,
                )

    # Mobile fixed bottom call bar
    st.markdown(
        f'<a class="callbar" href="tel:1930">{esc(t("phone_call_bar"))}</a>',
        unsafe_allow_html=True,
    )

    main, side = st.columns([5, 2], gap="large")

    with side:
        st.markdown(render_rail(), unsafe_allow_html=True)

    with main:
        st.markdown(
            f'<div class="intro"><h1>{esc(t("intro_heading"))}</h1>'
            f'<p>{esc(t("intro_p1"))}</p>'
            + (f'<p class="hi">{esc(t("intro_p2"))}</p>' if s.lang == "en" else "")
            + '</div>',
            unsafe_allow_html=True,
        )

        render_screenshot_input()
        st.text_area(
            t("input_label"),
            key="message_input",
            height=170,
            placeholder=t("input_placeholder"),
            on_change=on_text_change,
        )
        st.markdown(f'<p class="privacy">{esc(t("privacy_note"))}</p>', unsafe_allow_html=True)

        c1, c2 = st.columns([3, 1])
        c1.button(t("check_button"), type="primary", on_click=on_check, disabled=s.pending, use_container_width=True)
        c2.button(t("clear_button"), key="clear", on_click=on_clear, disabled=s.pending, use_container_width=True)

        with st.expander(t("try_example")):
            for i in range(0, len(SAMPLE_BUTTON_MAPPING), 2):
                cols = st.columns(2)
                for col, (str_key, data_key) in zip(cols, SAMPLE_BUTTON_MAPPING[i:i + 2]):
                    col.button(
                        t(str_key),
                        key=f"sample_{data_key}",
                        on_click=on_sample,
                        args=(data_key,),
                        use_container_width=True,
                        disabled=s.pending,
                    )

        # Run analysis in pass so buttons render disabled meanwhile
        if s.pending:
            text = s.message_input.strip()
            try:
                with st.spinner(t("spinner_text")):
                    output = get_pipeline().analyze(text, api_key=get_gemini_api_key(), language=s.lang)
                s.result = {"text": text, "output": output}
            except Exception:
                s.result, s.error = None, True
            s.pending = False
            st.rerun()

        if s.empty:
            st.markdown(
                f'<div class="note note-info"><b>{esc(t("empty_title"))}</b>{esc(t("empty_body"))}</div>',
                unsafe_allow_html=True,
            )
        elif s.error:
            st.markdown(
                f'<div class="note note-error"><b>{esc(t("error_title"))}</b>{esc(t("error_body"))}</div>',
                unsafe_allow_html=True,
            )
        elif s.result and s.result["text"] == s.message_input.strip():
            render_result(s.result["output"])


if __name__ == "__main__":
    render_app()
