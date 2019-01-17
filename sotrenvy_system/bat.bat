@echo off
ping /n 10 127.1>nul
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
		for /l %%i in (3,-1,0) do (
		cls
		echo %%i Close Download
		ping 127.1 -n 2 >nul
		)
		taskkill /f /t /im chrome.exe  
		if not exist C:\Users\Administrator\Downloads\hosts.txt goto downhostsfile --1
		
	:copyhosts
		if exist C:\Users\Administrator\Downloads\hosts.txt @copy C:\Users\Administrator\Downloads\hosts.txt C:\Windows\System32\drivers\etc\hosts /y

ping /n 3 127.1>nul
xcopy Z:\host\sotrenvy_system E:\sotrenvy_system /y

ping /n 5 127.1>nul
:readconfig
	echo read config file
	for /f "tokens=1-6,* delims=," %%a in (E:\sotrenvy_system\vpn_config.txt) do (
		set adslzhanghao=%%a
		set email=%%b
		set VpnDomain=%%c
		set acounturl=%%d
		set cipan=%%e
		set domain=%%f
	)
	echo Connect %adslzhanghao% %email% %VpnDomain% %acounturl% %cipan% %domain%
	if "%domain%"=="" (
	set domain=wuyongfeile
	)

	:disconnectnetwork
		@echo off
		Rasphone -h vpn
		Rasphone -h VPN
		Rasphone -h VPN1
		Rasphone -h VPN2
		Rasphone -h VPN3
		Rasphone -h VPN4
		Rasphone -h VPN5
		Rasphone -h VPN6
		Rasphone -h VPN7
		Rasphone -h VPN8
		Rasphone -h VPN9
		Rasphone -h VPN10
		ping -n 1 www.google.com >nul&if not errorlevel 1 (
			goto disconnectnetwork
		)
		
	:connectnetwork
	    echo check network
		Rasdial %VpnDomain% %adslzhanghao% elevenvpn2016

		ping -n 3 www.google.com >nul&if not errorlevel 1 (
			echo network is OK
		) else (
				Rasphone -h vpn
				Rasphone -h VPN
				Rasphone -h VPN1
				Rasphone -h VPN2
				Rasphone -h VPN3
				Rasphone -h VPN4
				Rasphone -h VPN5
				Rasphone -h VPN6
				Rasphone -h VPN7
				Rasphone -h VPN8
				Rasphone -h VPN9
				Rasphone -h VPN10
			echo Disconnect %adslzhanghao%

			for /l %%i in (3,-1,0) do (
				cls
				echo %%i Connect VPN  %adslzhanghao%
				echo VpnDomain %VpnDomain%
				ping 127.1 -n 2 >nul
			)
			goto connectnetwork
		)

ping /n 15 127.1>nul
start "" "E:\sotrenvy_system\storenvy.py"


exit
