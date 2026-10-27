# Public SMS collection awaiting fraud-label review

Source: https://github.com/junioralive/india-spam-sms-classification

Upstream file: `dataset/spam_ham_india.csv`; downloaded 27 October 2026. The user-supplied file matched the upstream download byte-for-byte (SHA-256 `e6a28126d1c4ec9d805a10cd89f2de2bb63650532102e9f35ab05c909c3a79f3`). License: MIT; copyright (c) 2024 JuniorAlive. Full notice is in `LICENSE-JuniorAlive.txt`.

Input: 2,267 records. Review collection: 2,053 nonempty, unique messages after Unicode/case/whitespace normalisation. Source row numbers preserve traceability. Full HTTP/www links, email addresses and contiguous Indian-format mobile numbers are replaced with placeholders. This is basic redaction, not guaranteed comprehensive anonymisation; some personal names, shortened links and other numbers may remain.

Original spam/ham labels are preserved. **Neither spam = SCAM nor ham = SAFE is a valid automatic conversion.** For example, the upstream spam class includes legitimate service promotions and government awareness notices. Public availability does not independently establish authenticity or label quality.

These records are deliberately excluded from the application's reference matcher and accuracy denominator. No API submission or automatic relabelling was performed. Before adding reviewed records to inference, two reviewers should assign SCAM/SAFE/SUSPICIOUS using a written policy, resolve disagreements and check duplicates/template overlap against all existing partitions. Do not use the current detector's predictions as ground-truth labels.

Do not claim these 2,053 review records are active scam references or independent fraud-evaluation examples.
