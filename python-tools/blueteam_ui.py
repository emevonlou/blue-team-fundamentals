#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
from pathlib import Path

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Header, RichLog, Static


def blueteam_path() -> str:
    return shutil.which("blueteam") or "blueteam"


def run_cmd(cmd: list[str]):
    """Run a command and capture stdout/stderr safely."""
    try:
        p = subprocess.run(cmd, text=True, capture_output=True)
        return p.returncode, (p.stdout or ""), (p.stderr or "")
    except Exception as e:
        return 99, "", str(e)


def load_repo_root() -> str:
    """Try to read repo_root from ~/.config/blueteam/config.json, fallback to repo-relative."""
    cfg = Path.home() / ".config" / "blueteam" / "config.json"
    try:
        data = json.loads(cfg.read_text(encoding="utf-8"))
        rr = data.get("repo_root")
        if rr and Path(rr).is_dir():
            return rr
    except Exception:
        pass
    # fallback: assume we're running inside the repo
    return str(Path(__file__).resolve().parents[1])


class StatusPanel(Static):
    def _risk_bar(self, status: str) -> str:
        # 10 blocks total
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
            self.update("No status yet. Run checks first.")
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
    # remove the bottom-right "^p palette"
    ENABLE_COMMAND_PALETTE = False

    CSS = """
    Screen { padding: 1; }

    #wrap { height: 100%; width: 100%; }

    #status {
        border: round #666;
        padding: 1;
        height: auto;
        width: 100%;
    }

    #controls1, #controls2 {
        height: auto;
        width: 100%;
    }

    /* This prevents the giant gap between button rows */
    #controls1 { margin-bottom: 0; }
    #controls2 { margin-top: 0; }

    Button { margin: 0 1 0 0; }

    #msg {
        border: round #666;
        padding: 1;
        height: auto;
        width: 100%;
    }

    #logview {
        border: round #666;
        padding: 1;
        height: 1fr;
        min-height: 12;
        width: 100%;
    }

    #status.ok { color: green; }
    #status.warn { color: yellow; }
    #status.crit { color: red; }
    """

    def __init__(self):
        super().__init__()
        self.repo_root = load_repo_root()
        self.reports_dir = os.path.join(self.repo_root, "reports")
        self.history_dir = os.path.join(self.reports_dir, "history")
        self._log_timer = None

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

            yield Static("Tip: Run checks first. Then toggle live logs or show history.", id="msg")
            yield RichLog(id="logview", auto_scroll=True)

    def on_mount(self) -> None:
        self.refresh_status()
        self.set_interval(3, self.refresh_status)

        log = self.query_one("#logview", RichLog)
        log.write("BlueTeam UI ready.")
        log.write(f"repo_root: {self.repo_root}")
        log.write("Tip: Toggle live logs to stream journalctl + last_run.json tails.")

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
            self.query_one("#msg", Static).update(err.strip())

    def _read_status_json(self) -> dict | None:
        rc, out, _ = run_cmd([blueteam_path(), "status", "--json"])
        if rc != 0 or not out.strip():
            return None
        try:
            return json.loads(out)
        except Exception:
            return None

    def _log_block(self, title: str, body: str, max_lines: int = 120) -> None:
        log = self.query_one("#logview", RichLog)
        log.write("")
        log.write(title)
        if not body.strip():
            log.write("(empty)")
            return
        for line in body.splitlines()[-max_lines:]:
            log.write(line.rstrip("\n"))

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
        log.write("[live] updating every 2s...")

        # 1) journalctl (systemd user service)
        rc, out, err = run_cmd(
            ["journalctl", "--user", "-u", "blue-team.service", "--no-pager", "-n", "80"]
        )
        self._log_block(f"[journalctl] blue-team.service (rc={rc})", out, max_lines=80)
        if err.strip():
            self._log_block("[journalctl stderr]", err, max_lines=40)

        # 2) last_run.json tails (always helpful)
        data = self._read_status_json() or {}
        stdout_tail = (data.get("stdout_tail") or "").strip()
        stderr_tail = (data.get("stderr_tail") or "").strip()
        self._log_block("[last_run.json] stdout_tail", stdout_tail, max_lines=80)
        self._log_block("[last_run.json] stderr_tail", stderr_tail, max_lines=80)

    def show_history(self) -> None:
        log = self.query_one("#logview", RichLog)
        log.clear()
        log.write("[history] recent runs")

        os.makedirs(self.history_dir, exist_ok=True)
        files = sorted(Path(self.history_dir).glob("*.json"), reverse=True)

        if not files:
            log.write("(no history yet)")
            log.write("Tip: run 'blueteam run' a few times to generate history entries.")
            return

        shown = 0
        for fp in files[:15]:
            try:
                data = json.loads(fp.read_text(encoding="utf-8"))
                ts = data.get("timestamp", fp.stem)
                st = data.get("status", "UNKNOWN")
                rc = data.get("runner_rc", "?")
                log.write(f"{ts} | {st} | rc={rc}")
                shown += 1
            except Exception as e:
                log.write(f"{fp.name} | ERROR: {e}")

        log.write("")
        log.write(f"(showing {shown} most recent files in {self.history_dir})")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""

        if bid == "run":
            self.query_one("#msg", Static).update("Running checks...")
            rc, _, _ = run_cmd([blueteam_path(), "run", "--json"])
            self.refresh_status()
            if rc == 0:
                self.query_one("#msg", Static).update("Checks passed. (OK)")
            elif rc == 2:
                self.query_one("#msg", Static).update("Warnings detected. (WARN)")
            else:
                self.query_one("#msg", Static).update("Critical findings detected. (CRIT)")
            # after running, show logs once
            self.refresh_logs()
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
            self.stop_log_stream()
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
