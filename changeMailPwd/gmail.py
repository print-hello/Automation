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
    while True:
        step_flag = 1
        hostname = socket.gethostname()
        conn = pymysql.connect(host='localhost', port=3306,
                               user='root', password='123456',
                               db='walmartmoneycard', charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
        conn1 = pymysql.connect(host='localhost', port=3306,
                                user='root', password='123456',
                                db='vpn', charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
        conn2 = pymysql.connect(host='localhost', port=3306,
                                user='root', password='123456',
                                db='new_pin', charset='utf8mb4',
                                cursorclass=pymysql.cursors.DictCursor)
        sql = 'SELECT * from email_info where computer=%s and id>994 and new_pwd_usable=0 order by id limit 1'
        result = fetch_one_sql(conn, sql, hostname)
        if result:
            email_id = result['id']
        else:
            sql = 'SELECT * from email_info where computer="-" and id>994 and new_pwd_usable=0 order by id limit 1'
            result = fetch_one_sql(conn, sql)
            if result:
                email_id = result['id']
                sql = 'UPDATE email_info set computer=%s where id=%s'
                commit_sql(conn, sql, (hostname, email_id))
            else:
                sql = 'SELECT * from email_info where id>994 and recovery_email_changed=0 and new_pwd_usable=1 and computer=%s order by id limit 1'
                result = fetch_one_sql(conn, sql, hostname)
                if result:
                    step_flag = 2
                    email_id = result['id']
                else:
                    step_flag = 0
                    print('Not data!')
                    break
        if step_flag > 0:
            email = result['email']
            print(email)
            sql = 'SELECT account from vpn where id>2421 and id<4730 order by RAND() limit 1'
            vpn_result = fetch_one_sql(conn1, sql)
            if vpn_result:
                vpn = vpn_result['account']
            connect_vpn(conn1, vpn)
            email_pwd = result['email_pwd']
            recovery_email = result['recovery_email']
            new_pwd_in_db = result['new_pwd']
            new_pwd = email_pwd + 'de'
            sql = 'SELECT * from email_info where id<995 and used_recovery_email=0 order by RAND() limit 1'
            recovery_res = fetch_one_sql(conn, sql)
            if recovery_res:
                new_recovery_id = recovery_res['id']
                new_recovery_email = recovery_res['email']
                new_recovery_pwd = recovery_res['email_pwd']
            else:
                print('No recovery_email!')
                break
            options = webdriver.ChromeOptions()
            options.add_argument('disable-infobars')
            driver = webdriver.Chrome(chrome_options=options)
            driver.maximize_window()
            driver.get('https://accounts.google.com')
            time.sleep(3)
            if driver.page_source.find('This site can’t be reached') > -1:
                driver.quit()
                continue
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'identifierId')))
                element.send_keys(email)
                driver.find_element_by_id('identifierNext').click()
            except Exception as e:
                sql = 'UPDATE email_info set new_pwd_usable=9 where id=%s'
                commit_sql(conn, sql, email_id)
                step_flag = 0
        if step_flag > 0:
            try:
                time.sleep(5)
                if step_flag == 2:
                    email_pwd = new_pwd_in_db
                driver.find_element_by_xpath(
                    '//content//input[@name="password"]').send_keys(email_pwd)
                driver.find_element_by_id('passwordNext').click()
                time.sleep(3)
                error_info = driver.find_element_by_xpath(
                    '//div[@class="GQ8Pzc"]')
                if error_info:
                    print('Password error!')
                    sql = 'UPDATE email_info set new_pwd_usable=9 where id=%s'
                    commit_sql(conn, sql, email_id)
                    driver.quit()
                    continue
            except Exception as e:
                pass
            try:
                time.sleep(5)
                element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//h1[@class="sfYUmb"]')))
                driver.find_element_by_xpath(
                    '//li[@class="C5uAFc"]/div').click()
                time.sleep(3)
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, 'identifierId')))
                element.send_keys(recovery_email)
                driver.find_element_by_xpath(
                    '//div[@class="qhFLie"]/div').click()
            except Exception as e:
                pass
            try:
                element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="N4lOwd"]')))
                time.sleep(3)
                driver.find_element_by_xpath(
                    '//div[@class="yKBrKe"]/div').click()
            except Exception as e:
                pass
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="tbyFuf"]//a[2]')))
                element.click()
            except Exception as e:
                pass
        # Change password
        if step_flag == 1:
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="ahh38c"]//div[6]')))
                element.click()
            except Exception as e:
                pass
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//content//input[@name="password"]')))
                element.send_keys(email_pwd)
                driver.find_element_by_id('passwordNext').click()
                time.sleep(3)
            except Exception as e:
                pass
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@name="password"]')))
                element.send_keys(new_pwd)
                driver.find_element_by_xpath(
                    '//input[@name="confirmation_password"]').send_keys(new_pwd)
                driver.find_element_by_xpath('//div[@jsname="XTYNyb"]').click()
                sql = 'UPDATE email_info set new_pwd=%s, new_pwd_usable=1 where id=%s'
                commit_sql(conn, sql, (new_pwd, email_id))
            except Exception as e:
                sql = 'UPDATE email_info set new_pwd_usable=9 where id=%s'
                commit_sql(conn, sql, email_id)
                step_flag = 0
            if step_flag == 0:
                driver.quit()
                continue
            try:
                windows = driver.window_handles
                driver.switch_to.window(windows[1])
                driver.close()
                print('Close the success page!')
                driver.switch_to.window(windows[0])
                time.sleep(1)
            except Exception as e:
                pass
        # Change email
        if step_flag > 0:
            try:
                time.sleep(3)
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//section//article[2]//div[@class="ahh38c"]/div[2]/div')))
                element.click()
            except Exception as e:
                print(e)
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="hyMrOd "]//a')))
                element.click()
                if step_flag == 2:
                    new_pwd = new_pwd_in_db
                driver.find_element_by_xpath(
                    '//content//input[@name="password"]').send_keys(new_pwd)
                driver.find_element_by_id('passwordNext').click()

                element.send_keys(new_pwd)
                driver.find_element_by_xpath(
                    '//input[@name="confirmation_password"]').send_keys(new_pwd)
                driver.find_element_by_xpath('//div[@jsname="XTYNyb"]').click()
            except Exception as e:
                pass
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@class="hySCje"]/div[2]')))
                element.click()
            except Exception as e:
                pass
            try:
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//input[@type="email"]')))
                element.clear()
                time.sleep(1)
                element.send_keys(new_recovery_email)
                driver.find_element_by_xpath(
                    '//div[@jsname="c6xFrd"]/div[2]').click()
                sql = 'UPDATE email_info set recovery_email=%s, recovery_email_pwd=%s, recovery_email_changed=1 where id=%s'
                commit_sql(conn, sql, (new_recovery_email,
                                       new_recovery_pwd, email_id))
                sql = 'UPDATE email_info set used_recovery_email=1 where id=%s'
                commit_sql(conn, sql, new_recovery_id)
            except Exception as e:
                pass
        time.sleep(2)
        try:
            driver.quit()
        except Exception as e:
            pass


if __name__ == '__main__':
    main()
