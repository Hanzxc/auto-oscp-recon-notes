"""Create and manage a per-target note workspace on disk."""

from __future__ import annotations

import json
from pathlib import Path

from ..models import Service

SUBDIRS = ("recon", "notes", "checklists")

# Note stub files seeded at ``init`` time so the learner has a consistent place
# to write findings as they work through a target. ``services.txt`` is left out
# here because ``import-nmap`` generates it from real scan data.
NOTE_STUBS: dict[str, str] = {
    "web.txt": "WEB NOTES\n\n- URLs:\n- Technologies:\n- Interesting paths:\n- Parameters / forms:\n",
    "credentials.txt": (
        "CREDENTIALS\n\n"
        "Only record credentials discovered through the authorized lab workflow.\n\n"
        "- Service:\n- Username:\n- Source / how found:\n"
    ),
    "findings.txt": "FINDINGS\n\n- Finding 1:\n- Finding 2:\n",
    "lessons-learned.txt": (
        "LESSONS LEARNED\n\n"
        "- What worked:\n- What failed:\n- What to check earlier next time:\n"
    ),
}

WORKSPACE_README = (
    "AUTO OSCP RECON NOTES - WORKSPACE\n\n"
    "This folder holds organized recon notes for one authorized lab target.\n\n"
    "Layout:\n"
    "  recon/        parsed scan data (services.json, nmap-summary.txt)\n"
    "  notes/        your working notes (services.txt, web.txt, ...)\n"
    "  checklists/   generated enumeration checklists\n"
    "  report.txt    final plain-text report template\n\n"
    "Reminder: this tool organizes recon output you provide. It does not scan\n"
    "or exploit anything. Use it only against systems you are authorized to test.\n"
)


def create_workspace(target: str | Path) -> Path:
    """Create the standard folder structure for a target.

    Creates ``recon/``, ``notes/``, ``checklists/``, an empty ``report.txt``,
    a ``README.txt`` describing the layout, and the note stub files. Existing
    files are left untouched so re-running ``init`` never clobbers real notes.

    Returns:
        The target directory as a :class:`~pathlib.Path`.
    """
    target = Path(target)
    for sub in SUBDIRS:
        (target / sub).mkdir(parents=True, exist_ok=True)

    _write_if_absent(target / "report.txt", "")
    _write_if_absent(target / "README.txt", WORKSPACE_README)
    for filename, contents in NOTE_STUBS.items():
        _write_if_absent(target / "notes" / filename, contents)

    return target


def write_services_json(target: str | Path, services: list[Service]) -> Path:
    """Write parsed services to ``recon/services.json`` and return its path."""
    target = Path(target)
    (target / "recon").mkdir(parents=True, exist_ok=True)
    path = target / "recon" / "services.json"
    payload = [service.to_dict() for service in services]
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return path


def read_services_json(target: str | Path) -> list[Service]:
    """Read ``recon/services.json`` back into :class:`Service` objects.

    Returns an empty list if the file does not exist yet, so ``checklist`` and
    ``report`` can still produce templates before any scan is imported.
    """
    path = Path(target) / "recon" / "services.json"
    if not path.is_file():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    return [Service.from_dict(item) for item in data]


def _write_if_absent(path: Path, contents: str) -> None:
    if not path.exists():
        path.write_text(contents, encoding="utf-8")
