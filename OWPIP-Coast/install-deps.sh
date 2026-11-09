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

if [[ "$(uname -s)" == "Linux" ]] && command -v apt-get >/dev/null; then
    if apt-cache show python3-wxgtk4.0 >/dev/null 2>&1; then
        install_pi_packages
    else
        echo "python3-wxgtk4.0 not in apt; falling back to pip."
        install_pip_packages
    fi
else
    install_pip_packages
fi

echo
python3 -c "import wx; print('wxPython OK:', wx.version())"
echo
echo "Done. Run the exhibit with:"
echo "  python3 owpip-coast.py"
