"""Cross-platform smoke check for a generated workspace.

Usage:
    python tests/smoke_check.py <workspace>

Exits non-zero if any expected output file is missing. Intended to be run after
the four CLI commands (init / import-nmap / checklist / report) against a target.
"""

import sys
from pathlib import Path


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python tests/smoke_check.py <workspace>")
        return 2

    root = Path(argv[1])
    required = [
        root / "recon" / "nmap-summary.txt",
        root / "recon" / "services.json",
        root / "notes" / "services.txt",
        root / "checklists" / "enum-checklist.txt",
        root / "report.txt",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        print(f"Missing files: {missing}")
        return 1

    print("smoke test passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
