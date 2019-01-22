import os
import time


class Adsl(object):

    def __init__(self):
        self.name = "宽带连接"
        self.username = '******'
        self.password = '******'
        self.connect()

    def connect(self):
        cmd_str = "rasdial %s %s %s" % (
            self.name, self.username, self.password)
        os.system(cmd_str)
        time.sleep(5)


if __name__ == '__main__':
    Adsl()
