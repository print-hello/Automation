import pymysql
import time
import socket
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from config import connect_vpn
from dbconnection import fetch_one_sql, commit_sql


def main():
    hostname = socket.gethostname()
    while True:
        step_flag = 1
        conn = pymysql.connect(host='localhost', port=3306,
                               user='root', password='123456',
                               db='walmartmoneycard', charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
        conn1 = pymysql.connect(host='localhost', port=3306,
                                user='root', password='123456',
                                db='vpn', charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
        sql = 'SELECT id, email, email_pwd from email_info where computer=%s and new_pwd is NULL order by id limit 1'
        result = fetch_one_sql(conn, sql, hostname)
        if result:
            email_id = result['id']
        else:
            sql = 'SELECT id, email, email_pwd from email_info where computer="-" and new_pwd is NULL order by id limit 1'
            result = fetch_one_sql(conn, sql)
            if result:
                email_id = result['id']
                sql = 'UPDATE email_info set computer=%s where id=%s'
                commit_sql(conn, sql, (hostname, email_id))
            else:
                step_flag = 0
                print('Not data!')
                break
        if step_flag == 1:
            email = result['email']
            print(email)
            sql = 'SELECT account from vpn where id>2421 and id<4730 order by RAND() limit 1'
            vpn_result = fetch_one_sql(conn1, sql)
            if vpn_result:
                vpn = vpn_result['account']
            connect_vpn(conn1, vpn)
            pwd = result['email_pwd']
            options = webdriver.ChromeOptions()
            options.add_argument('disable-infobars')
            driver = webdriver.Chrome(chrome_options=options)
            driver.maximize_window()
            driver.get('https://mail.yahoo.com')
            time.sleep(3)
            if driver.page_source.find('This site can’t be reached') > -1:
                driver.quit()
                continue
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'login-username')))
                element.send_keys(email)
                driver.find_element_by_id('login-signin').click()
            except Exception as e:
                step_flag = 0
            if step_flag == 0:
                driver.quit()
                continue
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'login-passwd')))
                element.send_keys(pwd)
                driver.find_element_by_id('login-signin').click()
            except Exception as e:
                step_flag = 0
            if step_flag == 0:
                driver.quit()
                continue
            try:
                element = WebDriverWait(driver, 3).until(
                    EC.presence_of_element_located((By.XPATH, '//button[@name="index"]')))
                if element:
                    print('Need verification, skip!')
                    driver.quit()
                    sql = 'UPDATE email_info set new_pwd="needVerification", computer="-" where id=%s'
                    commit_sql(conn, sql, email_id)
            except Exception as e:
                pass
            try:
                driver.find_element_by_xpath('//span[text()="Done"]').click()
            except Exception as e:
                pass
            try:
                driver.find_element_by_xpath(
                    '//button[@title="Maybe later"]').click()
            except Exception as e:
                pass
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//label[@for="ybarAccountMenu"]')))
                element.click()
            except Exception as e:
                step_flag = 0
            if step_flag == 0:
                driver.quit()
                continue
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//a[text()="Account Info"]')))
                element.click()
                windows = driver.window_handles
                driver.switch_to.window(windows[1])
                time.sleep(1)
            except Exception as e:
                pass
            try:
                element = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
                    (By.XPATH, '//span[text()="Account Security"]')))
                element.click()
            except Exception as e:
                pass
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//a[@class="cpw-link"]')))
                element.click()
            except Exception as e:
                step_flag = 0
            if step_flag == 0:
                driver.quit()
                continue
            new_pwd = pwd.strip() + 'print'
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'cpwd-password')))
                element.send_keys(new_pwd)
                time.sleep(1)
                driver.find_element_by_id(
                    'cpwd-confirm-password').send_keys(new_pwd)
                time.sleep(1)
                driver.find_element_by_xpath(
                    '//input[@value="Continue"]').click()
                sql = 'UPDATE email_info set new_pwd=%s, computer="-" where id=%s'
                commit_sql(conn, sql, (new_pwd, email_id))
                print('Change password success!')
            except Exception as e:
                step_flag = 0
            if step_flag == 0:
                driver.quit()
                continue
            time.sleep(3)
            driver.quit()


if __name__ == '__main__':
    main()
