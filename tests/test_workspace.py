from auto_oscp_recon_notes.models import Service
from auto_oscp_recon_notes.notes.workspace import (
    create_workspace,
    read_services_json,
    write_services_json,
)


def test_create_workspace_creates_expected_folders(tmp_path):
    target = tmp_path / "bluebox"

    create_workspace(target)

    assert (target / "recon").is_dir()
    assert (target / "notes").is_dir()
    assert (target / "checklists").is_dir()
    assert (target / "report.txt").is_file()


def test_create_workspace_seeds_note_stubs_and_readme(tmp_path):
    target = create_workspace(tmp_path / "bluebox")

    assert (target / "README.txt").is_file()
    assert (target / "notes" / "findings.txt").is_file()
    assert (target / "notes" / "credentials.txt").is_file()


def test_create_workspace_does_not_clobber_existing_notes(tmp_path):
    target = create_workspace(tmp_path / "bluebox")
    findings = target / "notes" / "findings.txt"
    findings.write_text("my real notes", encoding="utf-8")

    create_workspace(target)  # re-run init

    assert findings.read_text(encoding="utf-8") == "my real notes"


def test_services_json_roundtrip(tmp_path):
    target = create_workspace(tmp_path / "bluebox")
    services = [
        Service(host="192.0.2.10", port=80, protocol="tcp", name="http", state="open"),
    ]

    write_services_json(target, services)

    assert (target / "recon" / "services.json").is_file()
    assert read_services_json(target) == services


def test_read_services_json_missing_returns_empty(tmp_path):
    target = create_workspace(tmp_path / "bluebox")
    assert read_services_json(target) == []
