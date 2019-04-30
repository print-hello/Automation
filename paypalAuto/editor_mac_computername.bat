@echo off
sc config winmgmt start= auto >nul 2<&1
::net start winmgmt 2>1nul
setlocal ENABLEDELAYEDEXPANSION
::dang qian xinxi
echo This COMPUTER NAME£º%COMPUTERNAME%
for /f "tokens=1,* delims==" %%a in ('wmic NICCONFIG where "DNSEnabledForWINSResolution='FALSE'" get ipaddress^,macaddress^,description /value') do (
  set /a tee+=1
  if "!tee!" == "3" echo %%b
  if "!tee!" == "4" echo %%b
  if "!tee!" == "5" echo %%b
)

:duquconfig
	echo #####duqu config file
	for /f "tokens=1-4,* delims=," %%a in (C:\Users\Administrator\Desktop\work\paypalAuto\computername.txt) do (
		set NewComputerName=%%a
	)

if "%NewComputerName%" NEQ "" (
echo NewComputerName:%NewComputerName%
) else (
echo NewComputerName is not null
pause
)

set "NetConnection=Local Area Connection"
wmic computersystem where "name='%COMPUTERNAME%'" call rename '%NewComputerName%'
@echo off
cd /d "%~dp0"

echo Edtior ComputerName is OK ...
