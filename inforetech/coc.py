import sys
import time
from PIL import Image
from cStringIO import StringIO as cStringIO

from adb import ADB
from android import AndroidDevice


class CoC(object):
    PACKAGE_NAME = "com.supercell.clashofclans"
    MAIN_ACTIVITY = "GameApp"

    def __init__(self, android_device):
        self.dev = android_device

    def run(self):
        self.dev.unlock_screen()
        regions = self.dev.get_visible_regions(CoC.PACKAGE_NAME, CoC.MAIN_ACTIVITY)
        if len(regions) == 0:
            self.dev.run_application(CoC.PACKAGE_NAME, CoC.MAIN_ACTIVITY)
            time.sleep(5)
            while len(regions) == 0:
                time.sleep(1)
                regions = self.dev.get_visible_regions(CoC.PACKAGE_NAME, CoC.MAIN_ACTIVITY)

        for r in regions:
            print r
            if r[0] == 0 and r[1] == 0 and r[2] > r[0] and r[3] > r[1]:
                self.region = r
                self.left = r[0]
                self.top = r[1]
                self.right = r[2]
                self.bottom = r[3]
                break

    def quit(self):
        self.dev.press_home()

    def capture_screen(self):
        im = Image.open(cStringIO(self.dev.screencap()))
        return im.rotate(90).crop(self.region)

    def keep_alive(self, interval):
        from datetime import datetime
        while True:
            x = (self.right - self.left) / 2
            y = (self.bottom - self.top) * 3 / 4
            self.dev.tap(x, y)
            print >>sys.stderr, datetime.now(), "Tapped at (%d, %d)" % (x, y)
            time.sleep(interval)


def test():
    coc = CoC(AndroidDevice(ADB("/usr/local/bin/adb"),
                            "192.168.56.101",
                            5555))
    coc.run()
    #im = coc.capture_screen()
    #im.show()
    #coc.quit()
    coc.keep_alive()


if __name__ == "__main__":
    test()
