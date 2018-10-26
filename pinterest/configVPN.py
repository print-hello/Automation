import time
import subprocess
import requests

def checkVPN():
    p = subprocess.Popen('cmd.exe /c' + 'F:\\pinterest\\boot\\checkVPN.bat abc', 
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    curline = p.stdout.readline()
    while curline != b'':
        curlines = str(curline).replace('\\r\\n', '')
        curline = p.stdout.readline()
    p.wait()
    print(curlines)
    if curlines != "b'network is OK'":
        return 0
    else:
        return 1

def rasphoneVPN():
    p = subprocess.Popen("cmd.exe /c" + 'F:\\pinterest\\boot\\rasphoneVPN.bat abc', 
                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    curline = p.stdout.readline()
    while curline != b'':
        # print(curline)
        curline1 = str(curline).replace("\\r\\n", "")
        curline = p.stdout.readline()
    p.wait()

def getOutIP():
    url = "http://2018.ip138.com/ic.asp"
    r = requests.get(url)
    txt = r.text
    ip = txt[txt.find("[") + 1: txt.find("]")]
    print('ip:' + ip)
    return ip

def writeTxtTime():
    time_hour = int(time.strftime('%H', time.localtime(time.time()))) * 3600
    time_min = int(time.strftime('%M', time.localtime(time.time()))) * 60
    time_sec = int(time.strftime('%S', time.localtime(time.time())))
    time_str = str(time_hour + time_min + time_sec)
    with open('F:\\pinterest\\boot\\config_time.txt', 'w', encoding='utf-8') as fp:
        fp.write(time_str)
