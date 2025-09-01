from __future__ import annotations

import json
import os
import re
from datetime import datetime
from typing import Any, Dict, List

from flask import Flask, Response, abort, render_template, request


app = Flask(__name__, template_folder="templates")


YYYY_MM_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")


def parse_date_yyyy_mm(s: Any) -> str:
    if not isinstance(s, str):
        return str(s)
    try:
        if not YYYY_MM_RE.match(s):
            return s
        dt = datetime.strptime(s, "%Y-%m")
        return dt.strftime("%b %Y")
    except Exception:
        return s


app.jinja_env.filters["fmtdate"] = parse_date_yyyy_mm


def validate_resume(r: Dict[str, Any]) -> List[str]:
    errors: List[str] = []

    contact = r.get("contact") or {}
    if not isinstance(contact, dict):
        errors.append("contact must be an object")
    else:
        if not contact.get("name"):
            errors.append("contact.name is required")
        if not contact.get("email"):
            errors.append("contact.email is required")
        if not contact.get("phone"):
            errors.append("contact.phone is required")

    work = r.get("work")
    if not isinstance(work, list) or len(work) == 0:
        errors.append("work must be a non-empty array")
    else:
        for idx, w in enumerate(work):
            ctx = f"work[{idx}]"
            if not isinstance(w, dict):
                errors.append(f"{ctx} must be an object")
                continue
            if not w.get("employer"):
                errors.append(f"{ctx}.employer is required")
            if not w.get("title"):
                errors.append(f"{ctx}.title is required")
            if w.get("hours_per_week") in (None, ""):
                errors.append(f"{ctx}.hours_per_week is required")
            else:
                hpw = w.get("hours_per_week")
                if not isinstance(hpw, (int, float)):
                    errors.append(f"{ctx}.hours_per_week must be a number")
                else:
                    if hpw <= 0:
                        errors.append(f"{ctx}.hours_per_week must be > 0")
            start = w.get("start")
            if not start:
                errors.append(f"{ctx}.start is required")
            else:
                if not isinstance(start, str) or not YYYY_MM_RE.match(start):
                    errors.append(f"{ctx}.start must be YYYY-MM")
            present_raw = w.get("present", False)
            present = bool(present_raw)
            if present_raw not in (True, False) and present_raw is not None:
                errors.append(f"{ctx}.present must be a boolean if provided")
            end = w.get("end")
            if not present:
                if not end:
                    errors.append(f"{ctx}.end is required unless present=true")
                else:
                    if not isinstance(end, str) or not YYYY_MM_RE.match(end):
                        errors.append(f"{ctx}.end must be YYYY-MM")

    return errors


def load_resume_from_request() -> Dict[str, Any]:
    if request.method == "POST":
        try:
            data = request.get_json(force=True, silent=False)
        except Exception:
            return abort(Response("Invalid JSON body", status=400, mimetype="text/plain"))
        if not isinstance(data, dict):
            return abort(Response("JSON body must be an object", status=400, mimetype="text/plain"))
        return data

    # GET: read from file specified by ?src= path (default: resume.json)
    src = request.args.get("src", "resume.json")
    if not src:
        return abort(Response("Missing ?src path to JSON", status=400, mimetype="text/plain"))
    # Restrict to current working directory
    path = os.path.join(os.getcwd(), src)
    if not os.path.isfile(path):
        return abort(Response(f"File not found: {src}", status=404, mimetype="text/plain"))
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return abort(Response(f"Invalid JSON in {src}: {e}", status=400, mimetype="text/plain"))
    except Exception as e:
        return abort(Response(f"Unable to read {src}: {e}", status=400, mimetype="text/plain"))
    if not isinstance(data, dict):
        return abort(Response(f"Top-level JSON in {src} must be an object", status=400, mimetype="text/plain"))
    return data


@app.route("/")
def index() -> Response:
    msg = (
        "Minimal Federal Resume Renderer. "
        "Use GET /render?src=resume.json or POST /render with JSON body."
    )
    html = f"""
    <html><head><meta charset='utf-8'><title>Resume Renderer</title></head>
    <body style='font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; line-height:1.4;'>
      <p>{msg}</p>
      <ul>
        <li><a href='/render?src=resume.json'>Render sample resume.json</a></li>
      </ul>
    </body></html>
    """
    return Response(html, mimetype="text/html")


@app.route("/render", methods=["GET", "POST"])
def render_resume():
    r = load_resume_from_request()
    errors = validate_resume(r)
    if errors:
        return Response("; ".join(errors), status=400, mimetype="text/plain")
    return render_template("resume.html", r=r)


if __name__ == "__main__":
    app.run(debug=True)
