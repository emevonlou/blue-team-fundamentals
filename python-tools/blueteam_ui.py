#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
from datetime import datetime

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Header, Static, RichLog


CONFIG_FILE = os.path.join(os.path.expanduser("~"), ".config", "blueteam", "config.json")


def blueteam_path() -> str:
    return shutil.which("blueteam") or "blueteam"


def run_cmd(cmd: list[str]):
    """Run a command and capture stdout/stderr safely."""
    try:
        p = subprocess.run(cmd, text=True, capture_output=True)
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except Exception as e:
        return 99, "", str(e)


def load_repo_root() -> str:
    """Read repo_root from config, fallback to dev mode."""
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        rr = data.get("repo_root")
        if rr and os.path.isdir(rr):
            return rr
    except Exception:
        pass
    # dev fallback (python-tools/..)
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


REPO_ROOT = load_repo_root()
REPORTS_DIR = os.path.join(REPO_ROOT, "reports")
HISTORY_DIR = os.path.join(REPORTS_DIR, "history")
LAST_RUN = os.path.join(REPORTS_DIR, "last_run.json")


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

    #status {
        border: round #666;
        padding: 1;
        height: auto;
    }

    Horizontal { height: auto; }

    #msg {
        border: round #666;
        padding: 1;
        height: auto;
    }

    #logview {
        border: round #666;
        padding: 1;
        height: 18;
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

            with Horizontal(id="controls2"):
                yield Button("Toggle live logs", id="logs")
                yield Button("Show history", id="history")
                yield Button("Enable automation", id="enable")
                yield Button("Disable automation", id="disable")

            yield Static(
                "Tip: Run checks first. Toggle live logs to see recent service activity + last run output.",
                id="msg",
            )
            yield RichLog(id="logview")

    def on_mount(self) -> None:
        self._log_timer = None
        self.refresh_status()
        self.set_interval(5, self.refresh_status)

        log = self.query_one("#logview", RichLog)
        log.write(f"[ui] BlueTeam UI ready ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
        log.write("[ui] Tip: Click 'Run now' then 'Toggle live logs'.")

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

    def _read_last_run(self) -> dict:
        try:
            with open(LAST_RUN, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def start_log_stream(self) -> None:
        if self._log_timer:
            return
        self.refresh_logs()
        self._log_timer = self.set_interval(2, self.refresh_logs)

    def stop_log_stream(self) -> None:
        if self._log_timer:
            self._log_timer.stop()
        self._log_timer = None

    def refresh_logs(self) -> None:
        log = self.query_one("#logview", RichLog)
        log.clear()

        log.write("[live] journalctl --user -u blue-team.service (tail)")
        rc, out, err = run_cmd(
            ["journalctl", "--user", "-u", "blue-team.service", "--no-pager", "-n", "80"]
        )
        log.write(f"[live] rc={rc}")
        if out.strip():
            for line in out.splitlines()[-80:]:
                log.write(line)
        else:
            log.write("(no service logs found)")
            log.write("Tip: run 'blueteam run' or 'systemctl --user start blue-team.service'")

        if err.strip():
            log.write("")
            log.write("[journalctl stderr]")
            for line in err.splitlines()[-20:]:
                log.write(line)

        data = self._read_last_run()
        stdout_tail = (data.get("stdout_tail") or "").strip()
        stderr_tail = (data.get("stderr_tail") or "").strip()

        log.write("")
        log.write("[last_run.json] stdout_tail")
        if stdout_tail:
            for line in stdout_tail.splitlines()[-40:]:
                log.write(line)
        else:
            log.write("(empty)")

        log.write("")
        log.write("[last_run.json] stderr_tail")
        if stderr_tail:
            for line in stderr_tail.splitlines()[-40:]:
                log.write(line)
        else:
            log.write("(empty)")

    def show_history(self) -> None:
        log = self.query_one("#logview", RichLog)
        log.clear()
        log.write("[history] Recent runs (reports/history)")

        if not os.path.isdir(HISTORY_DIR):
            log.write("(history dir not found)")
            log.write(f"Expected: {HISTORY_DIR}")
            return

        files = sorted(os.listdir(HISTORY_DIR), reverse=True)
        files = [f for f in files if f.endswith(".json")]

        if not files:
            log.write("(no history files yet)")
            return

        for filename in files[:10]:
            path = os.path.join(HISTORY_DIR, filename)
            try:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                ts = data.get("timestamp", filename.replace(".json", ""))
                status = data.get("status", "UNKNOWN")
                rc = data.get("runner_rc", "N/A")
                dash_ok = data.get("dashboard_ok", None)
                dash = "OK" if dash_ok is True else "FAIL" if dash_ok is False else "N/A"
                log.write(f"{ts} | status={status} rc={rc} dash={dash}")
            except Exception as e:
                log.write(f"{filename} | ERROR: {e}")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""

        if bid == "run":
            self.query_one("#msg", Static).update("Running checks... (this may take a moment)")
            rc, _, _ = run_cmd([blueteam_path(), "run", "--json"])
            self.refresh_status()
            if rc == 0:
                self.query_one("#msg", Static).update("OK: checks completed. Reports updated.")
            elif rc == 2:
                self.query_one("#msg", Static).update("WARN: checks completed with findings. Review dashboard/logs.")
            else:
                self.query_one("#msg", Static).update("CRIT: errors or critical findings. Review dashboard/logs.")
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

        if bid == "history":
            self.show_history()
            self.query_one("#msg", Static).update("Showing last runs (history).")
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
