import os
import time


num = 0
while True:
	if num > 3600:
		os.system('Shutdown -r -t 0')
	time.sleep(5)
	print('Has been running', num, 'seconds')
	num += 5
