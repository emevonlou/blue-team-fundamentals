# Blue Team Fundamentals

[![CI](https://github.com/emevonlou/blue-team-fundamentals/actions/workflows/ci.yml/badge.svg)](https://github.com/emevonlou/blue-team-fundamentals/actions/workflows/ci.yml)

**Status:** Operational & Product-oriented  
**Latest release:** v1.0.3

Blue Team Fundamentals is a defensive security toolkit for Linux systems.  
It consolidates fundamental monitoring and defensive checks into a unified CLI and interactive terminal UI.

---

## Quick Start

Install your product (RPM):

```bash
sudo dnf install blueteam-fundamentals-1.0.3-1.fc40.noarch.rpm
```
- Verify the package:

```bash
rpm --checksig blueteam-fundamentals-1.0.3-1.fc40.noarch.rpm
```

- After installation, use the CLI:
Run daily checks

```bash
blueteam run
```

- Show current status:

```bash
blueteam status
```

- Launch interactive UI:

```bash
blueteam ui
```

- Automate daily runs:

```bash
blueteam enable
```

### Dashboard Preview

- The dashboard is generated automatically after running.

The HTML report is saved in reports/dashboard_auth.html.

### What’s Inside

- Blue Team Fundamentals includes:

File Integrity Monitoring
Detects unauthorized changes to system files.

Authentication Log Monitoring
Checks for brute-force or unusual login attempts.

Service Health Checks
Verifies essential service activity and logs.

Terminal UI (TUI)
An interactive interface to inspect health, logs, and history.

Historical Run Storage
Saves past statuses in reports/history.

RPM Packaging
Distributable on Fedora-based systems with signed packages.

### Architecture
.
├── docs/                      # Documentation sources
├── product/                  # Packaging + CLI entrypoint
├── python-tools/             # Dashboard + UI implementations
├── scripts-blue-team/        # Security routines
├── assets/                   # Images, previews
├── reports/                  # Generated output (local)
└── README.md                 # This file

### Severity & Exit Codes

To make automation reliable, the runner classifies status using exit codes:

| Exit code | Meaning                       |
| --------: | ----------------------------- |
|         0 | OK — checks completed cleanly |
|         2 | WARN — non-critical findings  |
|        10 | CRIT — critical findings      |

This ensures consistency across CLI, UI, automation, systemd timers, and logs.

### RPM Installation

```bash
sudo dnf install blueteam-fundamentals-*.rpm
```
- If using custom keys:

```bash
rpm --import assets/blueteam-rpm-publickey.asc
```

### License

This project is licensed under the MIT License (see LICENSE for details).

```markdown
## Dashboard Preview

![BlueTeam Dashboard](assets/dashboard_preview.png)





