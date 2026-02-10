#!/usr/bin/env python3
import json
import os
import subprocess
import shutil

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Button, Static
from textual.containers import Vertical, Horizontal


def run_cmd(cmd):
    p = subprocess.run(cmd, text=True, capture_output=True)
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


def blueteam_path():
    return shutil.which("blueteam") or "blueteam"


class StatusPanel(Static):
    def set_status(self, data):
        if not data:
            self.update("No status available yet. Run the security routine first.")
            return

        status = data.get("status", "UNKNOWN")
        ts = data.get("timestamp", "N/A")
        rc = data.get("runner_rc", "N/A")
        dash = data.get("dashboard_status", "N/A")

        self.update(
            f"Status     : {status}\n"
            f"Timestamp  : {ts}\n"
            f"Runner RC  : {rc}\n"
            f"Dashboard  : {dash}"
        )


class BlueTeamUI(App):
    CSS = """
    Screen {
        padding: 1;
    }

    #wrap {
        height: auto;
    }

    #status {
        border: round #666;
        padding: 1;
    }

    #msg {
        border: round #666;
        padding: 1;
        height: auto;
    }

    Button {
        margin: 0 1 0 0;
    }
    """

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Vertical(id="wrap"):
            yield StatusPanel(id="status")

            with Horizontal():
                yield Button("Run now", id="run")
                yield Button("Refresh status", id="refresh")
                yield Button("Open dashboard", id="open_dash")
                yield Button("View service logs", id="logs")

            yield Static(
                "Use this interface to run checks and inspect results without memorizing commands.",
                id="msg"
            )

        yield Footer()

    def on_mount(self):
        self.refresh_status()

    def refresh_status(self):
        rc, out, err = run_cmd([blueteam_path(), "status", "--json"])

        data = None
        if rc == 0 and out:
            try:
                data = json.loads(out)
            except Exception:
                data = None

        self.query_one(StatusPanel).set_status(data)

        if err:
            self.query_one("#msg", Static).update(err)

    def on_button_pressed(self, event: Button.Pressed):
        bid = event.button.id

        if bid == "refresh":
            self.refresh_status()
            self.query_one("#msg", Static).update("Status refreshed.")
            return

        if bid == "run":
            self.query_one("#msg", Static).update(
                "Running security checks. This may take a moment."
            )

            rc, out, err = run_cmd([blueteam_path(), "run", "--json"])

            if rc == 0 and out:
                try:
                    data = json.loads(out)
                    self.query_one(StatusPanel).set_status(data)
                    self.query_one(
                        "#msg", Static
                    ).update("Run completed. Reports were updated.")
                except Exception:
                    self.query_one(
                        "#msg", Static
                    ).update("Run completed, but output could not be parsed.")
            else:
                self.query_one(
                    "#msg", Static
                ).update(err or "Run failed.")

            return

        if bid == "open_dash":
            dash_path = os.path.abspath(
                os.path.join(os.getcwd(), "reports", "dashboard_auth.html")
            )
            opener = shutil.which("xdg-open")

            if opener and os.path.exists(dash_path):
                subprocess.run([opener, dash_path], check=False)
                self.query_one(
                    "#msg", Static
                ).update("Opening dashboard in browser.")
            else:
                self.query_one(
                    "#msg", Static
                ).update("Dashboard not found. Run checks first.")

            return

        if bid == "logs":
            rc, out, err = run_cmd(
                ["journalctl", "--user", "-u", "blue-team.service", "-n", "80", "--no-pager"]
            )

            if out:
                self.query_one(
                    "#msg", Static
                ).update(out[-800:] if len(out) > 800 else out)
            else:
                self.query_one(
                    "#msg", Static
                ).update(err or "No logs available yet.")

            return


if __name__ == "__main__":
    BlueTeamUI().run()
