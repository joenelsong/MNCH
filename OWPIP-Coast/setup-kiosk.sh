#!/usr/bin/env bash
# Turn screen blanking off and start the exhibit when the desktop logs in.
# Dependencies are installed separately by ./install-deps.sh.
# Run as the desktop user, not as root:
#   ./setup-kiosk.sh
set -euo pipefail

if [[ "$(id -u)" -eq 0 ]]; then
    echo "Run this as the desktop user, without sudo:"
    echo "  ./setup-kiosk.sh"
    exit 1
fi

APP_DIR="$(cd "$(dirname "$0")" && pwd)"
USER_NAME="$(id -un)"
START="${APP_DIR}/start_owpip.sh"
AUTOSTART="${HOME}/.config/labwc/autostart"

if [[ ! -f "${START}" ]]; then
    echo "Missing ${START}"
    exit 1
fi
chmod +x "${START}"

echo "=== OWPIP Coast screen blanking and autostart ==="
echo "User: ${USER_NAME}"
echo "Home: ${HOME}"
echo "App:  ${START}"
echo

echo "Creating the log file..."
sudo touch /var/log/owpip.log
sudo chmod 666 /var/log/owpip.log

echo "Writing ${AUTOSTART}..."
mkdir -p "${HOME}/.config/labwc"
touch "${AUTOSTART}"
sed -i $'s/\r$//' "${AUTOSTART}"
sed -i '/swayidle/d;/start_owpip\.sh/d;/owpip-coast\.py/d' "${AUTOSTART}"
printf '%s &\n' "${START}" >> "${AUTOSTART}"

for system_autostart in /etc/xdg/labwc/autostart /etc/xdg/labwc-greeter/autostart; do
    if [[ -f "${system_autostart}" ]] && grep -q swayidle "${system_autostart}"; then
        echo "Removing screen blanking from ${system_autostart}..."
        sudo sed -i '/swayidle/d' "${system_autostart}"
    fi
done

echo "Turning screen blanking off..."
if ! sudo raspi-config nonint do_blanking 1; then
    echo "raspi-config could not change screen blanking. The swayidle line was still removed."
fi

echo "Setting desktop autologin for ${USER_NAME}..."
if ! sudo raspi-config nonint do_boot_behaviour B4; then
    echo "raspi-config could not set desktop autologin."
fi
if [[ -f /etc/lightdm/lightdm.conf ]]; then
    sudo sed -i -E "s/^#?autologin-user=.*/autologin-user=${USER_NAME}/" /etc/lightdm/lightdm.conf
fi

echo
echo "Autostart file now contains:"
cat "${AUTOSTART}"
echo
echo "Done. Reboot so the exhibit starts with the desktop:"
echo "  sudo reboot"
echo
echo "If it still does not open, read the log:"
echo "  cat /var/log/owpip.log"
