"""Run with: python -m reports  (from repo root)"""

import sys


def _main():
    try:
        from .cli import main
    except ImportError:
        # Invoked as: python reports generate ...  (without -m)
        from pathlib import Path

        root = Path(__file__).resolve().parent.parent
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        from reports.cli import main
    return main()


if __name__ == "__main__":
    raise SystemExit(_main())
