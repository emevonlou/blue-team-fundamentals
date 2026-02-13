# Blue Team Fundamentals

[![CI](https://github.com/emevonlou/blue-team-fundamentals/actions/workflows/ci.yml/badge.svg)](https://github.com/emevonlou/blue-team-fundamentals/actions/workflows/ci.yml)

**Installable agent:** CLI + systemd automation  
**Use case:** Daily Linux Blue Team routine with reports and dashboard  
**Status:** Operational  
**Latest release:** v1.0.3 — Product Packaging & Installer  

---

## Overview

Blue Team Fundamentals is a Linux-focused defensive security project that implements a daily operational Blue Team routine.

It combines:

- File integrity monitoring  
- Authentication log analysis  
- Service health checks  
- Automated reporting  
- Local visual dashboard  

All packaged as an installable agent with CLI interface and systemd automation.

This project reflects real SOC workflows with emphasis on:

- Signal over noise  
- Least privilege  
- Operational clarity  

---

## Key Features

- File Integrity Monitoring (FIM) with whitelist and exit codes  
- SSH authentication log monitoring with severity classification  
- Critical service health checks  
- Daily master security report generation  
- Local dashboard (HTML + PNG) with trends and severity levels  
- Installable CLI (`blueteam`)  
- Automation via systemd user service + timer  
- Minimal-privilege sudo configuration  

---

## Quick Start

### Run manually

```bash
blueteam run

## Enable automation

blueteam enable

## Check status

blueteam status

## Terminal UI

- If you prefer a visual interface directly in the terminal:

blueteam ui

## Manual Execution (Development Mode)

cd scripts-blue-team
./run_all_security.sh

## Install via RPM (Fedora)

-Download the GPG-signed RPM from GitHub Releases.

sudo rpm --import docs/blueteam-rpm-publickey.asc

## Install package

sudo dnf install ./blueteam-fundamentals-1.0.3-1.fc40.noarch.rpm

## Enable Daily Automation

systemctl --user enable --now blue-team.timer
systemctl --user list-timers | grep blue-team

## Dashboard Preview

assets/dashboard_preview.png
