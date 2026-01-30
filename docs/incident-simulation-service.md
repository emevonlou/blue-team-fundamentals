# Incident Simulation — Service Down (Controlled)

## Summary
A controlled simulation was performed to validate monitoring behavior when a critical service appears down.

## Method
No services were stopped. A simulation flag was used:
- `SIMULATE_DOWN=crond`

## Expected Outcome
- The service health report should show:
  - `crond: NOT RUNNING (SIMULATED)`

## Evidence
- The report file in `reports/` contains the simulated status.

## Response (What a SOC would do)
- Verify actual service status: `systemctl status crond`
- Review recent logs: `journalctl -u crond`
- Restore service if required and investigate root cause

## Status
Closed — simulation validated successfully.
