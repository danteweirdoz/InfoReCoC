from inforetech.adb import ADB
from inforetech.android import AndroidDevice


def test():
    coc = CoC(AndroidDevice(ADB("/usr/local/bin/adb"),
                            "192.168.56.101",
                            5555))
    coc.run()
    coc.keep_alive()


if __name__ == "__main__":
    test()
