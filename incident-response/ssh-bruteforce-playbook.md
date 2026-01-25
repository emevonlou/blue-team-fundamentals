# SSH Brute Force Incident – Mini Playbook

## Detection
- Multiple failed SSH login attempts
- Repeated authentication failures from the same IP

## Containment
- Temporarily block the source IP
- Verify affected user accounts

## Eradication
- Enforce key-based authentication
- Disable password authentication if possible

## Recovery
- Monitor logs for recurring attempts
- Review SSH configuration

## Lessons Learned
- Importance of monitoring authentication logs
- Value of early detection
