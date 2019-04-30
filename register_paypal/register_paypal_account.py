import os
import pymysql
import time
from selenium import webdriver
from selenium.webdriver.support.select import Select
from selenium.webdriver.support import expected_conditions as EC
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
        sql = 'SELECT * from email_info where id>7174 and emailIsUsed=1 and created_paypal_account=0 and register_pp_mac="-"'
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
        if created_flag < 3:
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
                time.sleep(0.5)
                driver.find_element_by_id(
                    'paypalAccountData_lastName').send_keys(lastname)
                time.sleep(0.5)
                driver.find_element_by_id(
                    'paypalAccountData_email').send_keys(email)
                time.sleep(0.5)
                driver.find_element_by_id(
                    'paypalAccountData_password').send_keys(paypal_pwd)
                time.sleep(2)
                # 确认密码
                try:
                    driver.find_element_by_id(
                        'paypalAccountData_confirmPassword').send_keys(paypal_pwd)
                    time.sleep(0.5)
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
                    step_flag = 0
                else:
                    driver.find_element_by_xpath(
                        '//div[@class="btnGrp"]/button').click()
                    time.sleep(5)
                    while True:
                        add_info_page = ''
                        try:
                            add_info_page = driver.find_element_by_xpath(
                                '//div[@class="fieldGroupContainer"]/div[1]/div[1]/div/div/label').text
                            print(add_info_page)
                        except:
                            pass
                        if add_info_page == 'Street address':
                            time.sleep(3)
                            break
                        else:
                            time.sleep(3)
                    driver.find_element_by_xpath(
                        '//div[@data-label-content="Street address"]//input').send_keys(address)
                    time.sleep(0.5)
                    driver.find_element_by_id(
                        'paypalAccountData_city').send_keys(city)
                    time.sleep(0.5)
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
                    sql = 'UPDATE email_info set paypal_pwd=%s, created_paypal_account=1 where email=%s'
                    commit_sql(conn, sql, (paypal_pwd, email))
                    created_flag = 1
                    try:
                        driver.find_element_by_xpath('//a[@name="notnow"]').click()
                        time.sleep(3)
                    except:
                        pass
            # 绑卡
            if created_flag == 1 and step_flag == 1:
                if login_separately == 1:
                    login_flag = login_paypal(driver, email, paypal_pwd)
                    if login_flag == 1:
                        created_flag = link_card(driver, conn, email, card_num, expiration_date, card_csc)
                        login_separately = 0
                else:
                    while True:
                        next_step_page = ''
                        try:
                            next_step_page = driver.find_element_by_xpath(
                                '//div[@class="formLink "]//button')
                            # print(next_step_page)
                        except:
                            pass
                        if next_step_page:
                            driver.find_element_by_xpath(
                                '//div[@class="formLink "]//button').click()
                            time.sleep(3)
                            break
                        else:
                            time.sleep(3)
                    while True:
                        add_card_page = ''
                        try:
                            add_card_page = driver.find_element_by_xpath(
                                '//div[@class="fieldGroupContainer"]//label[@for="cardData_cardNumber"]').text
                            print(add_card_page)
                        except:
                            pass
                        if add_card_page == 'Debit or credit card number':
                            time.sleep(3)
                            break
                        else:
                            time.sleep(3)
                    driver.find_element_by_id(
                        'cardData_cardNumber').send_keys(card_num)
                    time.sleep(0.5)
                    driver.find_element_by_id(
                        'cardData_expiryDate').send_keys(expiration_date)
                    time.sleep(0.5)
                    driver.find_element_by_id('cardData_csc').send_keys(card_csc)
                    time.sleep(0.5)
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
            if created_flag == 2 and step_flag == 1:
                if login_separately == 1:
                    login_paypal(driver, email, paypal_pwd)
                # 判断邮箱类型
                email_type = email.split('@')[-1]
                if email_type == 'gmail.com':
                    print('Gmail!')
                    login_gmail(driver, conn, email, email_pwd, paypal_pwd, recovery_email)
                elif email_type == 'yahoo.com':
                    print('Yahoo!')
                    login_yahoo(driver, conn, email, email_pwd, paypal_pwd)
            p = subprocess.Popen('cmd.exe /c' + 'taskkill /F /im Client.exe',
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            p.wait()
            time.sleep(2)
            driver.quit()
            time.sleep(0.5)
            os.system('shutdown -s -t 5')
            time.sleep(10)
        else:
            print('Have already registered!')



def activate(driver, conn, email, paypal_pwd, activate_type):
    try_time = 0
    while True:
        input_flag = ''
        try:
            input_flag = driver.find_element_by_xpath(
                '//label[@for="password"]').text
        except:
            pass
        if input_flag == 'Password':
            driver.find_element_by_id('password').send_keys(paypal_pwd)
            time.sleep(1)
            driver.find_element_by_xpath('//button[@id="btnLogin"]').click()
            time.sleep(0.5)
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
            break
        else:
            try_time += 1
            time.sleep(3)
        if try_time > 3:
            break
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
                time.sleep(3)
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
        time.sleep(0.5)
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
        try_time = 0
        while True:
            email_flag = ''
            try:
                email_flag = driver.find_element_by_xpath(
                    '//a[@data-name="confirm_your_email"]')
            except:
                pass
            if email_flag:
                email_flag.click()
                time.sleep(3)
                driver.find_element_by_xpath('//button[@id="js_unconfirmedEmail"]').click()
                time.sleep(1)
                activate_flag = 1
            else:
                try_time += 1
                time.sleep(3)
            if try_time > 3:
                break
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
    search_input_times = 0
    while True:
        input_element = ''
        try:
            input_element = driver.find_element_by_xpath('//div[@id="login_emaildiv"]/div/label').text
        except:
            pass
        if input_element == 'Email or mobile number':
            time.sleep(1)
            driver.find_element_by_id('email').send_keys(email)
            time.sleep(1)
            try:
                driver.find_element_by_id('btnNext').click()
                time.sleep(5)
            except:
                pass
            driver.find_element_by_id('password').send_keys(paypal_pwd)
            time.sleep(1)
            driver.find_element_by_id('btnLogin').click()
            time.sleep(3)
            try:
                driver.find_element_by_xpath('//p[@class="secondaryLink"]/a').click()
                time.sleep(3)
            except:
                pass            
            break
        else:
            time.sleep(2)
            search_input_times += 1
        if search_input_times > 3:
            break
    search_home_times = 0
    while True:
        home_element = ''
        try:
            home_element = driver.find_element_by_xpath('//a[text()="Summary"]').text
        except:
            pass
        if home_element == 'Summary':
            login_flag = 1
            time.sleep(0.5)
            break
        else:
            time.sleep(3)
            search_home_times += 1
        if search_home_times > 3:
            login_flag = 0
            time.sleep(0.5)
            break
    return login_flag


def link_card(driver, conn, email, card_num, expiration_date, card_csc, created_flag=1):
    try_time = 0
    while True:
        link_button = ''
        try:
            link_button = driver.find_element_by_xpath(
                '//a[@id="bankCardLinkBankOrCard"]')
        except:
            pass
        if link_button:
            link_button.click()
            time.sleep(3)
        else:
            try_time += 1
            time.sleep(3)
        if try_time > 3:
            break
    try_link_card = 0
    while True:
        link_card_element = ''
        try:
            link_card_element = driver.find_element_by_xpath(
                '//p[@data-testid="addPrimaryText"]').text
        except:
            pass
        if link_card_element == 'Link a debit or credit card':
            driver.find_element_by_xpath('//a[@data-name="addCard"]').click()
            time.sleep(3)
        else:
            try_link_card += 1
            time.sleep(3)
        if try_link_card > 3:
            break
    next_step = 0
    while True:
        next_element = ''
        try:
            next_element = driver.find_element_by_xpath(
                '//a[@data-name="linkManually"]')
        except:
            pass
        if next_element:
            next_element.click()
            time.sleep(3)
        else:
            next_step += 1
            time.sleep(3)
        if next_step > 3:
            break
    while True:
        add_card_page = ''
        try:
            add_card_page = driver.find_element_by_name(
                'detailsSubmit').text
            print(add_card_page)
        except:
            pass
        if add_card_page == 'Link Card':
            driver.find_element_by_id('cardNumber').send_keys(card_num)
            time.sleep(1)
            driver.find_element_by_id('expDate').send_keys(expiration_date)
            time.sleep(0.5)
            driver.find_element_by_id('verificationCode').send_keys(card_csc)
            time.sleep(0.5)
            driver.find_element_by_name('detailsSubmit').click()
            time.sleep(5)
            try:
                driver.find_element_by_xpath('//a[@data-name="addCardDone"]').click()
                time.sleep(2)
                sql = 'UPDATE email_info set created_paypal_account=2 where email=%s'
                commit_sql(conn, sql, email)
                time.sleep(1)
                created_flag = 2
                driver.find_element_by_xpath('//a[text()="Summary"]').click()
                time.sleep(3)
            except:
                pass
            break
        else:
            time.sleep(3)
    return created_flag


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
