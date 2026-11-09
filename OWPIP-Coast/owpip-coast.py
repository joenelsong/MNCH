#!/usr/bin/env python3
import argparse
import os
import platform
import shutil
import subprocess
import sys
from collections import namedtuple

# external dependencies
import wx

VIDEO_PATH = os.path.join('images', 'Coquille.mp4')
# Exhibit art and button coordinates are authored at this size.
DESIGN_SIZE = (1600, 900)
# Video rectangle in design pixels: x1, y1, x2, y2.
VIDEO_RECT = (1, 95, 1102, 715)

CanvasFit = namedtuple('CanvasFit', ['x', 'y', 'width', 'height', 'scale'])
# Updated whenever the window size changes. Video playback reads it.
canvas_fit = None


def fit_canvas(design, client):
    """Largest 16:9 (design-shaped) rect that fits inside the client, centered.

    Returns a CanvasFit. The leftover area is a matte, not a stretched image.
    A 1920x1080 screen matches the art exactly, so the matte is empty.
    """
    dw, dh = design
    cw, ch = client
    if cw <= 0 or ch <= 0 or dw <= 0 or dh <= 0:
        return CanvasFit(0, 0, max(cw, 0), max(ch, 0), 1.0)
    scale = min(cw / float(dw), ch / float(dh))
    width = min(cw, int(round(dw * scale)))
    height = min(ch, int(round(dh * scale)))
    return CanvasFit((cw - width) // 2, (ch - height) // 2, width, height, scale)


def map_design_point(pos, fit):
    return (
        int(round(pos[0] * fit.scale)) + fit.x,
        int(round(pos[1] * fit.scale)) + fit.y,
    )


def video_bounds():
    """Video window in screen pixels for the current canvas fit."""
    fit = canvas_fit if canvas_fit is not None else fit_canvas(DESIGN_SIZE, DESIGN_SIZE)
    x1, y1, x2, y2 = VIDEO_RECT
    left, top = map_design_point((x1, y1), fit)
    right, bottom = map_design_point((x2, y2), fit)
    return left, top, right, bottom


def scaled_bitmap(bitmap, width, height):
    width = max(1, int(round(width)))
    height = max(1, int(round(height)))
    if bitmap.GetWidth() == width and bitmap.GetHeight() == height:
        return bitmap
    image = bitmap.ConvertToImage().Scale(width, height, wx.IMAGE_QUALITY_HIGH)
    return wx.Bitmap(image)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description='OWPIP Coast touchscreen exhibit')
    parser.add_argument(
        '--fullscreen',
        action='store_true',
        help='Run fullscreen (kiosk). Default on Raspberry Pi / Linux.',
    )
    parser.add_argument(
        '--windowed',
        action='store_true',
        help='Run in a normal window. Default on macOS for development.',
    )
    args = parser.parse_args(argv)
    if args.fullscreen and args.windowed:
        parser.error('Use only one of --fullscreen or --windowed')
    if args.windowed:
        fullscreen = False
    elif args.fullscreen:
        fullscreen = True
    else:
        # Pi exhibit defaults to fullscreen; Mac development defaults to a window.
        fullscreen = platform.system() != 'Darwin'
    return fullscreen


def _which(cmd):
    return shutil.which(cmd)


def video_is_playing():
    """True if the exhibit video player appears to be running."""
    if _which('omxplayer') or os.path.isfile('/usr/bin/omxplayer'):
        return (
            subprocess.run(
                ['pgrep', '-x', 'omxplayer'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).returncode
            == 0
        )
    if platform.system() == 'Darwin':
        # `open` launches QuickTime (or the default .mp4 handler).
        return (
            subprocess.run(
                ['pgrep', '-xq', 'QuickTime Player'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).returncode
            == 0
        )
    for name in ('mpv', 'ffplay', 'vlc'):
        if (
            subprocess.run(
                ['pgrep', '-x', name],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).returncode
            == 0
        ):
            return True
    return False


def stop_video():
    """Stop any video started by this app (best-effort)."""
    if _which('omxplayer') or os.path.isfile('/usr/bin/omxplayer'):
        subprocess.run(
            ['pkill', 'omxplayer'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    if platform.system() == 'Darwin':
        subprocess.run(
            ['pkill', '-x', 'QuickTime Player'],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    for name in ('mpv', 'ffplay', 'vlc'):
        subprocess.run(
            ['pkill', '-x', name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


def start_video():
    """
    Play the exhibit video with the best available player.
    Pi kiosk: omxplayer. macOS: open (QuickTime). Else: mpv/ffplay/xdg-open.
    """
    video = os.path.abspath(VIDEO_PATH)
    if not os.path.isfile(video):
        print('video file missing:', video)
        return

    left, top, right, bottom = video_bounds()
    width = max(1, right - left)
    height = max(1, bottom - top)
    omx = _which('omxplayer') or (
        '/usr/bin/omxplayer' if os.path.isfile('/usr/bin/omxplayer') else None
    )
    if omx:
        subprocess.Popen(
            [omx, '--win', '%d %d %d %d' % (left, top, right, bottom), '-o', 'local', video],
        )
        print('playing video (omxplayer)')
        return

    if platform.system() == 'Darwin':
        # Opens in the default macOS player (usually QuickTime).
        subprocess.Popen(['open', video])
        print('playing video (open)')
        return

    for player, args in (
        ('mpv', ['--geometry=%dx%d+%d+%d' % (width, height, left, top), video]),
        ('ffplay', ['-window_title', 'OWPIP', '-autoexit', video]),
        ('xdg-open', [video]),
    ):
        path = _which(player)
        if path:
            subprocess.Popen([path] + args)
            print('playing video (%s)' % player)
            return

    print('no video player found (install omxplayer on Pi, or mpv/ffplay)')


class LabelViewerPanel(wx.Panel):
    '''Class to create panel on the frame'''

    def __init__(self, parent, image, name, panel_size):
        wx.Panel.__init__(self, parent, size=panel_size)
        self.frame = parent
        self.name = name
        self.Bind(wx.EVT_CHAR, self.on_keypress)
        self.cursor = wx.Cursor(wx.CURSOR_BLANK)
        self.SetBackgroundColour(wx.BLACK)
        self.widgets = []
        self.buttons = []
        self.design_image = wx.Bitmap(image)
        self.scaled_bg = self.design_image
        self.fit = fit_canvas(DESIGN_SIZE, panel_size)

        # Uncomment the following line on wxpython 2.x
        # self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.Bind(wx.EVT_ERASE_BACKGROUND, self.draw_image)

    def hide_cursor(self):
        # Keep the system cursor visible in windowed/dev mode.
        if not self.frame.fullscreen:
            return
        for widget in self.widgets:
            widget.SetCursor(self.cursor)

    def on_keypress(self, event):
        keycode = event.GetKeyCode()
        if keycode == wx.WXK_ESCAPE:
            self.frame.close()

    def draw_image(self, event):
        """ Draws the fitted exhibit image. Leftover area stays black. """
        dc = event.GetDC()
        if not dc:
            dc = wx.ClientDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRegion(rect)
        dc.SetBackground(wx.Brush(wx.BLACK))
        dc.Clear()
        if self.scaled_bg and self.scaled_bg.IsOk():
            dc.DrawBitmap(self.scaled_bg, self.fit.x, self.fit.y, True)
        self.SetFocus()

    def apply_layout(self, fit):
        """Scale the background and buttons from design pixels into fit."""
        self.fit = fit
        self.SetBackgroundColour(wx.BLACK)
        self.scaled_bg = scaled_bitmap(self.design_image, fit.width, fit.height)
        for button in self.buttons:
            source = button['bitmap']
            button['widget'].SetBitmap(
                scaled_bitmap(
                    source,
                    source.GetWidth() * fit.scale,
                    source.GetHeight() * fit.scale,
                )
            )
            button['widget'].SetPosition(map_design_point(button['pos'], fit))
        self.Refresh()

    def switch_panel(self, event):
        stop_video()
        self.frame.switch_panel(self.name, event.GetEventObject().GetName())

    def play_video(self, event):
        if video_is_playing():
            print('already playing')
        else:
            start_video()

    def _add_bitmap_button(self, image_path, img_name, position, handler):
        image_path = './images/buttons/' + image_path
        bitmap = wx.Bitmap(image_path, wx.BITMAP_TYPE_PNG)
        widget = wx.StaticBitmap(self, name=img_name, pos=position, bitmap=bitmap)
        widget.Bind(wx.EVT_LEFT_DOWN, handler)
        self.widgets.append(widget)
        self.buttons.append({'widget': widget, 'bitmap': bitmap, 'pos': position})

    def add_button(self, image_path, img_name, position):
        self._add_bitmap_button(image_path, img_name, position, self.switch_panel)

    def play_button(self, image_path, img_name, position):
        self._add_bitmap_button(image_path, img_name, position, self.play_video)


class MainPanel(LabelViewerPanel):
    '''   Main home screen. '''

    def __init__(self, parent, image, name, panel_size):
        LabelViewerPanel.__init__(self, parent, image, name, panel_size)
        self.add_button('HomePage/Archaeology.png', 'Archaeology', (0, 450))
        self.add_button('HomePage/Diorama.png', 'Diorama', (0, 0))
        self.add_button('HomePage/GoSeeIt.png', 'GoSeeIt', (800, 450))
        self.add_button('HomePage/Video.png', 'Video', (800, 0))
        self.hide_cursor()
        self.SetFocus()


class LabelPanel(LabelViewerPanel):
    '''Add Buttons on other screen except Main'''

    def __init__(self, parent, background, name, panel_size, level, back_level):
        LabelViewerPanel.__init__(self, parent, background, name, panel_size)

        if level == 1:
            self.add_button('home.png', 'main', (22, 800))
        elif level == 1.1:
            self.add_button('home.png', 'main', (22, 800))
            self.play_button('play.png', 'Play', (540, 360))
        elif level == 1.2:
            self.add_button('home.png', 'main', (22, 800))
            self.add_button('Diorama/ClamDigger.png', 'ClamDigger', (672, 535))
            self.add_button('Diorama/FishWeir.png', 'FishWeir', (359, 478))
            self.add_button('Diorama/Midden.png', 'Midden', (965, 610))
            self.add_button('Diorama/PlankHouse1.png', 'PlankHouse', (0, 192))
            self.add_button('Diorama/PlankHouse2.png', 'PlankHouse', (0, 462))
            self.add_button('Diorama/Spear.png', 'Spear', (749, 572))
            self.add_button('artist.png', 'Artist', (1362, 800))
        elif level == 1.3:
            self.add_button('home.png', 'main', (22, 800))
            self.add_button('GoSeeIt/Chachalu.png', 'GoSeeItChachalu', (800, 0))
            self.add_button('GoSeeIt/MarineCenter.png', 'GoSeeItMarine', (0, 0))
        elif level == 2:
            self.add_button('home.png', 'main', (22, 800))
            self.add_button('back.png', back_level, (250, 800))
        self.hide_cursor()


class MainFrame(wx.Frame):
    """    Create Background Frame and create panels for each page   """

    def __init__(self, parent, image_size, fullscreen=True):
        wx.Frame.__init__(
            self,
            parent,
            wx.ID_ANY,
            title='OWPIP Coast',
            size=image_size,
        )
        self.design_size = image_size
        self.size = image_size
        self.fullscreen = fullscreen
        self._fit_key = None
        self.panels = []
        self.panel_dict = {}
        self.current_panel = 'main'
        self.SetBackgroundColour(wx.BLACK)

        main_panel = MainPanel(self, './images/pages/HomePage.png', 'main', image_size)
        self.panel_dict['main'] = main_panel

        self.add_panel('Archaeology', 1)
        self.add_panel('Video', 1.1)
        self.add_panel('Diorama', 1.2)
        self.add_panel('GoSeeIt', 1.3)
        self.add_panel('Artist', 2, 'Diorama')
        self.add_panel('ClamDigger', 2, 'Diorama')
        self.add_panel('FishWeir', 2, 'Diorama')
        self.add_panel('Midden', 2, 'Diorama')
        self.add_panel('PlankHouse', 2, 'Diorama')
        self.add_panel('Spear', 2, 'Diorama')
        self.add_panel('GoSeeItChachalu', 2, 'GoSeeIt')
        self.add_panel('GoSeeItMarine', 2, 'GoSeeIt')

        # Timer to switch back to main shelf
        self.timeout = 600000  # 10 min
        self.timeout_timer = wx.Timer(self, wx.ID_ANY)
        self.start_timeout_timer()

        # On macOS, ShowFullScreen alone does not show the window — call Show first.
        # Bind size after the first placement so startup does not scale twice.
        self.Freeze()
        self.Show()
        self.place_on_screen()
        self.fit_panels()
        self.Bind(wx.EVT_SIZE, self.on_size)
        self.Thaw()

    def work_area(self):
        index = wx.Display.GetFromWindow(self)
        if index == wx.NOT_FOUND:
            index = 0
        return wx.Display(index).GetClientArea()

    def place_on_screen(self):
        """Make the frame cover the screen it opened on."""
        if self.fullscreen:
            self.ShowFullScreen(True, style=wx.FULLSCREEN_ALL)
        else:
            self.SetRect(self.work_area())

    def on_size(self, event):
        self.fit_panels()
        event.Skip()

    def fit_panels(self):
        """Scale every page so the 1600x900 art fits this window."""
        global canvas_fit
        if not self.panel_dict:
            return
        size = self.GetClientSize()
        if size.width <= 0 or size.height <= 0:
            return
        key = (size.width, size.height)
        if key == self._fit_key:
            return
        self._fit_key = key
        fit = fit_canvas(self.design_size, key)
        canvas_fit = fit
        print(
            'Fitting %dx%d exhibit into %dx%d window as %dx%d at (%d, %d)'
            % (
                self.design_size[0],
                self.design_size[1],
                key[0],
                key[1],
                fit.width,
                fit.height,
                fit.x,
                fit.y,
            )
        )
        for panel in self.panel_dict.values():
            panel.SetPosition((0, 0))
            panel.SetSize(size)
            panel.apply_layout(fit)

    def add_panel(self, name, level, back_level='None'):
        bg = './images/pages/' + name + '.png'
        panel = LabelPanel(self, bg, name, self.size, level, back_level)
        panel.Hide()
        self.panel_dict[name] = panel

    def switch_panel(self, src_id, dest_id):
        print(src_id + '->' + dest_id)
        self.panel_dict[src_id].Hide()
        self.panel_dict[dest_id].Show()
        self.panel_dict[dest_id].SetFocus()
        self.current_panel = dest_id
        self.Layout()
        self.restart_timeout_timer()

    def start_timeout_timer(self):
        self.Bind(wx.EVT_TIMER, self.switch_on_timeout, self.timeout_timer)
        self.timeout_timer.Start(self.timeout)

    def restart_timeout_timer(self):
        self.timeout_timer.Stop()
        self.start_timeout_timer()

    def switch_on_timeout(self, event):
        self.switch_panel(self.current_panel, 'main')
        self.restart_timeout_timer()

    def close(self):
        self.Destroy()


if __name__ == '__main__':
    # Ensure relative image paths resolve when launched from elsewhere.
    os.chdir(os.path.dirname(os.path.abspath(__file__)) or '.')
    fullscreen = parse_args(sys.argv[1:])
    app = wx.App(False)
    # Art is authored at DESIGN_SIZE. MainFrame scales it to the screen.
    MainFrame(None, DESIGN_SIZE, fullscreen=fullscreen)
    app.MainLoop()
