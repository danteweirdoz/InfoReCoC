#!/usr/bin/env python

################################################################################
# Automation Toolkit for Clash of Clans by InfoRe Inc., Viet Nam
#
# Author: Nguyen Viet Cuong <mrcuongnv@gmail.com>
################################################################################

import sys
import os
import signal
from PIL import Image, ImageDraw

from multiprocessing import Process, Manager
from datetime import datetime
from time import sleep
from ctypes import c_bool, c_byte

from twisted.web.server import Site, NOT_DONE_YET
from twisted.web.resource import Resource
from twisted.internet import reactor
from twisted.web.util import redirectTo
from twisted.internet.task import deferLater

from jinja2 import Environment, PackageLoader

from inforetech.adb import ADB
from inforetech.android import AndroidDevice
from inforetech.coc import CoC


HTTP_SERVER_PORT = 8000
SCREENSHOT_TMP_FILE = "/tmp/screenshot.png"


class CoCKeepAlive(Resource):
    def __init__(self, shared, jinja):
        """
        :type shared: multiprocessing.Manager.Namespace
        :type jinja: jinja2.Environment
        """
        Resource.__init__(self)
        self.shared = shared
        self.jinja = jinja

    def render_GET(self, request):
        """
        :type request: twisted.web.http.Request
        """
        tpl = self.jinja.get_template("coc.html")
        return tpl.render(
            {
                "last_updated": datetime.now(),
                "model": self.shared.model,
                "being_kept_alive": self.shared.keep_alive
            }).encode("utf-8")

    def render_POST(self, request):
        """
        :type request: twisted.web.http.Request
        """
        keep_alive = 0
        if "keep_alive" in request.args:
            keep_alive = int(request.args["keep_alive"][0])
        self.shared.keep_alive = False if keep_alive == 0 else True
        os.kill(os.getppid(), signal.SIGUSR2)
        return redirectTo("coc", request)


class CoCScreenShot(Resource):
    def __init__(self, shared):
        Resource.__init__(self)
        self.shared = shared

    def _send_screenshot(self, request):
        while self.shared.screen_captured == 0:
            sleep(0.25)
        if os.access(SCREENSHOT_TMP_FILE, os.R_OK):
            ss_content = open(SCREENSHOT_TMP_FILE).read()
            os.unlink(SCREENSHOT_TMP_FILE)
            request.setHeader("content-type", "image/png")
            request.setHeader("content-length", len(ss_content))
            request.write(ss_content)
        else:
            request.write("Screen shot bas not been ready yet.")
        request.finish()

    def render_GET(self, request):
        """
        :type request: twisted.web.http.Request
        """
        self.shared.screen_captured = 0
        os.kill(os.getppid(), signal.SIGUSR1)
        d = deferLater(reactor, 0.5, lambda: request)
        d.addCallback(self._send_screenshot)
        return NOT_DONE_YET


def web_server(port, shared):
    """
    A web server for remotely controlling.

    :param port: Web server port
    :param shared: A inter-processes shared namespace.
    """
    jinja = Environment(loader=PackageLoader("keepalive", "template"))

    root = Resource()
    root.putChild("coc", CoCKeepAlive(shared, jinja))
    root.putChild("screenshot", CoCScreenShot(shared))

    site = Site(root)

    reactor.listenTCP(port, site)
    reactor.run()


def sigusr1(signum, stack):
    """
    Trigger the SIGUSR1 to take a screenshot and store it in a temporary file.

    :param signum:
    :param stack:
    """
    im = coc.capture_screen()
    im.thumbnail((640, 480), Image.ANTIALIAS)
    draw = ImageDraw.Draw(im)
    draw.text((0, im.size[1] - 20), str(datetime.now()), (255, 0, 0))
    try:
        im.save(SCREENSHOT_TMP_FILE)
        shared.screen_captured = 1
        print >>sys.stderr, datetime.now(), "Screen captured to %s!" % SCREENSHOT_TMP_FILE
    except Exception as e:
        shared.screen_captured = 2
        print >>sys.stderr, datetime.now(), "Error: %s" % str(e)


def sigusr2(signnum, stack):
    """
    Trigger SIGUSR2 to check the keep-alive status.

    :param signnum:
    :param stack:
    """
    pass


def main():
    global coc, shared

    if len(sys.argv) < 2:
        print "Syntax: %s <Keep-alive interval> [host:[port]] [http port]"
        return 1
    keep_alive_interval = int(sys.argv[1])
    host = None
    port = None
    if len(sys.argv) > 2:
        info = sys.argv[2].split(":")
        host = info[0]
        if len(info) > 1:
            port = int(info[1])

    http_server_port = int(sys.argv[3]) if len(sys.argv) > 3 else HTTP_SERVER_PORT

    coc = CoC(AndroidDevice(ADB("/usr/local/bin/adb"),
                            host, port))
    manager = Manager()
    shared = manager.Namespace()
    shared.keep_alive = manager.Value(c_bool, True)
    shared.screen_captured = manager.Value(c_byte, 0)
    shared.model = coc.model

    httpd = Process(name="WebServer:%d" % http_server_port,
                    target=web_server,
                    args=(http_server_port, shared,))
    httpd.start()
    print "HTTP Server started on port %d (PID: %d)" % (http_server_port, httpd.pid)

    signal.signal(signal.SIGUSR1, sigusr1)
    signal.signal(signal.SIGUSR2, sigusr2)
    try:
        coc.keep_alive(keep_alive_interval, shared)
    except KeyboardInterrupt:
        print "Interrupted."
    finally:
        if httpd is not None:
            print "Terminate the web server..."
            httpd.terminate()


if __name__ == "__main__":
    sys.exit(main())
