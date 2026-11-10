# OWPIP Coast — initial setup

Follow this on a new Raspberry Pi. The project path below is the usual one:

```text
/home/pi/Desktop/OWPIP-Coast
```

If the folder is somewhere else, use that path in every command.

## 1. Install

From the project directory:

```bash
cd /home/pi/Desktop/OWPIP-Coast
chmod +x install-deps.sh start_owpip.sh
./install-deps.sh
```

The script installs `python3-wxgtk4.0` and `mpv`, then prints `wxPython OK`.

`start_owpip.sh` in this folder should be:

```bash
#!/bin/bash
cd "$(dirname "$0")" || exit 1
LOG=/var/log/owpip.log
if ! touch "$LOG" 2>/dev/null; then
    LOG="$HOME/owpip.log"
fi
echo "###############" >> "$LOG"
date >> "$LOG"
exec python3 owpip-coast.py >> "$LOG" 2>&1
```

## 2. Run it once by hand

```bash
cd /home/pi/Desktop/OWPIP-Coast
python3 owpip-coast.py
```

Escape quits. On the Pi it opens fullscreen.

## 3. Keep the monitor on

Run this from a terminal on the desktop, not over SSH:

```text
sudo raspi-config
Display Options → Screen Blanking → No
```

Or, on the desktop: Control Centre → Display → Screen Blanking off. Reboot if it asks.

Current Raspberry Pi OS uses the labwc desktop. Blanking is a line in `~/.config/labwc/autostart` that starts with `swayidle`. After blanking is off, that line should be gone. If the screen still sleeps, delete any `swayidle` line from that file and reboot.

Older images that still boot to the X desktop (LightDM):

```bash
sudo nano /etc/lightdm/lightdm.conf
```

Set:

```text
xserver-command=X -s 0 -dpms
```

Then reboot.

## 4. Log in automatically

The exhibit starts after the desktop session starts, so the Pi has to log in by itself:

```text
sudo raspi-config
System Options → Boot / Auto Login → Desktop Autologin
```

## 5. Start the exhibit at login

```bash
chmod +x /home/pi/Desktop/OWPIP-Coast/start_owpip.sh
sudo touch /var/log/owpip.log
sudo chmod 666 /var/log/owpip.log
mkdir -p ~/.config/labwc
nano ~/.config/labwc/autostart
```

Add this line. The `&` at the end is required:

```bash
/home/pi/Desktop/OWPIP-Coast/start_owpip.sh &
```

Logs go to `/var/log/owpip.log` when that file is writable, otherwise to `/home/pi/owpip.log`.

X11 / LXDE (older Pi OS). Add this line to `~/.config/lxsession/LXDE-pi/autostart`:

```text
@/home/pi/Desktop/OWPIP-Coast/start_owpip.sh
```

Reboot. The exhibit should open after the desktop appears.

## 6. Optional

Log rotation:

```bash
sudo nano /etc/logrotate.d/owpip
```

```text
/var/log/owpip.log {
  rotate 12
  monthly
  compress
  missingok
  notifempty
  create 666 pi pi
}
```

Daily reboot at 3:00:

```bash
sudo nano /etc/crontab
```

```text
0 3 * * * root reboot
```
