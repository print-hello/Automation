import pymysql
import win32api
import win32con
from selenium import webdriver
import time
import socket
import os


def upload_pic():
    conn = pymysql.connect(host='localhost', port=3306,
        user='root', password='******',
        db='pin_upload', charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)
    conn1 = pymysql.connect(host='localhost', port=3306,
        user='root', password='******',
        db='new_pin', charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor)
    hostname = socket.gethostname()
    cursor = conn.cursor()
    cursor1 = conn1.cursor()
    cursor.execute('SELECT belong_web from pin_upload')
    results = cursor.fetchall()
    url_list = []
    for res in results:
        url = res['belong_web']
        url_list.append(url)
        # print(url)
    uniq_results = list(set(url_list))
    for url in uniq_results:
        try:
            cursor.execute('INSERT INTO web_url (url) values (%s)', url)
            conn.commit()
        except:
            pass
    print('The url has been updated.')
    cursor1.execute(
        'SELECT * from account where upload_done=0 and upload_computer="%s" and created_boards>4 order by id limit 1' % hostname)
    result = cursor1.fetchone()
    if result:
        belong_web = result['upload_web']
        email = result['email']
        pwd = result['pw']
        agent = result['agent']
        port = result['port']
        account_id = result['id']
        if belong_web:
            print(belong_web)
        else:
            print('Assign a new account.')
            cursor.execute('SELECT * from web_url where state=0 limit 1')
            get_url = cursor.fetchone()
            if get_url:
                new_url = get_url['url']
                cursor1.execute(
                    'UPDATE account set upload_web="%s", upload_computer="%s" where id=%s' % (new_url, hostname, account_id))
                conn1.commit()
                cursor.execute('UPDATE web_url set state=1 where url="%s"' % new_url)
                conn.commit()
                belong_web = new_url
            else:
                print('No new data...')
                time.sleep(9999)
    else:
        cursor1.execute(
            'SELECT * from account where upload_done=0 and upload_computer="-" and created_boards>4 order by id limit 1')
        result = cursor1.fetchone()
        if result:
            belong_web = result['upload_web']
            email = result['email']
            pwd = result['pw']
            agent = result['agent']
            port = result['port']
            account_id = result['id']
            if belong_web:
                print(belong_web)
            else:
                print('Assign a new account.')
                cursor.execute('SELECT * from web_url where state=0 limit 1')
                get_url = cursor.fetchone()
                if get_url:
                    new_url = get_url['url']
                    cursor1.execute(
                        'UPDATE account set upload_web="%s", upload_computer="%s" where id=%s' % (new_url, hostname, account_id))
                    conn1.commit()
                    cursor.execute('UPDATE web_url set state=1 where url="%s"' % new_url)
                    conn.commit()
                    belong_web = new_url
                else:
                    print('No new data...')
                    time.sleep(9999)
    options = webdriver.ChromeOptions()
    options.add_argument('user-agent="%s"' % agent)
    options.add_argument("--proxy-server=http://localhost:%d" % port)
    prefs = {
    'profile.default_content_setting_values':
    {'notifications': 2
     }
    }
    options.add_experimental_option('prefs', prefs)
    driver = webdriver.Chrome(chrome_options=options)
    driver.maximize_window()
    login_url = 'https://www.pinterest.com/login/?referrer=home_page'
    driver.get(login_url)
    driver.find_element_by_name("id").send_keys(email)
    driver.find_element_by_name("password").send_keys(pwd)
    driver.find_element_by_xpath("//form//button").click()
    time.sleep(5)
    print('Start uploading images...')
    while True:
        sql = 'SELECT * from pin_upload where saved=0 and belong_web="%s" order by id asc limit 1' % belong_web    
        cursor.execute(sql)
        result = cursor.fetchone()
        if result:
            upload_pic_path = result['savelink']
            upload_pic_board = result['saveboard']
            upload_pic_id = result['Id']
            driver.get(upload_pic_path)
            time.sleep(5)
            try:
                driver.find_element_by_xpath(
                    "//input[@id='pickerSearchField']").send_keys(upload_pic_board)
            except Exception as e:
                print('Image save failed, element not found')
            time.sleep(1)
            try:
                win32api.keybd_event(13, 0, 0, 0)
                win32api.keybd_event(
                    13, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(5)
            except Exception as e:
                pass
            try:
                driver.find_element_by_xpath(
                    "//div[@class='mainContainer']//div[1]/div/button").click()
                print('Uploading %d' % upload_pic_id)
                time.sleep(5)
                sql = "UPDATE pin_upload set saved=1 where id = %s" % upload_pic_id
                cursor.execute(sql)
                conn.commit()
            except Exception as e:
                pass
        else:
            print('End...')
            cursor1.execute('UPDATE account set upload_done=1, upload_computer="-" where id=%s' % account_id)
            conn1.commit()
            time.sleep(3)
            break
    cursor.close()
    conn.close()
    cursor1.close()
    conn1.close()
    os.system('shutdown -r -t 10')
    time.sleep(100)


if __name__ == '__main__':
    upload_pic()
