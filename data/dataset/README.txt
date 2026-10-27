SCAM SHIELD DATASET
===================

Everything here is plain CSV. Double-click any .csv file to open it in Excel.
If symbols such as the rupee sign look garbled: Data > From Text/CSV > File origin: UTF-8.

FILES
-----
messages_english.csv    982 English messages; existing records followed by the October 27 import.
messages_hinglish.csv   766 Hinglish messages (Hindi written in English letters).
legit_domains.csv       Official websites of banks and trusted organisations, one domain per row.
categories.csv          What each message category means, with counts.
sources.csv             Where each group of messages came from, with licence and attribution.

MESSAGE COLUMNS
---------------
message_id    EN-0001 style for English, HG-0001 for Hinglish.
message       The text of the message.
label         SCAM, SUSPICIOUS or SAFE.
category      The type of message. See categories.csv.
risk_signals  Warning signs (or genuine-message signs) noted for that message. Blank if none.
has_link      yes / no: whether the message contains a link.
language      en, hinglish or hi.
origin        public = real message from a public collection; synthetic = written for this project.
source_id     Links to sources.csv.
split         train / val / test. Use train for reference matching and keep test untouched for checking results.

LEGIT_DOMAINS COLUMNS
---------------------
domain        The website name only, with no https:// and no path.
domain_kind   main = the organisation's main site; alternate = another official site; zone_rule = a whole ending such as .bank.in.
match_rule    exact_or_subdomain: the link's host must equal the domain, or end with "." + the domain.
              ends_with_zone: the link's host must end with that ending.
              Never match by "contains": sbi.co.in.fake-site.com is NOT sbi.co.in.
status        checked = confirmed on the organisation's official portal when this list was prepared.
              unchecked = added from general knowledge. Confirm on the official site before relying on it.

NOTES
-----
- Messages marked synthetic use fictional names, phone numbers and links (ending in .example or .invalid). None of those links work.
- Placeholders in public messages: [PHONE], [NUMBER], [SHORTCODE].
- messages_hindi.csv adds 200 synthetic Devanagari Hindi references; Hindi performance is not established.
- Historical initial cleaning removed Devanagari messages (new Hindi references were added October 27), and template filler messages that describe themselves
  (for example "this message does not ask for a PIN") or point to placeholder links; UK-specific messages.
- SUSPICIOUS is the smallest group (50 per language). Add more real-looking borderline messages if you can.
- Most messages are synthetic. Do not present accuracy numbers from this data as real-world accuracy.

2026-10-27 IMPORT
1000 deduplicated synthetic messages added to train only. Original validation/test rows preserved. New labels are supplied, not independently reviewed. import_manifest.csv retains template IDs; import_report.json lists exclusions. Public spam/ham data is held separately in ../review and is not loaded by the app. No accuracy improvement is claimed.
