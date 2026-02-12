#!/usr/bin/env python3
import json
import shutil
import subprocess

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, RichLog, Header, Static


def blueteam_path() -> str:
    return shutil.which("blueteam") or "blueteam"


def run_cmd(cmd: list[str]):
    try:
        p = subprocess.run(cmd, text=True, capture_output=True)
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except Exception as e:
        return 99, "", str(e)


class StatusPanel(Static):
    def _risk_bar(self, status: str) -> str:
        if status == "OK":
            filled, label = 10, "LOW"
        elif status == "WARN":
            filled, label = 6, "MEDIUM"
        else:
            filled, label = 2, "HIGH"
        return f"[{'█' * filled}{'░' * (10 - filled)}] {label}"

    def set_status(self, data):
        if not data:
            self.remove_class("ok", "warn", "crit")
            self.update("No status available yet. Run the security routine first.")
            return

        status = data.get("status", "UNKNOWN")
        ts = data.get("timestamp", "N/A")
        rc = data.get("runner_rc", "N/A")

        dash_ok = data.get("dashboard_ok", None)
        dash = "OK" if dash_ok is True else "FAIL" if dash_ok is False else "N/A"

        self.remove_class("ok", "warn", "crit")
        if status == "OK":
            self.add_class("ok")
        elif status == "WARN":
            self.add_class("warn")
        else:
            self.add_class("crit")

        risk = self._risk_bar(status)

        self.update(
            f"Status     : {status}\n"
            f"Risk       : {risk}\n"
            f"Timestamp  : {ts}\n"
            f"Runner RC  : {rc}\n"
            f"Dashboard  : {dash}"
        )


class BlueTeamUI(App):
    CSS = """
    Screen { padding: 1; }

    #wrap { height: 100%; }

    #status {
        border: round #666;
        padding: 1;
        height: auto;
    }

    #controls1, #controls2 {
        height: auto;
    }

    #msg {
        border: round #666;
        padding: 1;
        height: auto;
    }

    #logview {
        border: round #666;
        padding: 1;
        height: 1fr;
        min-height: 12;
    }

    Button { margin: 0 1 0 0; }

    #status.ok { color: green; }
    #status.warn { color: yellow; }
    #status.crit { color: red; }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Vertical(id="wrap"):
            yield StatusPanel(id="status")

            with Horizontal(id="controls1"):
                yield Button("Run now", id="run")
                yield Button("Refresh status", id="refresh")
                yield Button("Open dashboard", id="open_dash")
                yield Button("View service logs", id="logs")

            with Horizontal(id="controls2"):
                yield Button("Enable automation", id="enable")
                yield Button("Disable automation", id="disable")

            yield Static("Tip: Click 'View service logs' to toggle live updates.", id="msg")
            yield RichLog(id="logview")

    def on_mount(self) -> None:
        self._log_timer = None
        self.refresh_status()
        self.set_interval(3, self.refresh_status)

        log = self.query_one("#logview", RichLog)
        log.write("BlueTeam UI ready.")
        log.write("Tip: Run checks, then toggle logs.")

    def refresh_status(self) -> None:
        rc, out, err = run_cmd([blueteam_path(), "status", "--json"])

        data = None
        if rc == 0 and out.strip():
            try:
                data = json.loads(out)
            except Exception:
                data = None

        self.query_one("#status", StatusPanel).set_status(data)

        if err.strip():
            self.query_one("#msg", Static).update(err)

    def _read_last_run_tails(self):
        rc, out, _ = run_cmd([blueteam_path(), "status", "--json"])
        if rc != 0 or not out.strip():
            return "", ""
        try:
            data = json.loads(out)
        except Exception:
            return "", ""
        return (data.get("stdout_tail", "") or ""), (data.get("stderr_tail", "") or "")

    def start_log_stream(self):
        if self._log_timer:
            return
        self.refresh_logs()
        self._log_timer = self.set_interval(2, self.refresh_logs)

    def stop_log_stream(self):
        if self._log_timer:
            self._log_timer.stop()
        self._log_timer = None

    def refresh_logs(self):
        log = self.query_one("#logview", RichLog)
        log.clear()

        # Always show something (debug marker)
        log.write("[ui] refresh_logs tick")

        # 1) systemd user service logs (captured here, not via blueteam logs)
        cmd = ["journalctl", "--user", "-u", "blue-team.service", "--no-pager", "-n", "120"]
        rc, out, err = run_cmd(cmd)

        log.write("")
        log.write(f"[blue-team.service] journalctl rc={rc}")

        if out.strip():
            for line in out.splitlines()[-120:]:
                log.write(line)
        else:
            log.write("(no service logs found)")
            log.write("Tip: run `systemctl --user start blue-team.service` to generate logs.")

        if err.strip():
            log.write("")
            log.write("[journalctl stderr]")
            for line in err.splitlines()[-40:]:
                log.write(line)

        # 2) last run tails (activity even when journal is quiet)
        stdout_tail, stderr_tail = self._read_last_run_tails()

        log.write("")
        log.write("[last run stdout tail]")
        if stdout_tail.strip():
            for line in stdout_tail.splitlines()[-80:]:
                log.write(line)
        else:
            log.write("(empty)")

        log.write("")
        log.write("[last run stderr tail]")
        if stderr_tail.strip():
            for line in stderr_tail.splitlines()[-80:]:
                log.write(line)
        else:
            log.write("(empty)")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""

        if bid == "run":
            self.query_one("#msg", Static).update("Running checks...")
            rc, _, _ = run_cmd([blueteam_path(), "run", "--json"])
            self.refresh_status()

            if rc == 0:
                self.query_one("#msg", Static).update("Checks passed.")
            elif rc == 2:
                self.query_one("#msg", Static).update("Warnings detected.")
            else:
                self.query_one("#msg", Static).update("Critical findings detected.")
            return

        if bid == "refresh":
            self.refresh_status()
            self.query_one("#msg", Static).update("Status refreshed.")
            return

        if bid == "open_dash":
            rc, _, _ = run_cmd([blueteam_path(), "dashboard"])
            self.query_one("#msg", Static).update("Dashboard opened." if rc == 0 else "Failed to open dashboard.")
            return

        if bid == "logs":
            if self._log_timer:
                self.stop_log_stream()
                self.query_one("#msg", Static).update("Live logs stopped.")
            else:
                self.start_log_stream()
                self.query_one("#msg", Static).update("Live logs started (updates every 2s).")
            return

        if bid == "enable":
            rc, _, _ = run_cmd([blueteam_path(), "enable"])
            self.query_one("#msg", Static).update("Automation enabled." if rc == 0 else "Failed to enable automation.")
            return

        if bid == "disable":
            rc, _, _ = run_cmd([blueteam_path(), "disable"])
            self.query_one("#msg", Static).update("Automation disabled." if rc == 0 else "Failed to disable automation.")
            return


if __name__ == "__main__":
    BlueTeamUI().run()
