#!/usr/bin/env python

import sys

from inforetech.adb import ADB
from inforetech.android import AndroidDevice
from inforetech.coc import CoC


def main():
    coc = CoC(AndroidDevice(ADB("/usr/local/bin/adb"),
                            "192.168.56.101",
                            5555))
    coc.run()
    im = coc.capture_screen()
    if len(sys.argv) > 1:
        im.save(sys.argv[1])
    else:
        im.show()


if __name__ == "__main__":
    sys.exit(main())
