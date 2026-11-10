# Oregon Where Past Is Present — Coast Touchscreen

Touchscreen exhibit original code created by Fazil (github: pafazil).
Updated by Neoteric Web Solutions LLC (joenelsong@gmail.com)

## Dependencies

| What | Purpose | How to install |
|------|---------|----------------|
| **Python 3.9+** | Runtime | Preinstalled on Raspberry Pi OS and macOS |
| **wxPython 4.2+** | Touchscreen UI | See install steps below |
| **mpv** | Video playback on Pi (Bookworm+) | `sudo apt install mpv` (included by install script) |

Everything else uses the Python standard library.

## Install on a new system

From this directory (`OWPIP-Coast/`):

```bash
chmod +x install-deps.sh
./install-deps.sh
```

That script picks the right method automatically:

- **Raspberry Pi OS** — installs `python3-wxgtk4.0` and `mpv` via apt (avoids broken pip wheels on ARM).
- **macOS / other** — runs `pip install .` using [`pyproject.toml`](pyproject.toml).

### Manual install

**Raspberry Pi OS (Bookworm or similar):**

```bash
sudo apt update
sudo apt install python3-wxgtk4.0 mpv
python3 -c "import wx; print(wx.version())"
```

**macOS (development):**

```bash
python3 -m pip install .
python3 owpip-coast.py --windowed
```

**Linux with pip only** (may compile wxPython from source; allow 30+ minutes):

```bash
sudo apt install libgtk-3-dev libpng-dev libjpeg-dev libtiff-dev   # Debian/Ubuntu
python3 -m pip install .
```

## Run

```bash
cd OWPIP-Coast
python3 owpip-coast.py              # fullscreen on Pi/Linux (kiosk default)
python3 owpip-coast.py --windowed   # windowed (default on macOS)
```

Or use the startup script on the Pi:

```bash
./start_owpip.sh
```

## Pi kiosk notes

On a new Pi, run `./install-deps.sh`, then `./setup-kiosk.sh` for screen blanking and autostart. The steps are in [`initial-setup.md`](initial-setup.md).
