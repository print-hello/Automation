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
	for /f "tokens=1-4,* delims=," %%a in (D:\work\pin_login_system\nameandmac.txt) do (
		set NewComputerName=%%a
		set NewMAC=%%b
	)

if "%NewComputerName%" NEQ "" (
echo NewComputerName:%NewComputerName% NewMAC:%NewMAC%
) else (
echo NewComputerName is not null
pause
)

set "NetConnection=Local Area Connection"
wmic computersystem where "name='%COMPUTERNAME%'" call rename '%NewComputerName%'
@echo off
cd /d "%~dp0"


>"%tmp%\$t.js" echo;try{WSH.echo(WSH.StdIn.ReadAll().replace(/[\r\n]+/g,'\r\n'))}catch(e){}
for /f "delims=" %%a in ('wmic NIC where "NetConnectionID='%NetConnection%'" get Name /value^|find "="^|cscript -nologo -e:jscript "%tmp%\$t.js"') do set "%%a"
echo;%Name%
set "regpath=HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Class\{4D36E972-E325-11CE-BFC1-08002BE10318}"
for /f "delims=" %%a in ('reg query "%regpath%"^|findstr "^HKEY_LOCAL_MACHINE.*}\\[0-9][0-9]*$"') do (
    for /f "tokens=1,2*" %%i in ('reg query "%%a" /v "DriverDesc"^|find "DriverDesc"') do (
        if /i "%Name%" equ "%%k" (
            echo;"%%a"
            netsh interface set interface "%NetConnection%" disable
            reg add "%%a" /v NetworkAddress /d "%NewMAC%" /f
            netsh interface set interface "%NetConnection%" enable
        )
    )
)
echo Edtior ComputerName And Mac is OK ...
