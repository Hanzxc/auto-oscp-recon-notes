"""Command-line interface for Auto OSCP Recon Notes.

Subcommands:
    init <target>                 Create a target workspace.
    import-nmap <target> <xml>    Parse Nmap XML into notes and recon data.
    checklist <target>            Generate enumeration checklists.
    report <target> [--force]     Generate the report template.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from . import __version__
from .notes import templates
from .notes.workspace import (
    create_workspace,
    read_services_json,
    write_services_json,
)
from .parsers.nmap_xml import NmapParseError, parse_nmap_xml
from .report import ReportExistsError, generate_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="oscp-notes",
        description=(
            "Organize authorized lab reconnaissance output into clean plain-text "
            "notes, checklists, and a report template. Does not scan or exploit."
        ),
    )
    parser.add_argument("--version", action="version", version=f"oscp-notes {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Create a target workspace")
    p_init.add_argument("target", help="Path / name of the target workspace")
    p_init.set_defaults(func=cmd_init)

    p_import = sub.add_parser("import-nmap", help="Import Nmap XML into the workspace")
    p_import.add_argument("target", help="Path / name of the target workspace")
    p_import.add_argument("xml_file", help="Path to an Nmap XML file (nmap -oX)")
    p_import.set_defaults(func=cmd_import_nmap)

    p_check = sub.add_parser("checklist", help="Generate service enumeration checklists")
    p_check.add_argument("target", help="Path / name of the target workspace")
    p_check.set_defaults(func=cmd_checklist)

    p_report = sub.add_parser("report", help="Generate the report template")
    p_report.add_argument("target", help="Path / name of the target workspace")
    p_report.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing non-empty report.txt",
    )
    p_report.set_defaults(func=cmd_report)

    return parser


# ---------------------------------------------------------------------------
# Command handlers
# ---------------------------------------------------------------------------

def cmd_init(args: argparse.Namespace) -> int:
    target = create_workspace(args.target)
    print(f"Created workspace: {target}{_sep(target)}")
    print("Created notes/, recon/, checklists/, and report.txt")
    return 0


def cmd_import_nmap(args: argparse.Namespace) -> int:
    target = Path(args.target)
    if not target.is_dir():
        print(f"Workspace not found: {target}. Run 'oscp-notes init {target}' first.")
        return 1
    create_workspace(target)

    try:
        services = parse_nmap_xml(args.xml_file)
    except NmapParseError as exc:
        print(f"Error: {exc}")
        return 1

    write_services_json(target, services)
    (target / "recon" / "nmap-summary.txt").write_text(
        templates.render_nmap_summary(services), encoding="utf-8"
    )
    (target / "notes" / "services.txt").write_text(
        templates.render_services_text(services), encoding="utf-8"
    )
    print(f"Imported {len(services)} open service(s) from {args.xml_file}")
    print("Wrote recon/services.json, recon/nmap-summary.txt, notes/services.txt")
    return 0


def cmd_checklist(args: argparse.Namespace) -> int:
    target = Path(args.target)
    if not target.is_dir():
        print(f"Workspace not found: {target}. Run 'oscp-notes init {target}' first.")
        return 1

    services = read_services_json(target)
    checklist_dir = target / "checklists"
    checklist_dir.mkdir(parents=True, exist_ok=True)

    outputs = {
        "enum-checklist.txt": templates.render_enum_checklist(services),
        "http-checklist.txt": templates.render_http_checklist(services),
        "smb-checklist.txt": templates.render_smb_checklist(services),
        "ssh-checklist.txt": templates.render_ssh_checklist(services),
    }
    for filename, contents in outputs.items():
        (checklist_dir / filename).write_text(contents, encoding="utf-8")

    print(f"Generated {len(outputs)} checklist file(s) in {checklist_dir}")
    if not services:
        print("Note: no services imported yet, so checklists contain general items only.")
    return 0


def cmd_report(args: argparse.Namespace) -> int:
    target = Path(args.target)
    if not target.is_dir():
        print(f"Workspace not found: {target}. Run 'oscp-notes init {target}' first.")
        return 1

    try:
        report_path = generate_report(target, force=args.force)
    except ReportExistsError as exc:
        print(f"Error: {exc}")
        return 1
    print(f"Wrote report: {report_path}")
    return 0


def _sep(path: Path) -> str:
    """Trailing separator for display, matching the plan's 'bluebox/' style."""
    return "" if str(path).endswith(("/", "\\")) else "/"


def main(argv: list[str] | None = None) -> int:
    """CLI entry point. Returns a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
