#!/usr/bin/env python3
"""Quick-and-dirty CVPR accepted paper extractor."""

from __future__ import annotations

import argparse
import dataclasses
import json
import re
import sys
from pathlib import Path
from typing import Iterable, List

import requests
from bs4 import BeautifulSoup, NavigableString, Tag



CVPR_BASE_URL = "https://cvpr.thecvf.com/Conferences/{year}/AcceptedPapers"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15"
)


@dataclasses.dataclass
class PaperEntry:
    title: str
    link: str | None
    session: str | None
    authors: List[str]
    location: str | None
    highlight: bool


def _normalize(text: str | None) -> str | None:
    if not text:
        return None
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned or None


def fetch_html(year: int) -> str:
    url = CVPR_BASE_URL.format(year=year)
    resp = requests.get(url, headers={"User-Agent": USER_AGENT}, timeout=30)
    resp.raise_for_status()
    return resp.text


def _extract_session(cell: Tag) -> str | None:
    """Grab the session text that lives right before the <br> delimiter."""
    br = cell.find("br")
    if not br:
        return None
    sib = br.previous_sibling
    while sib:
        if isinstance(sib, NavigableString):
            text = sib.strip()
            if text:
                return _normalize(text)
        elif isinstance(sib, Tag):
            text = _normalize(sib.get_text(" ", strip=True))
            if text:
                return text
        sib = sib.previous_sibling
    return None


def _extract_authors(cell: Tag) -> List[str]:
    block = cell.select_one("div.indented")
    if not block:
        return []
    text = block.get_text(" ", strip=True)
    if not text:
        return []
    authors = [
        author.strip()
        for author in re.split(r"[·\u00B7]+", text)
        if author.strip()
    ]
    return authors


def _is_highlight(cell: Tag) -> bool:
    img = cell.find("img")
    if not img:
        return False
    title = img.get("title", "").strip().lower()
    return "highlight" in title or "award" in title


def parse_papers(html: str) -> List[PaperEntry]:
    soup = BeautifulSoup(html, "html.parser")
    papers: List[PaperEntry] = []
    for row in soup.select("table tr"):
        cells = row.find_all("td")
        if not cells:
            continue
        first = cells[0]
        title_tag = first.find(["a", "strong"])
        if not title_tag:
            continue
        title = title_tag.get_text(" ", strip=True)
        link = title_tag.get("href")
        session = _extract_session(first)
        authors = _extract_authors(first)
        location = None
        if len(cells) >= 3:
            location = _normalize(cells[2].get_text(" ", strip=True))
        highlight = _is_highlight(first)
        papers.append(
            PaperEntry(
                title=title,
                link=link,
                session=session,
                authors=authors,
                location=location,
                highlight=highlight,
            )
        )
    return papers


def filter_papers(papers: Iterable[PaperEntry], keyword: str | None) -> List[PaperEntry]:
    if not keyword:
        return list(papers)
    lowered = keyword.lower()
    filtered = []
    for paper in papers:
        haystacks = [
            paper.title.lower(),
            " ".join(paper.authors).lower(),
            (paper.session or "").lower(),
        ]
        if any(lowered in hay for hay in haystacks):
            filtered.append(paper)
    return filtered


def render_papers(papers: Iterable[PaperEntry]) -> None:
    for idx, paper in enumerate(papers, start=1):
        print(f"{idx}. {paper.title}")
        if paper.link:
            print(f"   URL: {paper.link}")
        if paper.session:
            print(f"   Session: {paper.session}")
        if paper.location:
            print(f"   Location: {paper.location}")
        if paper.authors:
            print(f"   Authors: {', '.join(paper.authors)}")
        if paper.highlight:
            print("   ⭐ Highlighted")
        print()


def write_json(papers: Iterable[PaperEntry], path: str) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("w", encoding="utf-8") as handle:
        json.dump([dataclasses.asdict(p) for p in papers], handle, indent=2, ensure_ascii=False)


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract accepted paper metadata from the CVPR website."
    )
    parser.add_argument("--year", type=int, default=2024, help="Conference year to fetch (default: 2024)")
    parser.add_argument(
        "--keyword",
        help="If set, only keep papers whose title/session/authors contain this substring.",
    )
    parser.add_argument("--limit", type=int, help="Return only the first N matches.")
    parser.add_argument("--json", dest="json_path", help="Custom JSON output path (default: cvpr_<year>_accepted.json)")
    parser.add_argument(
        "--no-json",
        action="store_true",
        help="Disable automatic JSON export (prints only).",
    )
    return parser.parse_args(argv)


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    try:
        html = fetch_html(args.year)
    except requests.HTTPError as exc:
        print(f"Failed to fetch CVPR data: {exc}", file=sys.stderr)
        return 1
    papers = parse_papers(html)
    if not papers:
        print("No papers were parsed from the page.", file=sys.stderr)
        return 1
    papers = filter_papers(papers, args.keyword)
    if args.limit is not None:
        papers = papers[: args.limit]
    json_path: str | None = None
    if not args.no_json:
        json_path = args.json_path or f"cvpr_{args.year}_accepted.json"
    if json_path:
        write_json(papers, json_path)
        print(f"Wrote {len(papers)} records to {json_path}")
    render_papers(papers)
    print(f"Displayed {len(papers)} records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
