'''
Author: Vinter Wang
Email: printhello@163.com
'''
import os
import time
import socket
import datetime
from selenium import webdriver

from login_util import login
from login_util import get_coo
from DBPools import OPMysql
from util import write_txt_time

from opration_util import save_home_url
from opration_util import handle_pop_up
from opration_util import upload_pic
from opration_util import random_browsing
from opration_util import create_board
from opration_util import click_our_pin
from opration_util import follow


MYSQLINFO1 = {
    "host": 'localhost',
    "user": 'root',
    "passwd": '123456',
    "db": 'pinterest',
    "port": 3306,
    "charset": 'utf8mb4'
}


MYSQLINFO2 = {
    "host": 'localhost',
    "user": 'root',
    "passwd": '123456',
    "db": 'pin_upload',
    "port": 3306,
    "charset": 'utf8mb4'
}


PROXY_IP = 'localhost'


class OPPinterest():
    def __init__(self):
        super(OPPinterest, self).__init__()
        self.conn1 = OPMysql(MYSQLINFO1)
        self.conn2 = OPMysql(MYSQLINFO2)
        # logging.config.fileConfig('logging.conf')
        # self.logs = logging.getLogger()
        # email = logging.handlers.SMTPHandler(("smtp.163.com", 25), 'sendlogging@163.com',
        #                                      ['printhello@163.com'],
        #                                      "Logging from my app",
        #                                      credentials=(
        #                                          'sendlogging@163.com', '******'),
        #                                      )
        # self.logs.addHandler(email)
        # self.driver = ''
        self.step_flag = 1
        self.hostname = socket.gethostname()
        self.current_time = (datetime.datetime.utcnow() + datetime.timedelta(hours=8)).strftime("%Y-%m-%d")
        self.login_url = 'https://www.pinterest.com/login/?referrer=home_page'
        self.account_id = 0
        self.email = ''
        self.pwd = ''
        self.port = 0
        self.cookie = ''
        self.agent = ''
        self.success_num = 0
        self.config_id = 0
        # self.account_group = 0
        # self.save_pic_from_homepage_control = 0
        self.click_our_pin_control = 0

        # Try to locate the home element. If there is off, you don't need to do all kinds of pop-ups
        # self.login_state_flag = ''
        # Steps and params to control
        # self.upload_pic_control = 0
        self.upload_pic_min = 0
        self.upload_pic_max = 0
        self.random_browsing_control = 0
        self.browsing_pic_min = 0
        self.browsing_pic_max = 0
        self.save_home_url_control = 0
        self.create_board_num = 0
        self.save_pic_control = 0
        # self.follow_num = 0
        self.pin_self_count = 0
        self.created_boards = 0
        self.search_words_count = 0
        self.scroll_num = 0
        # self.upload_done = 0
        # self.pinterest_acotion()

    def action(self):
        while True:
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
                self.re_driver()
                login_state = login(
                    self.driver, self.login_url, self.account_id, self.email, self.pwd, self.cookie)
                time.sleep(1)
                if login_state == 1 or login_state == 11:
                    sql = "UPDATE account SET login_times=login_times+1 WHERE id=%s"
                    self.conn1.op_commit(sql, self.account_id)
                    if login_state == 11:
                        cookie = get_coo(self.driver)
                        sql = 'UPDATE account SET cookie=%s WHERE id=%s'
                        self.conn1.op_commit(sql, (cookie, self.account_id))
                    handle_pop_up(self.driver)
                else:
                    sql = 'UPDATE account SET state=%s, login_times=0, action_computer="-" WHERE id=%s'
                    self.conn1.op_commit(sql, (login_state, self.account_id))
                    self.step_flag = 0
                    print('Account log-in failure, will exit the browser!')
                    try:
                        self.driver.quit()
                    except:
                        pass
                    time.sleep(5)
                    continue
                if self.step_flag == 1:
                    
                    if self.save_home_url_control == 1:
                        print('Save home page!')
                        save_home_url(self.driver, self.conn1, self.account_id)

                    if self.create_board_num > 0 and self.created_boards < self.create_board_num:
                        print('Start create board')
                        create_board(self.driver, self.conn1, self.account_id, self.create_board_num)

                    if self.random_browsing_control == 1:
                        random_browsing(
                            self.driver, self.conn1, self.account_id, self.step_flag, self.save_pic_control, self.browsing_pic_min, self.browsing_pic_max)
                    
                    if self.follow_num > 0:
                        follow(self.driver, self.step_flag)

                    if self.click_our_pin_control == 1:
                        click_our_pin(self.driver, self.conn1, self.step_flag, self.current_time, self.scroll_num, self.pin_self_count, self.search_words_count, self.account_id)

                    if self.upload_pic_control == 1 and self.upload_done == 2:
                        upload_pic()

                    print('End of account processing...')
                    self.driver.quit()
                    sql = 'UPDATE account SET state=1, login_times=0, action_time=%s, action_computer="-" WHERE id=%s'
                    self.conn1.op_commit(sql, (self.current_time, self.account_id))
                    write_txt_time()
                    time.sleep(10)
            else:
                print('Not data! The system will reboot in 30 minutes...')
                write_txt_time()
                os.system('shutdown -r -t 1800')
                time.sleep(9999)

    # Access to the account
    def get_account(self):
        if self.hostname == 'vinter-wang':
            sql = 'SELECT * FROM account WHERE id=3085'
            result = self.conn1.op_select_one(sql)
        else:
            sql = "SELECT * FROM account WHERE port>100 AND upload_computer='-' AND action_computer=%s AND action_time<%s AND state=1 AND upload_done<10 AND login_times<4 order by action_time asc limit 1"
            result = self.conn1.op_select_one(sql, (self.hostname, self.current_time))
        if result:
            self.account_id = result["id"]
            self.email = result["email"]
            self.pwd = result["pw"]
            self.port = result['port']
            self.cookie = result['cookie']
            self.created_boards = result['created_boards']
            self.config_id = result['setting_other']
            self.account_group = result['account_group']
            self.agent = result['agent']
            self.upload_done = result['upload_done']
            if not self.agent:
                sql = 'SELECT * FROM user_agent WHERE terminal="computer" ORDER BY RAND() LIMIT 1'
                agent_in_sql = self.conn1.op_select_one(sql)
                if agent_in_sql:
                    self.agent = agent_in_sql['user_agent']
                    agent_id = agent_in_sql['Id']
                    sql = 'UPDATE account SET agent=%s WHERE id=%s'
                    self.conn1.op_commit(sql, (self.agent, self.account_id))
            print("Start account processing..." + '\n' + "ID:",
                  self.account_id, "Email:", self.email)
            write_txt_time()
        else:
            sql = "SELECT * FROM account WHERE port>100 AND upload_computer='-' AND action_computer='-' AND action_time<%s AND state=1 AND upload_done<10 AND login_times<4 ORDER BY action_time asc limit 1"
            result = self.conn1.op_select_one(sql, self.current_time)
            if result:
                self.account_id = result["id"]
                self.email = result["email"]
                self.pwd = result["pw"]
                self.port = result['port']
                self.cookie = result['cookie']
                self.created_boards = result['created_boards']
                self.config_id = result['setting_other']
                self.account_group = result['account_group']
                self.agent = result['agent']
                self.upload_done = result['upload_done']
                if not self.agent:
                    sql = 'SELECT * FROM user_agent WHERE terminal="computer" ORDER BY RAND() LIMIT 1'
                    agent_in_sql = self.conn1.op_select_one(sql)
                    if agent_in_sql:
                        self.agent = agent_in_sql['user_agent']
                        agent_id = agent_in_sql['Id']
                        sql = 'UPDATE account SET agent=%s WHERE id=%s'
                        self.conn1.op_commit(sql, (self.agent, self.account_id))
                        sql = 'UPDATE user_agent SET read_time=read_time+1 WHERE id=%s'
                        self.conn2.op_commit(sql, agent_id)
                print("Start account processing..." + '\n' + "ID:",
                      self.account_id, "Email:", self.email)
                sql = "UPDATE account SET action_computer=%s WHERE id=%s"
                self.conn1.op_commit(sql, (self.hostname, self.account_id))
                write_txt_time()

    def re_driver(self):
        webdriver_path = os.path.abspath('.') + '\\boot\\chromedriver.exe'
        options = webdriver.ChromeOptions()
        options.add_argument('disable-infobars')
        options.add_argument('user-agent="%s"' % self.agent)
        prefs = {
            'profile.default_content_setting_values':
            {'notifications': 2
             }
        }
        options.add_experimental_option('prefs', prefs)
        # options.add_argument(
        #     "--proxy-server=http://%s:%d" % (PROXY_IP, self.port))
        self.driver = webdriver.Chrome(executable_path=webdriver_path, options=options)
        self.driver.maximize_window()

    def get_account_count(self):
        sql = 'SELECT * FROM account_count WHERE id=1'
        result = self.conn1.op_select_one(sql)
        if result:
            all_count = result['all_count']
            real_time_num = result['real_time_num']
            last_update_time = result['last_update_time']
            if str(last_update_time) < self.current_time:
                change_domain_state = 'UPDATE domain SET state=0 WHERE state=1'
                self.conn2.op_commit(change_domain_state)
                clear_domain_account = 'UPDATE domain SET account_id=0'
                self.conn2.op_commit(clear_domain_account)
                recovery_mode = 'UPDATE account SET state=1 WHERE state=4'
                self.conn1.op_commit(recovery_mode)
                # change_group = 'UPDATE follow_url set account_group=account_group+1 WHERE for_config=10'
                # commit_sql(self.conn2, change_group)
                # all_group = 'SELECT count(-1) from follow_url WHERE for_config=10'
                # all_group_count = fetch_one_sql(
                #     self.conn2, all_group)['count(-1)']
                # debug_group = 'UPDATE follow_url set account_group=1 WHERE account_group>%s'
                # commit_sql(self.conn2, debug_group, all_group_count)
                sql = '''UPDATE account_count SET last_update_time=%s, all_count=
                    (SELECT COUNT(1) FROM account WHERE state=1 AND port>100) WHERE id=1'''
                self.conn1.op_commit(sql, self.current_time)
            else:
                sql = 'UPDATE account_count SET real_time_num=(SELECT count(1) FROM account WHERE state=1 AND port>100) WHERE id=1'
                self.conn1.op_commit(sql)
        if all_count - real_time_num > 10:
            os.system('shutdown -r -t 1800')
            time.sleep(9999)
            print('Too many account errors today to suspend operations!')

    def get_config(self):
        print('Run configuration:', self.config_id)
        sql = 'SELECT * FROM configuration WHERE priority=%s'
        result = self.conn1.op_select_one(sql, self.config_id)
        # choice_config_sorted = sorted(results, key=lambda priority: priority['priority'])
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
            # self.save_pic_from_homepage_control = result['save_pic_from_homepage_control']
            self.click_our_pin_control = result['click_our_pin_control']
            self.upload_pic_control = result['upload_pic_control']
            self.upload_pic_min = result['upload_pic_min']
            self.upload_pic_max = result['upload_pic_max']


if __name__ == '__main__':
    go = OPPinterest()
    go.action()