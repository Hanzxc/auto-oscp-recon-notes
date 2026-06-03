"""Auto OSCP Recon Notes.

A local note-generation tool for authorized pentest learning labs. It imports
reconnaissance output you already produced (Nmap XML), organizes services,
generates enumeration checklists, and exports plain-text notes and a report
template. It does not scan, exploit, or attack anything by itself.
"""

from .models import Service

__version__ = "0.1.0"
__all__ = ["Service", "__version__"]
