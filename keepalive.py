#!/usr/bin/env python

import sys
import os
import platform
import signal

from multiprocessing import Process, Manager

from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor

from jinja2 import Environment, PackageLoader

from inforetech.adb import ADB
from inforetech.android import AndroidDevice
from inforetech.coc import CoC


HTTP_SERVER_PORT = 8000


class CoCResource(Resource):
    def __init__(self, shared_keep_alive, jinja):
        Resource.__init__(self)
        self.shared_keep_alive = shared_keep_alive
        self.jinja = jinja

    def render_GET(self, request):
        tpl = self.jinja.get_template("coc.html")
        return tpl.render(
            {
                "hostname": platform.node().split(".")[0],
                "being_kept_alive": self.shared_keep_alive.value
            }).encode("utf-8")

    def render_POST(self, request):
        keep_alive = 0
        if request.args.has_key("keep_alive"):
            keep_alive = int(request.args["keep_alive"][0])
        self.shared_keep_alive.value = False if keep_alive == 0 else True
        os.kill(os.getppid(), signal.SIGCONT)
        return self.render_GET(request)


def web_server(port, shared_keep_alive):
    jinja = Environment(loader=PackageLoader("keepalive", "template"))
    coc_page = CoCResource(shared_keep_alive, jinja)
    root = Resource()
    root.putChild("coc", coc_page)
    site = Site(root)
    reactor.listenTCP(port, site)
    reactor.run()


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
    manager = Manager()
    shared_keep_alive = manager.Value("keep_alive", True)

    httpd = Process(target=web_server, args=(HTTP_SERVER_PORT, shared_keep_alive,))
    httpd.start()
    print "HTTP Server started on port %d" % HTTP_SERVER_PORT

    try:
        coc.keep_alive(keep_alive_interval, shared_keep_alive)
    except KeyboardInterrupt:
        print "Terminated."
    finally:
        if httpd is not None:
            httpd.terminate()


if __name__ == "__main__":
    sys.exit(main())
