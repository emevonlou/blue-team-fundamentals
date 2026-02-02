# Blue Team Fundamentals

**Installable agent:** CLI + systemd automation  
**Use case:** Daily Linux Blue Team routine with reports and dashboard

**Status:** Operational
**Latest release:** v1.0.3 Product Packaging & Installer

This repository demonstrates foundational Blue Team practices focused on
system monitoring, log analysis, and defensive security automation.

## Project Goals
- Practice real-world Blue Team techniques
- Build security monitoring scripts used in SOC environments
- Demonstrate secure scripting and operational awareness

## Quick Start

Run the full daily security routine:

```bash
cd scripts-blue-team
./run_all_security.sh

## Dashboard Preview
![Dashboard preview](assets/dashboard_preview.png)

## Repository Structure

- `scripts-blue-team/` — Bash scripts for monitoring + checks  
- `python-tools/` — Dashboard + analysis tooling  
- `docs/` — Documentation, incident sims, notes  
- `reports/` — Generated reports (not tracked)

## Key Features
- SSH failed login monitoring
- File integrity checking with whitelist + exit codes
- Service health checks
- Daily master report generation
- Dashboard (PNG + HTML)

## Security Considerations
- Minimal privilege: sudo restricted to required scripts
- Reports are local and not tracked
- Fail-fast behavior to avoid silent errors

## Disclaimer
This project is for educational and portfolio purposes only.



