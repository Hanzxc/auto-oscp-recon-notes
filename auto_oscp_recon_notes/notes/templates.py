"""Render parsed services into plain-text notes, summaries, and checklists.

Generated target files use ``.txt`` on purpose. The output avoids Markdown tables
and headings so learners can read the files cleanly in any terminal, editor, or
note-taking app.
"""

from __future__ import annotations

from collections import defaultdict

from ..models import Service

# ---------------------------------------------------------------------------
# Service classification
# ---------------------------------------------------------------------------

_HTTP_NAMES = {"http", "https", "http-alt", "http-proxy", "https-alt", "ssl/http"}
_HTTP_PORTS = {80, 443, 8000, 8008, 8080, 8443, 8888}
_SMB_NAMES = {"microsoft-ds", "netbios-ssn", "smb"}
_SMB_PORTS = {139, 445}
_SSH_NAMES = {"ssh"}
_SSH_PORTS = {22}


def is_http(service: Service) -> bool:
    name = service.name.lower()
    return name in _HTTP_NAMES or "http" in name or service.port in _HTTP_PORTS


def is_smb(service: Service) -> bool:
    return service.name.lower() in _SMB_NAMES or service.port in _SMB_PORTS


def is_ssh(service: Service) -> bool:
    return service.name.lower() in _SSH_NAMES or service.port in _SSH_PORTS


# ---------------------------------------------------------------------------
# Per-service note checklists
# ---------------------------------------------------------------------------

_GENERIC_NOTES = [
    "Confirm service and version",
    "Search for known issues for this version (authorized lab only)",
]

_HTTP_NOTES = [
    "Check page title",
    "Identify technologies",
    "Run directory discovery manually",
    "Check forms and parameters",
    "Take a screenshot",
]

_SMB_NOTES = [
    "List shares",
    "Check anonymous / guest access",
    "Enumerate users and host info",
    "Note SMB signing status",
]

_SSH_NOTES = [
    "Check banner",
    "Check supported auth methods",
    "Try valid credentials only if discovered through authorized lab workflow",
]


def _service_notes(service: Service) -> list[str]:
    if is_http(service):
        return _HTTP_NOTES
    if is_smb(service):
        return _SMB_NOTES
    if is_ssh(service):
        return _SSH_NOTES
    return _GENERIC_NOTES


def _group_by_host(services: list[Service]) -> dict[str, list[Service]]:
    grouped: dict[str, list[Service]] = defaultdict(list)
    for service in services:
        grouped[service.host].append(service)
    for host in grouped:
        grouped[host].sort(key=lambda s: (s.port, s.protocol))
    return grouped


def _heading(title: str, marker: str = "=") -> list[str]:
    return [title, marker * len(title), ""]


def _service_label(service: Service) -> str:
    return f"{service.endpoint} - {service.name or 'unknown'}"


# ---------------------------------------------------------------------------
# Renderers
# ---------------------------------------------------------------------------


def render_services_text(services: list[Service]) -> str:
    """Render ``notes/services.txt`` grouped by host, with per-service checklists."""
    lines = _heading("SERVICES")
    if not services:
        lines.append("No services imported yet. Run: oscp-notes import-nmap <target> <xml>")
        return "\n".join(lines) + "\n"

    for host, host_services in sorted(_group_by_host(services).items()):
        lines.append(f"HOST: {host}")
        lines.append("")
        for service in host_services:
            lines.append(f"SERVICE: {_service_label(service)}")
            lines.append(f"State: {service.state}")
            lines.append(f"Product: {service.product or '-'}")
            lines.append(f"Version: {service.version or '-'}")
            if service.extra_info:
                lines.append(f"Extra info: {service.extra_info}")
            lines.append("Notes:")
            for note in _service_notes(service):
                lines.append(f"  [ ] {note}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_nmap_summary(services: list[Service]) -> str:
    """Render ``recon/nmap-summary.txt``: a compact one-line-per-service summary."""
    lines = _heading("NMAP SUMMARY")
    if not services:
        lines.append("No open services found.")
        return "\n".join(lines) + "\n"

    grouped = _group_by_host(services)
    lines.append(f"Hosts: {len(grouped)}")
    lines.append(f"Open services: {len(services)}")
    lines.append("")
    for host, host_services in sorted(grouped.items()):
        lines.append(f"HOST: {host}")
        for service in host_services:
            product = service.product_version or "-"
            lines.append(
                f"  {service.endpoint:<10} {service.name or 'unknown':<16} {product}"
            )
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_enum_checklist(services: list[Service]) -> str:
    """Render a combined ``checklists/enum-checklist.txt`` covering all services."""
    lines = _heading("ENUMERATION CHECKLIST")
    lines.extend(_heading("GENERAL", "-"))
    lines.append("[ ] Record the target scope and authorization note")
    lines.append("[ ] Save raw Nmap output under recon/")
    lines.append("[ ] Re-run a full TCP port scan to confirm nothing was missed")
    lines.append("")

    if not services:
        lines.append("No services imported yet. Run import-nmap first.")
        return "\n".join(lines) + "\n"

    for host, host_services in sorted(_group_by_host(services).items()):
        lines.append(f"HOST: {host}")
        lines.append("")
        for service in host_services:
            lines.append(f"SERVICE: {_service_label(service)}")
            for note in _service_notes(service):
                lines.append(f"[ ] {note}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _render_service_checklist(title: str, services: list[Service], notes: list[str]) -> str:
    lines = _heading(title)
    if not services:
        lines.append("No matching services found in the imported scan.")
        return "\n".join(lines) + "\n"
    for service in sorted(services, key=lambda s: (s.host, s.port)):
        lines.append(f"{service.host} {service.endpoint}")
        for note in notes:
            lines.append(f"[ ] {note}")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def render_http_checklist(services: list[Service]) -> str:
    return _render_service_checklist(
        "HTTP / HTTPS CHECKLIST", [s for s in services if is_http(s)], _HTTP_NOTES
    )


def render_smb_checklist(services: list[Service]) -> str:
    return _render_service_checklist(
        "SMB CHECKLIST", [s for s in services if is_smb(s)], _SMB_NOTES
    )


def render_ssh_checklist(services: list[Service]) -> str:
    return _render_service_checklist(
        "SSH CHECKLIST", [s for s in services if is_ssh(s)], _SSH_NOTES
    )


def render_report(target_name: str, services: list[Service]) -> str:
    """Render ``report.txt``: a clean plain-text lab report template."""
    lines = _heading(f"LAB REPORT - {target_name}")
    lines.extend(_heading("TARGET SUMMARY", "-"))
    lines.append(f"Target: {target_name}")
    lines.append("Scope: Authorized lab target")
    lines.append("Date:")
    lines.append("")

    lines.extend(_heading("SERVICES FOUND", "-"))
    if services:
        lines.extend(_render_service_table(services))
    else:
        lines.append("No services imported yet.")
    lines.append("")

    lines.extend(_heading("INTERESTING FINDINGS", "-"))
    lines.append("Finding 1:")
    lines.append("Finding 2:")
    lines.append("")

    lines.extend(_heading("METHODOLOGY NOTES", "-"))
    lines.append("What worked:")
    lines.append("What failed:")
    lines.append("What to check earlier next time:")
    lines.append("")

    lines.extend(_heading("LESSONS LEARNED", "-"))
    lines.append("Lesson 1:")
    lines.append("Lesson 2:")
    lines.append("")

    lines.extend(_heading("APPENDIX: COMMANDS USED", "-"))
    lines.append("nmap ... (recorded by the learner)")
    return "\n".join(lines).rstrip() + "\n"


def _render_service_table(services: list[Service]) -> list[str]:
    rows = [
        (
            service.host,
            service.endpoint,
            service.name or "-",
            service.product or "-",
            service.version or "-",
        )
        for service in sorted(services, key=lambda s: (s.host, s.port, s.protocol))
    ]
    headers = ("Host", "Port", "Service", "Product", "Version")
    widths = [
        max(len(str(value)) for value in column)
        for column in zip(headers, *rows, strict=True)
    ]

    def fmt(row: tuple[str, str, str, str, str]) -> str:
        return "  ".join(str(value).ljust(width) for value, width in zip(row, widths, strict=True)).rstrip()

    return [fmt(headers), fmt(tuple("-" * width for width in widths)), *(fmt(row) for row in rows)]
