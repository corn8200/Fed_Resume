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

## Test
- Load sample: `http://127.0.0.1:5000/render?src=resume.json`
- POST custom JSON to `/render` with `Content-Type: application/json`
- Errors return HTTP 400 with reasons; missing files return 404.

## Print / Save as PDF
- Use your browser’s Print dialog; the page is sized to Letter with 0.5" margins and avoids breaking entries mid‑page.

## Notes
- No DB or client framework; JSON is the source of truth.
- Validation errors are aggregated and returned as plain text separated by `; `.

