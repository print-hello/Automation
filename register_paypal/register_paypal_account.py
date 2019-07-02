import os
import pymysql
import time
import datetime
import configparser
from selenium import webdriver
import win32api
import win32gui
import win32con
import subprocess
import change_computer_info
from dbconnection import fetch_one_sql
from dbconnection import commit_sql
from util import get_mac
from util import modify_port
from paypal_util import paypal_here_page_one
from paypal_util import paypal_here_page_two
from login_paypal import login_paypal
from login_mail import login_yahoo
from login_mail import login_gmail


def main():
    conn = pymysql.connect(host='localhost', port=3306,
                           user='root', password='123456',
                           db='walmartmoneycard', charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    step_flag = 1
    get_info_success = 0
    register_pp_mac = get_mac()
    current_time = (datetime.datetime.utcnow() +
                    datetime.timedelta(hours=8)).strftime("%Y-%m-%d")
    sql = 'SELECT * from config'
    register_config = fetch_one_sql(conn, sql)
    if register_config:
        # 注册 paypal 账号类型
        paypal_type = register_config['paypal_type']
        # 是否添加卡信息
        add_card = register_config['add_card']
        # 是否添加银行信息
        confirm_bank = register_config['confirm_bank']
        # email 是否注册过卡信息
        is_register_card_email = register_config['is_register_card_email']
        # 账号注册程度: 1 仅注册激活 2 注册绑定银行卡
        created_paypal_account_process = register_config['created_paypal_account_process']
    else:
        step_flag = 0
        print('Missing configuration information!')
    if step_flag == 1:
        if created_paypal_account_process == 0:
            sql = 'SELECT * from email_info where id>7174 and emailIsUsed=%s and created_paypal_account=%s and register_pp_mac=%s'
            register_info = fetch_one_sql(
                conn, sql, (is_register_card_email, created_paypal_account_process, register_pp_mac))
            if register_info:
                get_info_success = 1
                email_id = register_info['id']
                email = register_info['email']
                print(email_id, email)
            else:
                if created_paypal_account_process == 0:
                    sql = 'SELECT * from email_info where id>7174 and emailIsUsed=%s and created_paypal_account=%s and confirm_identity=0 and register_pp_mac="-" order by id desc limit 1'
                    register_info = fetch_one_sql(
                        conn, sql, (is_register_card_email, created_paypal_account_process))
                    if register_info:
                        get_info_success = 1
                        email_id = register_info['id']
                        email = register_info['email']
                        print(email_id, email)
                        with open('D:\\hostname.ini', 'r', encoding='utf-8') as fp:
                            hostname = fp.read().strip()
                            print(hostname)
                        sql = 'UPDATE email_info set register_pp_mac=%s, register_machine=%s where email=%s'
                        commit_sql(conn, sql, (register_pp_mac, hostname, email))
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
            confirm_identity_state = register_info['confirm_identity']
            confirm_email = register_info['confirm_email']
            created_flag = register_info['created_paypal_account']
            if created_flag > 0:
                login_with_input_box = True
            else:
                login_with_input_box = False
            if is_register_card_email == 0:
                sql = 'SELECT * from register_info where id>34000 and userInfoIsUsed=0 and read_num<4 order by id limit 1'
                personal_info = fetch_one_sql(conn, sql)
            elif is_register_card_email == 1:
                sql = 'SELECT * from register_info where id=%s'
                personal_info = fetch_one_sql(conn, sql, register_info_id)
            if personal_info:
                register_info_id = personal_info['id']
                print(register_info_id)
                try:
                    firstname = personal_info['firstname'].capitalize()
                    lastname = personal_info['lastname'].capitalize()
                    name = firstname + ' ' + lastname
                except:
                    name = ' '
                birthdate = personal_info['birthdate']
                address = personal_info['address']
                city = personal_info['city']
                state = personal_info['state']
                sql = 'SELECT * from state_change where state_abb=%s'
                get_full_state = fetch_one_sql(conn, sql, state)
                if get_full_state:
                    full_state = get_full_state['state_full']
                zip_num = personal_info['zip']
                ssn = personal_info['socialnumber'][-4:]
                phone_num = personal_info['mobilenumber']
            if created_flag <= int(created_paypal_account_process) or confirm_identity_state == 0 or confirm_email == 0:
                config_text = get_path_config()
                proxy_exe = config_text['proxy_exe']
                client_exe = config_text['client_exe']
                proxifier_path = config_text['proxifier_path']
                proxifier_file = config_text['proxifier_file']
                open_proxy_process(client_exe)
                driver = re_driver_and_choice_ip(paypal_type, state, city, proxy_exe, proxifier_path, proxifier_file)
                if paypal_type == 1:
                    pass
                elif paypal_type == 2:
                    if created_flag == 0:
                        step_flag = paypal_here_page_one(
                            driver, step_flag, firstname, lastname, email, paypal_pwd)
                        if step_flag == 1:
                            here_success = paypal_here_page_two(
                                driver, name, address, city, full_state, zip_num, birthdate, phone_num, ssn)
                            if here_success > -1 and is_register_card_email == 0:
                                sql = sql = 'UPDATE register_info set userInfoIsUsed=1, email_id=%s, read_num=read_num+1 where id=%s'
                                commit_sql(conn, sql, (email_id, register_info_id))
                            if here_success == 1:
                                account_type = 2
                            elif here_success == 0:
                                account_type = 3
                            if here_success > -1:
                                sql = 'UPDATE email_info set account_type=3, paypal_pwd=%s, register_info_id=%s, created_paypal_time=%s, created_paypal_account=1'
                                commit_sql(conn, sql, (account_type, paypal_pwd, register_info_id, current_time))
                                step_flag = 1
                if confirm_email == 0 and step_flag == 1:
                    # 需要进入登录框登录
                    if login_with_input_box:
                        if paypal_type == 2:
                            step_flag = paypal_here_page_one(driver, step_flag, firstname, lastname, email, paypal_pwd, True)
                        login_paypal(driver, email, paypal_pwd)
                    email_type = email.split('@')[-1]
                    if email_type == 'gmail.com':
                        print('Gmail!')
                        login_gmail(driver, conn, email, email_pwd, paypal_pwd, recovery_email)
                    elif email_type == 'yahoo.com':
                        print('Yahoo!')
                        step_flag = login_yahoo(driver, conn, email, email_pwd, paypal_pwd, step_flag, paypal_type)
                        if step_flag == 1:
                            sql = 'UPDATE email_info set confirm_email=1 where email=%s'
                            commit_sql(conn, sql, email)
                time.sleep(3)
                # the_end()
                time.sleep(9999)

            else:
                print('Have already registered!')


def get_path_config():
    config_text = {}
    conf = configparser.ConfigParser()
    conf.read('my_config.ini')
    proxifier_path = conf.get('modify_port', 'proxifier_path')
    proxifier_file = conf.get('modify_port', 'proxifier_file')
    client_exe = conf.get('proxy_path', 'client_exe')
    proxy_exe = conf.get('proxy_path', 'proxy_exe')
    config_text['proxifier_path'] = proxifier_path
    config_text['proxifier_file'] = proxifier_file
    config_text['client_exe'] = client_exe
    config_text['proxy_exe'] = proxy_exe

    return config_text


def get_confirm_bank_info():
    if confirm_identity_state == 0 and created_flag == 3:
        print('Confirm bank!')
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
            if login_on_page == 1:
                login_paypal(driver, email, paypal_pwd)
            confirm_identity(conn, driver, email, confirm_info_id, confirm_user,
                             confirm_pwd, routing_number, account_number, confirm_type)
        else:
            print('No Confirm Info!')


def open_proxy_process(client_exe):
    p = subprocess.Popen(client_exe, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    time.sleep(8)
    try_time = 1
    while True:
        win32api.keybd_event(13, 0, 0, 0)
        win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(1)
        dialog1 = win32gui.FindWindow(
            'ThunderRT6FormDC', '911 S5 3.1')
        login = win32gui.FindWindowEx(
            dialog1, 0, 'ThunderRT6CommandButton', None)
        win32gui.SendMessage(
            dialog1, win32con.WM_COMMAND, 0, login)
        time.sleep(5)
        try_time += 1
        if try_time > 10:
            break


def re_driver_and_choice_ip(paypal_type, state, city, proxy_exe, proxifier_path, proxifier_file):
    while True:
        p = subprocess.Popen('%s -changeproxy/all/%s/%s -citynolimit' % (proxy_exe, state, city),
                             shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.wait()
        time.sleep(5)
        modify_port(proxifier_path, proxifier_file)
        time.sleep(3)
        p = subprocess.Popen('Proxifier.exe %s' % proxifier_file,
                             shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        p.wait()
        time.sleep(3)
        options = webdriver.ChromeOptions()
        options.add_argument('disable-infobars')
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
        # 个人号
        if paypal_type == 1:
            if login_with_input_box:
                driver.get('https://www.paypal.com/us/signin')
            else:
                driver.get('https://www.paypal.com/welcome/signup')
        # Here 账号
        elif paypal_type == 2:
            driver.get(
                'https://www.paypal.com/us/bizsignup/entry?product=pph')
        time.sleep(3)
        if driver.page_source.find('This site can’t be reached') > -1:
            print('Net error!')
            driver.quit()
            time.sleep(1)
            continue
        else:
            break

    return driver


def the_end():
    p = subprocess.Popen('cmd.exe /c' + 'taskkill /F /im Client.exe',
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p.wait()
    p = subprocess.Popen('cmd.exe /c' + 'taskkill /F /im Proxifier.exe',
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p.wait()
    driver.quit()
    time.sleep(1)
    os.system('shutdown -s -t 10')
    p = subprocess.Popen('cmd.exe /c' + 'taskkill /F /im python.exe',
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    time.sleep(30)


def pip_python_package():
    p = subprocess.Popen(
        'cmd.exe /c pip install configparser', shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    p.wait()


if __name__ == '__main__':
    main()
