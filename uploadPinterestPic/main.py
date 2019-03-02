'''
Author: Vinter Wang
Email: printhello@163.com
'''
import pymysql
from selenium import webdriver
from selenium.webdriver import ActionChains
import random
import datetime
import time
import socket
from login import login
from dbconnection import fetch_one_sql, fetch_all_sql, commit_sql
from config import write_txt_time, connect_vpn
import win32api
import win32con
import os


class Main():
    def __init__(self):
        super(Main, self).__init__()
        self.conn = pymysql.connect(host='localhost', port=3306,
                                    user='root', password='123456',
                                    db='new_pin', charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)
        self.conn1 = pymysql.connect(host='localhost', port=3306,
                                     user='root', password='123456',
                                     db='vpn', charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        self.conn2 = pymysql.connect(host='localhost', port=3306,
                                     user='root', password='123456',
                                     db='pin_follow', charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        self.conn3 = pymysql.connect(host='localhost', port=3306,
                                     user='root', password='123456',
                                     db='pin_upload', charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        self.driver = ''
        self.hostname = socket.gethostname()
        self.current_time = datetime.datetime.now().strftime("%Y-%m-%d")
        self.email = ''
        self.pwd = ''
        self.vpn = ''
        self.cookie = ''
        self.agent = ''
        self.belong_web = ''
        self.account_id = 0
        self.success_num = 0
        self.config_id = 0
        # Try to locate the home element. If there is off, you don't need to do all kinds of pop-ups
        self.login_state_flag = ''
        # Steps and params to control
        self.access_home_page_control = 0
        self.create_board_num = 0
        self.save_pic_control = 0
        self.follow_num = 0
        self.pin_self_count = 0
        self.created_boards = 0
        self.search_words_count = 0
        self.scroll_num = 0
        self.upload_done = 0
        self.pinterest_acotion()

    def pinterest_acotion(self):
        while True:
            if self.success_num > 4:
                os.system('shutdown -r')
                print('clear cache')
                time.sleep(9999)
            write_txt_time()
            print(self.hostname)
            self.get_account()
            if self.account_id > 0:
                self.success_num += 1
                connect_vpn(self.conn1, self.vpn)
                write_txt_time()
                options = webdriver.ChromeOptions()
                options.add_argument('disable-infobars')
                options.add_argument('user-agent="%s"' % self.agent)
                prefs = {
                    'profile.default_content_setting_values':
                    {'notifications': 2
                     }
                }
                options.add_experimental_option('prefs', prefs)
                self.driver = webdriver.Chrome(chrome_options=options)
                self.driver.maximize_window()
                login_state = login(
                    self.driver, self.email, self.pwd, self.account_id, self.cookie, self.conn)
                time.sleep(2)
                try:
                    home_button = self.driver.find_element_by_xpath(
                        '//div[@aria-label="Home"]/a/div/div/div/div').text
                    if home_button == 'Home':
                        self.login_state_flag = 'on'
                except Exception as e:
                    self.login_state_flag = 'off'
                print('State of home page:', self.login_state_flag)
                if self.login_state_flag == 'on':
                    self.handle_pop_up()
                # print(login_state)
                if login_state == 1 and self.login_state_flag == 'on':
                    sql = "UPDATE account set login_times=login_times+1 where id=%s"
                else:
                    sql = "UPDATE account set state=4, login_times=0, action_computer='-' where id=%s"
                    try:
                        error_type = self.driver.find_element_by_xpath(
                            '//form//button/span').text
                        if error_type == 'Reset your password':
                            sql = 'UPDATE account set state=9, login_times=0, action_computer="-" where id=%s'
                            print('Error code: 9')
                    except Exception as e:
                        pass
                    time.sleep(3)
                    try:
                        if self.driver.page_source.find('Your account has been suspended') > -1:
                            sql = 'UPDATE account set state=99, login_times=0, action_computer="-" where id=%s'
                            print('Error code: 99')
                    except Exception as e:
                        pass
                commit_sql(self.conn, sql, self.account_id)
                if login_state == 0 or self.login_state_flag == 'off':
                    print('Account log-in failure, will exit the browser!')
                    try:
                        self.driver.quit()
                    except:
                        pass
                    time.sleep(5)
                    continue
                else:
                    write_txt_time()
                    self.access_home_page()
                    if self.created_boards < 5:
                        self.create_board()
                    self.upload_pic()
                    print('End of account processing...')
                    self.driver.quit()
                    sql = "UPDATE account set state=1, login_times=0, action_time=%s, action_computer='-' where id=%s"
                    commit_sql(self.conn, sql,
                               (self.current_time, self.account_id))
                    write_txt_time()
                    time.sleep(10)
            else:
                print('Not data...')
                write_txt_time()
                time.sleep(10)
                print('The system will reboot in 30 minutes')
                os.system('shutdown -r -t 1800')
                time.sleep(9999)

    # Access to the account
    def get_account(self):
        # self.get_account_count()
        if self.hostname == 'Vinter-Wang':
            sql = 'SELECT * from account where id=1'
            result = fetch_one_sql(self.conn, sql)
        else:
            sql = 'SELECT * from account where state=1 and action_time<%s and upload_done=666 and action_computer=%s order by action_time asc limit 1'
            result = fetch_one_sql(
                self.conn, sql, (self.current_time, self.hostname))
        if result:
            self.account_id = result["id"]
            self.email = result["email"]
            self.pwd = result["pw"]
            self.vpn = result['vpn']
            self.cookie = result['cookie']
            self.config_id = result['setting_other']
            self.created_boards = result['created_boards']
            self.agent = result['agent']
            self.belong_web = result['upload_web']
            if not self.agent:
                sql = 'SELECT * from user_agent where terminal="computer" and read_time<4 order by RAND() limit 1'
                agent_in_sql = commit_sql(self.conn2, sql)
                if agent_in_sql:
                    self.agent = agent_in_sql['user_agent']
                    agent_id = agent_in_sql['Id']
                    sql = 'UPDATE account set agent=%s where id=%s'
                    commit_sql(self.conn, sql, (self.agent, self.account_id))
                    sql = 'UPDATE user_agent set read_time=read_time+1 where id=%s'
                    commit_sql(self.conn2, sql, agent_id)
            print("Start account processing:", "ID:",
                  self.account_id, "Email:", self.email)
            write_txt_time()
        else:
            sql = 'SELECT * from account where state=1 and action_time<%s and upload_done=666 and action_computer="-" order by action_time asc limit 1'
            result = fetch_one_sql(self.conn, sql, self.current_time)
            if result:
                self.account_id = result["id"]
                self.email = result["email"]
                self.pwd = result["pw"]
                self.vpn = result['vpn']
                self.cookie = result['cookie']
                self.config_id = result['setting_other']
                self.created_boards = result['created_boards']
                self.account_group = result['account_group']
                self.agent = result['agent']
                self.belong_web = result['upload_web']
                if not self.agent:
                    sql = 'SELECT * from user_agent where terminal="computer" and read_time<4 order by RAND() limit 1'
                    agent_in_sql = fetch_one_sql(self.conn2, sql)
                    if agent_in_sql:
                        self.agent = agent_in_sql['user_agent']
                        agent_id = agent_in_sql['Id']
                        sql = 'UPDATE account set agent=%s where id=%s'
                        commit_sql(self.conn, sql,
                                   (self.agent, self.account_id))
                        sql = 'UPDATE user_agent set read_time=read_time+1 where id=%s'
                        commit_sql(self.conn2, sql, agent_id)
                print("Start account processing:", "ID:",
                      self.account_id, "Email:", self.email)
                sql = "UPDATE account set action_computer=%s where id=%s"
                commit_sql(self.conn, sql, (self.hostname, self.account_id))
                write_txt_time()

    # Access to the home page
    def access_home_page(self):
        home_page_element = self.driver.find_element_by_xpath(
            '//div[@aria-label="Saved"]/a')
        home_page = home_page_element.get_attribute('href')
        # print(home_page)
        sql = 'UPDATE account set home_page=%s where id=%s'
        commit_sql(self.conn, sql, (home_page, self.account_id))
        time.sleep(2)

    def handle_pop_up(self):
        try:
            self.driver.find_element_by_xpath(
                "//span[text()='Female']").click()
            time.sleep(1)
        except:
            pass
        time.sleep(1)
        try:
            click_confirm = self.driver.switch_to.alert
            click_confirm.accept()
            time.sleep(1)
        except Exception as e:
            print('No popovers to process, skip...')
        time.sleep(1)
        try:
            self.driver.find_element_by_xpath(
                '//div[@class="NuxPickerFooter"]//button').click()
            print('Preference already selected')
            time.sleep(1)
        except Exception as e:
            print('No need to select preference, skip...')
        time.sleep(1)
        try:
            self.driver.find_element_by_xpath(
                '//div[@class="ReactModalPortal"]//button[@aria-label="cancel"]').click()
            print('Preference set')
            time.sleep(1)
        except Exception as e:
            print('No preference Settings, skip...')
        time.sleep(1)
        try:
            self.driver.find_element_by_xpath(
                '//div[@class="ReactModalPortal"]//button').click()
            print('Email has been confirmed')
            time.sleep(1)
        except Exception as e:
            print('No need to confirm email, skip...')
        time.sleep(1)
        try:
            self.driver.find_element_by_xpath(
                "//div[@class='NagBase']/div/div[2]/button").click()
            print('The renewal agreement has been accepted')
            time.sleep(1)
        except Exception as e:
            print('No need to accept the update protocol, skip...')
        time.sleep(1)
        try:
            self.driver.find_element_by_xpath(
                '//button[@aria-label="Hide Checklist"]').click()
        except:
            pass
        time.sleep(2)
        write_txt_time()

    def upload_pic(self):
        all_upload_num = 0
        sql = 'SELECT * from config where id=1'
        upload_num_res = fetch_one_sql(self.conn3, sql)
        if upload_num_res:
            all_upload_num = upload_num_res['upload_num']
        print('Start uploading images...')
        while True:
            save_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = "SELECT count(-1) as allnum from pin_upload where belong_web=%s and save_time>=%s"
            upload_num = fetch_one_sql(
                self.conn3, sql, (self.belong_web, self.current_time))['allnum']
            if upload_num < all_upload_num:
                sql = 'SELECT * from pin_upload where saved=0 and belong_web=%s order by id asc limit 1'
                result = fetch_one_sql(self.conn3, sql, self.belong_web)
                if result:
                    upload_pic_path = result['savelink']
                    upload_pic_board = result['saveboard']
                    upload_pic_id = result['Id']
                    self.driver.get(upload_pic_path)
                    time.sleep(5)
                    try:
                        self.driver.find_element_by_xpath(
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
                    if self.driver.page_source.find('Sorry! We blocked this link because it may lead to spam.') > -1:
                        print('Domain name banned!')
                        sql = 'UPDATE web_url set state=4 where url=%s'
                        commit_sql(self.conn3, sql, self.belong_web)
                        sql = 'UPDATE account set upload_done=664 where id=%s'
                        commit_sql(self.conn, sql, account_id)
                        break
                    try:
                        self.driver.find_element_by_xpath(
                            "//div[@class='mainContainer']//div[1]/div/button").click()
                        time.sleep(5)
                        sql = 'UPDATE pin_upload set saved=1, save_time=%s where id=%s'
                        commit_sql(self.conn3, sql, (save_time, upload_pic_id))
                        print('Uploading %d' % int(upload_num + 1))
                        write_txt_time()
                    except Exception as e:
                        pass
                else:
                    print('Not data...')
                    sql = 'UPDATE account set upload_done=669 where id=%s'
                    commit_sql(self.conn, sql, account_id)
                    time.sleep(3)
                    break
            else:
                break

    def create_board(self):
        print('Start create board')
        sql = "SELECT board_name from board_template order by RAND() limit 5"
        results = fetch_all_sql(self.conn, sql)
        for board_echo in results:
            board_name = board_echo['board_name']
            print('Boardname', board_name)
            sql = "SELECT home_page from account where id=%s"
            result = fetch_one_sql(self.conn, sql, self.account_id)
            if result:
                home_page = result['home_page'] + 'boards/'
            try:
                self.driver.get(home_page)
                time.sleep(5)
                self.driver.find_element_by_xpath(
                    '//button[@aria-label="Profile actions overflow"]').click()
                time.sleep(2)
                self.driver.find_element_by_xpath(
                    '//div[@class="fixedHeader"]//div[text()="Create board"]').click()
                time.sleep(5)
                self.driver.find_element_by_xpath(
                    '//form//input[@id="boardEditName"]').send_keys(board_name)
                time.sleep(1)
                self.driver.find_element_by_xpath(
                    '//form//button[@type="submit"]').click()
                time.sleep(2)
                sql = "UPDATE account set created_boards=created_boards+1 where id=%s"
                commit_sql(self.conn, sql, self.account_id)
                time.sleep(3)
            except:
                pass
        self.driver.get('https://www.pinterest.com')
        time.sleep(5)


if __name__ == '__main__':
    Main()
    print('End...')
