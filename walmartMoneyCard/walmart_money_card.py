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
        get_msg_success = 0
        hostname = socket.gethostname()
        conn = pymysql.connect(host='172.16.253.100', port=3306,
                               user='root', password='123456',
                               db='walmartmoneycard', charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
        # # Get email
        sql = 'SELECT * from email_info where emailIsUsed=0 and register_computer=%s'
        get_email = fetch_one_sql(conn, sql, hostname)
        if get_email:
            email_id = get_email['Id']
            email = get_email['email']
        else:
            sql = 'SELECT * from email_info where emailIsUsed=0 and register_computer="-" order by id limit 1'
            get_email = fetch_one_sql(conn, sql)
            if get_email:
                email_id = get_email['Id']
                email = get_email['email']
                sql = 'UPDATE email_info set register_computer=%s where email=%s'
                commit_sql(conn, sql, (hostname, email))
            else:
                flow_flag = 0
        # Get register account message
        if flow_flag == 1:
            while True:
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
                    register_id = result['Id']
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
                    driver.get('https://www.walmartmoneycard.com/getacardnow')
                    time.sleep(5)
                    if driver.page_source.find('This site can’t be reached') > -1:
                        continue
                    driver.find_element_by_id('FirstName').send_keys(
                        firstname)  # FirstName
                    driver.find_element_by_id(
                        'LastName').send_keys(lastname)  # LastName
                    driver.find_element_by_id('Address1').send_keys(
                        address)  # Street Address
                    driver.find_element_by_id('City').send_keys(city)  # City
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
                    page_1 = driver.current_url
                    if page_1 != 'https://www.walmartmoneycard.com/getacardnow/direct-deposit-enrollment':
                        print('Error!')
                        sql = 'UPDATE register_info set userInfoIsUsed=1, email_id=0 where id=%s'
                        commit_sql(conn, sql, register_id)
                        driver.quit()
                        time.sleep(3)
                        continue
                    page_2 = driver.current_url
                    all_info_1 = driver.find_elements_by_xpath(
                        '//span[@class="cardValue col3"]')
                    bankRoutingNumber = all_info_1[0].text
                    directDepositAccountNumber = all_info_1[1].text
                    print(bankRoutingNumber, directDepositAccountNumber)
                    sql = 'UPDATE email_info set bankRoutingNumber=%s, directDepositAccountNumber=%s where email=%s'
                    commit_sql(conn, sql, (bankRoutingNumber,
                                           directDepositAccountNumber, email))
                    driver.find_element_by_xpath(
                        '//button[@id="btn-ctn"]').click()
                    time.sleep(5)
                    all_info_2 = driver.find_elements_by_xpath(
                        '//span[@class="cardValue col3"]')
                    temporaryCardNumber = all_info_2[0].text
                    expirationData = all_info_2[1].text
                    securityCode = all_info_2[2].text
                    print(temporaryCardNumber, expirationData, securityCode)
                    sql = 'UPDATE email_info set temporaryCardNumber=%s, expirationData=%s, securityCode=%s where email=%s'
                    commit_sql(conn, sql, (temporaryCardNumber,
                                           expirationData, securityCode, email))
                    driver.find_element_by_id('dynamicData').click()
                    time.sleep(3)
                    driver.find_element_by_xpath(
                        '//div[@class="actions"]/a').click()
                    user_id = create_random_str()
                    try:
                        driver.find_element_by_id(
                            'TxtUserID').send_keys(user_id)
                        time.sleep(1)
                    except Exception as e:
                        flow_flag = 0
                if flow_flag == 1:
                    break
            if flow_flag == 1:
                user_pwd = create_pwd()
                driver.find_element_by_id('TxtPassword').send_keys(user_pwd)
                time.sleep(1)
                driver.find_element_by_id(
                    'TxtConfirmPassword').send_keys(user_pwd)
                time.sleep(1)
                answer_1 = question_answer()
                answer_2 = question_answer()
                answer_3 = question_answer()
                driver.find_element_by_id('TxtAnswer1').send_keys(answer_1)
                time.sleep(2)
                driver.find_element_by_id('TxtAnswer2').send_keys(answer_2)
                time.sleep(2)
                driver.find_element_by_id('TxtAnswer3').send_keys(answer_3)
                time.sleep(2)
                driver.find_element_by_id('confirm-dynamic').click()
                time.sleep(5)
                driver.find_element_by_id('btnConfirm').click()
                time.sleep(3)
                if driver.page_source.find('That user ID is already taken. Please select another user ID.') > -1:
                    driver.find_element_by_id('TxtUserID').clear()
                    user_id = create_random_str()
                    time.sleep(1)
                    driver.find_element_by_id('TxtUserID').send_keys(user_id)
                try:
                    sql = 'UPDATE email_info set emailIsUsed=1, register_info_id=%s, user=%s, user_pwd=%s, answer_1=%s, answer_2=%s, answer_3=%s, create_time=%s where email=%s'
                    commit_sql(conn, sql, (register_id, user_id, user_pwd,
                                           answer_1, answer_2, answer_3, current_time, email))
                except Exception as e:
                    with open('%s.txt' % email, 'w', encoding='utf-8') as fp:
                        fp.write(email, register_id, user_id, user_pwd,
                                 answer_1, answer_2, answer_3, current_time)
                driver.find_element_by_id('btn-osconfirmation-submit').click()
                time.sleep(3)
                driver.quit()
                time.sleep(10)
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
    digit = random.randint(10, 15)
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
