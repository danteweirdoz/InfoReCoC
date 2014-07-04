from PIL import Image
from cStringIO import StringIO as cStringIO

from inforetech.adb import ADB
from inforetech.android import AndroidDevice
from inforetech.coc import CoC


def test():
    coc = CoC(AndroidDevice(ADB("/usr/local/bin/adb"),
                            "192.168.56.101",
                            5555))
    coc.run()
    im = coc.capture_screen()
    im.show()


if __name__ == "__main__":
    test()
