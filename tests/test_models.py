from auto_oscp_recon_notes.models import Service


def test_service_model_stores_basic_fields():
    service = Service(
        host="192.0.2.10",
        port=80,
        protocol="tcp",
        name="http",
        state="open",
        product="Apache httpd",
        version="2.4.41",
    )

    assert service.host == "192.0.2.10"
    assert service.port == 80
    assert service.name == "http"


def test_service_helpers():
    service = Service(
        host="192.0.2.10",
        port=22,
        protocol="tcp",
        name="ssh",
        state="open",
        product="OpenSSH",
        version="8.2p1",
    )

    assert service.endpoint == "22/tcp"
    assert service.product_version == "OpenSSH 8.2p1"


def test_service_is_hashable_despite_scripts_dict():
    # Regression: a frozen dataclass with a dict field must keep working in sets.
    service = Service(
        host="192.0.2.10",
        port=80,
        protocol="tcp",
        name="http",
        state="open",
        scripts={"http-title": "Welcome"},
    )

    assert service in {service}


def test_service_roundtrip_dict():
    service = Service(
        host="192.0.2.10",
        port=445,
        protocol="tcp",
        name="microsoft-ds",
        state="open",
        product="Samba smbd",
        version="4.11.6",
        scripts={"smb-os": "Samba"},
    )

    assert Service.from_dict(service.to_dict()) == service
