#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
USER_SYSTEMD_DIR="${HOME}/.config/systemd/user"
LOCAL_BIN="${HOME}/.local/bin"

echo "[*] Installing Blue Team product files..."
mkdir -p "${USER_SYSTEMD_DIR}"
mkdir -p "${LOCAL_BIN}"

# Copy systemd units
cp -f "${REPO_ROOT}/product/systemd/blue-team.service" "${USER_SYSTEMD_DIR}/blue-team.service"
cp -f "${REPO_ROOT}/product/systemd/blue-team.timer"   "${USER_SYSTEMD_DIR}/blue-team.timer"

# Install CLI wrapper to ~/.local/bin
cp -f "${REPO_ROOT}/product/blueteam" "${LOCAL_BIN}/blueteam"
chmod +x "${LOCAL_BIN}/blueteam"

echo "[*] Reloading systemd user units..."
systemctl --user daemon-reload

echo ""
echo "[OK] Installed!"
echo ""
echo "Next steps:"
echo "  1) Ensure ~/.local/bin is in PATH:"
echo "     echo \$PATH | grep -q \"${HOME}/.local/bin\" || echo 'Add ~/.local/bin to PATH'"
echo ""
echo "  2) Enable daily automation:"
echo "     blueteam enable"
echo ""
echo "  3) Run now:"
echo "     blueteam run"
echo ""
echo "  4) View logs:"
echo "     blueteam logs"
echo ""
echo "IMPORTANT (sudo):"
echo "  If the routine uses sudo inside scripts, systemd runs without a TTY."
echo "  Use a restricted sudoers rule to allow ONLY the required scripts."
echo "  (You already configured this manually; keep it tight.)"
