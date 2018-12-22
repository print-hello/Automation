@echo off

xcopy Z:\host\upload_pin F:\upload_pin /y

ping /n 10 127.1>nul
start "" "F:\upload_pin\uploadPin.py"