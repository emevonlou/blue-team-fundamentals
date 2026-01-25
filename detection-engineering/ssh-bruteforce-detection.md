# SSH Brute Force Detection

## Technique
**MITRE ATT&CK:** T1110 – Brute Force

## Data Sources
- Linux authentication logs
- SSH service logs

## Detection Logic
- Multiple failed SSH login attempts
- Same source IP within a short time window

## False Positives
- Misconfigured scripts
- Legitimate users mistyping passwords

## Response
- Correlate with firewall logs
- Trigger incident response playbook
