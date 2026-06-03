import pytest

from auto_oscp_recon_notes.cli import main
from auto_oscp_recon_notes.report import ReportExistsError, generate_report


def test_generate_report_empty_workspace(tmp_path):
    target = tmp_path / "bluebox"
    main(["init", str(target)])

    path = generate_report(target)

    assert path == target / "report.txt"
    text = path.read_text(encoding="utf-8")
    assert "LAB REPORT - bluebox" in text
    assert "No services imported yet." in text


def test_generate_report_with_services(tmp_path, nmap_fixture):
    target = tmp_path / "bluebox"
    main(["init", str(target)])
    main(["import-nmap", str(target), str(nmap_fixture)])

    text = generate_report(target).read_text(encoding="utf-8")

    assert "Host        Port     Service       Product       Version" in text
    assert "192.0.2.10  22/tcp   ssh" in text


def test_generate_report_refuses_non_empty_report_without_force(tmp_path):
    target = tmp_path / "bluebox"
    main(["init", str(target)])
    (target / "report.txt").write_text("manual notes\n", encoding="utf-8")

    with pytest.raises(ReportExistsError):
        generate_report(target)

    assert (target / "report.txt").read_text(encoding="utf-8") == "manual notes\n"


def test_generate_report_force_overwrites_non_empty_report(tmp_path):
    target = tmp_path / "bluebox"
    main(["init", str(target)])
    (target / "report.txt").write_text("manual notes\n", encoding="utf-8")

    text = generate_report(target, force=True).read_text(encoding="utf-8")

    assert "LAB REPORT - bluebox" in text
    assert "manual notes" not in text


def test_generate_report_custom_name(tmp_path):
    target = tmp_path / "bluebox"
    main(["init", str(target)])

    text = generate_report(target, target_name="HTB-Lab").read_text(encoding="utf-8")
    assert "LAB REPORT - HTB-Lab" in text
