import win32api  
import win32gui
import win32con
import time
import socket
import subprocess
import os


def verify(pp_nickname):
    p = subprocess.Popen('C:\\Users\\Administrator\\Desktop\\B.exe', shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    time.sleep(5)
    # win32api.MessageBox(win32con.NULL, 'hello!', 'hello', win32con.MB_OK)
    # current_point = win32api.GetCursorPos()
    # print(current_point)
    #点击用户和组
    # win32api.SetCursorPos((482, 552))
    # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    # time.sleep(1)
    # 点击网卡地址
    win32api.SetCursorPos((580, 550))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(1)
    # 点击系统版本
    win32api.SetCursorPos((868, 550))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(1)
    # 点击name
    # win32api.SetCursorPos((536, 182))
    # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    # time.sleep(1)
    # 勾选手动修改
    # win32api.SetCursorPos((547, 370))
    # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    # win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    # time.sleep(1)
    #点击修改
    win32api.SetCursorPos((600, 600))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(3)
    win32api.keybd_event(13, 0, 0, 0)
    win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(1)
    # 关闭
    win32api.SetCursorPos((962, 125))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
    time.sleep(2)
    with open('C:\\Users\\Administrator\\Desktop\\work\\paypalAuto\\computername.txt', 'w', encoding='utf-8') as fp:
        fp.write(pp_nickname)
    # p = subprocess.Popen('C:\\Users\\Administrator\\Desktop\\work\\paypalAuto\\editor_mac_computername.bat', shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p = subprocess.Popen('cmd.exe /c' + 'C:\\Users\\Administrator\\Desktop\\work\\paypalAuto\\editor_mac_computername.bat abc', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    p.wait()
    time.sleep(5)
    os.system('shutdown -r -t 5')