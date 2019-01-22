import os
import time
import requests
import json
# import pymysql
import socket
        

class Adsl(object):

    def __init__(self):
        with open('adsl_account.txt', 'r') as fp:
            account = fp.read().strip().split('-')
        self.name = "宽带连接"
        self.username = account[0]
        self.password = account[1]
        self.hostname = socket.gethostname()
        self.reconnect()

    def connect(self):
        cmd_str = "rasdial %s %s %s" % (
            self.name, self.username, self.password)
        os.system(cmd_str)
        time.sleep(5)

    def disconnect(self):
        cmd_str = "rasdial %s /disconnect" % self.name
        os.system(cmd_str)
        time.sleep(5)

    def get_host_ip(self):
        try:
            url = "http://2019.ip138.com/ic.asp"
            r = requests.get(url)
            txt = r.text
            ip = txt[txt.find("[") + 1: txt.find("]")]
        except:
            pass
        return ip

    def reconnect(self):
        headers = {'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36'}
        restart = 1
        while True:
            try:
                state = requests.get(
                    'http://ip.lianstone.net/index.php?hostname=%s' % self.hostname)
            except:
                self.disconnect()
                self.connect()
                restart += 1
            if restart > 5:
                os.system('shutdown -r -t 0')
                time.sleep(100)
            try:
                now_state_json = json.loads(state.text)
                now_state = int(now_state_json['status'])
                if now_state == 1:
                    while True:
                        self.disconnect()
                        self.connect()
                        time.sleep(3)
                        ping_outside = requests.get('https://www.google.com/', headers=headers)
                        if str(ping_outside) == '<Response [200]>':
                            break
                    current_ip = self.get_host_ip()
                    requests.get(
                        'http://ip.lianstone.net/zhuangtai.php?ip=%s&hostname=%s' % (current_ip, self.hostname))
                else:
                    time.sleep(3)
            except:
                pass


if __name__ == '__main__':
    Adsl()
