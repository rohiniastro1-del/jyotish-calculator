from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent / ".packages"
if PACKAGE_DIR.exists():
    sys.path.insert(0, str(PACKAGE_DIR))

from flask import Flask, render_template, request

from vedic_app.astro import CalculationError, calculate_reading, default_form_values
from vedic_app.data import CITIES


app = Flask(__name__)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
app.config["TEMPLATES_AUTO_RELOAD"] = True


@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


@app.route("/", methods=["GET", "POST"])
def index() -> str:
    form_values = default_form_values()
    results = None
    error = None
    build_mode = "natal"

    if request.method == "POST":
        form_values.update(request.form.to_dict())
        build_mode = request.form.get("buildMode", "natal")
        try:
            results = calculate_reading(form_values, build_mode=build_mode)
        except CalculationError as exc:
            error = str(exc)

    return render_template(
        "index.html",
        cities=CITIES,
        cities_json=json.dumps(CITIES, ensure_ascii=False),
        form_values=form_values,
        results=results,
        error=error,
        build_mode=build_mode,
        static_token=int(time.time()),
    )


if __name__ == "__main__":
    port = int(os.environ.get("ROHINI_ASTRO_PORT", "5000"))
    app.run(debug=False, use_reloader=False, threaded=False, port=port)
