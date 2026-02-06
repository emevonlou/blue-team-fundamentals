# Changelog

All notable changes to this project are documented in this file.

This project follows semantic versioning and focuses on
operational Blue Team workflows, automation, and signal over noise.

---

## v1.0.3 — Product Packaging & Installer

- Introduced installable CLI (`blueteam`)
- Added product installer script
- Added systemd user service and timer for daily automation
- Implemented persistent run status tracking
- Improved README with product-focused Quick Start
- Added dashboard preview image
- Minor documentation fixes and polish
- 
### Added
- Product installer (`product/install.sh`)
- Systemd user service unit template
- Product quickstart documentation

### Notes
- CLI reads repo_root from `~/.config/blueteam/config.json`
- Reports remain local in `reports/`

---

## v1.0.2 — Automation & Dashboard

- Added daily automation via systemd
- Implemented authentication dashboard (HTML + PNG)
- Added trend analysis and severity indicators
- Introduced master daily security report
- Improved auth log parsing and CSV summaries
- Reduced noise in file integrity monitoring

---

## v1.0.1 — Hardening Update

- Added integrity whitelist for common system files
- Improved file integrity change detection logic
- Added clearer severity signaling (OK / WARN / CRIT)
- Refined reporting output and structure

---

## v1.0.0 — Initial Release

- Initial Blue Team monitoring scripts
- File integrity check
- SSH authentication log monitoring
- Service health checks
