"""Load database files and categorize bibliography entries."""

from __future__ import annotations

import csv
import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import bibtexparser

from .settings import Settings


def categorize_bibliography_entries(bib_database, date_inicio, date_fin):
    """
    Categorize bibliography entries by type and note.

    Returns a dictionary with counts and entries for each category.
    If a required key is missing in an entry, stores a message in
    categories['messages'] and continues processing the remaining entries.
    """
    categories = {
        "jcr": {"entries": [], "count": 0},
        "cona": {"entries": [], "count": 0},
        "divul": {"entries": [], "count": 0},
        "otros": {"entries": [], "count": 0},
        "proc": {"entries": [], "count": 0},
        "mt": {"entries": [], "count": 0},
        "phd": {"entries": [], "count": 0},
        "preprint": {"entries": [], "count": 0},
        "messages": [],
        "total": 0,
    }

    for entry in bib_database.entries:
        try:
            entry_date = datetime.datetime(int(entry["year"]), int(entry["month"]), 1)

            if date_inicio <= entry_date <= date_fin:
                categories["total"] += 1

                if entry["ENTRYTYPE"] == "article":
                    note = entry.get("note", "").lower()
                    if note == "jcr":
                        categories["jcr"]["entries"].append(entry)
                        categories["jcr"]["count"] += 1
                    elif note == "conacyt":
                        categories["cona"]["entries"].append(entry)
                        categories["cona"]["count"] += 1
                    elif note == "divulgacion":
                        categories["divul"]["entries"].append(entry)
                        categories["divul"]["count"] += 1
                    else:
                        categories["otros"]["entries"].append(entry)
                        categories["otros"]["count"] += 1

                elif entry["ENTRYTYPE"] == "inproceedings":
                    categories["proc"]["entries"].append(entry)
                    categories["proc"]["count"] += 1

                elif entry["ENTRYTYPE"] == "mastersthesis":
                    categories["mt"]["entries"].append(entry)
                    categories["mt"]["count"] += 1

                elif entry["ENTRYTYPE"] == "phdthesis":
                    categories["phd"]["entries"].append(entry)
                    categories["phd"]["count"] += 1

                elif entry["ENTRYTYPE"] == "unpublished":
                    categories["preprint"]["entries"].append(entry)
                    categories["preprint"]["count"] += 1
        except KeyError as exc:
            missing_key = exc.args[0]
            entry_info = {
                "ID": entry.get("ID", "<missing ID>"),
                "ENTRYTYPE": entry.get("ENTRYTYPE", "<missing ENTRYTYPE>"),
                "title": entry.get("title", "<missing title>"),
                "year": entry.get("year", "<missing year>"),
                "month": entry.get("month", "<missing month>"),
            }
            message = (
                f"Missing key '{missing_key}' for entry {entry_info['ID']}: "
                f"{entry_info}"
            )
            categories["messages"].append(message)

    return categories


def to_date(cadena: str) -> datetime.datetime:
    """Parse CSV date string YYYY/MM/DD."""
    return datetime.datetime.strptime(cadena, "%Y/%m/%d")


def load_csv(database_dir: Path, filename: str) -> list[dict[str, str]]:
    path = database_dir / filename
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as csvfile:
        return list(csv.DictReader(csvfile))


@dataclass
class Context:
    """All loaded data needed by report builders."""

    productos: dict[str, Any]
    teaching: list[dict[str, str]] = field(default_factory=list)
    talks: list[dict[str, str]] = field(default_factory=list)
    developments: list[dict[str, str]] = field(default_factory=list)
    books: list[dict[str, str]] = field(default_factory=list)


def load_context(settings: Settings) -> Context:
    """Load bib + CSVs and categorize publications by date range."""
    bib_path = settings.database_dir / "myproducts.bib"
    with open(bib_path, encoding="utf-8") as bibtex_file:
        bib_database = bibtexparser.loads(bibtex_file.read())

    productos = categorize_bibliography_entries(
        bib_database, settings.date_from, settings.date_to
    )

    for message in productos.get("messages", []):
        print(message)

    return Context(
        productos=productos,
        teaching=load_csv(settings.database_dir, "teaching.csv"),
        talks=load_csv(settings.database_dir, "talks.csv"),
        developments=load_csv(settings.database_dir, "developments.csv"),
        books=load_csv(settings.database_dir, "books.csv"),
    )


def print_stats(ctx: Context, settings: Settings) -> None:
    """Print summary counts (replaces notebook print cells)."""
    p = ctx.productos
    print(f"{p['total']} products found")
    print(f"{p['jcr']['count']} JCR products found")
    print(f"{p['proc']['count']} Proceedings found")
    print(f"{p['mt']['count']} Master Thesis found")
    print(f"{p['phd']['count']} PhD Thesis found")
    print(f"{p['cona']['count']} conacyt articles")
    print(f"{p['preprint']['count']} preprints")
    print(f"{p['divul']['count']} divulgacion")
    print(f"{p['otros']['count']} otros")
    print(f"{len(p.get('messages', []))} entries with missing keys")
    print(f"{len(ctx.teaching)} teaching entries in database")
    print(f"{len(ctx.talks)} talks entries in database")
    print(f"{len(ctx.developments)} developments entries in database")
    print(
        f"Date range: {settings.date_from.date()} to {settings.date_to.date()}"
    )
