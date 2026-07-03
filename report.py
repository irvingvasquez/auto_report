#!/usr/bin/env python3
"""Convenience entry point. Run from repo root:

    python report.py stats
    python report.py generate full-cv --lang es
"""

from reports.cli import main

if __name__ == "__main__":
    raise SystemExit(main())
