"""Parse Nmap XML output into normalized :class:`Service` objects.

Only files the user already produced are read. This module never runs Nmap.
Generate input with, for example::

    nmap -sV -oX scans/target.xml <authorized-lab-target>
"""

from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path

from ..models import Service

MAX_XML_BYTES = 20 * 1024 * 1024


class NmapParseError(ValueError):
    """Raised when an Nmap XML file cannot be read or is not valid Nmap XML."""


def parse_nmap_xml(path: str | Path, include_closed: bool = False) -> list[Service]:
    """Parse an Nmap XML file into a list of :class:`Service` objects.

    Args:
        path: Path to an Nmap XML file (``nmap -oX``).
        include_closed: If ``False`` (default) only ``open`` ports are returned.

    Returns:
        Services in document order (host order, then port order).

    Raises:
        NmapParseError: If the file is missing or not parseable as Nmap XML.
    """
    path = Path(path)
    if not path.is_file():
        raise NmapParseError(f"Nmap XML file not found: {path}")

    data = path.read_bytes()
    if len(data) > MAX_XML_BYTES:
        raise NmapParseError(f"Nmap XML file is too large: {path}")
    if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        raise NmapParseError(f"Refusing XML with DTD/entity declarations: {path}")

    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:  # keep the message readable for learners
        raise NmapParseError(f"Could not parse XML in {path}: {exc}") from exc

    if root.tag != "nmaprun":
        raise NmapParseError(
            f"{path} does not look like Nmap XML (root tag is <{root.tag}>, expected <nmaprun>)."
        )

    services: list[Service] = []
    for host in root.findall("host"):
        address = _host_address(host)
        ports = host.find("ports")
        if ports is None:
            continue
        for port in ports.findall("port"):
            state_el = port.find("state")
            state = state_el.get("state", "") if state_el is not None else ""
            if not include_closed and state != "open":
                continue

            svc = port.find("service")
            scripts = {
                script.get("id", ""): script.get("output", "")
                for script in port.findall("script")
            }
            services.append(
                Service(
                    host=address,
                    port=int(port.get("portid", "0")),
                    protocol=port.get("protocol", ""),
                    name=svc.get("name", "") if svc is not None else "",
                    state=state,
                    product=svc.get("product", "") if svc is not None else "",
                    version=svc.get("version", "") if svc is not None else "",
                    extra_info=svc.get("extrainfo", "") if svc is not None else "",
                    scripts=scripts,
                )
            )
    return services


def _host_address(host: ET.Element) -> str:
    """Return the best host address, preferring IPv4, then IPv6, then MAC."""
    fallback = ""
    for addr in host.findall("address"):
        value = addr.get("addr", "")
        if addr.get("addrtype") == "ipv4":
            return value
        fallback = fallback or value
    return fallback
