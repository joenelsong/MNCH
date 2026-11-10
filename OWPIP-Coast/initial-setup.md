# OWPIP Coast — initial setup

On the Pi, as the `mnch` user, from the project directory.

Install dependencies. This also creates `/var/log/owpip.log`, owned by `mnch`, and the log rotation rule:

```bash
cd /home/mnch/Desktop/OWPIP-Coast
chmod +x install-deps.sh
./install-deps.sh
```

A line that starts with `##### log ready` means the log file is writable. The exhibit appends to that same file when it starts.

Turn screen blanking off and start the exhibit at login:

```bash
chmod +x setup-kiosk.sh
./setup-kiosk.sh
sudo reboot
```

Do not run `setup-kiosk.sh` with `sudo`. It asks for your password when it needs root.

On Raspberry Pi OS 11 (Bullseye) the script adds the exhibit to `~/.config/lxsession/LXDE-pi/autostart` and sets `xserver-command=X -s 0 -dpms` so the monitor stays on. Newer Pi OS uses `~/.config/autostart/owpip-coast.desktop` instead. It also turns on desktop autologin for `mnch`.

After reboot the exhibit should open on its own. Escape quits it.

In `/var/log/owpip.log`, a line that says `log ready` is from the installer. A row of `#` characters means `start_owpip.sh` ran. If the exhibit does not open, read the log:

```bash
cat /var/log/owpip.log
```

To try it once without rebooting:

```bash
python3 owpip-coast.py
```
