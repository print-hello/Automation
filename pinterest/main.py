'''
Author: Vinter Wang
Email: printhello@163.com
'''
import os
import time
import socket
import datetime
from selenium import webdriver

from DBPools import OPMysql

from login_util import login
from login_util import get_coo

from util import write_txt_time
from util import connect_vpn
from util import rasphone_vpn

from opration_util import random_browsing
from opration_util import save_home_url
from opration_util import click_our_pin
from opration_util import handle_pop_up
from opration_util import create_board
from opration_util import upload_pic
from opration_util import follow


MYSQLINFO = {
    "host": 'localhost',
    "user": 'root',
    "passwd": '123456',
    "db": 'pinterest',
    "port": 3306,
    "charset": 'utf8mb4'
}


PROXY_IP = '127.0.0.1'


class OPPinterest():
    def __init__(self):
        super(OPPinterest, self).__init__()
        self.conn = OPMysql(MYSQLINFO)
        # logging.config.fileConfig('logging.conf')
        # self.logs = logging.getLogger()
        # email = logging.handlers.SMTPHandler(("smtp.163.com", 25), 'sendlogging@163.com',
        #                                      ['printhello@163.com'],
        #                                      "Logging from my app",
        #                                      credentials=(
        #                                          'sendlogging@163.com', '******'),
        #                                      )
        # self.logs.addHandler(email)
        self.hostname = socket.gethostname()
        self.current_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d")
        self.login_url = 'https://www.pinterest.com/login/?referrer=home_page'
        self.home_url = 'https://www.pinterest.com/homefeed/'
        self.driver = None
        self.proxy_type = 0
        self.account_id = 0
        self.email = None
        self.pwd = None
        self.port = 0
        self.vpn = None
        self.upload_web = None
        self.cookie = None
        self.agent = None
        self.success_num = 0
        self.config_id = 0
        self.click_our_pin_control = 0

        # Try to locate the home element. If there is off, you don't need to do all kinds of pop-ups

        # Steps and params to control
        self.upload_pic_control = 0
        self.upload_pic_min = 0
        self.upload_pic_max = 0
        self.random_browsing_control = 0
        self.browsing_pic_min = 0
        self.browsing_pic_max = 0
        self.save_home_url_control = 0
        self.create_board_num = 0
        self.save_pic_control = 0
        self.follow_num = 0
        self.pin_self_count = 0
        self.created_boards = 0
        self.search_words_count = 0
        self.scroll_num = 0

    def action(self):
        while True:
            step_flag = 1
            if self.success_num > 4:
                os.system('shutdown -r')
                print('Clear cache')
                time.sleep(9999)
            write_txt_time()
            print('Host Name:', self.hostname)
            self.get_account_count()
            self.get_account()
            if self.account_id > 0:
                self.get_config()
                self.success_num += 1
                write_txt_time()
                step_flag = self.re_driver(step_flag)
                if step_flag == 1:
                    login_state = login(
                        self.driver, self.login_url, self.account_id, self.email, self.pwd, self.cookie)
                    time.sleep(1)
                    if login_state == 1 or login_state == 11:
                        sql = "UPDATE account SET state=1, action_time=%s, login_times=login_times+1 WHERE id=%s"
                        self.conn.op_commit(sql, (self.current_time, self.account_id))
                        if login_state == 11:
                            cookie = get_coo(self.driver)
                            sql = 'UPDATE account SET cookie=%s WHERE id=%s'
                            self.conn.op_commit(sql, (cookie, self.account_id))
                        self.driver.get(self.home_url)
                        time.sleep(5)
                        handle_pop_up(self.driver)
                    else:
                        sql = 'UPDATE account SET state=%s, login_times=0, action_computer="-" WHERE id=%s'
                        self.conn.op_commit(sql, (login_state, self.account_id))
                        step_flag = 0
                        print('Account log-in failure, will exit the browser!')
                        try:
                            self.driver.quit()
                        except:
                            pass
                        time.sleep(5)
                        continue
                if step_flag == 1:
                    
                    if self.save_home_url_control == 1:
                        print('Save home page!')
                        save_home_url(self.driver, self.conn, self.account_id)

                    if self.create_board_num > 0 and self.created_boards < self.create_board_num:
                        print('Start create board')
                        create_board(self.driver, self.conn, self.home_url, self.account_id, self.create_board_num)

                    if self.follow_num > 0:
                        follow(self.driver, self.conn, self.home_url, step_flag, self.account_id, self.follow_num)

                    if self.random_browsing_control == 1:
                        random_browsing(
                            self.driver, self.conn, self.home_url, self.account_id, step_flag, self.save_pic_control, self.browsing_pic_min, self.browsing_pic_max)
                    
                    if self.click_our_pin_control == 1:
                        click_our_pin(self.driver, self.conn, self.home_url, step_flag, self.current_time, self.scroll_num, self.pin_self_count, self.search_words_count, self.account_id)

                    if self.upload_web != '-' and self.upload_pic_control == 1:
                        upload_pic(self.driver, self.conn, step_flag, self.current_time, self.account_id, self.upload_web, self.upload_pic_min, self.upload_pic_max)

                    print('End of account processing...')
                    time.sleep(3)
                    self.driver.quit()
                    sql = 'UPDATE account SET login_times=0, action_computer="-" WHERE id=%s'
                    self.conn.op_commit(sql, self.account_id)
                    write_txt_time()
                    time.sleep(10)
            else:
                print('Not data! The system will reboot in 30 minutes...')
                write_txt_time()
                os.system('shutdown -r -t 1800')
                time.sleep(1800)
                break

    # Access to the account
    def get_account(self):
        sql = 'SELECT * from machine where v_name=%s'
        machine_info = self.conn.op_select_one(sql, self.hostname[0])
        if machine_info:
            machine_type = machine_info['machine_type']
            if self.hostname == 'Vinter-Wang':
                sql = 'SELECT * FROM account WHERE id=1993'
                result = self.conn.op_select_one(sql)
            else:
                sql = "SELECT * FROM account WHERE proxy_type=%s AND action_computer=%s AND action_time<%s AND state=1 AND login_times<4 ORDER BY action_time ASC LIMIT 1"
                result = self.conn.op_select_one(sql, (machine_type, self.hostname, self.current_time))

                if result:
                    self.get_account_info(result)
                else:
                    sql = "SELECT * FROM account WHERE proxy_type=%s AND action_computer='-' AND action_time<%s AND state=1 AND login_times<4 ORDER BY action_time ASC limit 1"
                    result = self.conn.op_select_one(sql, (machine_type, self.current_time))

                    if result:
                        self.get_account_info(result)

                        sql = "UPDATE account SET action_computer=%s WHERE id=%s"
                        self.conn.op_commit(sql, (self.hostname, self.account_id))
                        write_txt_time()
                    else:
                        print('Not Data!')

    def get_account_info(self, result):
        self.proxy_type = result['proxy_type']
        self.account_id = result["id"]
        self.email = result["email"]
        self.pwd = result["pw"]
        self.port = result['port']
        self.vpn = result['vpn']
        self.upload_web = result['upload_web']
        self.cookie = result['cookie']
        self.created_boards = result['created_boards']
        self.config_id = result['setting_num']
        self.agent = result['agent']

        if not self.agent:
            sql = 'SELECT * FROM user_agent WHERE terminal="computer" ORDER BY RAND() LIMIT 1'
            agent_in_sql = self.conn.op_select_one(sql)
            if agent_in_sql:
                self.agent = agent_in_sql['user_agent']
                agent_id = agent_in_sql['Id']
                sql = 'UPDATE account SET agent=%s WHERE id=%s'
                self.conn.op_commit(sql, (self.agent, self.account_id))

        print("Start account processing..." + '\n' + "ID:",
              self.account_id, "Email:", self.email)

    def re_driver(self, step_flag):
        execute_path = os.path.abspath('.')
        webdriver_path = execute_path + '\\boot\\chromedriver.exe'
        options = webdriver.ChromeOptions()
        options.add_argument('disable-infobars')
        options.add_argument('user-agent="%s"' % self.agent)
        prefs = {
            'profile.default_content_setting_values':
            {'notifications': 2
             }
        }
        options.add_experimental_option('prefs', prefs)
        
        if self.vpn:
            connect_vpn(self.conn, self.agent, self.vpn, execute_path)
        else:
            rasphone_vpn(execute_path)
            time.sleep(1)
            options.add_argument(
                "--proxy-server=http://%s:%d" % (PROXY_IP, self.port))

        self.driver = webdriver.Chrome(executable_path=webdriver_path, options=options)
        self.driver.maximize_window()

        return step_flag

    def get_account_count(self):
        sql = 'SELECT * FROM account_count WHERE id=1'
        result = self.conn.op_select_one(sql)
        if result:
            all_count = result['all_count']
            real_time_num = result['real_time_num']
            last_update_time = result['last_update_time']
            if str(last_update_time) < self.current_time:
                recovery_mode = 'UPDATE account SET state=1 WHERE state=0'
                self.conn.op_commit(recovery_mode)
                sql = '''UPDATE account_count SET last_update_time=%s, all_count=
                    (SELECT COUNT(1) FROM account WHERE state=1) WHERE id=1'''
                self.conn.op_commit(sql, self.current_time)
            else:
                sql = 'UPDATE account_count SET real_time_num=(SELECT count(1) FROM account WHERE state=1) WHERE id=1'
                self.conn.op_commit(sql)

        if all_count - real_time_num > 30:
            os.system('shutdown -r -t 1800')
            time.sleep(9999)
            print('Too many account errors today to suspend operations!')

    def get_config(self):
        print('Run configuration:', self.config_id)
        sql = 'SELECT * FROM configuration WHERE id=%s'
        result = self.conn.op_select_one(sql, self.config_id)
        if result:
            self.random_browsing_control = result['random_browsing_control']
            self.browsing_pic_min = result['bro_pic_min']
            self.browsing_pic_max = result['bro_pic_max']
            self.save_home_url_control = result['save_home_page']
            self.save_pic_control = result['save_pic_control']
            self.follow_num = result['follow_num']
            self.pin_self_count = result['pin_self_count']
            self.create_board_num = result['create_board_num']
            self.search_words_count = result['search_words_count']
            self.scroll_num = result['scroll_num']
            self.click_our_pin_control = result['click_our_pin_control']
            self.upload_pic_control = result['upload_pic_control']
            self.upload_pic_min = result['upload_pic_min']
            self.upload_pic_max = result['upload_pic_max']


if __name__ == '__main__':
    go = OPPinterest()
    go.action()