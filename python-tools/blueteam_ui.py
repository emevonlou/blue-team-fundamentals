#!/usr/bin/env python3
import json
import shutil
import subprocess

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Footer, Header, RichLog, Static


def blueteam_path() -> str:
    return shutil.which("blueteam") or "blueteam"


def run_cmd(cmd: list[str]):
    try:
        p = subprocess.run(cmd, text=True, capture_output=True)
        return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()
    except Exception as e:
        return 99, "", str(e)


class StatusPanel(Static):
    def set_status(self, data):
        if not data:
            self.update("No status available yet. Run the security routine first.")
            return

        status = data.get("status", "UNKNOWN")
        ts = data.get("timestamp", "N/A")
        rc = data.get("runner_rc", "N/A")

        dash_ok = data.get("dashboard_ok", None)
        if dash_ok is True:
            dash = "OK"
        elif dash_ok is False:
            dash = "FAIL"
        else:
            dash = "N/A"

        self.update(
            f"Status     : {status}\n"
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

    #msg {
        border: round #666;
        padding: 1;
        height: auto;
    }

    #logview {
        border: round #666;
        padding: 1;
        height: 1fr;
        min-height: 10;
    }

    #row1, #row2 {
        height: auto;
    }

    Button { margin: 0 1 0 0; }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Vertical(id="wrap"):
            yield StatusPanel(id="status")

            with Horizontal(id="row1"):
                yield Button("Run now", id="run")
                yield Button("Refresh status", id="refresh")
                yield Button("Open dashboard", id="open_dash")
                yield Button("View service logs", id="logs")

            with Horizontal(id="row2"):
                yield Button("Enable automation", id="enable")
                yield Button("Disable automation", id="disable")

            yield Static(
                "Tip: Click 'View service logs' to load logs below. "
                "If logs are empty, run checks first.",
                id="msg",
            )

            yield RichLog(id="logview")

        yield Footer()

    def on_mount(self):
        self.refresh_status()
        log = self.query_one("#logview", RichLog)
        log.write("BlueTeam UI ready.")
        log.write("Tip: Click 'Run now' to generate reports, then load logs.")

    def refresh_status(self):
        rc, out, err = run_cmd([blueteam_path(), "status", "--json"])

        data = None
        if out:
            try:
                data = json.loads(out)
            except Exception:
                data = None

        self.query_one("#status", StatusPanel).set_status(data)

        if err:
            self.query_one("#msg", Static).update(err)

    def _log_lines(self, title: str, text: str, limit: int = 120):
        log = self.query_one("#logview", RichLog)
        log.write("")
        log.write(title)
        if not text.strip():
            log.write("(no output)")
            return
        for line in text.splitlines()[-limit:]:
            log.write(line)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        bid = event.button.id or ""

        if bid == "run":
            self.query_one("#msg", Static).update("Running security checks. This may take a moment.")
            rc, out, err = run_cmd([blueteam_path(), "run", "--json"])
            self.refresh_status()

            if rc == 0:
                self.query_one("#msg", Static).update("All checks completed successfully. Reports updated.")
            else:
                self.query_one("#msg", Static).update("Critical findings detected. Review dashboard and logs.")

            if out:
                self._log_lines("[run] output (tail)", out, limit=60)
            if err:
                self._log_lines("[run] stderr (tail)", err, limit=60)
            return

        if bid == "refresh":
            self.refresh_status()
            self.query_one("#msg", Static).update("Status refreshed.")
            return

        if bid == "open_dash":
            rc, out, err = run_cmd([blueteam_path(), "dashboard"])
            self.query_one("#msg", Static).update(
                "Dashboard opened." if rc == 0 else "Failed to open dashboard."
            )
            if out:
                self._log_lines("[dashboard] output", out, limit=60)
            if err:
                self._log_lines("[dashboard] stderr", err, limit=60)
            return

        if bid == "logs":
            rc, out, err = run_cmd([blueteam_path(), "logs"])
            self.query_one("#msg", Static).update(
                "Logs loaded below." if rc == 0 else "Could not load logs. See output below."
            )
            self._log_lines("[service logs] journalctl (tail)", out, limit=120)
            if err:
                self._log_lines("[service logs] stderr", err, limit=60)
            return

        if bid == "enable":
            rc, out, err = run_cmd([blueteam_path(), "enable"])
            self.query_one("#msg", Static).update(
                "Daily automation enabled." if rc == 0 else "Failed to enable automation."
            )
            if out:
                self._log_lines("[enable] output", out, limit=60)
            if err:
                self._log_lines("[enable] stderr", err, limit=60)
            return

        if bid == "disable":
            rc, out, err = run_cmd([blueteam_path(), "disable"])
            self.query_one("#msg", Static).update(
                "Daily automation disabled." if rc == 0 else "Failed to disable automation."
            )
            if out:
                self._log_lines("[disable] output", out, limit=60)
            if err:
                self._log_lines("[disable] stderr", err, limit=60)
            return


if __name__ == "__main__":
    BlueTeamUI().run()
