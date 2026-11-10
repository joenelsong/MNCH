#!/usr/bin/env bash
# Install everything needed to run owpip-coast.py on a fresh machine.
set -euo pipefail

cd "$(dirname "$0")"

echo "=== OWPIP Coast — dependency install ==="
echo "Python: $(python3 --version 2>&1)"
echo "Platform: $(uname -s) $(uname -m)"
echo

install_pi_packages() {
    echo "Using apt (recommended on Raspberry Pi OS)..."
    sudo apt-get update
    sudo apt-get install -y python3-wxgtk4.0 mpv
}

install_pip_packages() {
    echo "Using pip (macOS and non-Pi Linux)..."
    python3 -m pip install --upgrade pip
    python3 -m pip install .
}

setup_log() {
    local log_user="${SUDO_USER:-$(id -un)}"
    if [[ "${log_user}" == "root" ]]; then
        log_user="$(id -un)"
    fi
    echo "Setting up /var/log/owpip.log for ${log_user}..."
    sudo touch /var/log/owpip.log
    sudo chown "${log_user}:${log_user}" /var/log/owpip.log
    sudo chmod 644 /var/log/owpip.log
    echo "##### log ready $(date) user=${log_user}" >> /var/log/owpip.log
    sudo tee /etc/logrotate.d/owpip >/dev/null <<EOF
/var/log/owpip.log {
  rotate 12
  monthly
  compress
  missingok
  notifempty
  create 644 ${log_user} ${log_user}
}
EOF
}

if [[ "$(uname -s)" == "Linux" ]] && command -v apt-get >/dev/null; then
    if apt-cache show python3-wxgtk4.0 >/dev/null 2>&1; then
        install_pi_packages
    else
        echo "python3-wxgtk4.0 not in apt; falling back to pip."
        install_pip_packages
    fi
    setup_log
else
    install_pip_packages
fi

echo
python3 -c "import wx; print('wxPython OK:', wx.version())"
echo
echo "Done. Run the exhibit with:"
echo "  python3 owpip-coast.py"
