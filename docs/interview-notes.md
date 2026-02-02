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




