@echo off

:shanchulishi
	set m=C:\Users\Administrator\Downloads
	del "%m%\*" /f /s /q /a
	for /f "delims=" %%i in ('dir /ad /w /b "%m%"') do (
	rd /s /q "%m%\%%i"
	)
	echo shanchu chenggong
	if exist C:\Users\Administrator\Downloads\*.txt goto shanchulishi
	
	:downhostsfile
		set web=http://104.247.192.122:2019/downloardwf.php?filename=pphost.txt^&downname=hosts.txt
		start /max "" "C:\Program Files\Google\Chrome\Application\chrome.exe" "%web%" 
		for /l %%i in (2,-1,0) do (
		cls
		echo %%i guanbi xiazai
		ping 127.1 -n 2 >nul
		)
		taskkill /f /t /im chrome.exe  
		if not exist C:\Users\Administrator\Downloads\hosts.txt goto downhostsfile --1
		
	:copyhosts
		if exist C:\Users\Administrator\Downloads\hosts.txt @copy C:\Users\Administrator\Downloads\hosts.txt C:\Windows\System32\drivers\etc\hosts /y

ping 127.1 -n 5 >nul
set "DownloadsLuJin=C:\Users\Administrator\Downloads"
set "WorkLuJin=C:\Users\Administrator\Desktop\work"
ping /n 5 127.1>nul
:shanchudown
	del "%DownloadsLuJin%\*" /f /s /q /a
	for /f "delims=" %%i in ('dir /ad /w /b "%DownloadsLuJin%"') do (
	rd /s /q "%DownloadsLuJin%\%%i"
	)
	echo shanchu chenggong
	if exist %DownloadsLuJin%\*.txt goto shanchudown
	if exist %DownloadsLuJin%\*.zip goto shanchudown

:shanchuwork
	del "%WorkLuJin%\*" /f /s /q /a
	for /f "delims=" %%i in ('dir /ad /w /b "%WorkLuJin%"') do (
	rd /s /q "%WorkLuJin%\%%i"
	)
	echo shanchu chenggong
	if exist %WorkLuJin%\*.txt goto shanchuwork
	if exist %WorkLuJin%\*.zip goto shanchuwork

	:downupdaterar
		set web=http://122.114.73.114/downloardwf.php?filename=register_paypal.zip
		start /max "" "C:\Program Files\Google\Chrome\Application\chrome.exe" "%web%" 
		for /l %%i in (5,-1,0) do (
		cls
		echo %%i guanbi xiazai
		ping 127.1 -n 5 >nul
		)
		taskkill /f /t /im chrome.exe
		if not exist %DownloadsLuJin%\*.zip goto downupdaterar

"C:\Program Files\WinRAR\WinRAR.exe" x -y %DownloadsLuJin%\register_paypal.zip %WorkLuJin%


ping /n 10 127.1>nul
start "" "C:\Users\Administrator\Desktop\work\register_paypal\register_paypal_account.py"
ping /n 5 127.1>nul
start "" "C:\Users\Administrator\Desktop\work\register_paypal\reboot.py"