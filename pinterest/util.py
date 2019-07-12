import time
import requests
import subprocess
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def explicit_wait(driver, track, ec_params, timeout=35, notify=True):
    if not isinstance(ec_params, list):
        ec_params = [ec_params]

    # find condition according to the tracks
    if track == "VOEL":
        elem_address, find_method = ec_params
        ec_name = "visibility of element located"

        find_by = (By.XPATH if find_method == "XPath" else
                   By.CSS_SELECTOR if find_method == "CSS" else
                   By.CLASS_NAME)
        locator = (find_by, elem_address)
        condition = EC.visibility_of_element_located(locator)

    elif track == "TC":
        expect_in_title = ec_params[0]
        ec_name = "title contains '{}' string".format(expect_in_title)

        condition = EC.title_contains(expect_in_title)

    elif track == "SO":
        ec_name = "staleness of"
        element = ec_params[0]
        condition = EC.staleness_of(element)

    # generic wait block
    try:
        wait = WebDriverWait(driver, timeout)
        result = wait.until(condition)

    except:
        if notify is True:
            print(
                "Timed out with failure while explicitly waiting until {}!\n"
                .format(ec_name))
        return False

    return result


def check_vpn():
    p = subprocess.Popen('cmd.exe /c' + 'F:\\pinterest\\boot\\checkvpn.bat abc',
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


def rasphone_vpn():
    p = subprocess.Popen("cmd.exe /c" + 'F:\\pinterest\\boot\\rasphonevpn.bat abc',
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    curline = p.stdout.readline()
    while curline != b'':
        # print(curline)
        curline1 = str(curline).replace("\\r\\n", "")
        curline = p.stdout.readline()
    p.wait()


def get_out_ip():
    url = "http://20019.ip138.com/ic.asp"
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
    # with open('F:\\new_pinterest\\boot\\config_time.txt', 'w', encoding='utf-8') as fp:
    #     fp.write(time_str)


def connect_vpn(conn, vpn):
    sql = "SELECT account, pwd, server, ip from vpn where account=%s"
    result = fetch_one_sql(conn, sql, vpn)
    if result:
        vpn = result['account']
        vpn_pwd = result['pwd']
        vpn_ip = result['ip']
        vpn_server = result['server'].replace('.lianstone.net', '')
        with open("F:\\new_pinterest\\boot\\vpn.txt", "w", encoding='utf-8') as fp:
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
    check_vpn()
    net_ip = get_out_ip()
    write_txt_time()
    while True:
        if net_ip == vpn_ip:
            print('VPN connection IP is correct!')
            break
        else:
            check_vpn()
            write_txt_time()
            time.sleep(10)
            net_ip = get_out_ip()