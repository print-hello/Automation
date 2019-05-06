import os
import time
import subprocess


num = 0
while True:
    print('Has been running', num, 'seconds')
    if num > 900:
        p = subprocess.Popen('cmd.exe /c' + 'taskkill /F /im Client.exe',
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.wait()
        time.sleep(2)
        os.system('Shutdown -s -t 0')
    time.sleep(5)
    num += 5
