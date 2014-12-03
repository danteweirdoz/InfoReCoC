# InfoRe COC - Automation Toolkit for Clash of Clans

*By InfoRe Inc., Viet Nam*

## Introduction

This tool aims to provide a remotely controlled automation system for Clash of Clans. The currently supported running environment is Linux due to some limitation of inter-process communication on Windows. This tool is written in Python.

A sample configuration should contains,

* Some virtual Android machines for running Clash of Clans.
* A virtual Linux machine for running InfoReCoC with at least a network interface which is located in the same network segment with above Android machines.
* A executable version of ADB toolkit (`adb` only), which should be defaultly located at `/usr/local/bin`.

## How to Run

To run an auto for a virtual Android machine, use the following syntax:

```bash
python keepalive.py <Keep-alive interval> [host:[port]] [http port]
```

in which,

* `Keep-alive interval` is number of seconds between server notification of alive, which may be 60 for example.
* `host:port` is the IP or host name and the connection port of the virtual Android machine, such as
192.168.56.101:5555.
* `http port` is the port of the web server to be used for remotely controlling the InfoReCoC.

A practical sample is as follow.

```bash
python keepalive.py 60 192.168.56.101:5555 8001
```

After that, you can access the following things via a web browser.

* Controller interface: http://<IP>:8001/coc
* Screenshot: http://<IP>:8001/screenshot

in which, **IP** is the IP address of the virtual Linux machine.

*I will update this guide later if I have free time*
