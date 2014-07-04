#!/usr/bin/env python

from inforetech.adb import ADB
from inforetech.android import AndroidDevice
from inforetect.coc import CoC


def main():
    if len(sys.argv) < 2:
        print "Syntax: %s <Keep-alive interval> [host:[port]]"
        return 1
    keep_alive_interval = int(sys.argv[1])
    host = None
    port = None
    if len(sys.argv) > 2:
        info = sys.argv[2].split(":")
        host = info[0]
        if len(info) > 1:
            port = int(info[1])

    coc = CoC(AndroidDevice(ADB("/usr/local/bin/adb"),
                            host, port))
    coc.run()
    try:
        coc.keep_alive(keep_alive_interval)
    except KeyboardInterrupt:
        print "Terminated."


if __name__ == "__main__":
    sys.exit(main())
