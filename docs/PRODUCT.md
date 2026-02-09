# BlueTeam Product Guide

This guide documents installation, daily operation, and troubleshooting for the
**Blue Team Fundamentals** agent (`blueteam`).

---

## Install (RPM / Fedora)

1) Download the **signed** RPM from GitHub Releases.

2) Import the public key and verify the RPM:

```bash
sudo rpm --import docs/blueteam-rpm-publickey.asc
rpm -Kv blueteam-fundamentals-1.0.3-1.fc40.noarch.rpm
```

3. Install 

```bash
sudo dnf install ./blueteam-fundamentals-1.0.3-1.fc40.noarch.rpm
```

## Commands

- Run the full security routine once:

```bash
blueteam run
```

- Check the last execution status:

```bash
blueteam status
```

- Enable daily automation using a systemd user timer:

```bash
systemctl --user enable --now blue-team.timer
systemctl --user list-timers | grep blue-team
```
- View logs:

```bash
blueteam logs
journalctl --user -u blue-team.service -n 100 --no-pager
```

## systemd (user) operations

- Check service and timer state:

```bash
systemctl --user status blue-team.service
systemctl --user status blue-team.timer
```

- Manually trigger the service:

```bash
systemctl --user start blue-team.service
```

- Reload unit files after updates:

```bash
systemctl --user daemon-reload
```

## Output files

- Reports and dashboards are written locally under the reports/ directory:

Text reports (*.txt)

CSV summaries (*.csv)

JSON status file (last_run.json)

HTML dashboard (dashboard_auth.html)

PNG charts (auth_failed_attempts_trend.png)

These files are runtime artifacts and should not be committed to the repository.


## Troubleshooting

1) “sudo: a terminal is required” when running via systemd

Systemd user services run without a TTY.
If a script requires sudo, it must be allowed via a restricted sudoers rule
for that specific script only.

Avoid blanket NOPASSWD rules.

2) Dashboard fails due to missing Python dependencies

- If you see:

ModuleNotFoundError: No module named 'matplotlib'

- Install the dependency:

```bash
sudo dnf install -y python3-matplotlib
```

3) Timer runs but no output is generated

- Check logs:

```bash
journalctl --user -u blue-team.service --no-pager -n 200
```

- Confirm the timer is enabled:

```bash
systemctl --user list-timers | grep blue-team
```

4) RPM signature verification fails

- Ensure the public key is imported before verification:

```bash
sudo rpm --import docs/blueteam-rpm-publickey.asc
rpm -Kv blueteam-fundamentals-1.0.3-1.fc40.noarch.rpm
```

