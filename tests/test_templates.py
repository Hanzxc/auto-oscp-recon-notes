from auto_oscp_recon_notes.models import Service
from auto_oscp_recon_notes.notes import templates


def _sample_services():
    return [
        Service(host="192.0.2.10", port=22, protocol="tcp", name="ssh",
                state="open", product="OpenSSH", version="8.2p1"),
        Service(host="192.0.2.10", port=80, protocol="tcp", name="http",
                state="open", product="Apache httpd", version="2.4.41"),
        Service(host="192.0.2.10", port=445, protocol="tcp", name="microsoft-ds",
                state="open", product="Samba smbd", version="4.11.6"),
    ]


def test_render_services_text_includes_host_and_service():
    text = templates.render_services_text(_sample_services())
    assert "HOST: 192.0.2.10" in text
    assert "SERVICE: 22/tcp - ssh" in text
    assert "OpenSSH" in text
    assert "[ ] Check banner" in text  # ssh-specific checklist item


def test_render_services_text_empty():
    text = templates.render_services_text([])
    assert "No services imported yet" in text


def test_render_nmap_summary_counts():
    text = templates.render_nmap_summary(_sample_services())
    assert "Open services: 3" in text
    assert "Apache httpd 2.4.41" in text


def test_render_enum_checklist_has_service_sections():
    text = templates.render_enum_checklist(_sample_services())
    assert "ENUMERATION CHECKLIST" in text
    assert "SERVICE: 80/tcp - http" in text
    assert "[ ] Run directory discovery manually" in text


def test_http_checklist_only_http_services():
    text = templates.render_http_checklist(_sample_services())
    assert "192.0.2.10 80/tcp" in text
    assert "22/tcp" not in text


def test_smb_checklist_detects_microsoft_ds():
    text = templates.render_smb_checklist(_sample_services())
    assert "192.0.2.10 445/tcp" in text
    assert "[ ] List shares" in text


def test_ssh_checklist_detects_ssh():
    text = templates.render_ssh_checklist(_sample_services())
    assert "192.0.2.10 22/tcp" in text


def test_render_report_has_sections_and_table():
    text = templates.render_report("bluebox", _sample_services())
    assert "LAB REPORT - bluebox" in text
    for heading in ("TARGET SUMMARY", "SERVICES FOUND", "INTERESTING FINDINGS",
                    "METHODOLOGY NOTES", "LESSONS LEARNED", "APPENDIX"):
        assert heading in text
    assert "192.0.2.10  80/tcp   http" in text
