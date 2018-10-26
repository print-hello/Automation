'''
Author: Vinter Wang
Email: printhello@163.com
'''

import pymysql
from selenium import webdriver
import random
import datetime
import time
import socket
from login import login
from changePasswordLogin import clickLogin
from dbConnection import readOneSQL, readAllSQL, writeSQL
from configVPN import writeTxtTime, checkVPN, rasphoneVPN, getOutIP
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
                                     db='pinterest', charset='utf8mb4',
                                     cursorclass=pymysql.cursors.DictCursor)
        self.driver = ''
        self.hostname = socket.gethostname()
        self.check_vpn_num = 0
        self.email = ''
        self.pwd = ''
        self.cookie = ''
        self.vpn = ''
        self.account_id = 0
        self.success_num = 0
        self.upload_pic_min_num = 3
        self.upload_pic_max_num = 5
        self.get_account_success = 1
        self.current_time = datetime.datetime.now().strftime("%Y-%m-%d")
        # Steps to control
        self.step_control = 3
        # Try to locate the home element. If there is one, you don't need to do all kinds of pop-ups
        self.login_state_flag = ''
        self.pinterestAcotion()

    def pinterestAcotion(self):
        while True:
            if self.success_num > 4 and self.hostname != 'ChangePassword':
                os.system('shutdown -r')
                print('clear cache')
                time.sleep(9999)
            writeTxtTime()
            print(self.hostname)

            self.getAccount()
            if self.account_id > 0:
                self.success_num += 1
                self.connectVPN()
                writeTxtTime()
                options = webdriver.ChromeOptions()
                # options.add_argument('user-agent="Mozilla/5.0 (iPod; U; CPU iPhone OS 2_1 like Mac OS X; ja-jp) AppleWebKit/525.18.1 (KHTML, like Gecko) Version/3.1.1 Mobile/5F137 Safari/525.20"')
                prefs = {
                    'profile.default_content_setting_values':
                    {'notifications': 2
                     }
                }
                options.add_experimental_option('prefs', prefs)
                ''' chrome_options = options '''
                self.driver = webdriver.Chrome(chrome_options=options)
                self.driver.maximize_window()

                if self.hostname == 'ChangePassword':
                    login_state = clickLogin(
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
                    self.handlePopUp()
                # print(login_state)
                if login_state == 1 and self.login_state_flag == 'on':
                    sql = "update account set login_times=login_times+1 where id=%s" % self.account_id
                else:
                    sql = "update account set state=4, login_times=0 where id=%s" % self.account_id
                    try:
                        error_type = self.driver.find_element_by_xpath(
                            '//form//button/span').text
                        # print(error_type)
                        if error_type == 'Reset your password':
                            sql = 'update account set state=9, login_times=0 where id=%s' % self.account_id
                            print('Error code: 9-1')
                    except Exception as e:
                        pass
                    time.sleep(3)
                    try:
                        error_type = self.driver.find_element_by_xpath(
                            '//button[@aria-label="Reset your password"]')
                        sql = 'update account set state=9, login_times=0 where id=%s' % self.account_id
                        print('Error code: 9-2')
                    except Exception as e:
                        pass

                writeSQL(self.conn, sql)
                if login_state == 0 or self.login_state_flag == 'off':
                    if self.hostname == 'ChangePassword':
                        step_num = int(input('''Please select operation:
                            1: remove the next account
                            2: no account can be found and marked'''))
                        if step_num == 1:
                            pass
                        if step_num == 2:
                            sql = 'update account set state=99, login_times=0 where id=%s' % self.account_id
                            writeSQL(self.conn, sql)
                    print('Account log-in failure, will exit the browser!')
                    try:
                        self.driver.quit()
                    except:
                        pass
                    time.sleep(5)
                    continue
                else:
                    sql = "update account set state=1,  action_time='%s' where id=%s" % (
                        self.current_time, self.account_id)
                    writeSQL(self.conn, sql)
                    writeTxtTime()
                    self.accessHomePage()
                    time.sleep(3)
                    if self.step_control == 1:
                        self.createBoard()
                        time.sleep(3)
                        # self.uploadPic()
                    if self.step_control == 3:
                        self.randomBrowsing()
                    print('End of account processing...')
                    self.driver.quit()
                    writeTxtTime()
                    time.sleep(10)
            else:
                print('Not data...')
                writeTxtTime()
                time.sleep(10)
                print('The computer is about to be turned off')
                os.system('shutdown -s')
                time.sleep(120)

    # Access to the account
    def getAccount(self):
        if self.hostname == 'Vinter-Wang':
            sql = "select * from account where action_time<'%s' and state=1 and login_times<4 order by action_time asc limit 1" % (
                self.current_time)
            # sql = "select * from account where action_time<'2018-10-18' and state=1 and login_times<4 order by action_time asc limit 1"
            # sql = 'select * from account where id=88'
        elif self.hostname == 'ChangePassword':
            sql = "select * from account where action_time<'%s' and state=9 or state=4 and login_times<4 order by action_time asc limit 1" % (
                self.current_time)
        else:
            sql = "select * from account where action_computer='%s' and action_time<'%s' and state=1 and login_times<4 order by action_time asc limit 1" % (
                self.hostname, self.current_time)
        result = readOneSQL(self.conn, sql)
        if result:
            self.account_id = result["id"]
            self.email = result["email"]
            self.pwd = result["pw"]
            self.vpn = result['vpn']
            self.cookie = result['cookie']
            print("Start account processing:", self.email)
            writeTxtTime()
        else:
            sql = "select * from account where action_computer='-' and action_time<'%s' and state=1 and login_times<4 order by action_time asc limit 1" % (
                self.current_time)
            result = readOneSQL(self.conn, sql)
            if result:
                self.account_id = result["id"]
                self.email = result["email"]
                self.pwd = result["pw"]
                self.vpn = result['vpn']
                self.cookie = result['cookie']
                print("Start account processing:", self.email)
                sql = "update account set action_computer='%s' where id=%s" % (
                    self.hostname, self.account_id)
                writeSQL(self.conn, sql)
                writeTxtTime()

    def connectVPN(self):
        sql = "select account, pwd, server, ip from vpn where account='%s'" % self.vpn
        results = readAllSQL(self.conn1, sql)
        if results:
            for row in results:
                self.vpn = row['account']
                vpn_pwd = row['pwd']
                vpn_ip = row['ip']
                vpn_server = row['server'].replace('.lianstone.net', '')
                with open("F:\\pinterest\\boot\\vpn.txt", "w", encoding='utf-8') as fp:
                    print(vpn_server + "," + self.vpn + "," + vpn_pwd)
                    fp.write(vpn_server + "," + self.vpn + "," + vpn_pwd)
        else:
            print(
                'No corresponding VPN account has been detected and the system is being shut down...')
            time.sleep(600)
            os.system('Shutdown -s -t 0')
        print('Disconnect the original VPN connection')
        rasphoneVPN()
        writeTxtTime()
        print('Handling new VPN...')
        self.check_vpn_num = checkVPN()
        net_ip = getOutIP()
        writeTxtTime()
        while True:
            if net_ip == vpn_ip:
                print('VPN connection IP is correct!')
                break
            else:
                self.check_vpn_num = checkVPN()
                writeTxtTime()
                time.sleep(10)
                net_ip = getOutIP()

    # Access to the home page
    def accessHomePage(self):
        home_page_element = self.driver.find_element_by_xpath(
            '//div[@aria-label="Saved"]/a')
        home_page = home_page_element.get_attribute('href')
        # print(home_page)
        sql = 'update account set home_page="%s" where id=%s' % (
            home_page, self.account_id)
        writeSQL(self.conn, sql)
        time.sleep(2)

    def handlePopUp(self):
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

    def uploadPic(self):
        upload_pic_num = random.randint(
            self.upload_pic_min_num, self.upload_pic_max_num)
        print('Upload number of picture processing:', upload_pic_num)
        if upload_pic_num > 0:
            sql = "select * from publish where saved=0 ORDER BY RAND() limit %s" % upload_pic_num
        print('Start uploading images...')
        count = 0
        while True:
            sql = "select * from save_web_pic where saved=0"
            cur = conn1.cursor()
            cur.execute(sql)
            results = cur.fetchall()
            if results:
                for rows in results:
                    upload_pic_path = rows['pic_path']
                    upload_pic_board = rows['board']
                    upload_pic_id = rows['id']
                    sql = "update save_web_pic set saved = 1 where id = %s" % upload_pic_id
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

                    sql = "update save_web_pic set saved = 2 where id = %s" % upload_pic_id
                    cur1 = conn1.cursor()
                    cur1.execute(sql)
                    conn1.commit()
                    cur1.close()
            else:
                print('pass')
        time.sleep(2)

    # Random browse
    def randomBrowsing(self):
        # self.driver.get('https://www.pinterest.com')
        time.sleep(3)
        random_browsing_num = random.randint(2, 6)
        print('Start random browsing:', random_browsing_num, 'time')
        for i in range(random_browsing_num):
            try:
                writeTxtTime()
                # web_pin_arr = self.driver.find_elements_by_xpath("//div[@class='pinWrapper']")
                web_pin_arr = self.driver.find_elements_by_xpath(
                    "//div[@data-grid-item='true']")
                click_num = random.randint(1, 8)
                print('Start the', i + 1, 'browse, click the',
                      click_num, 'pin on the page...')
                web_pin_num = 1
                for web_pin_one in web_pin_arr:
                    if web_pin_num == click_num:
                        try:
                            click_confirm = self.driver.switch_to.alert
                            time.sleep(2)
                            click_confirm.accept()
                        except Exception as e:
                            print('No popovers to process, skip...')
                        time.sleep(2)
                        web_pin_one.click()
                        time.sleep(5)
                        windows = self.driver.window_handles
                        try:
                            # Gets the new page handle
                            self.driver.switch_to.window(windows[1])
                            self.driver.close()
                            print('Close the AD page')
                            time.sleep(1)
                            # go back to the original interface
                            self.driver.switch_to.window(windows[0])
                            time.sleep(1)
                        except Exception as e:
                            # self.savePic()
                            pass
                        time.sleep(1)
                        self.driver.execute_script('window.scrollTo(1, 3000)')
                        time.sleep(2)
                        break
                    else:
                        web_pin_num += 1
                time.sleep(3)

            except Exception as e:
                print(e)

    def createBoard(self):
        print('Start create board')
        board_name = 'My favourite'
        sql = 'select home_page from account where id=%s ' % self.account_id
        result = readOneSQL(self.conn, sql)
        if result:
            home_page = result['home_page'] + 'boards/'
        self.driver.get(home_page)
        time.sleep(3)
        self.driver.find_element_by_xpath(
            '//div[@data-test-id="createBoardCard"]').click()
        time.sleep(2)
        self.driver.find_element_by_xpath(
            '//form//input[@id="boardEditName"]').send_keys(board_name)
        time.sleep(1)
        self.driver.find_element_by_xpath(
            '//div[@class="ReactModalPortal"]//button[@type="submit"]').click()
        time.sleep(2)

    # save a picture
    def savePic(self):
        board_name = 'My favourite'
        try:
            saved = self.driver.find_element_by_xpath(
                '//div[@class="sticky"]//span').text
        except Exception as e:
            try:
                time.sleep(2)
                self.driver.find_element_by_xpath(
                    '//div[@data-test-id="boardSelectionDropdown"]').click()
            except Exception as e:
                self.driver.find_element_by_xpath(
                    '//div[@data-test-id="boardSelectionDropdown"]').click()
            time.sleep(3)
            try:
                slef.driver.find_element_by_xpath(
                    '//div[@data-test-id="SaveButton"]').click()
                time.sleep(2)
            except Exception as e:
                board_selector = self.driver.find_elements_by_xpath(
                    '//div[@data-test-id="board-picker-section"]/div/div/div[2]/div')
                for board_selector_one in board_selector:
                    board_text = board_selector_one.text
                    if board_text == board_name:
                        board_selector_one.click()


if __name__ == '__main__':
    Main()
    print('End...')
