@echo off
:DeleteHistory
	set m=C:\Users\Administrator\Downloads
	del "%m%\*" /f /s /q /a
	for /f "delims=" %%i in ('dir /ad /w /b "%m%"') do (
	rd /s /q "%m%\%%i"
	)
	echo Delete Success
	if exist C:\Users\Administrator\Downloads\*.txt goto DeleteHistory
:downhostsfile
		set web=http://172.16.253.100/downloard.php
		start /max "" "C:\Users\Administrator\AppData\Local\Google\Chrome\Application\chrome.exe" "%web%" 
		for /l %%i in (8,-1,0) do (
		cls
		echo %%i Close Download
		ping 127.1 -n 2 >nul
		)
		taskkill /f /t /im chrome.exe  
		if not exist C:\Users\Administrator\Downloads\hosts.txt goto downhostsfile --1
		
	:copyhosts
		if exist C:\Users\Administrator\Downloads\hosts.txt @copy C:\Users\Administrator\Downloads\hosts.txt C:\Windows\System32\drivers\etc\hosts /y
echo %time%
set now_tme=%time%
set /a hh=%now_tme:~0,2%
set /a mm=%now_tme:~3,2%
set /a ss=%now_tme:~6,2%
set /a ns=(%hh%*60+%mm%)*60+%ss%
echo %hh%-%mm%-%ss%
echo current time  %ns%
echo %ns%>F:\pinterest\boot\config_time.txt


xcopy Z:\host\pinterest F:\pinterest /y

xcopy Z:\host\pinterest\boot F:\pinterest\boot /y

ping /n 15 127.1>nul
start "" "F:\pinterest\reboot.py"
start "" "F:\pinterest\main.py"




:startcmd

echo after 150s

ping /n 150 127.1>nul

echo %time%
set now_tme=%time%
set /a hh=%now_tme:~0,2%
set /a mm=%now_tme:~3,2%
set /a ss=%now_tme:~6,2%
set /a ns=(%hh%*60+%mm%)*60+%ss%
echo %hh%-%mm%-%ss%
echo current time  %ns%



echo now times min  %now_tme%
setlocal enabledelayedexpansion
set adslzhanghao=0
for /f "delims=" %%a in (F:\pinterest\boot\config_time.txt) do (set  adslzhanghao=%%a)


set /a ns1=%adslzhanghao%
echo text time  %ns1%

set /a tim_flag=%ns%-%ns1%

echo time difference %tim_flag%

if %tim_flag% LSS -180 (
	echo %tim_flag%
	#taskkill /f /im python.exe
	#taskkill /f /im py.exe
	taskkill /f /im chromedriver.exe
	taskkill /f /im chrome.exe
	taskkill /f /im geckodriver.exe
	ping /n 3 127.1>nul
	
	start "" "F:\pinterest\main.py"
	ping /n 5 127.1>nul
)

if %tim_flag% GTR 180 (
	echo %tim_flag%
	#taskkill /f /im python.exe
	#taskkill /f /im py.exe
	taskkill /f /im chromedriver.exe
	taskkill /f /im chrome.exe
	taskkill /f /im geckodriver.exe
	ping /n 3 127.1>nul
	start "" "F:\pinterest\main.py"
	ping /n 5 127.1>nul
)



goto startcmd