# Database

Single source of truth for all reports. Edit these files, then run `python -m reports generate …`.

## BibTeX: `myproducts.bib`

### Required fields (every entry)

| Field | Purpose |
|-------|---------|
| `year` | Publication year — used for date filtering |
| `month` | Publication month (1–12) — used for date filtering |
| `author`, `title` | Display in reports |

### Category field: `note`

For `@article` entries, `note` determines the report section:

| `note` value | Section | Description |
|--------------|---------|-------------|
| `jcr` | JCR journals | Indexed journal articles |
| `conacyt` | CONACYT journals | CONACYT-indexed articles |
| `divulgacion` | Divulgación | Science outreach articles |
| *(other or empty)* | Otros | Other articles |

For `@inproceedings`, set `note = {proceedings}` (optional; all inproceedings go to proceedings regardless).

Other entry types are categorized by `ENTRYTYPE`:

| ENTRYTYPE | Section |
|-----------|---------|
| `inproceedings` | Proceedings |
| `mastersthesis` | Master students |
| `phdthesis` | PhD students |
| `unpublished` | Preprints |

### Optional fields

| Field | Used for |
|-------|----------|
| `if` | Impact factor (JCR list) |
| `doi` | Hyperlink in output |
| `journal`, `booktitle` | Venue name |
| `year_reported`, `month_reported` | Reporting date (convention: acceptance date) |
| `selected_publication` | `yes` — include in short CV |
| `link`, `school` | Thesis PDF links, institution |

### Date semantics

- **`year` / `month`**: publication date; entries are included when this date falls within the report's `--from` / `--to` range.
- **`year_reported` / `month_reported`**: when the product was reported to an institution (acceptance date convention).

Missing `year` or `month` causes the entry to be skipped; a warning is printed and collected in `categories['messages']`.

### Example: JCR article

```bibtex
@Article{example2025,
  author    = {Vasquez, Juan Irving and Coauthor, Name},
  title     = {Example Paper Title},
  journal   = {Journal Name},
  year      = {2025},
  month     = {06},
  note      = {jcr},
  if        = {3.4},
  doi       = {https://doi.org/10.1000/example},
}
```

### Example: Conference paper

```bibtex
@InProceedings{example2025conf,
  author    = {Vasquez, Juan Irving and Coauthor, Name},
  title     = {Example Conference Paper},
  booktitle = {2025 International Conference on Example},
  year      = {2025},
  month     = {09},
  note      = {proceedings},
  doi       = {https://doi.org/10.1000/conf},
}
```

## CSV files

### `teaching.csv`

| Column | Format | Description |
|--------|--------|-------------|
| `Nombre` | text | Course name |
| `Nivel` | text | Maestría / Doctorado |
| `Inicio`, `Fin` | `YYYY/MM/DD` | Course dates |
| `Horas` | integer | Total hours |

### `talks.csv`

| Column | Description |
|--------|-------------|
| `Date` | `YYYY/MM/DD` |
| `Type` | `platica`, `taller`, `evento`, or `entrevista` |
| `Title`, `Event`, `Place` | Talk details |
| `Link` | Optional URL (PDF or YouTube) |

### `books.csv`

| Column | Description |
|--------|-------------|
| `Author`, `Title`, `Editorial`, `Year`, `URL` | Book metadata |

### `developments.csv`

| Column | Description |
|--------|-------------|
| `Date`, `Name`, `User`, `License`, `Validation` | Technology developments |

### `tesistas_db.csv`

Advised students (master/PhD) — used separately from BibTeX thesis entries when needed.

## Field → section mapping (code reference)

This mirrors `categorize_bibliography_entries()` in `reports/data.py`:

```
article + note=jcr        → jcr
article + note=conacyt    → cona
article + note=divulgacion → divul
article + (other note)    → otros
inproceedings             → proc
mastersthesis             → mt
phdthesis                 → phd
unpublished               → preprint
```
