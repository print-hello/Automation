import requests
import json
import time


with open('hostname.txt', 'r') as fp:
    hostname = fp.read().strip()
print('hostname:', hostname)

res = requests.get(
    'http://ip.lianstone.net/changestate.php?status=1&hostname=%s' % hostname)
while True:
    state = requests.get(
        'http://ip.lianstone.net/index.php?hostname=%s' % hostname)
    now_state_json = json.loads(state.text)
    now_state = int(now_state_json['status'])
    if now_state == 0:
        res = requests.get(
            'http://ip.lianstone.net/getip.php?hostname=%s' % hostname)
        ip = json.loads(res.text)['ip']
        break
    time.sleep(1)

with open('C:\\Windows\\System32\\drivers\\etc\\hosts', 'r') as f1:
    lines = f1.readlines()

with open('C:\\Windows\\System32\\drivers\\etc\\hosts', 'w') as f2:
    i = 1
    for line in lines:
        # print(line)
        ip_split = line.split(' ')
        try:
            ip_first = ip_split[0].strip()
            ip_last = ip_split[1].strip()
            if ip_last == 'www.changehostip.com':
                line = line.replace(ip_first, ip)
                # print(line)
                i = 0
        except:
            pass
        f2.write(line)
    # print(i)

if i == 1:
    with open('C:\\Windows\\System32\\drivers\\etc\\hosts', 'a+') as f3:
        add_host = ip + ' ' + 'www.changehostip.com'
        # print(add_host)
        f3.write(add_host)

print(ip)
time.sleep(3)
