import time
import win32api
import win32gui
import win32con
import random
import pymysql
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import socket
import subprocess
import datetime
from dbconnection import fetch_one_sql, fetch_all_sql, commit_sql


def register_account():
    # p = subprocess.Popen('C:\\Users\\Administrator\\Desktop\\911S5 2018-05-23 fixed\\Client.exe',
    #                      shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    # time.sleep(8)
    # try_time = 1
    # while True:
    #     win32api.keybd_event(13, 0, 0, 0)
    #     win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)
    #     time.sleep(1)
    #     dialog1 = win32gui.FindWindow('ThunderRT6FormDC', '911 S5 3.1')
    #     login = win32gui.FindWindowEx(
    #         dialog1, 0, 'ThunderRT6CommandButton', None)
    #     win32gui.SendMessage(dialog1, win32con.WM_COMMAND, 0, login)
    #     time.sleep(5)
    #     try_time += 1
    #     if try_time > 5:
    #         break
    while True:
        flow_flag = 1
        current_time = datetime.datetime.now().strftime("%Y-%m-%d")
        hostname = socket.gethostname()
        conn = pymysql.connect(host='localhost', port=3306,
                               user='root', password='123456',
                               db='walmartmoneycard', charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
        sql = 'SELECT count(1) as allcount from email_info where emailIsUsed=1 and create_time=%s'
        all_count = fetch_one_sql(conn, sql, current_time)['allcount']
        if all_count > 1000:
            print('Today is enough!')
            break
        # # Get email
        sql = 'SELECT * from email_info where id>7174 and emailIsUsed=0 and register_computer=%s and try_create_times<6 order by id limit 1'
        get_email = fetch_one_sql(conn, sql, hostname)
        if get_email:
            email_id = get_email['id']
            email = get_email['email']
            print(email)
        else:
            sql = 'SELECT * from email_info where id>7174 and emailIsUsed=0 and register_computer="-" and try_create_times<6 order by id limit 1'
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
                get_msg_success = 0
                sql = 'SELECT * from register_info where id>19661 and userInfoIsUsed=0 and email_id=%s and read_num<4 order by id limit 1'
                result = fetch_one_sql(conn, sql, email_id)
                if result:
                    get_msg_success = 1
                    sql = 'SELECT * from email_info where id=%s'
                    try_create_times = fetch_one_sql(conn, sql, email_id)[
                        'try_create_times']
                    print(int(try_create_times) + 1, 'times!')
                    if int(try_create_times) > 5:
                        break
                else:
                    sql = 'SELECT * from register_info where id>19661 and userInfoIsUsed=0 and read_num<4 order by id limit 1'
                    result = fetch_one_sql(conn, sql)
                    if result:
                        get_msg_success = 1
                        sql = 'SELECT * from email_info where id=%s'
                        try_create_times = fetch_one_sql(conn, sql, email_id)[
                            'try_create_times']
                        print(int(try_create_times) + 1, 'times!')
                        if int(try_create_times) > 5:
                            break
                    else:
                        print('Not register info!')
                        get_msg_success = 4
                        break
                if get_msg_success == 1:
                    sql = 'UPDATE email_info set try_create_times=try_create_times+1 where id=%s'
                    commit_sql(conn, sql, email_id)
                    register_id = result['id']
                    print('Register ID:', register_id)
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
                    sql = 'SELECT cardType from config where id=1'
                    cardType_r = fetch_one_sql(conn, sql)
                    if cardType_r:
                        cardType = cardType_r['cardType']
                    while True:
                        p = subprocess.Popen('C:\\Users\\Administrator\\Desktop\\911S5 2018-05-23 fixed\\ProxyTool\\Autoproxytool.exe -changeproxy/all/%s/%s -citynolimit' % (state, city),
                                             shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                        p.wait()
                        time.sleep(5)
                        options = webdriver.ChromeOptions()
                        options.add_argument('disable-infobars')
                        driver = webdriver.Chrome(options=options)
                        driver.maximize_window()
                        if cardType == 1:
                            driver.get(
                                'https://www.walmartmoneycard.com/getacardnow')
                            time.sleep(5)
                        elif cardType == 2:
                            driver.get('https://secure.greendot.com/signup')
                            time.sleep(5)
                        if driver.page_source.find('This site can’t be reached') > -1:
                            driver.quit()
                            continue
                        else:
                            break
                    if cardType == 1:
                        get_next_email = walmart_card(
                            driver, conn, register_id, firstname, lastname, address, city, zip_num, email, mobilenumber, socialnumber, birthdate, pinnumber, current_time)
                    elif cardType == 2:
                        get_next_email = green_dot_bank(driver, conn, register_id, firstname, lastname, address, city,
                                       zip_num, email, mobilenumber, socialnumber, birthdate, pinnumber, current_time)
                if get_next_email == 1:
                    break
        if get_msg_success == 4:
            break
        conn.close()


def walmart_card(driver,
                 conn,
                 register_id,
                 firstname,
                 lastname,
                 address,
                 city,
                 zip_num,
                 email,
                 mobilenumber,
                 socialnumber,
                 birthdate,
                 pinnumber,
                 current_time,
                 get_next_email=0):
    next_step = 1
    try:
        card_type = random.randint(1, 2)
        if card_type == 2:
            driver.find_element_by_xpath(
                '//label[@for="cardtype-mastercard"]').click()
            time.sleep(1)
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
        time.sleep(3)
        try:
            driver.find_element_by_id('btnSendMyCard').click()
        except:
            pass
        time.sleep(5)
    except Exception as e:
        next_step = 0

    if next_step == 1:
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
            next_step = 0

    if next_step == 1:
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
            next_step = 0

    if next_step == 1:
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
            sql = 'UPDATE email_info set cardType=1, emailIsUsed=1, register_info_id=%s, user=%s, user_pwd=%s, answer_1=%s, answer_2=%s, answer_3=%s, create_time=%s, register_computer="-" where email=%s'
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

    return get_next_email


def green_dot_bank(driver,
                   conn,
                   register_id,
                   firstname,
                   lastname,
                   address,
                   city,
                   zip_num,
                   email,
                   mobilenumber,
                   socialnumber,
                   birthdate,
                   pinnumber,
                   current_time,
                   get_next_email=0):
    next_step = 1
    input_first_name_XP = '//input[@id="FirstName"]'
    is_normal = explicit_wait(driver, "VOEL", [input_first_name_XP, "XPath"], 10, False)
    if is_normal:
        try:
            driver.find_element_by_xpath(input_first_name_XP).send_keys(firstname)
            time.sleep(1)
            driver.find_element_by_id('LastName').send_keys(lastname)
            time.sleep(1)
            driver.find_element_by_id('Street').send_keys(address)
            time.sleep(1)
            driver.find_element_by_id('Zip').send_keys(zip_num)
            time.sleep(1)
            driver.find_element_by_id('Email').send_keys(email)
            time.sleep(1)
            driver.find_element_by_id('Phone').send_keys(mobilenumber)
            time.sleep(1)
            driver.find_element_by_id('SSN').send_keys(socialnumber)
            time.sleep(1)
            driver.find_element_by_id('DateOfBirth').send_keys(birthdate)
            time.sleep(1)
            driver.find_element_by_id('AtmPin').send_keys(pinnumber)
            time.sleep(1)
            driver.find_element_by_id('IsAgreedToECA').click()
            time.sleep(1)
            driver.find_element_by_xpath(
                '//form[@id="main-form"]/section[2]/div/div/a').click()
            time.sleep(5)
            try:
                driver.find_element_by_xpath('//button[@class="smallbutton"]').click()
            except:
                pass
        except:
            pass
    else:
        sql = 'UPDATE register_info set userInfoIsUsed=0 where id=%s'
        commit_sql(conn, sql, register_id)
        next_step = 0

    if next_step == 1:
        bankRoutingNumber_XP = '//tbody//tr[2]/td'
        bankRoutingNumber_result = explicit_wait(driver, "VOEL", [bankRoutingNumber_XP, "XPath"], 10, False)
        if bankRoutingNumber_result:
            bankRoutingNumber = driver.find_element_by_xpath(bankRoutingNumber_XP).text
            directDepositAccountNumber = driver.find_element_by_xpath('//tbody//tr[3]/td').text
            print(bankRoutingNumber, directDepositAccountNumber)
            sql = 'UPDATE email_info set bankRoutingNumber=%s, directDepositAccountNumber=%s where email=%s'
            commit_sql(conn, sql, (bankRoutingNumber,
                                   directDepositAccountNumber, email))
            driver.find_element_by_xpath('//button[text()="CONTINUE"]').click()
        else:
            next_step = 0

    if next_step == 1:
        temporaryCardNumber_XP = '//main[@class="page-main"]//section[2]//p[1]'
        temporaryCardNumber_result = explicit_wait(driver, "VOEL", [temporaryCardNumber_XP, "XPath"], 10, False)
        if temporaryCardNumber_result:
            temporaryCardNumber = driver.find_element_by_xpath(temporaryCardNumber_XP).text
            if temporaryCardNumber:
                temporaryCardNumber = temporaryCardNumber.split(':')[-1].strip().replace('-', ' ')
            expirationData = driver.find_element_by_xpath('//main[@class="page-main"]//section[2]//p[2]').text
            expirationData_split = expirationData.split(':')[-1].strip().split('/')
            expirationData = expirationData_split[0] + '/' + expirationData_split[-1][-2:]
            securityCode = driver.find_element_by_xpath('//main[@class="page-main"]//section[2]//p[3]').text
            securityCode = securityCode.split(':')[-1].strip()
            print(temporaryCardNumber,
                  expirationData, securityCode)
            sql = 'UPDATE email_info set temporaryCardNumber=%s, expirationData=%s, securityCode=%s where email=%s'
            commit_sql(conn, sql, (temporaryCardNumber,
                                   expirationData, securityCode, email))
            driver.find_element_by_xpath('//main[@class="page-main"]//section[2]//button').click()
            time.sleep(3)
            driver.find_element_by_xpath('//div[@id="modal-info"]//a').click()
        else:
            next_step = 0

    if next_step == 1:
        input_id_XP = '//input[@id="TxtUserID"]'
        input_id_result = explicit_wait(driver, "VOEL", [input_id_XP, "XPath"], 15, False)
        if input_id_result:
            user_id = create_random_str()
            driver.find_element_by_xpath(input_id_XP).send_keys(user_id)
            time.sleep(1)
            user_pwd = create_pwd()
            driver.find_element_by_xpath('//input[@id="TxtPassword"]').send_keys(user_pwd)
            time.sleep(1)
            driver.find_element_by_xpath('//input[@id="TxtConfirmPassword"]').send_keys(user_pwd)
            time.sleep(1)
            answer_1 = question_answer()
            driver.find_element_by_xpath('//input[@id="TxtAnswer1"]').send_keys(answer_1)
            time.sleep(1)
            driver.find_element_by_xpath('//input[@id="TxtConfirmEmail"]').send_keys(email)
            time.sleep(1)
            driver.find_element_by_xpath('//input[@id="btnContinue"]').click()
            last_submit_XP = '//input[@id="btnConfirm"]'
            explicit_wait(driver, "VOEL", [last_submit_XP, "XPath"])
            last_submit = driver.find_element_by_xpath(last_submit_XP)
            (ActionChains(driver)
             .move_to_element(last_submit)
             .click()
             .perform())
            sql = 'UPDATE email_info set cardType=2, emailIsUsed=1, register_info_id=%s, user=%s, user_pwd=%s, answer_1=%s, create_time=%s, register_computer="-" where email=%s'
            commit_sql(conn, sql, (register_id, user_id, user_pwd,
                                   answer_1, current_time, email))

            end_submit_XP = '//div[@class="btn-group"]//a[2]'
            explicit_wait(driver, "VOEL", [end_submit_XP, "XPath"])
            end_submit = driver.find_element_by_xpath(end_submit_XP)
            (ActionChains(driver)
             .move_to_element(end_submit)
             .click()
             .perform())
            time.sleep(3)
            get_next_email = 1

    try:
        driver.quit()
    except Exception as e:
        pass
    time.sleep(5)

    return get_next_email


def explicit_wait(driver, track, ec_params, timeout=35, notify=True):
    if not isinstance(ec_params, list):
        ec_params = [ec_params]

    # find condition according to the tracks
    if track == "VOEL":
        elem_address, find_method = ec_params
        ec_name = "visibility of element located"

        find_by = (By.XPATH if find_method == "XPath" else
                   By.CSS_SELECTOR if find_method == "CSS" else
                   By.CLASS_NAME)
        locator = (find_by, elem_address)
        condition = EC.visibility_of_element_located(locator)

    elif track == "TC":
        expect_in_title = ec_params[0]
        ec_name = "title contains '{}' string".format(expect_in_title)

        condition = EC.title_contains(expect_in_title)

    elif track == "SO":
        ec_name = "staleness of"
        element = ec_params[0]
        condition = EC.staleness_of(element)

    # generic wait block
    try:
        wait = WebDriverWait(driver, timeout)
        result = wait.until(condition)

    except:
        if notify is True:
            print(
                "Timed out with failure while explicitly waiting until {}!\n"
                .format(ec_name))
        return False

    return result


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
