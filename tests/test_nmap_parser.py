import pytest

from auto_oscp_recon_notes.parsers.nmap_xml import NmapParseError, parse_nmap_xml


def test_parse_nmap_xml_returns_open_services(nmap_fixture):
    services = parse_nmap_xml(nmap_fixture)

    assert len(services) == 3  # closed 139/tcp is excluded
    assert services[0].host == "192.0.2.10"
    assert services[0].state == "open"


def test_parse_ignores_closed_ports_by_default(nmap_fixture):
    ports = {service.port for service in parse_nmap_xml(nmap_fixture)}
    assert 139 not in ports
    assert ports == {22, 80, 445}


def test_parse_can_include_closed_ports(nmap_fixture):
    ports = {service.port for service in parse_nmap_xml(nmap_fixture, include_closed=True)}
    assert 139 in ports


def test_parse_preserves_product_and_version(nmap_fixture):
    by_port = {service.port: service for service in parse_nmap_xml(nmap_fixture)}
    assert by_port[22].product == "OpenSSH"
    assert by_port[22].version == "8.2p1"
    assert by_port[80].product == "Apache httpd"


def test_parse_captures_script_output(nmap_fixture):
    by_port = {service.port: service for service in parse_nmap_xml(nmap_fixture)}
    assert by_port[80].scripts["http-title"] == "Welcome to the Lab"


def test_parse_missing_file_raises():
    with pytest.raises(NmapParseError):
        parse_nmap_xml("does-not-exist.xml")


def test_parse_non_nmap_xml_raises(tmp_path):
    bad = tmp_path / "bad.xml"
    bad.write_text("<root><a/></root>", encoding="utf-8")
    with pytest.raises(NmapParseError):
        parse_nmap_xml(bad)


def test_parse_rejects_xml_with_dtd_or_entities(tmp_path):
    bad = tmp_path / "entity.xml"
    bad.write_text(
        '<!DOCTYPE nmaprun [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>'
        "<nmaprun>&xxe;</nmaprun>",
        encoding="utf-8",
    )

    with pytest.raises(NmapParseError, match="DTD/entity"):
        parse_nmap_xml(bad)
