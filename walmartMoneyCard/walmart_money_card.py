import time
import random
import pymysql
from selenium import webdriver
from selenium.webdriver.support.select import Select
import socket
import subprocess
import datetime
from dbconnection import fetch_one_sql, fetch_all_sql, commit_sql


def register_account():
    current_time = datetime.datetime.now().strftime("%Y-%m-%d")
    while True:
        flow_flag = 1
        hostname = socket.gethostname()
        conn = pymysql.connect(host='localhost', port=3306,
                               user='root', password='123456',
                               db='walmartmoneycard', charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
        # # Get email
        sql = 'SELECT * from email_info where emailIsUsed=0 and new_pwd_usable=1 and recovery_email_changed=1 and id>994 and register_computer=%s and try_create_times<8 order by id limit 1'
        get_email = fetch_one_sql(conn, sql, hostname)
        if get_email:
            email_id = get_email['id']
            email = get_email['email']
            print(email)
        else:
            sql = 'SELECT * from email_info where emailIsUsed=0 and new_pwd_usable=1 and recovery_email_changed=1 and id>994 and register_computer="-" and try_create_times<8 order by id limit 1'
            get_email = fetch_one_sql(conn, sql)
            if get_email:
                email_id = get_email['id']
                email = get_email['email']
                print(email)
                sql = 'UPDATE email_info set register_computer=%s where email=%s'
                commit_sql(conn, sql, (hostname, email))
            else:
                flow_flag = 0
                print('No email')
                break
        # Get register account message
        if flow_flag == 1:
            while True:
                get_next_email = 0
                get_msg_success = 0
                msg_info_flag = 1
                sql = 'SELECT * from email_info where id=%s'
                try_create_times = fetch_one_sql(conn, sql, email_id)[
                    'try_create_times']
                print(int(try_create_times) + 1, 'times!')
                if int(try_create_times) > 7:
                    break
                sql = 'SELECT * from register_info where userInfoIsUsed=0 and email_id=%s and read_num<4 order by id limit 1'
                result = fetch_one_sql(conn, sql, email_id)
                if result:
                    get_msg_success = 1
                else:
                    sql = 'SELECT * from register_info where userInfoIsUsed=0 and read_num<4 order by id limit 1'
                    result = fetch_one_sql(conn, sql)
                    if result:
                        get_msg_success = 1
                if get_msg_success == 1:
                    sql = 'UPDATE email_info set try_create_times=try_create_times+1 where id=%s'
                    commit_sql(conn, sql, email_id)
                    register_id = result['id']
                    sql = 'UPDATE register_info set userInfoIsUsed=1, email_id=%s, read_num=read_num+1 where id=%s'
                    commit_sql(conn, sql, (email_id, register_id))
                    firstname = result['firstname']
                    lastname = result['lastname']
                    address = result['address']
                    city = result['city']
                    state = result['state']
                    zip_num = result['zip']
                    socialnumber = result['socialnumber']
                    birthdate = result['birthdate']
                    mobilenumber = result['mobilenumber']
                    pinnumber = result['pinnumber']
                    # operation
                    options = webdriver.ChromeOptions()
                    options.add_argument('disable-infobars')
                    # options.add_argument('user-agent="%s"' % agent)
                    p = subprocess.Popen('C:\\Users\\Administrator\\Desktop\\walmartMoneyCard\\911S5\\ProxyTool\\Autoproxytool.exe -changeproxy/US',
                                         shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    p.wait()
                    time.sleep(5)
                    driver = webdriver.Chrome(chrome_options=options)
                    driver.maximize_window()
                    try:
                        driver.get(
                            'https://www.walmartmoneycard.com/getacardnow')
                        time.sleep(5)
                    except:
                        driver.quit()
                        continue
                    if driver.page_source.find('This site can’t be reached') > -1:
                        driver.quit()
                        continue
                    try:
                        driver.find_element_by_id('FirstName').send_keys(
                            firstname)  # FirstName
                        driver.find_element_by_id(
                            'LastName').send_keys(lastname)  # LastName
                        driver.find_element_by_id('Address1').send_keys(
                            address)  # Street Address
                        driver.find_element_by_id(
                            'City').send_keys(city)  # City
                        Select(driver.find_element_by_id('State')
                               ).select_by_visible_text('' + state + '')
                        driver.find_element_by_id('ZIP').send_keys(zip_num)
                        driver.find_element_by_id(
                            'Email').send_keys(email)  # Email
                        driver.find_element_by_id('PhoneMobile').send_keys(
                            mobilenumber)  # PhoneMobile
                        driver.find_element_by_id('SocialSecurityNumber').send_keys(
                            socialnumber)  # SocialSecurityNumber
                        driver.find_element_by_id(
                            'BirthDate-Mirror').send_keys(birthdate)  # BirthDate
                        driver.find_element_by_id(
                            'CardPIN').send_keys(pinnumber)  # CardPIN
                        time.sleep(3)
                        driver.find_element_by_id('lbl-for-eca2').click()
                        time.sleep(3)
                        driver.find_element_by_id('Continue').click()
                        time.sleep(8)
                    except Exception as e:
                        msg_info_flag = 0
                        driver.quit()
                        time.sleep(1)
                        continue
                    if msg_info_flag == 1:
                        try:
                            all_info_1 = driver.find_elements_by_xpath(
                                '//span[@class="cardValue col3"]')
                            time.sleep(2)
                            bankRoutingNumber = all_info_1[0].text
                            directDepositAccountNumber = all_info_1[1].text
                            print(bankRoutingNumber, directDepositAccountNumber)
                            sql = 'UPDATE email_info set bankRoutingNumber=%s, directDepositAccountNumber=%s where email=%s'
                            commit_sql(conn, sql, (bankRoutingNumber,
                                                   directDepositAccountNumber, email))
                            driver.find_element_by_xpath(
                                '//button[@id="btn-ctn"]').click()
                            time.sleep(5)
                        except Exception as e:
                            msg_info_flag = 0
                            driver.quit()
                            time.sleep(1)
                            continue
                    if msg_info_flag == 1:
                        try:
                            all_info_2 = driver.find_elements_by_xpath(
                                '//span[@class="cardValue col3"]')
                            time.sleep(2)
                            temporaryCardNumber = all_info_2[0].text
                            expirationData = all_info_2[1].text
                            securityCode = all_info_2[2].text
                            print(temporaryCardNumber,
                                  expirationData, securityCode)
                            sql = 'UPDATE email_info set temporaryCardNumber=%s, expirationData=%s, securityCode=%s where email=%s'
                            commit_sql(conn, sql, (temporaryCardNumber,
                                                   expirationData, securityCode, email))
                            driver.find_element_by_id('dynamicData').click()
                            time.sleep(3)
                            driver.find_element_by_xpath(
                                '//div[@class="actions"]/a').click()
                            time.sleep(2)
                        except Exception as e:
                            msg_info_flag = 0
                            driver.quit()
                            time.sleep(1)
                            continue
                    if msg_info_flag == 1:
                        try:
                            user_id = create_random_str()
                            driver.find_element_by_id(
                                'TxtUserID').send_keys(user_id)
                            time.sleep(1)
                            user_pwd = create_pwd()
                            driver.find_element_by_id(
                                'TxtPassword').send_keys(user_pwd)
                            time.sleep(1)
                            driver.find_element_by_id(
                                'TxtConfirmPassword').send_keys(user_pwd)
                            time.sleep(1)
                            answer_1 = question_answer()
                            answer_2 = question_answer()
                            answer_3 = question_answer()
                            driver.find_element_by_id(
                                'TxtAnswer1').send_keys(answer_1)
                            time.sleep(2)
                            driver.find_element_by_id(
                                'TxtAnswer2').send_keys(answer_2)
                            time.sleep(2)
                            driver.find_element_by_id(
                                'TxtAnswer3').send_keys(answer_3)
                            time.sleep(2)
                            driver.find_element_by_id(
                                'confirm-dynamic').click()
                            time.sleep(5)
                            driver.find_element_by_id('btnConfirm').click()
                            time.sleep(3)
                            sql = 'UPDATE email_info set emailIsUsed=1, register_info_id=%s, user=%s, user_pwd=%s, answer_1=%s, answer_2=%s, answer_3=%s, create_time=%s where email=%s'
                            commit_sql(conn, sql, (register_id, user_id, user_pwd,
                                                   answer_1, answer_2, answer_3, current_time, email))
                            driver.find_element_by_id(
                                'btn-osconfirmation-submit').click()
                            time.sleep(3)
                            get_next_email = 1
                        except Exception as e:
                            pass
                    try:
                        driver.quit()
                    except Exception as e:
                        pass
                    time.sleep(5)
                    if get_next_email == 1:
                        break
        conn.close()


def create_random_str():
    random_str = ''
    ch = chr(random.randrange(ord('a'), ord('z') + 1))
    random_str += ch
    digit = random.randint(6, 11)
    for i in range(digit):
        temp = random.randrange(0, 2)
        if temp == 0:
            ch = chr(random.randrange(ord('a'), ord('z') + 1))
            random_str += ch
        elif temp == 1:
            ch = str((random.randrange(0, 10)))
            random_str += ch
    return random_str


def create_pwd():
    random_str = ''
    ch = chr(random.randrange(ord('a'), ord('z') + 1))
    random_str += ch
    digit = random.randint(9, 14)
    for i in range(digit):
        temp = random.randrange(0, 3)
        if temp == 0:
            ch = chr(random.randrange(ord('A'), ord('Z') + 1))
            random_str += ch
        elif temp == 1:
            ch = chr(random.randrange(ord('a'), ord('z') + 1))
            random_str += ch
        else:
            ch = str((random.randrange(0, 10)))
            random_str += ch
    return random_str


def question_answer():
    random_str = ''
    digit = random.randint(4, 8)
    for i in range(digit):
        ch = chr(random.randrange(ord('a'), ord('z') + 1))
        random_str += ch
    return random_str


if __name__ == '__main__':
    register_account()
