# Release 20261027-cleanup1

- Use project-root .env with environment variables taking precedence.
- Remove the obsolete personal dataset path; resolve relative dataset overrides from the project root.
- Fall back to bundled official domains when alternate message data has no domain list.
- Validate Gemini output locally and close the provider client after each request.
- Keep invalid datasets unavailable, including empty training splits.
- Fix the Help repository link, translated fallback labels and missing-dataset warning.
- Anchor the feedback dialog near the top of embedded pages and retain browser-only downloads.
- Remove unused imports, an unused schema and obsolete palette declarations; improve dark button contrast.
- Preserve both current and alternate Streamlit interfaces and standalone FastAPI mode.
- Add isolated offline regression tests, development requirements and scripts/release.ps1.

The confidence label remains heuristic. Some rule overrides can still return English text.
These checks are not a detection-accuracy benchmark or independent verification of all dataset licences.
