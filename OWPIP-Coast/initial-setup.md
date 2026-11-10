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

That script turns screen blanking off, turns on desktop autologin for `mnch`, and puts this line in `~/.config/labwc/autostart`:

```bash
/home/mnch/Desktop/OWPIP-Coast/start_owpip.sh &
```

After reboot the exhibit should open on its own. Escape quits it.

If it does not open, read both logs. An empty `/var/log/owpip.log` means startup wrote to the home file instead:

```bash
cat /var/log/owpip.log
cat /home/mnch/owpip.log
```

To try it once without rebooting:

```bash
python3 owpip-coast.py
```
