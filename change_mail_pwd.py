import pymysql
import time
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


def main():
    while True:
        step_flag = 1
        conn = pymysql.connect(host='172.16.253.100', port=3306,
                               user='root', password='123456',
                               db='walmartmoneycard', charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
        sql = 'SELECT id, email, email_pwd from email_info where new_pwd is NULL order by id limit 1'
        result = fetch_one_sql(conn, sql)
        if result:
            email_id = result['id']
            email = result['email']
            print(email)
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
            time.sleep(5)
            try:
                driver.find_element_by_xpath(
                    '//button[@title="Maybe later"]').click()
            except Exception as e:
                pass
            try:
                driver.find_element_by_xpath('//span[text()="Done"]').click()
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
            new_pwd = pwd.strip() + '2019'
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
                sql = 'UPDATE email_info set new_pwd=%s where id=%s'
                commit_sql(conn, sql, (new_pwd, email_id))
                print('Change password success!')
            except Exception as e:
                step_flag = 0
            if step_flag == 0:
                driver.quit()
                continue
            time.sleep(3)
            driver.quit()
        conn.close()


def fetch_one_sql(conn, sql, data=None):
    cursor = conn.cursor()
    cursor.execute(sql, data)
    result = cursor.fetchone()
    cursor.close()
    return result


def commit_sql(conn, sql, data=None):
    cursor = conn.cursor()
    cursor.execute(sql, data)
    conn.commit()
    cursor.close()


if __name__ == '__main__':
    main()
