"""High-level report generation: read parsed services and write ``report.txt``."""

from __future__ import annotations

from pathlib import Path

from .notes.templates import render_report
from .notes.workspace import read_services_json


class ReportExistsError(FileExistsError):
    """Raised when report generation would overwrite an existing report."""


def generate_report(
    target: str | Path,
    target_name: str | None = None,
    *,
    force: bool = False,
) -> Path:
    """Generate ``<target>/report.txt`` from imported services.

    Args:
        target: Path to the target workspace.
        target_name: Display name used in the report title. Defaults to the
            workspace folder name.
        force: Overwrite an existing non-empty report when ``True``.

    Returns:
        The path to the written ``report.txt``.
    """
    target = Path(target)
    name = target_name or target.name
    services = read_services_json(target)
    report_path = target / "report.txt"
    if report_path.exists() and report_path.read_text(encoding="utf-8").strip() and not force:
        raise ReportExistsError(
            f"Refusing to overwrite non-empty report: {report_path}. "
            "Re-run with --force if you want to replace it."
        )
    report_path.write_text(render_report(name, services), encoding="utf-8")
    return report_path
