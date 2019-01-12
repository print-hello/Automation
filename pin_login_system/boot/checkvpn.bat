@echo off 
:nofile


:start1


for /f "tokens=1-2,* delims=," %%a in (D:\work\pin_login_system\boot\vpn.txt) do (



	set vpnserver=%%a
	set adslzhanghao=%%b
	set vpnpwd=%%c
	
	
	echo Connect %%a %%b


	Rasdial %%a %%b %%c



	ping -n 3 www.google.com >nul&if not errorlevel 1 (
	
		
		goto end1

	) else (

		echo Disconnect %%b
		Rasphone -h %%a

	)
	
)


:end1




ping -n 3 www.google.com >nul&if not errorlevel 1 (
		
	echo network is OK


) else (
	
	echo Disconnect %adslzhanghao%
	Rasphone -h %vpnserver%
	


	goto start1

)





 

