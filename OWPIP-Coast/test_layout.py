"""Layout math for the 1600x900 exhibit canvas."""
import importlib.util
import os
import unittest

ROOT = os.path.dirname(os.path.abspath(__file__))


def load_app():
    spec = importlib.util.spec_from_file_location(
        'owpip_coast', os.path.join(ROOT, 'owpip-coast.py')
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FitCanvasTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = load_app()

    def test_native_canvas_fills_exactly(self):
        fit = self.app.fit_canvas((1600, 900), (1600, 900))
        self.assertEqual((fit.x, fit.y, fit.width, fit.height), (0, 0, 1600, 900))
        self.assertEqual(fit.scale, 1)

    def test_1080p_fills_the_screen(self):
        # 1920x1080 is the same 16:9 shape as the art, so there is no matte.
        fit = self.app.fit_canvas((1600, 900), (1920, 1080))
        self.assertEqual((fit.x, fit.y, fit.width, fit.height), (0, 0, 1920, 1080))

    def test_720p_fills_the_screen(self):
        fit = self.app.fit_canvas((1600, 900), (1280, 720))
        self.assertEqual((fit.x, fit.y, fit.width, fit.height), (0, 0, 1280, 720))

    def test_taller_screen_centers_vertical_matte(self):
        fit = self.app.fit_canvas((1600, 900), (1920, 1243))
        self.assertEqual(fit.width, 1920)
        self.assertEqual(fit.height, 1080)
        self.assertEqual(fit.x, 0)
        self.assertEqual(fit.y, (1243 - 1080) // 2)

    def test_ultrawide_centers_side_matte(self):
        # 5120x1440 is 32:9. The exhibit stays 16:9 and uses the full height.
        fit = self.app.fit_canvas((1600, 900), (5120, 1440))
        self.assertEqual((fit.x, fit.y, fit.width, fit.height), (1280, 0, 2560, 1440))
        self.assertEqual(fit.scale, 1.6)

    def test_video_window_tracks_the_canvas(self):
        app = self.app
        app.canvas_fit = app.fit_canvas(app.DESIGN_SIZE, (1920, 1080))
        left, top, right, bottom = app.video_bounds()
        self.assertEqual(left, int(round(1 * 1.2)))
        self.assertEqual(top, int(round(95 * 1.2)))
        self.assertEqual(right - left, int(round(1102 * 1.2)) - int(round(1 * 1.2)))
        self.assertEqual(bottom - top, int(round(715 * 1.2)) - int(round(95 * 1.2)))


class PanelLayoutTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.appmod = load_app()
        import wx

        cls.wx = wx
        cls._wxapp = wx.App(False)
        os.chdir(ROOT)

    def test_home_buttons_scale_with_the_background(self):
        wx = self.wx
        frame = wx.Frame(None, size=(1920, 1080))
        frame.fullscreen = False
        panel = self.appmod.MainPanel(
            frame, './images/pages/HomePage.png', 'main', (1600, 900)
        )
        fit = self.appmod.fit_canvas((1600, 900), (1920, 1080))
        panel.SetSize((1920, 1080))
        panel.apply_layout(fit)

        self.assertEqual(panel.scaled_bg.GetSize(), (1920, 1080))
        positions = {b['widget'].GetName(): b['widget'].GetRect() for b in panel.buttons}
        self.assertEqual(positions['Diorama'], wx.Rect(0, 0, 960, 540))
        self.assertEqual(positions['Video'], wx.Rect(960, 0, 960, 540))
        self.assertEqual(positions['Archaeology'], wx.Rect(0, 540, 960, 540))
        self.assertEqual(positions['GoSeeIt'], wx.Rect(960, 540, 960, 540))
        frame.Destroy()


if __name__ == '__main__':
    unittest.main()
