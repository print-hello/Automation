import time
import subprocess
import requests
from dbconnection import read_all_sql

def check_vpn():
    p = subprocess.Popen(
        'D:\\work\\pin_login_system\\boot\\checkvpn.bat', shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
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

def rasphone_vpn():
    p = subprocess.Popen(
        'D:\\work\\pin_login_system\\boot\\rasphonevpn.bat', shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    curline = p.stdout.readline()
    while curline != b'':
        # print(curline)
        curline1 = str(curline).replace("\\r\\n", "")
        curline = p.stdout.readline()
    p.wait()

def get_out_ip():
    url = "http://2018.ip138.com/ic.asp"
    r = requests.get(url)
    txt = r.text
    ip = txt[txt.find("[") + 1: txt.find("]")]
    print('ip:' + ip)
    return ip

def write_txt_time():
    time_hour = int(time.strftime('%H', time.localtime(time.time()))) * 3600
    time_min = int(time.strftime('%M', time.localtime(time.time()))) * 60
    time_sec = int(time.strftime('%S', time.localtime(time.time())))
    time_str = str(time_hour + time_min + time_sec)
    with open('D:\\work\\pin_login_system\\boot\\config_time.txt', 'w', encoding='utf-8') as fp:
        fp.write(time_str)

def connect_vpn(conn, vpn):
    sql = "SELECT account, pwd, server, ip from vpn where account='%s'" % vpn
    results = read_all_sql(conn, sql)
    if results:
        for row in results:
            vpn = row['account']
            vpn_pwd = row['pwd']
            vpn_ip = row['ip']
            vpn_server = row['server'].replace('.lianstone.net', '')
            with open("D:\\work\\pin_login_system\\boot\\vpn.txt", "w", encoding='utf-8') as fp:
                print(vpn_server + "," + vpn + "," + vpn_pwd)
                fp.write(vpn_server + "," + vpn + "," + vpn_pwd)
    else:
        print(
            'No corresponding VPN account has been detected and the system is being shut down...')
        time.sleep(600)
        os.system('Shutdown -s -t 0')
    print('Disconnect the original VPN connection')
    rasphone_vpn()
    write_txt_time()
    print('Handling new VPN...')
    check_vpn_num = check_vpn()
    net_ip = get_out_ip()
    write_txt_time()
    while True:
        if net_ip == vpn_ip:
            print('VPN connection IP is correct!')
            break
        else:
            check_vpn_num = check_vpn()
            write_txt_time()
            time.sleep(10)
            net_ip = get_out_ip()