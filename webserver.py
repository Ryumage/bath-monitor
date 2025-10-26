#!/usr/bin/env python3
"""
webserver.py

Routing:
- /                 -> landing page with cards grid
- /<bath>/<chart>   -> per-bath per-chart page (e.g. /south/heatmap)

Loads chart plugin classes from charts/ and invokes render() per page.
Assumes charts are in the `charts` package and each chart class subclasses
charts.chart_base.ChartBase with attributes:
    - name (str): url key for chart, e.g. "heatmap"
    - title (str): human title
    - priority (int): sorting order
and method:
    - render(self) -> dict with {"title": str, "html": str}
"""

from __future__ import annotations

import importlib
import pkgutil
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Type

import pandas as pd
from flask import Flask, abort, render_template, send_from_directory

from config import BATHS, DB_FILE, IMAGE_DIR

# charts.chart_base must exist inside charts package
from charts.chart_base import ChartBase  # type: ignore

APP_DIR = Path(__file__).resolve().parent

app = Flask(__name__, static_folder="static", template_folder="templates")


def load_chart_classes() -> List[Type[ChartBase]]:
    """
    Discover all ChartBase subclasses inside the charts/ directory.
    Returns sorted list by priority (smallest first).
    """
    chart_classes: List[Type[ChartBase]] = []
    plugins_dir = APP_DIR / "charts"

    if not plugins_dir.exists():
        return []

    for finder, module_name, ispkg in pkgutil.iter_modules([str(plugins_dir)]):
        # skip non-modules (shouldn't happen)
        module = importlib.import_module(f"charts.{module_name}")
        for attr_name in dir(module):
            obj = getattr(module, attr_name)
            if isinstance(obj, type) and issubclass(obj, ChartBase) and obj is not ChartBase:
                chart_classes.append(obj)

    chart_classes.sort(key=lambda cls: getattr(cls, "priority", 999))
    return chart_classes


# Load once at startup
CHART_CLASSES = load_chart_classes()


@app.route("/")
def index():
    """Landing page: grid with all baths (cards)."""
    # pass BATHS to template (labels + image links)
    return render_template("index.html", baths=BATHS)


@app.route("/<bath>/<chart>")
def bath_chart(bath: str, chart: str):
    """
    Render per-bath per-chart page.
    - bath: e.g. 'south'
    - chart: chart.name e.g. 'heatmap'
    """
    # basic validation
    if bath not in BATHS:
        abort(404)

    # find chart class by .name
    chart_cls = next((c for c in CHART_CLASSES if getattr(c, "name", None) == chart), None)
    if chart_cls is None:
        abort(404)

    # load data from sqlite
    df = pd.DataFrame()
    if DB_FILE.exists():
        with sqlite3.connect(str(DB_FILE)) as conn:
            # We intentionally do not limit by days here; plugins decide
            try:
                df = pd.read_sql_query(f"SELECT * FROM {bath} ORDER BY timestamp", conn)
            except Exception:
                # if table does not exist or other error, keep df empty
                df = pd.DataFrame()

    if not df.empty:
        df["timestamp"] = pd.to_datetime(df["timestamp"])

    # instantiate plugin and render
    chart_instance = chart_cls(bath, df)
    rendered = chart_instance.render()
    chart_title = rendered.get("title", getattr(chart_cls, "title", chart))
    chart_html = rendered.get("html", "<p>No chart produced.</p>")

    # build chart metadata for tabs/links (name + title)
    chart_meta = [{"name": c.name, "title": getattr(c, "title", c.__name__)} for c in CHART_CLASSES]

    # image url
    image_path = Path(IMAGE_DIR) / f"{bath}.jpg"
    image_url = f"/images/{bath}.jpg" if image_path.exists() else None

    # render template
    return render_template(
        "bath_chart.html",
        baths=BATHS,
        selected_bath=bath,
        chart_name=chart,
        chart_title=chart_title,
        chart_html=chart_html,
        chart_meta=chart_meta,
        image_url=image_url,
        active_chart=chart,  # used by header dropdown to preserve chart name
    )


@app.route("/images/<path:filename>")
def serve_image(filename: str):
    """Serve images (bath images + wave.svg)."""
    return send_from_directory(str(IMAGE_DIR), filename)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
