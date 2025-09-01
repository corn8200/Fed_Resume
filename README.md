# Minimal Federal Résumé Renderer (Flask)

A tiny Flask app that loads a résumé JSON (file or POST body), validates required federal résumé fields, and renders a print‑optimized USAJOBS‑style HTML with a “Print / Save as PDF” button.

## Requirements
- Python 3.10+
- Dependency: Flask (installed into a venv)

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install flask
```

## Run
```bash
FLASK_APP=app.py flask run
# or
python app.py
```

## Routes
- GET `/` — usage text with link to sample.
- GET `/render?src=resume.json` — loads JSON file from disk and renders.
- POST `/render` — body is JSON object; renders template.
- Errors: 400 (validation/bad JSON) as plain text; 404 for missing file.

## JSON Contract (Minimum)
- **contact**: object with required `name`, `email`, `phone`; optional `location`, `links` map.
- **work**: array (≥1). Each item requires `employer`, `title`, `start` (YYYY-MM), `hours_per_week` (number > 0). `end` (YYYY-MM) required unless `present=true`. Optional: `series_grade`, `location`, `salary`, `supervisor`, `can_contact_supervisor` (bool), `highlights` (array of strings), `address`, `duties`, `present` (bool).
- Optional top-level: `summary`, `education`, `certifications`, `training`, `languages`, `clearances`, `awards`, `publications`, `affiliations`, `volunteer`, `references`, `citizenship`, `veterans_preference`, `eligibilities` (array of hiring authorities).

See `resume.json` for a complete example.

## Validation
- `contact.name`, `contact.email`, `contact.phone` must be present and non-empty.
- `work` must contain at least one object.
- Per work item: `employer`, `title`, `start`, `hours_per_week` required.
- `hours_per_week` must be a number > 0; `present` (if provided) must be boolean.
- `start` and `end` must match `YYYY-MM`; `end` is required unless `present=true`.
- All validation errors are aggregated and returned as HTTP 400 text joined by `; `.

## Print / Save as PDF
- Print-first CSS: `@page { size: Letter; margin: 0.5in; }`.
- Sticky on-screen “Print / Save as PDF” button (hidden when printing).
- Tight, readable typography; avoids page breaks inside entries.

## Quick Test
- Load sample: `http://127.0.0.1:5000/render?src=resume.json`
- POST custom JSON:
  ```bash
  curl -sS -X POST http://127.0.0.1:5000/render \
    -H 'Content-Type: application/json' \
    -d @resume.json
  ```

## Notes
- No DB or client framework; JSON is the source of truth.
- Jinja filter `fmtdate` converts `YYYY-MM` → `Mon YYYY`.
