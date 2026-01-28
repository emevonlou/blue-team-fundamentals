# Incident Simulation — File Integrity Alert

## Summary
During routine execution of the daily security report, file integrity
violations were detected by the integrity monitoring mechanism.

This event was part of a controlled learning environment and represents
a simulated integrity incident.

## Detection
The alert was triggered by the `file_integrity_check.sh` script, which
compares current file hashes against a protected baseline database.

The following message was observed:

sha256sum: WARNING: computed checksums did NOT match

This indicates that monitored files were modified since the baseline
was created.

## Affected Assets
- System configuration files under `/etc`
- Integrity database: `integrity_db.sha256`

## Root Cause (Expected)
Legitimate system changes such as:
- Package updates
- Service configuration updates
- Normal system maintenance

No malicious activity was identified.

## Response
- Alert was reviewed
- Modified files were identified
- No unauthorized changes were found
- No remediation was required

## Lessons Learned
- File integrity monitoring is effective for detecting changes
- Not all integrity alerts indicate malicious behavior
- Context and validation are critical before response

## Status
Closed — informational alert

