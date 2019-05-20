import os
import re
import pymysql
import time
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import win32api
import win32gui
import win32con
import subprocess
import uuid
import receiveEmail
import change_computer_info


def main():
    conn = pymysql.connect(host='localhost', port=3306,
                           user='root', password='123456',
                           db='walmartmoneycard', charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    error_code = ''
    step_flag = 1
    get_info_success = 0
    register_pp_mac = get_mac()
    sql = 'SELECT * from email_info where id>7174 and emailIsUsed=1 and register_pp_mac=%s'
    register_info = fetch_one_sql(conn, sql, register_pp_mac)
    if register_info:
        get_info_success = 1
        email = register_info['email']
        print(email)
    else:
        sql = 'SELECT * from email_info where id>7174 and emailIsUsed=1 and created_paypal_account=0 and register_pp_mac="-" and temporaryCardNumber!="" limit 1'
        register_info = fetch_one_sql(conn, sql)
        if register_info:
            get_info_success = 1
            email = register_info['email']
            print(email)
            sql = 'UPDATE email_info set register_pp_mac=%s where email=%s'
            commit_sql(conn, sql, (register_pp_mac, email))
            change_computer_info.verify()
        else:
            print('Not data!')
    if get_info_success == 1:
        email_pwd = register_info['email_pwd']
        paypal_pwd = register_info['email_pwd'] + '@pp'
        recovery_email = register_info['recovery_email']
        card_num = register_info['temporaryCardNumber']
        expiration_date = register_info['expirationData']
        card_csc = register_info['securityCode']
        register_info_id = register_info['register_info_id']
        created_flag = register_info['created_paypal_account']
        confirm_identity_state = register_info['confirm_identity']
        if created_flag > 0:
            login_separately = 1
        else:
            login_separately = 0
        sql = 'SELECT * from register_info where id=%s'
        personal_info = fetch_one_sql(conn, sql, register_info_id)
        if personal_info:
            firstname = personal_info['firstname']
            lastname = personal_info['lastname']
            address = personal_info['address']
            city = personal_info['city']
            state = personal_info['state']
            zip_num = personal_info['zip']
            phone_num = personal_info['mobilenumber']
        if created_flag < 3 or confirm_identity_state == 0:
            p = subprocess.Popen('C:\\Users\\Administrator\\Desktop\\911S5 2018-05-23 fixed\\Client.exe',
                                 shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            time.sleep(8)
            try_time = 1
            while True:
                win32api.keybd_event(13, 0, 0, 0)
                win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)
                time.sleep(1)
                dialog1 = win32gui.FindWindow('ThunderRT6FormDC', '911 S5 3.1')
                login = win32gui.FindWindowEx(
                    dialog1, 0, 'ThunderRT6CommandButton', None)
                win32gui.SendMessage(dialog1, win32con.WM_COMMAND, 0, login)
                time.sleep(5)
                try_time += 1
                if try_time > 5:
                    break
            while True:
                p = subprocess.Popen('C:\\Users\\Administrator\\Desktop\\911S5 2018-05-23 fixed\\ProxyTool\\Autoproxytool.exe -changeproxy/all/%s/%s -citynolimit' % (state, city),
                                     shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                p.wait()
                time.sleep(5)
                modify_port()
                time.sleep(3)
                p = subprocess.Popen('Proxifier.exe C:\\Users\\Administrator\\Desktop\\work\\register_paypal\\1558888888.ppx',
                                     shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                p.wait()
                time.sleep(3)
                options = webdriver.ChromeOptions()
                options.add_argument('disable-infobars')
                driver = webdriver.Chrome(chrome_options=options)
                driver.maximize_window()
                # 个人号
                if login_separately == 0:
                    driver.get('https://www.paypal.com/welcome/signup')
                elif login_separately == 1:
                    driver.get('https://www.paypal.com/us/signin')
                # 商业号 https://www.paypal.com/bizsignup
                time.sleep(3)
                if driver.page_source.find('This site can’t be reached') > -1:
                    print('Net error!')
                    driver.quit()
                    time.sleep(1)
                    continue
                else:
                    break
            if created_flag == 0:
                driver.find_element_by_id(
                    'paypalAccountData_firstName').send_keys(firstname)
                time.sleep(1)
                driver.find_element_by_id(
                    'paypalAccountData_lastName').send_keys(lastname)
                time.sleep(1)
                driver.find_element_by_id(
                    'paypalAccountData_email').send_keys(email)
                time.sleep(1)
                driver.find_element_by_id(
                    'paypalAccountData_password').send_keys(paypal_pwd)
                time.sleep(2)
                # 确认密码
                try:
                    driver.find_element_by_id(
                        'paypalAccountData_confirmPassword').send_keys(paypal_pwd)
                    time.sleep(1)
                except:
                    pass
                try:
                    error_code = driver.find_element_by_xpath(
                        '//form//p/span').text
                    print(error_code)
                except:
                    pass
                if error_code == 'It looks like you already signed up. Log in to your account.':
                    print('Already signed up')
                    sql = 'UPDATE email_info set created_paypal_account=-1 where email=%s'
                    commit_sql(conn, sql, email)
                    step_flag = 0
                else:
                    driver.find_element_by_xpath(
                        '//div[@class="btnGrp"]/button').click()
                    input_address_XP = '//div[@data-label-content="Street address"]//input'
                    explicit_wait(driver, "VOEL", [input_address_XP, "XPath"])
                    driver.find_element_by_xpath(input_address_XP).send_keys(address)
                    time.sleep(1)
                    driver.find_element_by_id(
                        'paypalAccountData_city').send_keys(city)
                    time.sleep(1)
                    Select(driver.find_element_by_id(
                        "paypalAccountData_state")).select_by_value(state)
                    time.sleep(1)
                    driver.find_element_by_id(
                        'paypalAccountData_zip').send_keys(zip_num)
                    time.sleep(1)
                    driver.find_element_by_id(
                        'paypalAccountData_phone').send_keys(phone_num)
                    time.sleep(1)
                    driver.find_element_by_xpath(
                        '//div[@class="signupCheckBox"]//label').click()
                    time.sleep(1)
                    driver.find_element_by_xpath(
                        '//div[@class="btnGrp"]/button').click()
                    time.sleep(5)
                    info_error = ''
                    try:
                        info_error = driver.find_element_by_xpath(
                            '//div[@class="notification"]//span').text
                    except:
                        pass
                    if info_error:
                        print('Info Error!')
                        sql = 'UPDATE email_info set emailIsUsed=9 where email=%s'
                        commit_sql(conn, sql, email)
                    else:
                        sql = 'UPDATE email_info set paypal_pwd=%s, created_paypal_account=1 where email=%s'
                        commit_sql(conn, sql, (paypal_pwd, email))
                        created_flag = 1
                        try_set_up = 0
                        while True:
                            set_up_profile = ''
                            try:
                                set_up_profile = driver.find_element_by_xpath(
                                    '//a[@name="notnow"]')
                            except:
                                pass
                            if set_up_profile:
                                set_up_profile.click()
                                time.sleep(3)
                                break
                            else:
                                try_set_up += 1
                                time.sleep(3)
                            if try_set_up > 2:
                                break
            # 绑卡
            if created_flag == 1 and step_flag == 1:
                if login_separately == 1:
                    login_flag = login_paypal(driver, email, paypal_pwd)
                    if login_flag == 1:
                        created_flag = link_card(
                            driver, conn, email, card_num, expiration_date, card_csc)
                        login_separately = 0
                else:
                    next_step_page_XP = '//div[@class="formLink "]//button'
                    explicit_wait(driver, "VOEL", [next_step_page_XP, "XPath"])
                    next_step_page = driver.find_element_by_xpath(next_step_page_XP)
                    (ActionChains(driver)
                     .move_to_element(next_step_page)
                     .click()
                     .perform())

                    input_cardNumber_XP = '//input[@id="cardData_cardNumber"]'
                    explicit_wait(driver, "VOEL", [input_cardNumber_XP, "XPath"])
                    driver.find_element_by_xpath(input_cardNumber_XP).send_keys(card_num)
                    time.sleep(1)
                    driver.find_element_by_id(
                        'cardData_expiryDate').send_keys(expiration_date)
                    time.sleep(1)
                    driver.find_element_by_id(
                        'cardData_csc').send_keys(card_csc)
                    time.sleep(1)
                    driver.find_element_by_xpath(
                        '//div[@class="btnGrp"]/button').click()
                    time.sleep(5)
                    while True:
                        end_flag = ''
                        try:
                            end_flag = driver.find_element_by_xpath(
                                '//form//h1').text
                            print(end_flag)
                        except:
                            pass
                        if end_flag == 'Your account’s ready to use! Shop, send money, and more with PayPal':
                            sql = 'UPDATE email_info set created_paypal_account=2 where email=%s'
                            commit_sql(conn, sql, email)
                            time.sleep(1)
                            created_flag = 2
                            print('Successful!')
                            break
                        else:
                            time.sleep(3)
            if created_flag == 2 and step_flag == 1:
                if login_separately == 1:
                    login_paypal(driver, email, paypal_pwd)
                # 判断邮箱类型
                email_type = email.split('@')[-1]
                if email_type == 'gmail.com':
                    print('Gmail!')
                    login_gmail(driver, conn, email, email_pwd,
                                paypal_pwd, recovery_email)
                elif email_type == 'yahoo.com':
                    print('Yahoo!')
                    login_yahoo(driver, conn, email, email_pwd, paypal_pwd)
            if confirm_identity_state == 0:
                sql = 'SELECT * from paypal_confirm_info where used=0 and read_num<3 order by id limit 1'
                confirm_info = fetch_one_sql(conn, sql)
                if confirm_info:
                    confirm_info_id = confirm_info['id']
                    confirm_user = confirm_info['user']
                    confirm_pwd = confirm_info['user_pwd']
                    routing_number = confirm_info['routing_number']
                    account_number = confirm_info['account_number']
                    confirm_type = confirm_info['pay_type']
                    sql = 'UPDATE paypal_confirm_info set used=1, read_num=read_num+1 where id=%s'
                    commit_sql(conn, sql, confirm_info_id)
                    if created_flag == 3:
                        login_paypal(driver, email, paypal_pwd) 
                    confirm_identity(conn, driver, email, confirm_info_id, confirm_user, confirm_pwd, routing_number, account_number, confirm_type)
                else:
                    print('No Confirm Info!')
            time.sleep(3)
            driver.get('https://www.bsdress.com/ip.php')
            time.sleep(5)
            ip_911 = driver.find_element_by_css_selector('body').text
            print(ip_911)
            if ip_911:
                sql = 'UPDATE email_info set ip911=%s where email=%s'
                commit_sql(conn, sql, (ip_911, email))
                time.sleep(2)
            p = subprocess.Popen('cmd.exe /c' + 'taskkill /F /im Client.exe',
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            p.wait()
            time.sleep(1)
            p = subprocess.Popen('cmd.exe /c' + 'taskkill /F /im Proxifier.exe',
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            p.wait()
            time.sleep(2)
            driver.quit()
            time.sleep(1)
            os.system('shutdown -s -t 8')
            time.sleep(3)
            p = subprocess.Popen('cmd.exe /c' + 'taskkill /F /im CMacService.exe',
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            time.sleep(1)
            p = subprocess.Popen('cmd.exe /c' + 'taskkill /F /im CMacTray.exe',
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            time.sleep(1)
            p = subprocess.Popen('cmd.exe /c' + 'taskkill /F /im python.exe',
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            time.sleep(10)
        else:
            print('Have already registered!')


def activate(driver, conn, email, paypal_pwd, activate_type):

    input_password_XP = '//input[@id="password"]'
    explicit_wait(driver, "VOEL", [input_password_XP, "XPath"])
    time.sleep(8)
    driver.find_element_by_xpath(input_password_XP).send_keys(paypal_pwd)
    time.sleep(1)
    driver.find_element_by_xpath('//button[@id="btnLogin"]').click()
    time.sleep(1)
    if activate_type == 1:
        sql = 'UPDATE email_info set created_paypal_account=3 where email=%s'
        commit_sql(conn, sql, email)
        time.sleep(5)
        try:
            driver.find_element_by_xpath(
                '//p[@class="secondaryLink"]/a').click()
            time.sleep(3)
        except Exception as e:
            print(e)
    if activate_type == 0:
        while True:
            msg_code = ''
            try:
                msg_code = driver.find_element_by_xpath('//form/div[1]/p').text
            except:
                pass
            if msg_code == 'Your email is all set!':
                time.sleep(1)
                # Not now
                driver.find_element_by_xpath(
                    '//button[@id="/appData/action"]').click()
                time.sleep(5)
                sql = 'UPDATE email_info set created_paypal_account=3 where email=%s'
                commit_sql(conn, sql, email)
                break
            else:
                time.sleep(3)


def login_gmail(driver, conn, email, email_pwd, paypal_pwd, recovery_email):
    js = 'window.open("https://accounts.google.com/ServiceLogin?continue=https%3A%2F%2Fmail.google.com%2Fmail%2F&service=mail&sacu=1&rip=1");'
    driver.execute_script(js)
    windows = driver.window_handles
    # Gets the new page handle
    driver.switch_to.window(windows[1])
    time.sleep(3)
    if driver.page_source.find('This site can’t be reached') > -1:
        print('Net Error!')
        driver.refence()
        time.sleep(5)
    try:
        # element = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.ID, 'identifierId')))
        # element.send_keys(email)
        driver.find_element_by_id('identifierId').send_keys(email)
        time.sleep(1)
        driver.find_element_by_id('identifierNext').click()
        time.sleep(5)
    except Exception as e:
        pass
    try:
        driver.find_element_by_name('password').send_keys(email_pwd)
        driver.find_element_by_id('passwordNext').click()
        time.sleep(3)
        error_info = driver.find_element_by_xpath(
            '//div[@class="GQ8Pzc"]')
        if error_info:
            print('Password error!')
    except Exception as e:
        pass
    try:
        time.sleep(5)
        element1 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//li[@class="C5uAFc"]/div')))
        element1.click()
        time.sleep(3)
        element2 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'identifierId')))
        element2.send_keys(recovery_email)
        driver.find_element_by_xpath(
            '//div[@class="qhFLie"]/div').click()
    except Exception as e:
        pass
    try:
        element3 = WebDriverWait(driver, 5).until(
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
        time.sleep(3)
    except Exception as e:
        pass
    try:
        driver.find_element_by_xpath(
            '//button[@name="welcome_dialog_next"]').click()
        time.sleep(2)
        driver.find_element_by_xpath('//button[@name="ok"]').click()
        time.sleep(2)
    except:
        pass
    try:
        email_element = driver.find_elements_by_xpath(
            '//div[@class="yW"]//span[@name="service@paypal.com"]')
        email_element[0].click()
        time.sleep(3)
    except:
        pass
    while True:
        link_element = ''
        try:
            link_element = driver.find_element_by_xpath(
                '//a[text()="Confirm My Email"]')
        except:
            pass
        if link_element:
            link_element.click()
            time.sleep(5)
            break
    windows = driver.window_handles
    # Gets the new page handle
    driver.switch_to.window(windows[2])
    time.sleep(3)
    activate(driver, conn, email, paypal_pwd)


def login_yahoo(driver, conn, email, email_pwd, paypal_pwd):
    activate_flag = 0
    activate_type = 0
    time.sleep(5)
    activate_url = receiveEmail.get_url(email, email_pwd)
    if activate_url == 'No email':
        # 登录重新发送邮件
        print(activate_url)
        try:
            driver.find_element_by_xpath('//div[@class="myAccount"]/a').click()
            time.sleep(3)
        except:
            pass
        email_flag_XP = '//a[@data-name="confirm_your_email"]'
        explicit_wait(driver, "VOEL", [email_flag_XP, "XPath"])
        email_flag = driver.find_element_by_xpath(email_flag_XP)
        (ActionChains(driver)
         .move_to_element(email_flag)
         .click()
         .perform())
        time.sleep(3)
        driver.find_element_by_xpath(
            '//button[@id="js_unconfirmedEmail"]').click()
        time.sleep(1)
        activate_flag = 1
        if activate_flag == 1:
            time.sleep(10)
            activate_url = receiveEmail.get_url(email, email_pwd)
            activate_type = 1
    else:
        activate_flag = 1
    if activate_flag == 1:
        js = 'window.open("%s");' % activate_url
        driver.execute_script(js)
        windows = driver.window_handles
        # Gets the new page handle
        driver.switch_to.window(windows[1])
        time.sleep(3)
        activate(driver, conn, email, paypal_pwd, activate_type)


def login_paypal(driver, email, paypal_pwd):
    input_email_XP = '//input[@id="email"]'
    explicit_wait(driver, "VOEL", [input_email_XP, "XPath"])
    driver.find_element_by_xpath(input_email_XP).send_keys(email)
    time.sleep(1)
    try:
        driver.find_element_by_id('btnNext').click()
    except:
        pass
    input_password_XP = '//input[@id="password"]'
    explicit_wait(driver, "VOEL", [input_password_XP, "XPath"])
    driver.find_element_by_xpath(input_password_XP).send_keys(paypal_pwd)
    time.sleep(1)
    driver.find_element_by_id('btnLogin').click()
    time.sleep(3)
    try:
        driver.find_element_by_xpath(
            '//p[@class="secondaryLink"]/a').click()
        time.sleep(3)
    except:
        pass
    home_element = ''
    home_element_XP = '//a[text()="Summary"]'
    explicit_wait(driver, "VOEL", [home_element_XP, "XPath"])
    try:
        home_element = driver.find_element_by_xpath(home_element_XP).text
    except:
        pass
    if home_element == 'Summary':
        login_flag = 1
    else:
        login_flag = 0
    return login_flag


def link_card(driver, conn, email, card_num, expiration_date, card_csc, created_flag=1):

    link_button_XP = '//a[@id="bankCardLinkBankOrCard"]'
    explicit_wait(driver, "VOEL", [link_button_XP, "XPath"])
    link_button = driver.find_element_by_xpath(link_button_XP)
    (ActionChains(driver)
     .move_to_element(link_button)
     .click()
     .perform())

    link_card_XP = '//a[@data-name="addCard"]'
    explicit_wait(driver, "VOEL", [link_card_XP, "XPath"])
    link_card = driver.find_element_by_xpath(link_card_XP)
    (ActionChains(driver)
     .move_to_element(link_card)
     .click()
     .perform())

    next_element_XP = '//a[@data-name="linkManually"]'
    explicit_wait(driver, "VOEL", [next_element_XP, "XPath"])
    next_element = driver.find_element_by_xpath(next_element_XP)
    (ActionChains(driver)
     .move_to_element(next_element)
     .click()
     .perform())

    cardNumber_XP = '//input[@id="cardNumber"]'
    explicit_wait(driver, "VOEL", [cardNumber_XP, "XPath"])
    driver.find_element_by_xpath(cardNumber_XP).send_keys(card_num)
    time.sleep(1)
    driver.find_element_by_id('expDate').send_keys(expiration_date)
    time.sleep(1)
    driver.find_element_by_id('verificationCode').send_keys(card_csc)
    time.sleep(1)
    driver.find_element_by_name('detailsSubmit').click()
    time.sleep(5)
    try:
        driver.find_element_by_xpath(
            '//a[@data-name="addCardDone"]').click()
        time.sleep(2)
        sql = 'UPDATE email_info set created_paypal_account=2 where email=%s'
        commit_sql(conn, sql, email)
        time.sleep(1)
        created_flag = 2
        driver.find_element_by_xpath('//a[text()="Summary"]').click()
        time.sleep(3)
    except:
        pass

    return created_flag


def confirm_identity(conn, driver, email, confirm_info_id, confirm_user, confirm_pwd, routing_number, account_number, confirm_type):

    accountNumberLast4 = account_number[-4:]
    click_bank_link_XP = '//a[@id="bankCardLinkBankOrCard"]'
    explicit_wait(driver, "VOEL", [click_bank_link_XP, "XPath"])
    click_bank_link = driver.find_element_by_xpath(click_bank_link_XP)
    (ActionChains(driver)
     .move_to_element(click_bank_link)
     .click()
     .perform())

    add_bank_link_XP = '//a[@data-name="addBank"]'
    explicit_wait(driver, "VOEL", [add_bank_link_XP, "XPath"])
    add_bank_link = driver.find_element_by_xpath(add_bank_link_XP)
    (ActionChains(driver)
     .move_to_element(add_bank_link)
     .click()
     .perform())

    click_bank_logo_XP = '//a[@name="manualAddBank"]'
    explicit_wait(driver, "VOEL", [click_bank_logo_XP, "XPath"])
    click_bank_logo = driver.find_element_by_xpath(click_bank_logo_XP)
    (ActionChains(driver)
     .move_to_element(click_bank_logo)
     .click()
     .perform())

    input_routing_XP = '//input[@name="routingNumberGroup"]'
    explicit_wait(driver, "VOEL", [input_routing_XP, "XPath"])
    if confirm_type == 'Savings':
        time.sleep(3)
        # driver.find_element_by_xpath('//label[@for="savingsRadioBtn"]').click()
        driver.find_element_by_xpath('//input[@id="savingsRadioBtn"]').click()
    time.sleep(2)
    driver.find_element_by_xpath(input_routing_XP).send_keys(routing_number)
    time.sleep(1)

    # Account Number 
    driver.find_element_by_name('accountNumberInput').send_keys(account_number)
    time.sleep(1)
    driver.find_element_by_name('addBank').click()
    time.sleep(5)
    security_check = ''
    try:
        security_check = driver.find_element_by_xpath('//div[@class="challengesSection"]//h1').text
    except:
        pass             
    if security_check == 'Quick security check':
        sql = 'UPDATE email_info set confirm_identity=9 where email=%s'
        commit_sql(conn, sql, email)
    else:
        pending_confirm_button_XP = '//button[@name="pendingConfirmBank"]'
        pending_confirm_button_state = explicit_wait(driver, "VOEL", [pending_confirm_button_XP, "XPath"], 10, False)
        if pending_confirm_button_state:
            pending_confirm_button = driver.find_element_by_xpath(pending_confirm_button_XP)
            (ActionChains(driver)
             .move_to_element(pending_confirm_button)
             .click()
             .perform())

            confirm_instantly_XP = '//a[@name="confirmInstantly"]'
            explicit_wait(driver, "VOEL", [confirm_instantly_XP, "XPath"])
            confirm_instantly = driver.find_element_by_xpath(confirm_instantly_XP)
            (ActionChains(driver)
             .move_to_element(confirm_instantly)
             .click()
             .perform())
        else:
            user_pwd_confirm_XP = '//div[@class="confirmBank-confirmInstantly"]/a'
            explicit_wait(driver, "VOEL", [user_pwd_confirm_XP, "XPath"], 5)
            user_pwd_confirm = driver.find_element_by_xpath(user_pwd_confirm_XP)
            (ActionChains(driver)
             .move_to_element(user_pwd_confirm)
             .click()
             .perform())

        input_user_XP = '//form/div/div[1]/input'
        explicit_wait(driver, "VOEL", [input_user_XP, "XPath"])
        driver.find_element_by_xpath(input_user_XP).send_keys(confirm_user)
        time.sleep(1)
        driver.find_element_by_xpath('//form/div/div[3]/input').send_keys(confirm_pwd)
        time.sleep(1)
        driver.find_element_by_name('continue').click()

        choice_account_number_XP = '//label[@for="accountNumber-%s"]' % accountNumberLast4
        confirm_last_step = explicit_wait(driver, "VOEL", [choice_account_number_XP, "XPath"], 120, False)
        if confirm_last_step:
            choice_account_number = driver.find_element_by_xpath(choice_account_number_XP)
            (ActionChains(driver)
             .move_to_element(choice_account_number)
             .click()
             .perform())
            time.sleep(1)
            driver.find_element_by_name('continue').click()
        else:
            try:
                driver.find_element_by_name('continue').click()
                choice_account_number_XP = '//label[@for="accountNumber-%s"]' % accountNumberLast4
                confirm_last_step = explicit_wait(driver, "VOEL", [choice_account_number_XP, "XPath"], 120, False)
                if confirm_last_step:
                    choice_account_number = driver.find_element_by_xpath(choice_account_number_XP)
                    (ActionChains(driver)
                     .move_to_element(choice_account_number)
                     .click()
                     .perform())
                    time.sleep(1)
                    driver.find_element_by_name('continue').click()
            except:
                pass

        confirm_success = ''
        confirm_success_XP = '//div[@id="overpanel-header"]/h2'
        success_flag = explicit_wait(driver, "VOEL", [confirm_success_XP, "XPath"], 15,  False)
        if success_flag:
            try:
                confirm_success = driver.find_element_by_xpath(confirm_success_XP).text
            except:
                pass
            if confirm_success == 'Bank linked!':
                sql = 'UPDATE email_info set confirm_identity=1, confirm_type=%s, confirmAccountNumber=%s where email=%s'
                commit_sql(conn, sql, (confirm_type, account_number, email))
                print('Confirm Successsful!')
        else:
            print('Change back to the state!')
            sql = 'UPDATE paypal_confirm_info set used=0 where id=%s'
            commit_sql(conn, sql, confirm_info_id)


def modify_port():
    path = 'C:\\Users\\Administrator\\AppData\\Roaming\\Proxifier\\Profiles'
    file = 'C:\\Users\\Administrator\\Desktop\\work\\register_paypal\\1558888888.ppx'
    filenames = os.listdir(path)
    for filename in filenames:
        with open(path + '\\' + filename, 'r', encoding='utf-8') as fp:
            info = fp.read()
    port_str = re.search(r'<Port>\d*</Port>', info).group()
    print(port_str)
    with open(file, 'r', encoding='utf-8') as f1, open('%s.bak' % file, 'w', encoding='utf-8') as f2:
        for line in f1:
            f2.write(re.sub(r'<Port>\d*</Port>', port_str, line))
    os.remove(file)
    os.rename('%s.bak' % file, file)


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


def get_mac():
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    mac_address = ''.join([mac[e:e + 2] for e in range(0, 11, 2)])
    mac_address = mac_address.upper()
    # print(mac_address)
    return mac_address


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
