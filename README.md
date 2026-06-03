# Auto OSCP Recon Notes

A small, local Python CLI that turns reconnaissance output you already produced
into clean, structured plain-text notes for OSCP-style lab practice. It imports
Nmap XML, organizes services, generates enumeration checklists, and exports
`.txt` notes plus a report template.

> **This tool is for authorized learning labs and owned environments only. It does not exploit targets or perform scanning by itself. It organizes recon output that you provide.**

It is built for HTB, TryHackMe, and OSCP practice environments where manual
analysis still matters. The point is repeatable note-taking discipline, not
auto-pwning.

## Why it exists

OSCP-style practice generates a lot of scattered output. This tool gives a
repeatable workflow: one folder per target, parsed service data, per-service
enumeration checklists, and a report template you fill in as you learn. It
connects cybersecurity practice with the clean documentation habits used in
hands-on data center operations.

## Safety scope

**Included (MVP):**

- Import local Nmap XML files.
- Parse ports, protocols, services, products, versions, and NSE script output.
- Generate plain-text `.txt` notes and checklists.
- Generate a sanitized report template.
- Ship safe sample data only, using RFC 5737 documentation IP `192.0.2.10`.

**Deliberately not included:**

- No automatic scanning.
- No exploitation, credential attacks, or brute forcing.
- No stealth, evasion, or bypass features.
- No real target data.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Requires Python 3.11+. No third-party runtime dependencies. The dev extra only
installs `pytest` and `ruff`.

## Quick start

```bash
# 1. Create a target workspace
oscp-notes init bluebox

# 2. Import Nmap XML you produced manually, e.g.
#    nmap -sV -oX scans/bluebox.xml <authorized-lab-target>
oscp-notes import-nmap bluebox scans/bluebox.xml

# 3. Generate service enumeration checklists
oscp-notes checklist bluebox

# 4. Generate the plain-text report
oscp-notes report bluebox

# If report.txt already has manual notes, the command refuses to overwrite it.
# Use --force only when you intentionally want to replace the report template.
oscp-notes report bluebox --force
```

You can try it immediately against the bundled sample scan:

```bash
oscp-notes init /tmp/demo
oscp-notes import-nmap /tmp/demo examples/sample-target/scans/nmap-basic.xml
oscp-notes checklist /tmp/demo
oscp-notes report /tmp/demo
```

## Example output

A workspace looks like this:

```text
bluebox/
├── README.txt
├── recon/
│   ├── nmap-summary.txt
│   └── services.json
├── notes/
│   ├── services.txt
│   ├── web.txt
│   ├── credentials.txt
│   ├── findings.txt
│   └── lessons-learned.txt
├── checklists/
│   ├── enum-checklist.txt
│   ├── http-checklist.txt
│   ├── smb-checklist.txt
│   └── ssh-checklist.txt
└── report.txt
```

`notes/services.txt` excerpt:

```text
SERVICES
========

HOST: 192.0.2.10

SERVICE: 22/tcp - ssh
State: open
Product: OpenSSH
Version: 8.2p1
Notes:
  [ ] Check banner
  [ ] Check supported auth methods
  [ ] Try valid credentials only if discovered through authorized lab workflow
```

A fully rendered sample report lives at [docs/sample-report.txt](docs/sample-report.txt),
and a complete generated workspace is committed under
[examples/sample-target/expected-output/](examples/sample-target/expected-output/).

## Output format

Human-facing notes, checklists, and reports use `.txt`, not `.md`, so they open
cleanly in any terminal, editor, or note-taking app. The generated report avoids
Markdown tables on purpose. `recon/services.json` is internal parsed data for the
tool. This repository `README.md` stays Markdown because GitHub renders it as the
landing page.

## Project status

MVP. The four core commands work, the package ships tests and sample data, and
CI runs the suite on GitHub Actions.

## Roadmap

- **0.2** - import plain-text Nmap output, `ffuf` / `gobuster` import, Obsidian export.
- **0.3** - per-service YAML checklist templates, command log tracking, finding severity labels.
- **1.0** - stable CLI, full docs, CI passing, `pipx` install.

## Skills demonstrated

```text
- Python CLI design with argparse subcommands
- XML parsing with xml.etree.ElementTree
- Plain-text report generation
- OSCP-style enumeration methodology
- Test-driven development with pytest
- Security documentation workflow
```

## Development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest -q
ruff check .
```

## License

MIT, see [LICENSE](LICENSE).
