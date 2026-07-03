"""Command-line interface for auto_report."""

from __future__ import annotations

import argparse
import sys

from .build import BUILDERS
from .data import load_context, print_stats
from .settings import load_settings


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="reports",
        description="Generate academic productivity reports from database/",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    stats_p = sub.add_parser("stats", help="Print publication and activity counts")
    stats_p.add_argument("--from", dest="date_from", metavar="DATE")
    stats_p.add_argument("--to", dest="date_to", metavar="DATE")
    stats_p.add_argument("--config", dest="config_path")

    gen_p = sub.add_parser("generate", help="Generate report fragment files")
    gen_p.add_argument(
        "report",
        help=f"Report name: {', '.join(sorted(BUILDERS))}",
    )
    gen_p.add_argument("--lang", choices=["es", "en"], default="es")
    gen_p.add_argument("--from", dest="date_from", metavar="DATE")
    gen_p.add_argument("--to", dest="date_to", metavar="DATE")
    gen_p.add_argument("--output", dest="edi_output", help="EDI output directory")
    gen_p.add_argument("--config", dest="config_path")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    config_path = getattr(args, "config_path", None)
    settings = load_settings(
        config_path=config_path,
        date_from=getattr(args, "date_from", None),
        date_to=getattr(args, "date_to", None),
        lang=getattr(args, "lang", None),
        edi_output=getattr(args, "edi_output", None),
    )

    ctx = load_context(settings)

    if args.command == "stats":
        print_stats(ctx, settings)
        return 0

    if args.command == "generate":
        builder = BUILDERS.get(args.report)
        if builder is None:
            print(f"Unknown report: {args.report!r}", file=sys.stderr)
            print(f"Available: {', '.join(sorted(BUILDERS))}", file=sys.stderr)
            return 1
        builder(ctx, settings)
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(main())
