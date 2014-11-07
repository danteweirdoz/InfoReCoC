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
        self.model = android_device.get_model()
        self.region = None

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
                break

    def quit(self):
        self.dev.press_home()

    def capture_screen(self):
        """
        :rtype : PIL.Image.Image
        """
        im = Image.open(cStringIO(self.dev.screencap()))
        return im.rotate(90).crop(self.region)

    def keep_alive(self, interval, shared):
        from datetime import datetime
        while True:
            print >>sys.stderr, datetime.now()
            if shared.keep_alive:
                regions = self.dev.get_visible_regions(CoC.PACKAGE_NAME, CoC.MAIN_ACTIVITY)
                print >>sys.stderr, "\tRegions: %d (%s)" % (len(regions), ", ".join([str(r) for r in regions]))
                if len(regions) == 0:
                    print >>sys.stderr, "\tForce running Game..."
                    self.run()
                    continue
                elif len(regions) == 1:
                    # The game window only
                    r = regions[0]
                    x = abs((r[2] - r[0]) / 2)
                    y = abs((r[3] - r[1]) * 3 / 4)
                    self.dev.tap(x, y)
                    print >>sys.stderr, "\tTapped on Game at (%d, %d)" % (x, y)
                elif len(regions) == 2:
                    # There is a message window
                    r = regions[1]
                    x = abs((r[2] - r[0]) / 2)
                    y = max(r[3] - 20, r[1] + 20)
                    self.dev.tap(x, y)
                    print >>sys.stderr, "\tTapped on Notification at (%d, %d)" % (x, y)
                if self.region is None and len(regions) > 0:
                    self.region = regions[0]
            else:
                print >>sys.stderr, "\tKeep rest"

            # Sleep
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
