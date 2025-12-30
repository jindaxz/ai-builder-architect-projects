#!/usr/bin/env python3
"""Minimal Flask front-end for the CVPR extractor."""

from __future__ import annotations

from pathlib import Path
from typing import List

from flask import Flask, render_template, request

from cvpr_extractor import (
    PaperEntry,
    fetch_html,
    filter_papers,
    parse_papers,
    write_json,
)

app = Flask(__name__)


def _extract_papers(year: int, keyword: str | None, limit: int | None) -> tuple[List[PaperEntry], str]:
    html = fetch_html(year)
    papers = parse_papers(html)
    papers = filter_papers(papers, keyword)
    if limit is not None:
        papers = papers[:limit]
    json_path = Path(f"cvpr_{year}_accepted.json")
    write_json(papers, str(json_path))
    return papers, json_path.name


@app.route("/", methods=["GET", "POST"])
def index():
    context = {
        "year": "2024",
        "keyword": "",
        "limit": "20",
        "error": None,
        "papers": [],
        "json_path": None,
    }
    if request.method == "POST":
        context["year"] = request.form.get("year", "2024").strip() or "2024"
        context["keyword"] = request.form.get("keyword", "").strip()
        context["limit"] = request.form.get("limit", "").strip()
        try:
            year_val = int(context["year"])
        except ValueError:
            context["error"] = "Year must be a number."
            return render_template("index.html", **context)
        keyword_val = context["keyword"] or None
        limit_val = None
        if context["limit"]:
            try:
                limit_val = max(1, int(context["limit"]))
            except ValueError:
                context["error"] = "Limit must be a number."
                return render_template("index.html", **context)
        try:
            papers, json_path = _extract_papers(year_val, keyword_val, limit_val)
        except Exception as exc:  # pylint: disable=broad-except
            context["error"] = f"Failed to fetch CVPR data: {exc}"
            return render_template("index.html", **context)
        context["papers"] = papers
        context["json_path"] = json_path
        context["count"] = len(papers)
    return render_template("index.html", **context)


if __name__ == "__main__":
    app.run(debug=True)
