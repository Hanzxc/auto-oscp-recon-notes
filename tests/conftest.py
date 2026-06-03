"""Shared pytest fixtures."""

from pathlib import Path

import pytest

FIXTURE_XML = Path(__file__).parent / "fixtures" / "nmap-basic.xml"


@pytest.fixture
def nmap_fixture() -> Path:
    """Path to the bundled sample Nmap XML (192.0.2.10, 3 open services)."""
    return FIXTURE_XML
