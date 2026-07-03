"""Report builders registered for CLI dispatch."""

from __future__ import annotations

import datetime
from pathlib import Path
from typing import Callable

import pandas as pd

from .data import Context, load_context
from .settings import REPO_ROOT, Settings
from . import writers as w

BUILDERS: dict[str, Callable[[Context, Settings], None]] = {}


def register(name: str):
    def wrap(fn):
        BUILDERS[name] = fn
        return fn

    return wrap


def _out_dir(*parts: str) -> Path:
    return REPO_ROOT.joinpath(*parts)


def _pie_labels(ctx: Context, lang: str) -> tuple[list[int], list[str]]:
    p = ctx.productos
    counts, labels = [], []
    sections = [
        ("jcr", "JCR" if lang == "en" else "Artículos JCR"),
        ("proc", "Proceedings" if lang == "en" else "Congresos"),
        ("divul", "Outreach" if lang == "en" else "Divulgación"),
        ("mt", "Master Thesis" if lang == "en" else "Tesis de Maestría"),
        ("phd", "PhD Thesis" if lang == "en" else "Tesis de Doctorado"),
        ("cona", "Conacyt" if lang == "en" else "Artículos Conacyt"),
    ]
    for key, label in sections:
        if p[key]["count"] > 0:
            counts.append(p[key]["count"])
            labels.append(f"{label} ({p[key]['count']})")
    return counts, labels


def _write_full_cv_sections(
    ctx: Context,
    settings: Settings,
    out: Path,
    *,
    lang: str,
    teaching_min: datetime.datetime | None,
    include_books: bool = True,
    include_otros: bool = True,
    include_phd: bool = True,
    include_eventos: bool = True,
    include_entrevistas: bool = True,
    talks_date_filter: bool = True,
    proceedings_doi: bool = True,
) -> None:
    p = ctx.productos
    out.mkdir(parents=True, exist_ok=True)

    counts, labels = _pie_labels(ctx, lang)
    chart_name = "products_en" if lang == "en" else "products"
    if counts:
        w.write_pie_chart(counts, labels, out / chart_name)

    if p["jcr"]["count"] > 0:
        w.write_jcr_latex(p["jcr"]["entries"], out / "jcr_journals.tex", lang=lang)
    else:
        w.write_file_clear(out / "jcr_journals.tex")

    if p["cona"]["count"] > 0:
        w.write_journals_latex(p["cona"]["entries"], out / "conacyt_journals.tex")
    else:
        w.write_file_clear(out / "conacyt_journals.tex")

    if p["proc"]["count"] > 0:
        w.write_proceedings_latex(
            p["proc"]["entries"],
            out / "proceedings.tex",
            lang=lang,
            include_doi=proceedings_doi,
        )
    else:
        w.write_file_clear(out / "proceedings.tex")

    if include_books and ctx.books:
        w.write_books_latex(ctx.books, out / "books.tex")
    elif include_books:
        w.write_file_clear(out / "books.tex")

    if include_otros and p["otros"]["count"] > 0:
        w.write_otros_latex(p["otros"]["entries"], out / "otros.tex")
    elif include_otros:
        w.write_file_clear(out / "otros.tex")

    if p["mt"]["count"] > 0:
        w.write_thesis_list_latex(p["mt"]["entries"], out / "master_students.tex")
    else:
        w.write_file_clear(out / "master_students.tex")

    if include_phd:
        if p["phd"]["count"] > 0:
            w.write_thesis_list_latex(p["phd"]["entries"], out / "phd_students.tex")
        else:
            w.write_file_clear(out / "phd_students.tex")

    teach_from = teaching_min if teaching_min else settings.date_from
    teaching = w._filter_teaching(ctx.teaching, teach_from, settings.date_to)
    w.write_teaching_latex(teaching, out / "teaching.tex")

    if ctx.developments:
        w.write_developments_latex(ctx.developments, out / "developments.tex")
    else:
        w.write_file_clear(out / "developments.tex")

    talk_dates = (settings.date_from, settings.date_to) if talks_date_filter else (None, None)
    w.write_talks_latex(
        ctx.talks, "platica", out / "talks.tex",
        date_from=talk_dates[0], date_to=talk_dates[1],
    )
    w.write_talks_latex(ctx.talks, "taller", out / "workshop.tex")

    if p["divul"]["count"] > 0:
        w.write_divulgacion_latex(p["divul"]["entries"], out / "divulgacion.tex")
    else:
        w.write_file_clear(out / "divulgacion.tex")

    if include_eventos:
        w.write_talks_latex(
            ctx.talks, "evento", out / "eventos.tex",
            date_from=settings.date_from if talks_date_filter else None,
            date_to=settings.date_to if talks_date_filter else None,
            link_icon="{\\faFilePdfO}",
        )

    if include_entrevistas:
        w.write_talks_latex(
            ctx.talks, "entrevista", out / "entrevistas.tex",
            date_from=settings.date_from if talks_date_filter else None,
            date_to=settings.date_to if talks_date_filter else None,
            link_icon="{\\faYoutubePlay}",
        )

    if p["preprint"]["count"] > 0:
        w.write_preprints_latex(p["preprint"]["entries"], out / "preprints.tex")
    else:
        w.write_file_clear(out / "preprints.tex")


@register("full-cv")
def build_full_cv(ctx: Context, settings: Settings) -> None:
    lang = settings.lang
    out = _out_dir("reports", "full_cv", "text")

    if lang == "es":
        _write_full_cv_sections(
            ctx, settings, out, lang="es",
            teaching_min=settings.teaching_min_date,
            include_books=True, include_otros=True, include_phd=True,
            include_eventos=True, include_entrevistas=True,
            talks_date_filter=True, proceedings_doi=True,
        )
    else:
        # EN full CV: Aug 1 start convention, full teaching range, fewer sections
        _write_full_cv_sections(
            ctx, settings, out, lang="en",
            teaching_min=None,
            include_books=False, include_otros=False, include_phd=False,
            include_eventos=False, include_entrevistas=False,
            talks_date_filter=False, proceedings_doi=False,
        )

    print(f"Generated full CV ({lang}) fragments in {out}")


@register("short-cv")
def build_short_cv(ctx: Context, settings: Settings) -> None:
    out = _out_dir("reports", "short_cv", "text")
    out.mkdir(parents=True, exist_ok=True)
    p = ctx.productos
    author_fn = w.format_author_for_cv
    interval_years = (settings.date_to - settings.date_from).days / 365.25

    if p["jcr"]["count"] > 0:
        w.write_jcr_latex(
            p["jcr"]["entries"], out / "jcr_journals.tex",
            lang="en", author_fn=author_fn, selected_only=True,
        )
    else:
        w.write_file_clear(out / "jcr_journals.tex")

    if p["cona"]["count"] > 0:
        w.write_journals_latex(p["cona"]["entries"], out / "conacyt_journals.tex")
    else:
        w.write_file_clear(out / "conacyt_journals.tex")

    if p["proc"]["count"] > 0:
        w.write_proceedings_latex(
            p["proc"]["entries"], out / "proceedings.tex",
            lang="en", author_fn=author_fn, selected_only=True, include_doi=False,
        )
    else:
        w.write_file_clear(out / "proceedings.tex")

    w.write_thesis_summary_latex(p["mt"]["count"], interval_years, "master", out / "master_students.tex")
    w.write_thesis_summary_latex(p["phd"]["count"], interval_years, "phd", out / "phd_students.tex")

    teaching = w._filter_teaching(ctx.teaching, settings.date_from, settings.date_to)
    w.write_teaching_latex(teaching, out / "teaching.tex")

    if ctx.developments:
        w.write_developments_latex(ctx.developments, out / "developments.tex")
    else:
        w.write_file_clear(out / "developments.tex")

    w.write_talks_latex(ctx.talks, "platica", out / "talks.tex")
    w.write_talks_latex(ctx.talks, "taller", out / "workshop.tex")

    if p["divul"]["count"] > 0:
        w.write_divulgacion_latex(p["divul"]["entries"], out / "divulgacion.tex")
    else:
        w.write_file_clear(out / "divulgacion.tex")

    print(f"Generated short CV fragments in {out}")


@register("web-page")
def build_web_page(ctx: Context, settings: Settings) -> None:
    out = _out_dir("reports", "web_page", "html")
    out.mkdir(parents=True, exist_ok=True)
    p = ctx.productos

    counts, labels = _pie_labels(ctx, "en")
    if counts:
        w.write_pie_chart(counts, labels, out / "products_en")

    if p["jcr"]["count"] > 0:
        w.write_jcr_html(p["jcr"]["entries"], out / "jcr_journals.html")
    else:
        w.write_file_clear(out / "jcr_journals.html")

    if p["cona"]["count"] > 0:
        w.write_journals_html(p["cona"]["entries"], out / "conacyt_journals.html", "CONACYT Journals")
    else:
        w.write_file_clear(out / "conacyt_journals.html")

    w.write_proceedings_html(p["proc"]["entries"], out / "proceedings.html")

    if p["preprint"]["count"] > 0:
        w.write_preprints_html(p["preprint"]["entries"], out / "preprints.html")
    else:
        w.write_file_clear(out / "preprints.html")

    w.write_thesis_html(p["mt"]["entries"], out / "master_students.html", "Master Students")
    w.write_thesis_html(p["phd"]["entries"], out / "phd_students.html", "PhD Students")

    parts = [
        out / "encabezado.html",
        out / "jcr_journals.html",
        out / "conacyt_journals.html",
        out / "proceedings.html",
        out / "preprints.html",
        out / "my_thesis.html",
        out / "master_students.html",
        out / "phd_students.html",
    ]
    w.concatenate_html(parts, out / "publications.html")
    print(f"Generated web page HTML in {out}")


@register("simple-list")
def build_simple_list(ctx: Context, settings: Settings) -> None:
    lang = settings.lang
    out = _out_dir("reports", "simple_list", "text")

    _write_full_cv_sections(
        ctx, settings, out, lang=lang,
        teaching_min=None,
        include_books=False, include_otros=False, include_phd=False,
        include_eventos=(lang == "es"),
        include_entrevistas=False,
        talks_date_filter=False, proceedings_doi=(lang == "es"),
    )
    print(f"Generated simple list ({lang}) fragments in {out}")


EDI_CATEGORY_MAP = {
    "jcr": "revistas_a",
    "cona": "revistas_b",
    "divul": "revistas_e",
    "proc": "art_cong_int",
    "mt": "tesis_mae_tpo",
}


@register("edi")
def build_edi(ctx: Context, settings: Settings) -> None:
    puntos_path = REPO_ROOT / "reports" / "EDI" / "puntos_EDI.csv"
    puntos_df = pd.read_csv(puntos_path)
    puntos_dict = puntos_df.set_index("ID_Corto")["Puntos"].to_dict()

    if settings.edi_output:
        settings.edi_output.mkdir(parents=True, exist_ok=True)
        print(f"EDI output directory: {settings.edi_output}")

    total_points = 0
    p = ctx.productos

    for category, edi_id in EDI_CATEGORY_MAP.items():
        data = p.get(category, {"count": 0})
        count = data["count"] if isinstance(data, dict) else 0
        if count > 0 and edi_id in puntos_dict:
            points_per = int(puntos_dict[edi_id])
            category_points = count * points_per
            total_points += category_points
            print(f"{category}: {count} items × {points_per} points = {category_points}")

    print(f"\nTotal EDI points: {total_points}")

    if settings.edi_probatorios:
        print(f"Probatorios folder: {settings.edi_probatorios}")
