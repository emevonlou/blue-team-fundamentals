# Interview Notes — Blue Team Fundamentals

## What this project demonstrates
- Defensive automation using Bash (Linux-focused)
- SOC-style monitoring routines
- Log analysis and basic attack detection
- File integrity monitoring with protected baseline
- False-positive reduction using a whitelist
- Reporting (TXT + CSV) and operational consistency
- Incident simulation and documentation mindset

## Key design choices (and why)
- Reports are not tracked in Git to avoid noise and prevent sensitive data exposure
- Root-required scripts are explicit to avoid silent failures
- Whitelists are used to reduce alert fatigue and focus on high-signal events
- CSV summaries enable trend analysis and future dashboards
- A master report provides an executive daily view

## How to explain this project in an interview
This project simulates a daily Blue Team security routine on a Linux system.
It performs integrity checks, authentication log analysis, and service health
verification, generating structured reports for review.

## Example SOC-style statements
- “Not every alert is malicious; I triage events by context.”
- “I focus on reducing false positives without weakening detection.”
- “I validate detections using controlled simulations and document lessons learned.”
