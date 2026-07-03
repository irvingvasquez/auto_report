"""Write LaTeX and HTML report fragments."""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Callable, Optional

import matplotlib.pyplot as plt

from .data import Context, to_date
from .settings import Settings


def _sorted_entries(entries: list, key: str = "year") -> list:
    return sorted(entries, key=lambda i: i.get(key, "0"), reverse=True)


def _write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def write_file_clear(path: Path) -> None:
    """Write an empty file (clears a generated section)."""
    _write_file(path, "")


def _write_itemize(path: Path, lines: list[str]) -> None:
    if not lines:
        _write_file(path, "")
        return
    body = "\\begin{itemize} \n" + "".join(lines) + "\\end{itemize} \n"
    _write_file(path, body)


def format_author_for_cv(authors_raw: str) -> str:
    """Abbreviate multi-author lists for short CV (EN)."""
    for sep in (" and ", ";", ","):
        if sep in authors_raw:
            authors = [a.strip() for a in authors_raw.split(sep) if a.strip()]
            if len(authors) > 1:
                first = authors[0].split()[-1]
                return f"{first} et. al."
            break
    return authors_raw


def _filter_talks(
    talks: list,
    talk_type: str,
    date_from: Optional[datetime.datetime] = None,
    date_to: Optional[datetime.datetime] = None,
) -> list:
    result = []
    for entry in talks:
        if entry.get("Type") != talk_type:
            continue
        if date_from is not None and date_to is not None:
            talk_date = to_date(entry["Date"])
            if not (date_from <= talk_date <= date_to):
                continue
        result.append(entry)
    return result


def _filter_teaching(
    teaching: list,
    date_from: datetime.datetime,
    date_to: datetime.datetime,
) -> list:
    result = []
    for entry in teaching:
        start = to_date(entry["Inicio"])
        end = to_date(entry["Fin"])
        if date_from <= start and date_to >= end:
            result.append(entry)
    return result


# --- LaTeX writers ---


def write_jcr_latex(
    entries: list,
    path: Path,
    *,
    lang: str = "es",
    author_fn: Optional[Callable[[str], str]] = None,
    selected_only: bool = False,
) -> None:
    lines = []
    for entry in _sorted_entries(entries):
        if selected_only and entry.get("selected_publication") != "yes":
            continue
        author = entry["author"]
        if author_fn:
            author = author_fn(author)
        line = (
            f"\\item {author}, {entry['title']},"
            f"\\textit{{ {entry['journal']},}} ({entry['year']}),"
        )
        if "doi" in entry:
            icon = "\\faFilePdfO" if lang == "en" else "\\faExternalLink"
            line += f" \\href{{{entry['doi']}}} {{{icon}}},"
        if "if" in entry:
            line += f" I.F. {entry['if']} "
        lines.append(line + "\n")
    _write_itemize(path, lines)


def write_journals_latex(entries: list, path: Path) -> None:
    lines = []
    for entry in _sorted_entries(entries):
        lines.append(
            f"\\item {entry['author']}, {entry['title']},"
            f"\\textit{{ {entry['journal']},}} ({entry['year']}) \n"
        )
    _write_itemize(path, lines)


def write_proceedings_latex(
    entries: list,
    path: Path,
    *,
    lang: str = "es",
    author_fn: Optional[Callable[[str], str]] = None,
    selected_only: bool = False,
    include_doi: bool = True,
) -> None:
    lines = []
    for entry in _sorted_entries(entries):
        if selected_only and entry.get("selected_publication") != "yes":
            continue
        author = entry["author"]
        if author_fn:
            author = author_fn(author)
        line = (
            f"\\item {author}, {entry['title']}, "
            f"\\textit{{ {entry['booktitle']},}} {entry['year']}"
        )
        if include_doi and lang == "es" and "doi" in entry:
            line += f", \\href{{{entry['doi']}}} {{\\faFilePdfO}}"
        lines.append(line + " \n")
    _write_itemize(path, lines)


def write_books_latex(books: list, path: Path) -> None:
    lines = []
    for row in books:
        lines.append(
            f"\\item {row['Author']}, {row['Title']}, {row['Editorial']}, "
            f"{row['Year']}, \\href{{{row['URL']}}} {{\\faExternalLink}} \n"
        )
    _write_itemize(path, lines)


def write_otros_latex(entries: list, path: Path) -> None:
    lines = []
    for entry in _sorted_entries(entries):
        line = f"\\item {entry.get('author', '')}, {entry.get('title', '')}"
        medio = (
            entry.get("journal")
            or entry.get("booktitle")
            or entry.get("publisher")
            or entry.get("school")
            or entry.get("howpublished")
            or ""
        )
        if medio:
            line += f", \\textit{{ {medio} }}"
        if entry.get("year"):
            line += f", ({entry['year']})"
        if entry.get("doi"):
            line += f", \\href{{{entry['doi']}}}{{\\faExternalLink}}"
        elif entry.get("link"):
            line += f", \\href{{{entry['link']}}}{{\\faExternalLink}}"
        lines.append(line + ".\n")
    _write_itemize(path, lines)


def write_thesis_list_latex(entries: list, path: Path) -> None:
    lines = []
    for entry in _sorted_entries(entries):
        link = entry.get("link", "")
        lines.append(
            f"\\item {entry['author']}, \\textit{{ {entry['title']} }}, "
            f"\\href{{ {link} }}{{\\faFilePdfO}}, {entry['year']}, "
            f"{entry['school']}. \n"
        )
    _write_itemize(path, lines)


def write_thesis_summary_latex(
    count: int, years: float, degree: str, path: Path
) -> None:
    label = "master" if degree == "master" else "PhD"
    text = (
        f"{count} supervised {label} students in the last {years:.0f} years."
    )
    _write_file(path, text + "\n")


def write_teaching_latex(entries: list, path: Path) -> None:
    lines = []
    for entry in entries:
        lines.append(
            f"\\item {entry['Inicio']}, \\textit{{ {entry['Nombre']},}} "
            f"nivel {entry['Nivel']}, {entry['Horas']} horas. \n"
        )
    _write_itemize(path, lines)


def write_developments_latex(entries: list, path: Path) -> None:
    lines = []
    for entry in entries:
        lines.append(
            f"\\item {entry['Date']}, \\textit{{ {entry['Name']},}} "
            f"{entry['User']}, {entry['License']}, {entry['Validation']} \n"
        )
    _write_itemize(path, lines)


def write_talks_latex(
    talks: list,
    talk_type: str,
    path: Path,
    *,
    date_from: Optional[datetime.datetime] = None,
    date_to: Optional[datetime.datetime] = None,
    link_icon: Optional[str] = None,
) -> None:
    filtered = _filter_talks(talks, talk_type, date_from, date_to)
    lines = []
    for entry in filtered:
        line = (
            f"\\item {entry['Date']}, {entry['Title']}, "
            f"en \\textit{{ {entry['Event']},}} {entry['Place']}"
        )
        if link_icon and entry.get("Link"):
            line += f", \\href{{{entry['Link']}}}{{{link_icon}}}"
        lines.append(line + ".\n" if link_icon else line + " \n")
    _write_itemize(path, lines)


def write_divulgacion_latex(entries: list, path: Path) -> None:
    lines = []
    for entry in _sorted_entries(entries):
        lines.append(
            f"\\item {entry['author']}, {entry['title']},"
            f"\\textit{{ {entry['journal']},}} ({entry['year']})\n"
        )
    _write_itemize(path, lines)


def write_preprints_latex(entries: list, path: Path) -> None:
    lines = []
    for entry in _sorted_entries(entries):
        lines.append(
            f"\\item {entry['author']}, {entry['title']}, "
            f"{entry.get('journal', '')}, {entry['year']}, "
            f"\\href{{{entry.get('link', '')}}}{{\\faFilePdfO}} \n"
        )
    _write_itemize(path, lines)


def write_pie_chart(
    counts: list[int],
    labels: list[str],
    path_prefix: Path,
) -> None:
    if not counts:
        return
    fig, ax = plt.subplots(figsize=(9, 4.5), subplot_kw=dict(aspect="equal"))
    ax.pie(counts, labels=labels, autopct="%1.1f%%", shadow=True, startangle=90)
    ax.axis("equal")
    plt.tight_layout()
    path_prefix.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(str(path_prefix) + ".pdf", format="pdf")
    plt.savefig(str(path_prefix) + ".png", format="png")
    plt.close()


# --- HTML writers ---


def write_jcr_html(entries: list, path: Path) -> None:
    lines = ["<h2><strong>Journal Papers<br /></strong></h2> \n<ul> \n"]
    for entry in _sorted_entries(entries):
        doi = entry.get("doi", "")
        if_val = entry.get("if", "")
        if_suffix = f", I.F. {if_val} " if if_val else " "
        lines.append(
            f"<li> {entry['author']}, "
            f"<strong>{entry['title']}</strong>, "
            f"<em> {entry['journal']}</em>, ({entry['year']}), "
            f'<a href="{doi}">{doi}</a>{if_suffix}</li> \n'
        )
    lines.append("</ul> \n")
    _write_file(path, "".join(lines))


def write_journals_html(entries: list, path: Path, heading: str) -> None:
    lines = [f"<h2><strong>{heading}<br /></strong></h2> \n<ul> \n"]
    for entry in _sorted_entries(entries):
        lines.append(
            f"<li> {entry['author']}, "
            f"<strong>{entry['title']}</strong>, "
            f"<em> {entry['journal']}</em>, ({entry['year']}) </li> \n"
        )
    lines.append("</ul> \n")
    _write_file(path, "".join(lines))


def write_proceedings_html(entries: list, path: Path) -> None:
    if not entries:
        return
    lines = ["<h2><strong>Conferences<br /></strong></h2> \n<ul> \n"]
    for entry in _sorted_entries(entries):
        doi = entry.get("doi", "")
        doi_part = f', <a href="{doi}">{doi}</a>' if doi else ""
        lines.append(
            f"<li> {entry['author']}, "
            f"<strong>{entry['title']}</strong>, "
            f"<em> {entry['booktitle']}</em>, {entry['year']}{doi_part} </li> \n"
        )
    lines.append("</ul> \n")
    _write_file(path, "".join(lines))


def write_preprints_html(entries: list, path: Path) -> None:
    lines = ["<h2><strong>Preprints:<br /></strong></h2> \n<ul> \n"]
    for entry in _sorted_entries(entries):
        link = entry.get("link", "")
        lines.append(
            f"<li> {entry['author']}, "
            f"<strong>{entry['title']}</strong>, "
            f"{entry.get('journal', '')}, {entry['year']}, "
            f'<a href="{link}">{link}</a> </li> \n'
        )
    lines.append("</ul> \n")
    _write_file(path, "".join(lines))


def write_thesis_html(entries: list, path: Path, heading: str) -> None:
    if not entries:
        return
    lines = [f"<h2><strong>{heading}<br /></strong></h2> \n<ul> \n"]
    for entry in _sorted_entries(entries):
        link = entry.get("link", "")
        lines.append(
            f'<li> {entry["author"]}, '
            f'<a href="{link}"><strong>{entry["title"]}</strong></a>, '
            f'{entry["year"]}, {entry.get("school", "")} </li> \n'
        )
    lines.append("</ul> \n")
    _write_file(path, "".join(lines))


def concatenate_html(parts: list[Path], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    with open(output, "w", encoding="utf-8") as outfile:
        for part in parts:
            if part.exists():
                outfile.write(part.read_text(encoding="utf-8"))
                outfile.write("\n")
