import pymysql
import time
import re
from selenium import webdriver
import subprocess
import queue
import requests
import hashlib
import json
import win32api
import win32gui
import win32con
import socket
from change_computer_info import verify
import datetime
import os
import uuid
import random


q = queue.Queue()


PAYPAL_INFO = {
    'paypal': {
        'pp_nickname': '',
        'token': '',
        'paypal_state': '',
        'usable_money': '',
        'disable_money': ''
    },
    'order': {}
}


WITHDRAW_INFO = {
    'pp_nickname': '',
    'amount': '',
    'real_amount': '',
    'pp_draw_status': '',
    'token': ''
}


STATE_LIST = ['Withdraw to Credit Card', 'Instant Withdraw to Credit Card', 'Instant Withdraw to PayPal', 'Withdraw to PayPal']


def post_data(email):
    raw_str = email + 'python'
    m = hashlib.md5()
    b = raw_str.encode(encoding='utf-8')
    m.update(b)
    str_md5 = m.hexdigest()
    return str_md5


def main():
    # 关闭调查问卷按钮 //div[@id="customer_satisfaction_survey"]//span/div/div/button
    step_flag = 1
    upgrade_flag = 0
    hostname = socket.gethostname()
    time.sleep(0.5)
    conn = pymysql.connect(host='localhost', port=3306,
                           user='pp2', password='123456',
                           db='auto_info', charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    sql = 'SELECT * from paypal_info where paypal_id=%s'
    paypal_msg = fetch_one_sql(conn, sql, hostname)
    if paypal_msg:
        mac_address = get_mac()
        pp_nickname = paypal_msg['paypal_id']
        print(pp_nickname)
        email = paypal_msg['email']
        password = paypal_msg['pwd']
        cookies = paypal_msg['cookies']
        state = paypal_msg['country_state']
        withdraw_state = paypal_msg['withdraw']
        sql = 'SELECT * from state_change where state_abb=%s'
        get_full_state = fetch_one_sql(conn, sql, state)
        if get_full_state:
            full_state = get_full_state['state_full']
        city = paypal_msg['city'].capitalize()
        try:
            firstname = paypal_msg['firstname'].capitalize()
            lastname = paypal_msg['lastname'].capitalize()
            name = firstname + ' ' + lastname
        except:
            name = ' '
        print(name)
        phonenum = paypal_msg['mobilenumber']
        if not phonenum:
            phonenum = ' '
        address = paypal_msg['address']
        if not address:
            address = ' '
        zip_num = paypal_msg['zip']
        if not zip_num:
            zip_num = ' '
        birthdate = paypal_msg['birthdate']
        if not birthdate:
            birthdate = ' '
        recovery_email = paypal_msg['recovery_email']
        if not recovery_email:
            recovery_email = ' '
        directDepositAccountNumber = paypal_msg['directDepositAccountNumber']
        if not directDepositAccountNumber:
            directDepositAccountNumber = ' '
        try:
            ssn = paypal_msg['socialnumber'][-4:]
        except:
            ssn = ' '
        run_auto = paypal_msg['run_auto']
        withdraw_flag = 1
        sql = 'SELECT computer_name from computer_info where mac_address=%s'
        res = fetch_one_sql(conn, sql, mac_address)
        res_flag = res['computer_name']
        with open('C:\\Users\\Administrator\\Desktop\\%s.txt' % pp_nickname, 'w', encoding='utf-8') as fp:
            fp.write(pp_nickname + '\n' + 'PayPal: ' + email + '\n' + 'PayPalpassword: ' + password + '\n' + 'state: ' + state + '\n' + 'city: ' + city + '\n' + 'name: ' + name +
                     '\n' + 'phonenumber: ' + phonenum + '\n' + 'address: ' + address + '\n' + 'zip: ' + zip_num + '\n' + 'birthdate: ' + birthdate + '\n' + 'ssn: ' + ssn + '\n' + 'recovery_email: ' + recovery_email + '\n' + 'directDepositAccountNumber: ' + directDepositAccountNumber)
        if res_flag:
            pass
        else:
            sql = 'UPDATE computer_info set computer_name=%s where mac_address=%s'
            commit_sql(conn, sql, (hostname, mac_address))
        if int(run_auto) == 1:
            step_flag = 2
        elif int(run_auto) == 0:
            step_flag = 1
        elif int(run_auto) == -1:
            step_flag = -1
    else:
        mac_address = get_mac()
        sql = 'SELECT * from computer_info where mac_address=%s and computer_name is NULL'
        machine = fetch_one_sql(conn, sql, mac_address)
        if machine:
            PC_name = machine['PC_name']
            sql = 'SELECT * from paypal_info where read_flag=0 and PC_name=%s and is_end=1 order by id limit 1'
            paypal_msg = fetch_one_sql(conn, sql, PC_name)
            if paypal_msg:
                pp_nickname = paypal_msg['paypal_id']
                print(pp_nickname, ':', 'Get account, Change info!')
                email = paypal_msg['email']
                password = paypal_msg['pwd']
                state = paypal_msg['country_state']
                city = paypal_msg['city']
                sql = 'UPDATE paypal_info set read_flag=1 where paypal_id=%s'
                commit_sql(conn, sql, pp_nickname)
                verify(pp_nickname)
                step_flag = 0
            else:
                step_flag = 0
                print('Not data!')
        else:
            step_flag = 0
            print('No Machine!')          
    if step_flag > 0:
        PAYPAL_INFO['paypal']['email'] = email
        PAYPAL_INFO['paypal']['pp_nickname'] = pp_nickname
        order_state_element = ''
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
            driver.get('https://www.paypal.com/us/signin')
            time.sleep(3)
            if driver.page_source.find('This site can’t be reached') > -1:
                print('Net error!')
                driver.quit()
                time.sleep(1)
                continue
            else:
                break
        login_flag = click_login(driver, conn, email, password, pp_nickname)
        if driver.page_source.find('Confirm your phone for extra security') > -1:
            upgrade_flag = 1
            login_flag = 1
            sql = 'UPDATE paypal_info set login_state=1 where paypal_id=%s'
            commit_sql(conn, sql, pp_nickname)
            time.sleep(0.5)
        if step_flag == 2 and login_flag == 1:
            search_upgrade = 0
            while True:
                upgrade_element = ''
                try:
                    upgrade_element = driver.find_element_by_xpath(
                        '//a[@data-name="confirm_your_mobile"]')
                except:
                    pass
                if upgrade_element:
                    upgrade_flag = 1
                    break
                else:
                    time.sleep(2)
                    search_upgrade += 1
                if search_upgrade > 3:
                    break
            if upgrade_flag == 1:
                upgrade_account(driver, name, phonenum, address, city, full_state, zip_num, ssn, birthdate)
            try:
                info_num = driver.find_element_by_xpath(
                    '//div[@data-testid="AlertBellIcon"]//span').text
                # print(info_num)
                if int(info_num) > 3:
                    # paypal_error(driver)
                    PAYPAL_INFO['paypal']['paypal_state'] = '4'
                    withdraw_flag = 0
                else:
                    PAYPAL_INFO['paypal']['paypal_state'] = '1'
                    # driver.find_element_by_xpath('//div[@data-testid="AlertBellIcon"]').click()
            except:
                pass
            try:
                order_state_element = driver.find_elements_by_xpath(
                    '//div[@class="table-responsive"]/table//tr//td[2]/a')
                if not order_state_element:
                    driver.refresh()
                    time.sleep(5)
                    order_state_element = driver.find_elements_by_xpath(
                        '//div[@class="table-responsive"]/table//tr//td[2]/a')
                if order_state_element:
                    if not PAYPAL_INFO['paypal']['paypal_state']:
                        PAYPAL_INFO['paypal']['paypal_state'] = '1'
                for order in order_state_element:
                    order_num = order.get_attribute('href')
                    order_num = order_num.replace('https://www.paypal.com', '')
                    print(order_num)
                    q.put(order_num)
            except:
                pass
            while q.qsize() > 0:
                custom = ''
                order_flag = q.get()
                print(order_flag)
                while True:
                    order_state = ''
                    search_state_times = 0
                    while True:
                        try:
                            order_state = driver.find_element_by_xpath(
                                '//div[@class="table-responsive"]/table//tr//td[2]/a[@href="%s"]//li' % order_flag).text
                            # print(order_state)
                        except Exception as e:
                            pass
                        if not order_state:
                            time.sleep(3)
                            try:
                                all_order_state = driver.find_elements_by_xpath(
                                    '//div[@class="table-responsive"]/table//tr//td[2]/a//li')
                                order_state = all_order_state[0].text
                            except:
                                pass
                            if not order_state:
                                try:
                                    order_state = driver.find_element_by_xpath(
                                        '//div[@class="table-responsive"]/table//tr//td[2]/a[@href="%s"]//li/span' % order_flag).text
                                except:
                                    pass
                        if order_state:
                            print(order_state)
                            break
                        else:
                            time.sleep(2)
                            search_state_times += 1
                        if search_state_times > 3:
                            break
                    # Denied 取款失败
                    if order_state == 'Completed':
                        if custom:
                            if PAYPAL_INFO['paypal']['paypal_state'] == '1':
                                PAYPAL_INFO['order'][custom] = '1'
                            elif PAYPAL_INFO['paypal']['paypal_state'] == '4':
                                PAYPAL_INFO['order'][custom] = '2'
                        else:
                            order_type = driver.find_element_by_xpath(
                                '//div[@class="table-responsive"]/table//tr//td[2]/a[@href="%s"]/b' % order_flag).text
                            if order_type in STATE_LIST:
                                break
                            else:
                                try:
                                    driver.find_element_by_xpath(
                                        '//div[@class="table-responsive"]/table//tr//td[2]/a[@href="%s"]' % order_flag).click()
                                    time.sleep(3)
                                except:
                                    pass
                                try:
                                    custom = driver.find_element_by_xpath(
                                        '//section[@class="Notes pagebreak"]//p').text
                                    print(custom)
                                    driver.find_element_by_xpath(
                                        '//a[text()="Summary"]').click()
                                    time.sleep(5)
                                except:
                                    pass
                                if PAYPAL_INFO['paypal']['paypal_state'] == '1':
                                    PAYPAL_INFO['order'][custom] = '1'
                                elif PAYPAL_INFO['paypal']['paypal_state'] == '4':
                                    PAYPAL_INFO['order'][custom] = '2'
                        break
                    elif order_state == 'ON HOLD' or order_state == 'Held' or order_state == 'On Hold':
                        if custom:
                            if PAYPAL_INFO['paypal']['paypal_state'] == '1':
                                PAYPAL_INFO['order'][custom] = '3'
                            elif PAYPAL_INFO['paypal']['paypal_state'] == '4':
                                PAYPAL_INFO['order'][custom] = '4'
                        else:
                            try:
                                driver.find_element_by_xpath(
                                    '//div[@class="table-responsive"]/table//tr//td[2]/a[@href="%s"]' % order_flag).click()
                                time.sleep(3)
                            except:
                                pass
                            try:
                                custom = driver.find_element_by_xpath(
                                    '//section[@class="Notes pagebreak"]//p').text
                                print(custom)
                                driver.find_element_by_xpath(
                                    '//a[text()="Summary"]').click()
                                time.sleep(5)
                            except:
                                pass
                            if PAYPAL_INFO['paypal']['paypal_state'] == '1':
                                PAYPAL_INFO['order'][custom] = '3'
                            elif PAYPAL_INFO['paypal']['paypal_state'] == '4':
                                PAYPAL_INFO['order'][custom] = '4'
                        break
                    elif order_state == 'Pending':
                        # print('Pending!')
                        order_msg = submit_order(driver, order_flag)
                        if order_msg:
                            custom = order_msg['custom']
                            print(custom)
                            if order_msg['success_flag'] == '4':
                                if PAYPAL_INFO['paypal']['paypal_state'] == '1':
                                    PAYPAL_INFO['order'][custom] = '3'
                                elif PAYPAL_INFO['paypal']['paypal_state'] == '4':
                                    PAYPAL_INFO['order'][custom] = '4'
                                break
                    elif order_state == 'Unclaimed':
                        exchange_remittance(driver, order_flag)
                        # print('Unclaimed!')
                    else:
                        print('Unknow Error!')
                        break
            try:
                get_balance(driver, conn, pp_nickname, email)
                PAYPAL_INFO['order'] = json.loads(PAYPAL_INFO['order'])
                PAYPAL_INFO['paypal'] = json.loads(PAYPAL_INFO['paypal'])
                withdraw_money = int(PAYPAL_INFO['paypal']['usable_money'].split('.')[0])
                print('withdraw: ', withdraw_money)
                if withdraw_flag == 1 and withdraw_money > 10 and withdraw_state == 1:
                    withdraw(driver, conn, pp_nickname, email)
                sql = 'UPDATE paypal_info set is_end=0 where paypal_id=%s'
                commit_sql(conn, sql, pp_nickname)
            except:
                pass
            p = subprocess.Popen('cmd.exe /c' + 'taskkill /F /im Client.exe',
                                 stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            p.wait()
            time.sleep(2)
            driver.quit()
            time.sleep(0.5)
            os.system('shutdown -s -t 5')
            time.sleep(10)
        else:
            time.sleep(1200)


def get_balance(driver, conn, pp_nickname, email):
    try:
        balance_text = driver.find_element_by_xpath(
            '//span[@data-test="totalAvailableAmount"]').text
        time.sleep(0.5)
        if balance_text[0] == '-':
            balance = '-' + re.search(r'[0-9]*\.[0-9]*', balance_text).group()
        else:
            balance = re.search(r'[0-9]*\.[0-9]*', balance_text).group()
        print(balance)
        PAYPAL_INFO['paypal']['usable_money'] = balance
    except:
        driver.find_element_by_xpath(
            '//a[text()="Summary"]').click()
        time.sleep(5)
        balance_text = driver.find_element_by_xpath(
            '//span[@data-test="totalAvailableAmount"]').text
        time.sleep(0.5)
        balance = re.search(r'[0-9]*\.[0-9]*', balance_text).group()
        print(balance)
        PAYPAL_INFO['paypal']['usable_money'] = balance
    try:
        disable_balance_text = driver.find_element_by_xpath(
            '//div[@class="money"]//div[@data-test="withheld"]//a/div/span').text
        time.sleep(0.5)
        disable_balance = re.search(
            r'[0-9]*\.[0-9]*', disable_balance_text).group()
        print(disable_balance)
        PAYPAL_INFO['paypal']['disable_money'] = disable_balance
    except:
        PAYPAL_INFO['paypal']['disable_money'] = '0'
    str_md5 = post_data(email)
    PAYPAL_INFO['paypal']['token'] = str_md5
    time.sleep(0.5)
    print(PAYPAL_INFO)
    PAYPAL_INFO['order'] = json.dumps(PAYPAL_INFO['order'])
    PAYPAL_INFO['paypal'] = json.dumps(PAYPAL_INFO['paypal'])
    time.sleep(1)
    try:
        r = requests.post(
            'http://localhost/adminpp2019/api/edit_enable_and_disable.html', data=PAYPAL_INFO)
        # print(r.text)
        time.sleep(0.5)
        code_state_json = json.loads(r.text)
        code_num = code_state_json['code']
        print('code_num:', code_num)
    except:
        code_num = 999
    try:
        sql = 'UPDATE paypal_info set code=%s where paypal_id=%s'
        commit_sql(conn, sql, (code_num, pp_nickname))
        time.sleep(1)
        current_time = datetime.datetime.now().strftime("%Y-%m-%d")
        PAYPAL_INFO_str = json.dumps(PAYPAL_INFO)
        sql = 'INSERT INTO result_msg (paypal_id, msg, action_time) values (%s, %s, %s)'
        commit_sql(conn, sql, (pp_nickname,
                               PAYPAL_INFO_str, current_time))
        time.sleep(1)
    except:
        pass


def commit_sql(conn, sql, data=None):
    cursor = conn.cursor()
    cursor.execute(sql, data)
    conn.commit()
    cursor.close()


def submit_order(driver, order_flag):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d")
    # 获取数额
    error_msg = ''
    order_msg = {
        'success_flag': '',
        'custom': ''
    }
    try:
        money_text = driver.find_element_by_xpath(
            '//div[@class="table-responsive"]/table//tr//td[3]/a[@href="%s"]' % order_flag).text
        time.sleep(0.5)
        money = re.search(r'[0-9]*\.[0-9]*', money_text).group()
        print(money)
        # print(currency)
        time.sleep(0.5)
        # 点击订单(elements)
        order_type = driver.find_element_by_xpath(
            '//div[@class="table-responsive"]/table//tr//td[2]/a[@href="%s"]/b' % order_flag).text
        if order_type in STATE_LIST:
            order_msg['custom'] = '00000'
            order_msg['success_flag'] = '4'
        else:
            driver.find_element_by_xpath(
                '//div[@class="table-responsive"]/table//tr//td[2]/a[@href="%s"]' % order_flag).click()
            time.sleep(3)
            # 提交订单
            order_msg['custom'] = driver.find_element_by_xpath(
                '//section[@class="Notes pagebreak"]//p').text
            print(order_msg['custom'])
            time.sleep(0.5)
            driver.find_element_by_xpath(
                '//section[@class="PurchaseDetails"]//ul/li[1]/a').click()
            time.sleep(3)
            driver.find_element_by_name('additionalCapture').click()
            time.sleep(0.5)
            driver.find_element_by_name('transactionAmount').send_keys(money)
            time.sleep(0.5)
            # 第二次提交
            driver.find_element_by_id('continue-btn').click()
            time.sleep(3)
            driver.find_element_by_id('capturefund-btn').click()
            time.sleep(3)
            # if driver.page_source.find('You have successfully captured funds.') > -1:
            # if funds_flag:
            #     print('Successfully captured funds!')
            #     order_msg['success_flag'] = '1'
            try:
                error_msg = driver.find_element_by_xpath(
                    '//div[@class="SubFlowErrorMsg"]/div').text
            except:
                pass
            if error_msg == 'We are sorry, we cannot process this settlement at this time.':
                print('False captured funds!')
                order_msg['success_flag'] = '4'
            else:
                order_msg['success_flag'] = '1'
            time.sleep(3)
            driver.find_element_by_xpath('//a[text()="Summary"]').click()
            time.sleep(3)
        print(order_msg)
        return order_msg
    except:
        driver.find_element_by_xpath('//a[text()="Summary"]').click()
        time.sleep(3)


def exchange_remittance(driver, order_flag):
    try:
        driver.find_element_by_xpath(
            '//div[@class="table-responsive"]/table//tr//td[2]/a[@href="%s"]' % order_flag).click()
        time.sleep(3)
    except:
        driver.find_element_by_xpath(
            '//div[@class="table-responsive"]/table//tr//td[2]/a').click()
        time.sleep(3)
    try:
        # 兌汇接受
        driver.find_element_by_xpath(
            '//section[@class="PurchaseDetails"]//ul/li[1]/a').click()
        time.sleep(3)
        # 兌汇提交
        driver.find_element_by_id('submit-btn').click()
        time.sleep(3)
        if driver.page_source.find('You have successfully accepted this payment.') > -1:
            print('Exchange remittance successfully!')
        time.sleep(3)
        driver.find_element_by_xpath('//a[text()="Summary"]').click()
        time.sleep(3)
    except:
        driver.find_element_by_xpath('//a[text()="Summary"]').click()
        time.sleep(3)


def paypal_error(driver):
    try:
        driver.find_element_by_xpath(
            '//div[@class="notifications-container"]/div/div/a').click()
        time.sleep(3)
        # 获取报错数量
        error_num_element = driver.find_elements_by_xpath(
            '//div[@class="appealstep-wrapper "]')
        error_num = len(error_num_element)
        print(error_num)
        if int(error_num) > 1:
            print('Really dead!')
            PAYPAL_INFO['paypal']['paypal_state'] = '8'
        else:
            print('Not really dead!')
            PAYPAL_INFO['paypal']['paypal_state'] = '4'
    except:
        driver.find_element_by_xpath(
            '//div[@data-testid="AlertBellIcon"]/a').click()
        time.sleep(0.5)
        driver.find_element_by_xpath(
            '//div[@class="notifications-container"]/div/div/a').click()
        time.sleep(3)
        # 获取报错数量
        error_num_element = driver.find_elements_by_xpath(
            '//div[@class="appealstep-wrapper "]')
        print(error_num_element)
        error_num = len(error_num_element)
        print(error_num)
        if int(error_num) > 1:
            error = 'Really dead!'
            print('Really dead!')
            PAYPAL_INFO['paypal']['paypal_state'] = '8'
        else:
            error = 'Not really dead!'
            print('Not really dead!')
            PAYPAL_INFO['paypal']['paypal_state'] = '4'
        time.sleep(2)
    driver.find_element_by_xpath('//a[text()="Summary"]').click()
    time.sleep(5)


def upgrade_account(driver, name, phonenum, address, city, full_state, zip_num, ssn, birthdate):
    try:
        driver.find_element_by_xpath(
            '//p[@class="secondaryLink"]/a').click()
        time.sleep(3)
        driver.get('https://www.paypal.com/myaccount/bundle/business/upgrade')
        time.sleep(3)
        # driver.get('https://www.paypal.com/myaccount/settings/account')
        # driver.find_element_by_xpath(
        #     '//a[text()="Upgrade to a Business account"]').click()
        # time.sleep(3)
        driver.find_element_by_xpath(
            '//label[@for="existing_account"]').click()
        time.sleep(1)
        driver.find_element_by_id('next_btn').click()
    except:
        pass
    add_info_flag = 0
    while True:
        add_person_info = ''
        try:
            add_person_info = driver.find_element_by_xpath('//div[@class="FormField"]//label[@for="businessLegalName"]').text
        except:
            pass
        if add_person_info == 'Legal business name':
            time.sleep(1)
            break
        else:
            add_info_flag += 1
            time.sleep(3)
        if add_info_flag > 5:
            break
    try:
        driver.find_element_by_id('businessLegalName').send_keys(name)
        time.sleep(0.5)
        driver.find_element_by_id(
            'businessPhoneNumber').send_keys(phonenum)
        time.sleep(0.5)
        driver.find_element_by_id(
            'businessAddress[businessAddressStreet1]').send_keys(address)
        time.sleep(0.5)
        driver.find_element_by_id(
            'businessAddress[businessAddressCity]').send_keys(city)
        # 选择州
        driver.find_element_by_xpath('//div[@class="Select"]').click()
        time.sleep(0.5)
        driver.find_element_by_xpath(
            '//ul[@id="businessAddress[businessAddressState]-menu"]//li[text()="%s"]' % full_state).click()
        time.sleep(0.5)
        driver.find_element_by_id(
            'businessAddress[businessAddressZip]').send_keys(zip_num)
        time.sleep(0.5)
        driver.find_element_by_xpath(
            '//div[@class="agreementAcceptedText component-wrapper Checkbox"]/div/div').click()
        time.sleep(0.5)
        driver.find_element_by_id('upgradeContinueButton').click()
        time.sleep(5)
        # 选择 Individual
        while True:
            choice_individual = ''
            try:
                choice_individual = driver.find_element_by_xpath('//label[@id="businessType-label"]').text
            except:
                pass
            if choice_individual == 'Business type':
                time.sleep(1)
                driver.find_element_by_xpath(
                    '//form//div[@id="businessType"]/div').click()
                break
            else:
                time.sleep(3)
        time.sleep(3)
        win32api.keybd_event(40, 0, 0, 0)
        win32api.keybd_event(40, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(1)
        win32api.keybd_event(13, 0, 0, 0)
        win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(1)
        # 选择产品
        driver.find_element_by_id('merchantCategoryCode').send_keys("women")
        win32api.keybd_event(40, 0, 0, 0)
        win32api.keybd_event(40, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(1)
        win32api.keybd_event(13, 0, 0, 0)
        win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(1)
        time.sleep(0.5)
        driver.find_element_by_xpath(
            '//form//div[@id="businessAverageMonthlyVolume"]').click()
        time.sleep(0.5)
        driver.find_element_by_xpath(
            '//ul[@id="businessAverageMonthlyVolume-menu"]//li[text()="Up to USD $4,999"]').click()
        # 提交
        driver.find_element_by_id('continueButton').click()
        time.sleep(3)
        while True:
            add_more_info = ''
            try:
                add_more_info = driver.find_element_by_xpath('//div[@class="Input-parent"]//label[@for="dateOfBirth"]').text
            except:
                pass
            if add_more_info == 'Date of birth':
                time.sleep(1)
                # ssn 后四位
                driver.find_element_by_id('ssn').send_keys(ssn)
                time.sleep(0.5)
                break
            else:
                time.sleep(3)
        driver.find_element_by_id('dateOfBirth').send_keys(birthdate)
        time.sleep(0.5)
        driver.find_element_by_id('personalInfoSubmitButton').click()
        time.sleep(5)
    except:
        pass
    try:
        driver.find_element_by_xpath('//a[text()="Summary"]').click()
        time.sleep(3)
    except:
        pass


def withdraw(driver, conn, pp_nickname, email):
    WITHDRAW_INFO['pp_nickname'] = pp_nickname
    withdraw_md5 = post_data(email)
    WITHDRAW_INFO['token'] = withdraw_md5
    for withdraw_times in range(1, 3):
        error_element = ''
        try:
            driver.find_element_by_xpath(
                '//div[@class="money"]//a[text()="Withdraw Money"]').click()
            time.sleep(3)
            driver.find_element_by_xpath(
                '//article[@data-testid="instant"]').click()
            time.sleep(3)
            driver.find_element_by_xpath('//div[@class="actions"]/button').click()
            time.sleep(3)
            # 获取可提取余额
            spans = driver.find_elements_by_xpath(
                '//div[@class="amount-summary"]//div[2]/span')
            available_balance_text = spans[0].text
            available_balance = re.search(
                r'[0-9]*\.[0-9]*', available_balance_text).group().split('.')[0]
            print(available_balance)
        except:
            pass          
        if int(available_balance) > 50:
            if withdraw_times == 1:
                available_current = random.randint(40, 49)
                print('available_balance: ', available_current)
                next_available_balance = int(available_balance) -  int(available_current)
                print(next_available_balance)
            elif withdraw_times == 2:
                available_current = next_available_balance
        else:
            available_current = int(available_balance)
        # 输入金额
        driver.find_element_by_id('amountInputField').send_keys(
            str(available_current) + '00')
        # 提交
        driver.find_element_by_xpath(
            '//button[@data-testid="primary"]').click()
        time.sleep(5)
        try:
            error_element = driver.find_element_by_xpath('//div[@class="amount-page"]/div/p')
        except:
            pass
        if error_element:
            print('Cannot withdraw!')
            if withdraw_times == 1:
               WITHDRAW_INFO['amount'] = available_balance
            elif withdraw_times == 2:
               WITHDRAW_INFO['amount'] = available_current
            WITHDRAW_INFO['real_amount'] = '0'
            WITHDRAW_INFO['pp_draw_status'] = '2'
            print(WITHDRAW_INFO)
            r = requests.post(
                'http://localhost/adminpp2019/api/start_draw.html', data=WITHDRAW_INFO)
            # print(r.text)
            time.sleep(0.5)
            code_state_json = json.loads(r.text)
            withdraw_code_num = code_state_json['code']
            print('withdraw_code_num:', withdraw_code_num)
            break
        else:
            driver.find_element_by_xpath(
                '//button[@data-testid="primary"]').click()
            time.sleep(5)
            spans = driver.find_elements_by_xpath(
                '//div[@class="amount-summary"]//div[2]/span')
            real_balance_text = spans[-1].text
            real_balance = re.search(r'[0-9]*\.[0-9]*', real_balance_text).group()
            print(real_balance)
            time.sleep(1)
            driver.find_element_by_xpath(
                '//button[@data-testid="primary"]').click()
            time.sleep(5)
            try:
                driver.find_element_by_xpath(
                    '//button[@data-testid="primary"]').click()
                time.sleep(5)
            except:
                pass
            WITHDRAW_INFO['amount'] = str(available_current)
            WITHDRAW_INFO['real_amount'] = str(real_balance)
            WITHDRAW_INFO['pp_draw_status'] = '1'
            print(WITHDRAW_INFO)
            try:
                r = requests.post(
                    'http://localhost/adminpp2019/api/start_draw.html', data=WITHDRAW_INFO)
                # print(r.text)
                time.sleep(0.5)
                code_state_json = json.loads(r.text)
                withdraw_code_num = code_state_json['code']
                print('withdraw_code_num:', withdraw_code_num)
            except:
                withdraw_code_num = 999


def login(driver, email, password, cookies):
    login_flag = 0
    if cookies:
        print('cookieLogin...')
        time.sleep(2)
        try:
            cookies_str = json.loads((cookies).replace("\\", ""))
            print(cookies_str)
            for coo in cookies_str:
                coo.pop('domain')
                driver.add_cookie(coo)
            driver.refresh()
            time.sleep(3)
            login_flag = 1
        except Exception as e:
            print('The cookies is invalid. You are trying to login')
            time.sleep(5)
            driver.refresh()
            click_login(driver, conn, email, password, pp_nickname)
            login_flag = 2
    else:
        click_login(driver, conn, email, password, pp_nickname)
        login_flag = 2
    return login_flag


def click_login(driver, conn, email, password, pp_nickname):
    search_input_times = 0
    search_home_times = 0
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
            driver.find_element_by_id('password').send_keys(password)
            time.sleep(1)
            driver.find_element_by_id('btnLogin').click()
            time.sleep(5)
            break
        else:
            time.sleep(2)
            search_input_times += 1
        if search_input_times > 3:
            break
    while True:
        home_element = ''
        try:
            home_element = driver.find_element_by_xpath('//a[text()="Summary"]').text
        except:
            pass
        if home_element:
            login_flag = 1
            sql = 'UPDATE paypal_info set login_state=1 where paypal_id=%s'
            commit_sql(conn, sql, pp_nickname)
            time.sleep(0.5)
            break
        else:
            time.sleep(2)
            search_home_times += 1
        if search_home_times > 3:
            login_flag = 0
            sql = 'UPDATE paypal_info set login_state=4 where paypal_id=%s'
            commit_sql(conn, sql, pp_nickname)
            time.sleep(0.5)
            break
    return login_flag


def get_coo(driver, conn, pp_nickname):
    cookies = driver.get_cookies()
    cookies = json.dumps(cookies)
    cookies = cookies.replace('\\', '\\\\')
    cookies = cookies.replace('\"', '\\"')
    sql = "UPDATE paypal_info set cookies=%s where paypal_id=%s"
    commit_sql(conn, sql, (cookies, pp_nickname))


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
