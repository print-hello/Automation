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
from change_password_login import click_login
from dbconnection import read_one_sql, read_all_sql, write_sql
from config import write_txt_time, connect_vpn
import win32api
import win32con
import os


class Main():
    def __init__(self):
        super(Main, self).__init__()
        self.conn = pymysql.connect(host='localhost', port=3306,
                                    user='root', password='******',
                                    db='pinterest', charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)
        self.conn1 = pymysql.connect(host='localhost', port=3306,
                                     user='root', password='******',
                                     db='vpn', charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        self.conn2 = pymysql.connect(host='localhost', port=3306,
                                     user='root', password='******',
                                     db='pin_follow', charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        self.driver = ''
        self.hostname = socket.gethostname()
        self.current_time = datetime.datetime.now().strftime("%Y-%m-%d")
        self.email = ''
        self.pwd = ''
        self.vpn = ''
        self.cookie = ''
        self.agent = ''
        self.account_id = 0
        self.success_num = 0
        self.config_id = 0
        self.account_group = 0
        self.save_pic_from_homepage_control = 0
        self.click_specific_pin_control = 0
        # Try to locate the home element. If there is off, you don't need to do all kinds of pop-ups
        self.login_state_flag = ''
        # Steps and params to control
        self.upload_pic_control = 0
        self.upload_pic_min_num = 0
        self.upload_pic_max_num = 0
        self.random_browsing_control = 0
        self.browsing_pic_min_num = 0
        self.browsing_pic_max_num = 0
        self.access_home_page_control = 0
        self.create_board_control = 0
        self.save_pic_control = 0
        self.follow_num = 0
        self.pin_self_count = 0
        self.search_words_count = 0
        self.scroll_num = 0
        self.pin_count = 0
        self.pinterest_acotion()

    def pinterest_acotion(self):
        while True:
            if self.success_num > 4 and self.hostname != 'ChangePassword':
                os.system('shutdown -r')
                print('clear cache')
                time.sleep(9999)
            write_txt_time()
            print(self.hostname)

            self.get_account()
            if self.account_id > 0:
                self.get_config()
                self.success_num += 1
                connect_vpn(self.conn1, self.vpn)
                write_txt_time()
                options = webdriver.ChromeOptions()
                options.add_argument('user-agent="%s"' % self.agent)
                prefs = {
                    'profile.default_content_setting_values':
                    {'notifications': 2
                     }
                }
                options.add_experimental_option('prefs', prefs)
                self.driver = webdriver.Chrome(chrome_options=options)
                self.driver.maximize_window()

                if self.hostname == 'ChangePassword':
                    login_state = click_login(
                        self.driver, self.email, self.pwd, self.account_id, self.cookie, self.conn)
                else:
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
                    sql = "UPDATE account set login_times=login_times+1 where id=%s" % self.account_id
                else:
                    sql = "UPDATE account set state=4, login_times=0, action_computer='-' where id=%s" % self.account_id
                    try:
                        error_type = self.driver.find_element_by_xpath(
                            '//form//button/span').text
                        # print(error_type)
                        if error_type == 'Reset your password':
                            sql = 'UPDATE account set state=9, login_times=0, action_computer="-" where id=%s' % self.account_id
                            print('Error code: 9')
                    except Exception as e:
                        pass
                    time.sleep(3)
                    try:
                        if self.driver.page_source.find('Your account has been suspended') > -1:
                            sql = 'UPDATE account set state=99, login_times=0, action_computer="-" where id=%s' % self.account_id
                            print('Error code: 99')
                    except Exception as e:
                        pass
                write_sql(self.conn, sql)
                if login_state == 0 or self.login_state_flag == 'off':
                    if self.hostname == 'ChangePassword':
                        step_num = int(input('''Please select operation:
                            1: remove the next account
                            2: no account can be found and marked'''))
                        if step_num == 1:
                            pass
                        elif step_num == 2:
                            sql = 'UPDATE account set state=99, login_times=0 where id=%s' % self.account_id
                            write_sql(self.conn, sql)
                    print('Account log-in failure, will exit the browser!')
                    try:
                        self.driver.quit()
                    except:
                        pass
                    time.sleep(5)
                    continue
                else:
                    write_txt_time()
                    if self.access_home_page_control == 1:
                        self.access_home_page()
                    # if self.create_board_control == 1:
                    #     self.create_board()
                    # if self.upload_pic_control == 1:
                    #     self.upload_pic()
                    if self.random_browsing_control == 1:
                        self.random_browsing()
                    if self.follow_num > 0:
                        self.follow()
                    if self.click_specific_pin_control == 1:
                        self.click_specific_pin()
                    if self.save_pic_from_homepage_control == 1:
                        self.save_pic_from_homepage()
                    print('End of account processing...')
                    self.driver.quit()
                    sql = "UPDATE account set state=1, login_times=0, action_time='%s', action_computer='-' where id=%s" % (
                        self.current_time, self.account_id)
                    write_sql(self.conn, sql)
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
        self.get_account_count()
        if self.hostname == 'Vinter-Wang':
            sql = 'SELECT * from account where id=1'
        elif self.hostname == 'ChangePassword':
            sql = "SELECT * from account where action_time<'%s' and state=9 or state=4 and login_times<4 order by action_time asc limit 1" % (
                self.current_time)
        else:
            sql = "SELECT * from account where action_computer='%s' and action_time<'%s' and state=1 and login_times<4 order by action_time asc limit 1" % (
                self.hostname, self.current_time)
        result = read_one_sql(self.conn, sql)
        if result:
            self.account_id = result["id"]
            self.email = result["email"]
            self.pwd = result["pw"]
            self.vpn = result['vpn']
            self.cookie = result['cookie']
            self.config_id = result['setting_other']
            self.account_group = result['account_group']
            self.agent = result['agent']
            if not self.agent:
                sql = 'SELECT * from user_agent where terminal="computer" and read_time<4 order by RAND() limit 1'
                agent_in_sql = read_one_sql(self.conn2, sql)
                if agent_in_sql:
                    self.agent = agent_in_sql['user_agent']
                    agent_id = agent_in_sql['Id']
                    sql = 'UPDATE account set agent="%s" where id=%s' % (
                        self.agent, self.account_id)
                    write_sql(self.conn, sql)
                    sql = 'UPDATE user_agent set read_time=read_time+1 where id=%s' % agent_id
                    write_sql(self.conn2, sql)
            print("Start account processing:", "ID:",
                  self.account_id, "Email:", self.email)
            write_txt_time()
        else:
            sql = "SELECT * from account where action_computer='-' and action_time<'%s' and state=1 and login_times<4 order by action_time asc limit 1" % (
                self.current_time)
            result = read_one_sql(self.conn, sql)
            if result:
                self.account_id = result["id"]
                self.email = result["email"]
                self.pwd = result["pw"]
                self.vpn = result['vpn']
                self.cookie = result['cookie']
                self.config_id = result['setting_other']
                self.account_group = result['account_group']
                self.agent = result['agent']
                if not self.agent:
                    sql = 'SELECT * from user_agent where terminal="computer" and read_time<4 order by RAND() limit 1'
                    agent_in_sql = read_one_sql(self.conn2, sql)
                    if agent_in_sql:
                        self.agent = agent_in_sql['user_agent']
                        agent_id = agent_in_sql['Id']
                        sql = 'UPDATE account set agent="%s" where id=%s' % (
                            self.agent, self.account_id)
                        write_sql(self.conn, sql)
                        sql = 'UPDATE user_agent set read_time=read_time+1 where id=%s' % agent_id
                        write_sql(self.conn2, sql)
                print("Start account processing:", "ID:",
                      self.account_id, "Email:", self.email)
                sql = "UPDATE account set action_computer='%s' where id=%s" % (
                    self.hostname, self.account_id)
                write_sql(self.conn, sql)
                write_txt_time()

    def get_account_count(self):
        sql = 'SELECT * from account_count'
        result = read_one_sql(self.conn, sql)
        if result:
            all_count = result['all_count']
            real_time_num = result['real_time_num']
            last_update_time = result['last_update_time']
            if str(last_update_time) < self.current_time:
                recovery_mode = 'UPDATE account set state=1 where state=4'
                write_sql(self.conn, recovery_mode)
                change_group = 'UPDATE follow_url set account_group=account_group+1 where for_config=10'
                write_sql(self.conn2, change_group)
                all_group = 'SELECT count(-1) from follow_url where for_config=10'
                all_group_count = read_one_sql(
                    self.conn2, all_group)['count(-1)']
                debug_group = 'UPDATE follow_url set account_group=1 where account_group>%s' % all_group_count
                write_sql(self.conn2, debug_group)
                sql = '''UPDATE account_count set last_update_time="%s", all_count=
                    (SELECT count(1) from `account` where state=1) where id=1''' % self.current_time
            else:
                sql = 'UPDATE account_count set real_time_num=(SELECT count(1) from `account` where state=1) where id=1'
            write_sql(self.conn, sql)
        if all_count - real_time_num > 10:
            os.system('shutdown -r -t 1800')
            time.sleep(9999)
            print('Too many account errors today to suspend operations!')

    def get_config(self):
        print('Run configuration:', self.config_id)
        if self.hostname == 'ChangePassword':
            sql = 'SELECT * from configuration where priority=0'
        else:
            sql = 'SELECT * from configuration where priority=%s' % self.config_id
        result = read_one_sql(self.conn, sql)
        # choice_config_sorted = sorted(results, key=lambda priority: priority['priority'])
        if result:
            self.random_browsing_control = result['random_browsing_control']
            self.browsing_pic_min_num = result['browsing_pic_min_num']
            self.browsing_pic_max_num = result['browsing_pic_max_num']
            self.access_home_page_control = result['access_home_page_control']
            self.save_pic_control = result['save_pic_control']
            self.follow_num = result['follow_num']
            self.pin_self_count = result['pin_self_count']
            self.search_words_count = result['search_words_count']
            self.scroll_num = result['scroll_num']
            self.save_pic_from_homepage_control = result['save_pic_from_homepage_control']
            self.click_specific_pin_control = result['click_specific_pin_control']

    # Access to the home page
    def access_home_page(self):
        home_page_element = self.driver.find_element_by_xpath(
            '//div[@aria-label="Saved"]/a')
        home_page = home_page_element.get_attribute('href')
        # print(home_page)
        sql = 'UPDATE account set home_page="%s" where id=%s' % (
            home_page, self.account_id)
        write_sql(self.conn, sql)
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
            # self.driver.find_element_by_xpath(
            #     '//div[@class="ReactModalPortal"]/div/div/div/div/div/div[3]/div/div[2]/div/button').send_keys(Keys.SPACE)
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
        time.sleep(2)
        write_txt_time()

    def upload_pic(self):
        upload_pic_num = random.randint(
            self.upload_pic_min_num, self.upload_pic_max_num)
        print('Upload number of picture processing:', upload_pic_num)
        if upload_pic_num > 0:
            sql = "SELECT * from publish where saved=0 ORDER BY RAND() limit %s" % upload_pic_num
        print('Start uploading images...')
        count = 0
        while True:
            sql = "SELECT * from save_web_pic where saved=0"
            cur = conn1.cursor()
            cur.execute(sql)
            results = cur.fetchall()
            if results:
                for rows in results:
                    upload_pic_path = rows['pic_path']
                    upload_pic_board = rows['board']
                    upload_pic_id = rows['id']
                    sql = "UPDATE save_web_pic set saved = 1 where id = %s" % upload_pic_id
                    cur1 = conn1.cursor()
                    cur1.execute(sql)
                    conn1.commit()
                    cur1.close()
                    driver.get(upload_pic_path)
                    time.sleep(5)
                    flag_content = 'Psst! You already saved this Pin to'
                    if driver.page_source.find(flag_content) > -1:
                        print('is saved...')
                        time.sleep(2)
                    else:
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
                            count += 1
                            print('Uploading %d' % count)
                        except Exception as e:
                            print("You don't need to create a taxonomy",
                                  upload_pic_board)
                        time.sleep(5)
                    sql = "UPDATE save_web_pic set saved = 2 where id = %s" % upload_pic_id
                    cur1 = conn1.cursor()
                    cur1.execute(sql)
                    conn1.commit()
                    cur1.close()
            else:
                print('pass')
        time.sleep(2)

    # Random browse
    def random_browsing(self, search_pattern=0, board_name='like', belong=2):
        random_browsing_num = random.randint(
            self.browsing_pic_min_num, self.browsing_pic_max_num)
        print('Start random browsing:', random_browsing_num, 'time')
        for i in range(random_browsing_num):
            try:
                write_txt_time()
                web_pin_arr = self.driver.find_elements_by_xpath(
                    "//div[@data-grid-item='true']")
                click_num = random.randint(1, 8)
                print('Start the', i + 1, 'browsing')
                web_pin_num = 1
                for web_pin_one in web_pin_arr:
                    if web_pin_num == click_num:
                        web_pin_one.click()
                        time.sleep(5)
                        try:
                            self.close_AD_page()
                        except Exception as e:
                            if search_pattern == 1:
                                self.save_pic(board_name)
                            elif search_pattern == 0 and self.save_pic_control == 1 and (i + 1) % 2 == 0:
                                self.save_pic()
                        win32api.keybd_event(27, 0, 0, 0)
                        win32api.keybd_event(
                            27, 0, win32con.KEYEVENTF_KEYUP, 0)
                        time.sleep(3)
                        # self.driver.execute_script('window.scrollTo(1, 4000)')
                        win32api.keybd_event(35, 0, 0, 0)
                        win32api.keybd_event(
                            35, 0, win32con.KEYEVENTF_KEYUP, 0)
                        time.sleep(3)
                        break
                    else:
                        web_pin_num += 1
            except Exception as e:
                print(e)
            time.sleep(3)
        write_txt_time()

    def close_AD_page(self):
        windows = self.driver.window_handles
        # Gets the new page handle
        self.driver.switch_to.window(windows[1])
        self.driver.close()
        print('Close the AD page')
        time.sleep(1)
        # go back to the original interface
        self.driver.switch_to.window(windows[0])
        time.sleep(1)

    # save a picture
    def save_pic(self, board_name='like', belong=2, specific_pin_url='empty', specific_pin_pic_url='empty'):
        saved_flag = ''
        if specific_pin_url != 'empty':
            pin_url = specific_pin_url
            pin_pic_url = specific_pin_pic_url
        else:
            pin_url = self.driver.current_url
            time.sleep(1)
            pin_pic_url = self.driver.find_element_by_xpath(
                '//a[@class="imageLink"]//img').get_attribute('src')
        add_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            saved_flag = self.driver.find_elements_by_xpath(
                '//div[@data-test-id="saved-info"]/div/a/span').text
        except:
            pass
        if saved_flag == 'Saved to ':
            print('The picture has been saved.')
        else:
            if belong == 2:
                sql = '''SELECT * from other_pin_history where pin_pic_url="%s" and account_id=%s''' % (
                    pin_pic_url, self.account_id)
            elif belong == 1:
                sql = '''SELECT * from pin_history where pin_pic_url="%s" and account_id=%s''' % (
                    pin_pic_url, self.account_id)
            result = read_one_sql(self.conn, sql)
            if result:
                print('The picture has been saved.')
            else:
                time.sleep(3)
                try:
                    self.driver.find_element_by_xpath(
                        '//div[@data-test-id="boardSelectionDropdown"]').click()
                    time.sleep(5)
                    self.driver.find_element_by_xpath(
                        "//input[@id='pickerSearchField']").send_keys(board_name)
                    time.sleep(5)
                except Exception as e:
                    print(e)
                try:
                    board_selector = self.driver.find_elements_by_xpath(
                        '//div[@data-test-id="board-picker-section"]//div[2]/div')
                    board_selector_list = []
                    for board_selector_one in board_selector:
                        board_text = board_selector_one.text
                        if board_text == board_name:
                            board_selector_list.append(board_selector_one)
                    if len(board_selector_list) > 0:
                        board_selector_list[0].click()
                        time.sleep(2)
                    else:
                        raise Exception
                except:
                    time.sleep(3)
                    self.driver.find_element_by_xpath(
                        '//div[@data-test-id="create-board"]/div').click()
                    time.sleep(3)
                    self.driver.find_element_by_name(
                        'boardName').clear()
                    time.sleep(1)
                    self.driver.find_element_by_name(
                        'boardName').send_keys(board_name)
                    self.driver.find_element_by_xpath(
                        "//form//button[@type='submit']").click()
                    time.sleep(2)
                if belong == 2:
                    sql = '''INSERT INTO other_pin_history (account_id, pin_url, pin_pic_url, add_time) values (
                        %s, %s, %s, %s)'''
                elif belong == 1:
                    sql = '''INSERT INTO pin_history (account_id, pin_url, pin_pic_url, add_time) values (
                        %s, %s, %s, %s)'''
                params = (self.account_id, pin_url, pin_pic_url, add_time)
                cur = self.conn.cursor()
                cur.execute(sql, params)
                self.conn.commit()
                cur.close()
                self.pin_count += 1
                time.sleep(3)
        write_txt_time()

    def create_board(self):
        print('Start create board')
        board_name = 'My favourite'
        sql = "SELECT home_page from account where id=%s" % self.account_id
        result = read_one_sql(self.conn, sql)
        if result:
            home_page = result['home_page'] + 'boards/'
        self.driver.get(home_page)
        time.sleep(3)
        self.driver.find_element_by_xpath(
            '//div[@data-test-id="create_boardCard"]').click()
        time.sleep(2)
        self.driver.find_element_by_xpath(
            '//form//input[@id="boardEditName"]').send_keys(board_name)
        time.sleep(1)
        self.driver.find_element_by_xpath(
            '//div[@class="ReactModalPortal"]//button[@type="submit"]').click()
        time.sleep(2)

    def click_specific_pin(self):
        print('Start searching for our company images')
        sql = "SELECT web_url from follow_url where for_config=%s" % self.config_id
        results = read_all_sql(self.conn2, sql)
        http_in_sql_list = []
        for res in results:
            http_in_sql = res['web_url']
            http_in_sql_list.append(http_in_sql)
        # print(http_in_sql_list)
        sql = "SELECT * from search_words where us=1 order by RAND() limit %s" % self.search_words_count
        key_wrods = read_all_sql(self.conn2, sql)
        if key_wrods:
            for key_wrod in key_wrods:
                search_key_words = key_wrod['word']
                board_name = key_wrod['boards']
                # belong = result['us']
                try:
                    self.driver.find_element_by_name('q').click()
                    time.sleep(1)
                    self.driver.find_element_by_name('q').clear()
                    time.sleep(1)
                    self.driver.find_element_by_name(
                        'q').send_keys(search_key_words)
                    time.sleep(1)
                    win32api.keybd_event(13, 0, 0, 0)
                    win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)
                except:
                    pass
                try:
                    self.driver.find_element_by_name("searchBoxInput").click()
                    time.sleep(1)
                    self.driver.find_element_by_name("searchBoxInput").clear()
                    time.sleep(1)
                    self.driver.find_element_by_name(
                        "searchBoxInput").send_keys(search_key_words)
                    time.sleep(1)
                    win32api.keybd_event(13, 0, 0, 0)
                    win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)
                except:
                    pass
                time.sleep(8)
                for _ in range(self.scroll_num):
                    try:
                        web_pin_arr = self.driver.find_elements_by_xpath(
                            "//div[@data-grid-item='true']")
                        # print(len(web_pin_arr))
                    except:
                        time.sleep(3)
                        web_pin_arr = self.driver.find_elements_by_xpath(
                            "//div[@data-grid-item='true']")
                    for web_pin_one in web_pin_arr:
                        try:
                            ActionChains(self.driver).move_to_element(
                                web_pin_one).perform()
                            time.sleep(3)
                        except:
                            pass
                        try:
                            web_pin = self.driver.find_element_by_xpath(
                                "//a[@class='navigateLink']//div[2]/div")
                            time.sleep(3)
                            web_pin_url = web_pin.text
                            # print(web_pin_url)
                            if web_pin_url in http_in_sql_list:
                                time.sleep(1)
                                specific_pin_url = web_pin_one.find_element_by_xpath(
                                    './/div[@class="pinWrapper"]/div/a').get_attribute('href')
                                time.sleep(1)
                                specific_pin_pic_url = web_pin_one.find_element_by_xpath(
                                    './/div[@class="pinWrapper"]//img').get_attribute('src')
                                self.save_pic(
                                    board_name=board_name, belong=1, specific_pin_url=specific_pin_url, specific_pin_pic_url=specific_pin_pic_url)
                        except Exception as e:
                            pass
                        if self.pin_count == self.pin_self_count:
                            break
                    if self.pin_count == self.pin_self_count:
                        break
                    else:
                        win32api.keybd_event(35, 0, 0, 0)
                        win32api.keybd_event(
                            35, 0, win32con.KEYEVENTF_KEYUP, 0)
                        time.sleep(5)
                        write_txt_time()
                if self.pin_count == self.pin_self_count:
                    break

    def follow(self):
        print('Turn on the follow function, count:', self.follow_num)
        sql = '''SELECT * from follow_url where for_config=10 limit %s''' % self.follow_num
        results = read_all_sql(self.conn2, sql)
        if results:
            for res in results:
                web_url_id = res['Id']
                web_url = res['web_url']
                home_url = res['home_url']
                sql = 'SELECT * from follow_history where user_id=%s and follow_account="%s"' % (
                    web_url_id, self.email)
                judge_exist = read_one_sql(self.conn2, sql)
                if judge_exist:
                    print('Already followed!')
                else:
                    try:
                        self.driver.get(home_url)
                    except:
                        pass
                    time.sleep(5)
                    try:
                        follow_state = self.driver.find_element_by_xpath(
                            '//div[@class="fixedHeader"]//div[3]//div[2]/button/div').text
                        if follow_state == 'Follow':
                            self.driver.find_element_by_xpath(
                                '//div[@class="fixedHeader"]//div[3]//div[2]/button').click()
                            time.sleep(1)
                            # self.driver.execute_script('window.scrollTo(1, 4000)')
                            # time.sleep(3)
                    except:
                        pass
                    try:
                        follow_state = self.driver.find_element_by_xpath(
                            '//div[@class="CreatorFollowButton step0"]//div[2]/div').text
                        if follow_state == 'Follow':
                            self.driver.find_element_by_xpath(
                                '//div[@class="CreatorFollowButton step0"]/div/div/div/div').click()
                            time.sleep(1)
                    except:
                        pass
                    cursor = self.conn2.cursor()
                    cursor.execute('INSERT INTO follow_history (user_id, user, user_homepage, follow_account) values (%s, %s, %s, %s)', (
                        web_url_id, web_url, home_url, self.email))
                    self.conn2.commit()
                    cursor.close()
        write_txt_time()


    def save_pic_from_homepage(self):
        sql = "SELECT * from follow_url where for_config=10 and account_group=%s" % self.account_group
        result = read_one_sql(self.conn2, sql)
        if result:
            http_in_sql = result['web_url']
            home_url = result['home_url']
            home_url_split = home_url.split('/')[-1]
        try:
            self.driver.find_element_by_xpath(
                '//div[@aria-label="Pins from people you follow"]/a/div').click()
            time.sleep(5)
            self.driver.find_element_by_xpath(
                '//button[@aria-label="Find new people to follow"]').click()
        except:
            self.driver.find_element_by_xpath(
                '//div[@data-test-id="button-container"]/div[2]').click()
        time.sleep(5)
        all_following = self.driver.find_elements_by_xpath(
            '//div[@data-grid-item="true"]')
        for one_following in all_following:
            following_homepage = one_following.find_element_by_xpath(
                './div/div/div/a').get_attribute('href')
            following_homepage_split = following_homepage.split('/')[-1]
            if following_homepage_split == home_url_split:
                one_following.click()
                time.sleep(5)
                break
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[1])
        self.driver.execute_script('window.scrollTo(1, 500)')
        time.sleep(5)
        try:
            web_pin_arr = self.driver.find_elements_by_xpath(
                "//div[@data-grid-item='true']")
        except:
            time.sleep(3)
            web_pin_arr = self.driver.find_elements_by_xpath(
                "//div[@data-grid-item='true']")
        pin_count = 0
        for web_pin_one in web_pin_arr:
            try:
                ActionChains(self.driver).move_to_element(
                    web_pin_one).perform()
                time.sleep(3)
            except:
                pass
            try:
                web_pin = self.driver.find_element_by_xpath(
                    "//a[@class='navigateLink']//div[2]/div")
                time.sleep(2)
                web_pin_url = web_pin.text
                if web_pin_url == http_in_sql:
                    time.sleep(1)
                    specific_pin_url = web_pin_one.find_element_by_xpath(
                        './/div[@class="pinWrapper"]/div/a').get_attribute('href')
                    time.sleep(1)
                    specific_pin_pic_url = web_pin_one.find_element_by_xpath(
                        './/div[@class="pinWrapper"]//img').get_attribute('src')
                    board_name = 'dress'
                    self.save_pic(
                        board_name=board_name, belong=1, specific_pin_url=specific_pin_url, specific_pin_pic_url=specific_pin_pic_url)
                    time.sleep(3)
                    pin_count += 1
            except Exception as e:
                pass
            if pin_count == self.pin_self_count:
                break
        write_txt_time()


if __name__ == '__main__':
    Main()
    print('End...')
