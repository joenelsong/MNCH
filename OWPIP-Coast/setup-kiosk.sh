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
LABWC_AUTOSTART="${HOME}/.config/labwc/autostart"
DESKTOP_AUTOSTART="${HOME}/.config/autostart/owpip-coast.desktop"

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

VERSION_CODENAME=""
if [[ -f /etc/os-release ]]; then
    # shellcheck disable=SC1091
    . /etc/os-release
fi

setup_bullseye() {
    local session_dir="${HOME}/.config/lxsession/LXDE-pi"
    local session_file="${session_dir}/autostart"
    local system_file="/etc/xdg/lxsession/LXDE-pi/autostart"

    echo "Bullseye desktop: writing ${session_file}"
    mkdir -p "${session_dir}"
    # The user file replaces the system one, so keep the desktop lines.
    if [[ -f "${system_file}" ]]; then
        if [[ ! -f "${session_file}" ]] || ! grep -q lxpanel "${session_file}"; then
            cp "${system_file}" "${session_file}"
        fi
    fi
    touch "${session_file}"
    sed -i $'s/\r$//' "${session_file}"
    sed -i '/xscreensaver/d;/start_owpip\.sh/d;/owpip-coast\.py/d' "${session_file}"
    printf '@%s\n' "${START}" >> "${session_file}"
    rm -f "${DESKTOP_AUTOSTART}"

    echo "Turning screen blanking off in LightDM..."
    if [[ -f /etc/lightdm/lightdm.conf ]]; then
        if grep -qE '^#?xserver-command=' /etc/lightdm/lightdm.conf; then
            sudo sed -i -E 's/^#?xserver-command=.*/xserver-command=X -s 0 -dpms/' /etc/lightdm/lightdm.conf
        else
            sudo sed -i '/^\[Seat:\*\]/a xserver-command=X -s 0 -dpms' /etc/lightdm/lightdm.conf
        fi
    fi

    echo
    echo "Session autostart file:"
    cat "${session_file}"
}

setup_labwc() {
    echo "Writing ${DESKTOP_AUTOSTART}..."
    mkdir -p "${HOME}/.config/autostart"
    cat > "${DESKTOP_AUTOSTART}" <<EOF
[Desktop Entry]
Type=Application
Name=OWPIP Coast
Comment=Start the touchscreen exhibit at login
Exec=${START}
Path=${APP_DIR}
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

    if [[ -f "${LABWC_AUTOSTART}" ]]; then
        sed -i $'s/\r$//' "${LABWC_AUTOSTART}"
        sed -i '/swayidle/d;/start_owpip\.sh/d;/owpip-coast\.py/d' "${LABWC_AUTOSTART}"
    fi

    for system_autostart in /etc/xdg/labwc/autostart /etc/xdg/labwc-greeter/autostart; do
        if [[ -f "${system_autostart}" ]] && grep -q swayidle "${system_autostart}"; then
            echo "Removing screen blanking from ${system_autostart}..."
            sudo sed -i '/swayidle/d' "${system_autostart}"
        fi
    done

    echo
    echo "Login autostart file:"
    cat "${DESKTOP_AUTOSTART}"
}

if [[ "${VERSION_CODENAME:-}" == "bullseye" ]]; then
    setup_bullseye
else
    setup_labwc
fi

echo "Turning screen blanking off..."
if ! sudo raspi-config nonint do_blanking 1; then
    echo "raspi-config could not change screen blanking."
fi

echo "Setting desktop autologin for ${USER_NAME}..."
if ! sudo raspi-config nonint do_boot_behaviour B4; then
    echo "raspi-config could not set desktop autologin."
fi
if [[ -f /etc/lightdm/lightdm.conf ]]; then
    sudo sed -i -E "s/^#?autologin-user=.*/autologin-user=${USER_NAME}/" /etc/lightdm/lightdm.conf
fi

echo
echo "Done. Reboot so the exhibit starts with the desktop:"
echo "  sudo reboot"
echo
echo "A startup run adds a row of # characters to /var/log/owpip.log."
echo "The 'log ready' line is only from install-deps.sh."
