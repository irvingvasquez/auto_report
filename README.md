# Automatic Productivity Report

A unified platform for Mexican researchers to build productivity reports (Conacyt, SNI, IPN EDI, Politécnico, etc.) with minimal effort. Python generates LaTeX/HTML fragments from a central database; LaTeX templates assemble the final documents — similar to how Flask uses templates for web pages.

## Architecture

```
database/          Source data (BibTeX + CSV)
config.yaml        Date ranges and paths
reports/           Python package + report templates
  ├── data.py      Load and categorize entries
  ├── writers.py   Write .tex / .html fragments
  ├── build.py     Report registry (full-cv, web-page, …)
  └── cli.py       Command-line interface
```

See [docs/GUIDE.md](docs/GUIDE.md) for workflows, glossary, and troubleshooting.  
See [database/README.md](database/README.md) for data schemas.

## Installation

```sh
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Or with conda:

```sh
conda create -n report python=3
conda activate report
conda install jupyter numpy matplotlib
pip install bibtexparser pyyaml
```

LaTeX with `fontawesome` is required to compile CV PDFs.

## Quick start

```sh
# Show publication counts for the configured date range
python -m reports stats
# or:  python report.py stats

# Generate full CV fragments (Spanish)
python -m reports generate full-cv --lang es
# or:  python report.py generate full-cv --lang es

# Compile PDF
cd reports/full_cv/templates && pdflatex cv_jivg_es_full.tex
```

Run these from the **repo root** (`auto_report/`). Use `-m reports` or `report.py` — not `python reports` alone.

## CLI reference

```sh
python -m reports stats [--from YYYY-MM-DD] [--to YYYY-MM-DD]

python -m reports generate full-cv [--lang es|en] [--from ...] [--to ...]
python -m reports generate short-cv [--from ...] [--to ...]
python -m reports generate web-page [--from ...] [--to ...]
python -m reports generate simple-list [--lang es|en] [--from ...] [--to ...]
python -m reports generate edi [--from ...] [--to ...] [--output DIR]
```

Unknown report names print the list of registered builders.

## Report catalog

| Report | Output directory | LaTeX template | Typical use |
|--------|------------------|----------------|-------------|
| `full-cv` (es) | `reports/full_cv/text/` | `templates/cv_jivg_es_full.tex` | SNI, general CV |
| `full-cv` (en) | `reports/full_cv/text/` | `templates/cv_jivg_en_full.tex` | International CV |
| `short-cv` | `reports/short_cv/text/` | `template/cv_jivg_en_short.tex` | Short grant CV |
| `web-page` | `reports/web_page/html/` | — (HTML) | jivg.org publications |
| `simple-list` | `reports/simple_list/text/` | full CV templates | Minimal lists |
| `edi` | configurable | — (points summary) | IPN EDI evaluation |

Hand-edited prose (bios, statements, certifications) lives alongside generated fragments in each report's `text/` folder — see [docs/GUIDE.md](docs/GUIDE.md) for which files to edit manually.

## Project layout

```
auto_report/
├── config.yaml           Settings (dates, paths)
├── database/             myproducts.bib + CSV files
├── docs/GUIDE.md         Workflows and troubleshooting
├── reports/
│   ├── cli.py            CLI entry point
│   ├── data.py           Data loading
│   ├── writers.py        Fragment writers
│   ├── build.py          Report builders (registry)
│   ├── full_cv/          Full CV templates + text/
│   ├── short_cv/         Short CV
│   ├── web_page/         HTML output
│   ├── simple_list/      Simple publication lists
│   └── EDI/              EDI rubric (puntos_EDI.csv)
└── scripts/              Utility scripts (bib2dataframe.py)
```

Jupyter notebooks under each report folder remain for exploration; prefer the CLI for reproducible runs.
