import os
import time
import datetime

num = 0
while True:
	print('Has been running', num/60, 'min')
	if num > 3600:
		os.system('Shutdown -r -t 0')
	time.sleep(2)
	num += 2
