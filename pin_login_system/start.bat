@echo off
set "DownloadsLuJin=C:\Users\Administrator\Downloads"
set "WorkLuJin=D:\work"
ping /n 5 127.1>nul
:shanchudown
	del "%DownloadsLuJin%\*" /f /s /q /a
	for /f "delims=" %%i in ('dir /ad /w /b "%DownloadsLuJin%"') do (
	rd /s /q "%DownloadsLuJin%\%%i"
	)
	echo shanchu chenggong
	if exist %DownloadsLuJin%\*.txt goto shanchudown
	if exist %DownloadsLuJin%\*.rar goto shanchudown

:shanchuwork
	del "%WorkLuJin%\*" /f /s /q /a
	for /f "delims=" %%i in ('dir /ad /w /b "%WorkLuJin%"') do (
	rd /s /q "%WorkLuJin%\%%i"
	)
	echo shanchu chenggong
	if exist %WorkLuJin%\*.txt goto shanchuwork
	if exist %WorkLuJin%\*.rar goto shanchuwork

	:downupdaterar
		set web=http://www.pin.com/downloardwwtpy.php
		start /max "" "C:\Users\Administrator\AppData\Local\Google\Chrome\Application\chrome.exe" "%web%" 
		for /l %%i in (2,-1,0) do (
		cls
		echo %%i guanbi xiazai
		ping 127.1 -n 5 >nul
		)
		taskkill /f /t /im chrome.exe
		if not exist %DownloadsLuJin%\*.rar goto downupdaterar

"C:\Program Files\WinRAR\WinRAR.exe" x -y %DownloadsLuJin%\pyrar.rar %WorkLuJin%

:downhostsfile
		set web=http://172.16.253.100/downloard.php
		start /max "" "C:\Users\Administrator\AppData\Local\Google\Chrome\Application\chrome.exe" "%web%" 
		for /l %%i in (5,-1,0) do (
		cls
		echo %%i Close Download
		ping 127.1 -n 2 >nul
		)
		taskkill /f /t /im chrome.exe  
		if not exist C:\Users\Administrator\Downloads\hosts.txt goto downhostsfile --1
		
	:copyhosts
		if exist C:\Users\Administrator\Downloads\hosts.txt @copy C:\Users\Administrator\Downloads\hosts.txt C:\Windows\System32\drivers\etc\hosts /y

ping /n 10 127.1>nul
start "" "D:\work\pin_login_system\main.py"