#!/usr/bin/env python3
"""Very small Tkinter GUI wrapper around the CVPR extractor."""

from __future__ import annotations

import threading
import tkinter as tk
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText

from cvpr_extractor import (
    PaperEntry,
    fetch_html,
    filter_papers,
    parse_papers,
    write_json,
)


class ExtractorGUI(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("CVPR Extractor Demo")
        self.geometry("800x600")
        self.resizable(True, True)

        self.year_var = tk.StringVar(value="2024")
        self.keyword_var = tk.StringVar()
        self.limit_var = tk.StringVar(value="10")
        self.status_var = tk.StringVar(value="Ready.")

        self._build_form()

    def _build_form(self) -> None:
        wrapper = tk.Frame(self, padx=10, pady=10)
        wrapper.pack(fill="x")

        tk.Label(wrapper, text="Year").grid(row=0, column=0, sticky="w")
        tk.Entry(wrapper, textvariable=self.year_var, width=8).grid(
            row=0, column=1, padx=(0, 10), sticky="w"
        )

        tk.Label(wrapper, text="Keyword (optional)").grid(row=0, column=2, sticky="w")
        tk.Entry(wrapper, textvariable=self.keyword_var, width=20).grid(
            row=0, column=3, padx=(0, 10), sticky="w"
        )

        tk.Label(wrapper, text="Limit (optional)").grid(row=0, column=4, sticky="w")
        tk.Entry(wrapper, textvariable=self.limit_var, width=8).grid(
            row=0, column=5, padx=(0, 10), sticky="w"
        )

        self.fetch_button = tk.Button(
            wrapper, text="Fetch Papers", command=self.fetch_papers
        )
        self.fetch_button.grid(row=0, column=6, sticky="w")

        self.output = ScrolledText(self, wrap="word")
        self.output.pack(fill="both", expand=True, padx=10, pady=10)

        status_bar = tk.Frame(self, padx=10, pady=5)
        status_bar.pack(fill="x")
        tk.Label(status_bar, textvariable=self.status_var, anchor="w").pack(
            fill="x"
        )

    def fetch_papers(self) -> None:
        try:
            year = int(self.year_var.get())
        except ValueError:
            messagebox.showerror("Invalid year", "Year must be an integer.")
            return

        keyword = self.keyword_var.get().strip() or None
        limit_str = self.limit_var.get().strip()
        limit = None
        if limit_str:
            try:
                limit = max(1, int(limit_str))
            except ValueError:
                messagebox.showerror("Invalid limit", "Limit must be an integer.")
                return

        self.fetch_button.config(state="disabled")
        self.status_var.set("Fetching CVPR data…")
        self.output.delete("1.0", tk.END)

        threading.Thread(
            target=self._fetch_worker, args=(year, keyword, limit), daemon=True
        ).start()

    def _fetch_worker(self, year: int, keyword: str | None, limit: int | None) -> None:
        try:
            html = fetch_html(year)
            papers = parse_papers(html)
            papers = filter_papers(papers, keyword)
            if limit is not None:
                papers = papers[:limit]
            json_path = f"cvpr_{year}_accepted.json"
            write_json(papers, json_path)
        except Exception as exc:  # pylint: disable=broad-except
            self.after(
                0,
                lambda: self._handle_error(
                    f"Failed to fetch papers: {exc}",
                ),
            )
            return

        self.after(0, lambda: self._display_results(papers, json_path))

    def _display_results(self, papers: list[PaperEntry], json_path: str) -> None:
        self.fetch_button.config(state="normal")
        if not papers:
            self.status_var.set("No papers matched your filters.")
            return

        buffer = []
        for idx, paper in enumerate(papers, start=1):
            buffer.append(f"{idx}. {paper.title}")
            if paper.link:
                buffer.append(f"   URL: {paper.link}")
            if paper.session:
                buffer.append(f"   Session: {paper.session}")
            if paper.location:
                buffer.append(f"   Location: {paper.location}")
            if paper.authors:
                buffer.append(f"   Authors: {', '.join(paper.authors)}")
            if paper.highlight:
                buffer.append("   ⭐ Highlighted")
            buffer.append("")

        self.output.insert("1.0", "\n".join(buffer))
        self.status_var.set(
            f"Fetched {len(papers)} papers. Saved JSON to {json_path}."
        )

    def _handle_error(self, message: str) -> None:
        self.fetch_button.config(state="normal")
        self.status_var.set("Error.")
        messagebox.showerror("CVPR Extractor", message)


def main() -> None:
    app = ExtractorGUI()
    app.mainloop()


if __name__ == "__main__":
    main()
