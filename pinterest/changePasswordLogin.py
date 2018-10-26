from selenium import webdriver
import time
import requests
import json
from dbConnection import readOneSQL, readAllSQL, writeSQL
import pymysql

def clickLogin(driver, email, pwd, account_id, cookie, conn):
    login_url = 'https://www.pinterest.com/login/?referrer=home_page'
    login_flag = ''

    driver.get(login_url)
    driver.find_element_by_name("id").send_keys(email)
    driver.find_element_by_name("password").send_keys(pwd)
    driver.find_element_by_xpath("//form//button").click()
    time.sleep(5)

    # Determine if the login was successful
    try:
        login_flag = driver.find_element_by_xpath('//form//button/div').text
    except:
        pass
    if login_flag == 'Log in':
        login_state = 0
    else:
        login_state = 1
        cookies = driver.get_cookies()
        cookies = json.dumps(cookies)
        cookies = cookies.replace('\\', '\\\\')
        cookies = cookies.replace('\"', '\\"')
        sql = "update account set cookie='%s' where id=%s" % (cookies, account_id)
        writeSQL(conn, sql)

    return login_state
