import json

from auto_oscp_recon_notes.cli import main


def test_init_creates_workspace(tmp_path):
    target = tmp_path / "bluebox"

    rc = main(["init", str(target)])

    assert rc == 0
    assert (target / "recon").is_dir()
    assert (target / "report.txt").is_file()


def test_import_nmap_writes_outputs(tmp_path, nmap_fixture):
    target = tmp_path / "bluebox"
    main(["init", str(target)])

    rc = main(["import-nmap", str(target), str(nmap_fixture)])

    assert rc == 0
    services_json = target / "recon" / "services.json"
    assert services_json.is_file()
    data = json.loads(services_json.read_text(encoding="utf-8"))
    assert len(data) == 3
    assert (target / "recon" / "nmap-summary.txt").is_file()

    services_txt = (target / "notes" / "services.txt").read_text(encoding="utf-8")
    assert "192.0.2.10" in services_txt


def test_import_nmap_without_workspace_fails(tmp_path, nmap_fixture):
    rc = main(["import-nmap", str(tmp_path / "missing"), str(nmap_fixture)])
    assert rc == 1


def test_import_nmap_existing_directory_creates_missing_subdirs(tmp_path, nmap_fixture):
    target = tmp_path / "existing"
    target.mkdir()

    rc = main(["import-nmap", str(target), str(nmap_fixture)])

    assert rc == 0
    assert (target / "notes" / "services.txt").is_file()


def test_checklist_generates_files(tmp_path, nmap_fixture):
    target = tmp_path / "bluebox"
    main(["init", str(target)])
    main(["import-nmap", str(target), str(nmap_fixture)])

    rc = main(["checklist", str(target)])

    assert rc == 0
    for name in ("enum-checklist.txt", "http-checklist.txt", "smb-checklist.txt", "ssh-checklist.txt"):
        assert (target / "checklists" / name).is_file()

    http = (target / "checklists" / "http-checklist.txt").read_text(encoding="utf-8")
    assert "80/tcp" in http


def test_report_command_includes_services(tmp_path, nmap_fixture):
    target = tmp_path / "bluebox"
    main(["init", str(target)])
    main(["import-nmap", str(target), str(nmap_fixture)])

    rc = main(["report", str(target)])

    assert rc == 0
    report = (target / "report.txt").read_text(encoding="utf-8")
    assert "LAB REPORT - bluebox" in report
    assert "192.0.2.10  80/tcp   http" in report


def test_report_command_refuses_to_overwrite_non_empty_report(tmp_path):
    target = tmp_path / "bluebox"
    main(["init", str(target)])
    (target / "report.txt").write_text("manual notes\n", encoding="utf-8")

    rc = main(["report", str(target)])

    assert rc == 1
    assert (target / "report.txt").read_text(encoding="utf-8") == "manual notes\n"


def test_report_command_force_overwrites_non_empty_report(tmp_path):
    target = tmp_path / "bluebox"
    main(["init", str(target)])
    (target / "report.txt").write_text("manual notes\n", encoding="utf-8")

    rc = main(["report", str(target), "--force"])

    assert rc == 0
    assert "LAB REPORT - bluebox" in (target / "report.txt").read_text(encoding="utf-8")
