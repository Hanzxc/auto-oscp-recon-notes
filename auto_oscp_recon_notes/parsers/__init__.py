"""Parsers that turn recon tool output into :class:`~auto_oscp_recon_notes.models.Service` objects."""

from .nmap_xml import parse_nmap_xml

__all__ = ["parse_nmap_xml"]
