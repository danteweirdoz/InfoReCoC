import os
from subprocess import check_output


class ADB(object):
    def __init__(self, path_to_adb=None):
        self.adb = self.__find_adb(path_to_adb)
        self.url = ""

    # Find the runnable adb
    @staticmethod
    def __find_adb(path_to_adb=None):
        if path_to_adb is not None:
            if os.path.isfile(path_to_adb) and os.access(path_to_adb, os.R_OK | os.X_OK):
                return path_to_adb
        for path in os.environ["PATH"].split(os.pathsep):
            adb_path = os.path.join(path.strip(), "adb")
            if os.path.isfile(adb_path) and os.access(adb_path, os.R_OK | os.X_OK):
                return adb_path
        return None

    # Run a command with shell
    def __run(self, command):
        try:
            return check_output("%s %s" % (self.adb, command), shell=True)
        except:
            return ""

    # Connect to remote host
    def connect(self, host=None, port=None):
        if host is not None:
            hp = host if port is None else "%s:%d" % (host, port)
            self.__run("connect %s" % hp)
            self.url = "-s %s" % hp

    # Run a shell command on remote host
    def shell(self, command):
        return self.__run("%s shell %s" % (self.url, command))
