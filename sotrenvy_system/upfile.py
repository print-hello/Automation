import win32gui
import win32con
import time


def select_upfilename_chrome(driver, filepath):
    driver.find_element_by_xpath(
        "//div[@id='fileUploader']/div/div[2]").click()
    time.sleep(1)
    # win32gui
    dialog = win32gui.FindWindow('#32770', u'Open')
    ComboBoxEx32 = win32gui.FindWindowEx(dialog, 0, 'ComboBoxEx32', None)
    ComboBox = win32gui.FindWindowEx(ComboBoxEx32, 0, 'ComboBox', None)
    Edit = win32gui.FindWindowEx(ComboBox, 0, 'Edit', None)
    button = win32gui.FindWindowEx(dialog, 0, 'Open(O)', None)

    win32gui.SendMessage(Edit, win32con.WM_SETTEXT,
                         None, filepath)
    win32gui.SendMessage(dialog, win32con.WM_COMMAND, 1, button)


def select_upfilename_firefox(driver, filepath):
    driver.find_element_by_xpath(
        "//div[@id='fileUploader']//div//div[2]").click()
    time.sleep(1)
    # win32gui
    dialog = win32gui.FindWindow('#32770', u'Open')
    ComboBoxEx32 = win32gui.FindWindowEx(dialog, 0, 'ComboBoxEx32', None)
    ComboBox = win32gui.FindWindowEx(ComboBoxEx32, 0, 'ComboBox', None)
    Edit = win32gui.FindWindowEx(ComboBox, 0, 'Edit', None)
    button = win32gui.FindWindowEx(dialog, 0, 'Open(O)', None)
    time.sleep(1)
    win32gui.SendMessage(Edit, win32con.WM_SETTEXT,
                         None, filepath)
    time.sleep(1)
    win32gui.SendMessage(dialog, win32con.WM_COMMAND, 1, button)
