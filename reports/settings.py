"""Configuration loading for auto_report."""

from __future__ import annotations

import datetime
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import yaml
except ImportError:
    yaml = None


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_CONFIG_PATH = REPO_ROOT / "config.yaml"


@dataclass
class Settings:
    """Runtime settings. CLI flags override config file values."""

    database_dir: Path = REPO_ROOT / "database"
    date_from: datetime.datetime = datetime.datetime(2008, 1, 1)
    date_to: datetime.datetime = datetime.datetime(2026, 12, 31)
    teaching_recent_years: int = 2
    edi_probatorios: Optional[Path] = None
    edi_output: Optional[Path] = None
    lang: str = "es"
    config_path: Path = field(default_factory=lambda: DEFAULT_CONFIG_PATH)

    @property
    def teaching_min_date(self) -> datetime.datetime:
        delta = datetime.timedelta(days=self.teaching_recent_years * 365)
        return self.date_to - delta


def _parse_date(value: str) -> datetime.datetime:
    return datetime.datetime.strptime(value, "%Y-%m-%d")


def _expand_path(value: str) -> Path:
    return Path(value).expanduser().resolve()


def load_settings(
    config_path: Optional[Path] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    lang: Optional[str] = None,
    edi_output: Optional[str] = None,
) -> Settings:
    """Load settings from config.yaml with optional CLI overrides."""
    path = config_path or DEFAULT_CONFIG_PATH
    settings = Settings(config_path=path)

    if path.exists() and yaml is not None:
        with open(path, encoding="utf-8") as fh:
            raw = yaml.safe_load(fh) or {}

        if "database_dir" in raw:
            db = raw["database_dir"]
            settings.database_dir = (
                REPO_ROOT / db if not Path(db).is_absolute() else Path(db)
            )

        if "date_from" in raw:
            settings.date_from = _parse_date(raw["date_from"])
        if "date_to" in raw:
            settings.date_to = _parse_date(raw["date_to"])
        if "teaching_recent_years" in raw:
            settings.teaching_recent_years = int(raw["teaching_recent_years"])
        if raw.get("edi_probatorios"):
            settings.edi_probatorios = _expand_path(raw["edi_probatorios"])
        if raw.get("edi_output"):
            settings.edi_output = _expand_path(raw["edi_output"])

    if date_from:
        settings.date_from = _parse_date(date_from)
    if date_to:
        settings.date_to = _parse_date(date_to)
    if lang:
        settings.lang = lang
    if edi_output:
        settings.edi_output = _expand_path(edi_output)

    return settings
