import os
import re
import pymysql
# import psutil
import shutil
import subprocess
import time
import win32gui
import datetime


TARGET_NUM = 8
PATTERN = re.compile(r'.*DoVirt CrystalMac By Cwood@qq.com')


def main():
    conn = pymysql.connect(host='localhost', port=3306,
                           user='root', password='123456',
                           db='walmartmoneycard', charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    print('删除无用机器...')
    delete_machine(conn)
    with open('file_path.txt', 'r', encoding='utf-8') as fp:
        file_path = fp.read().strip()
        # print(file_path)
    print('更新机器列表...')
    for root, dirs, files in os.walk('%s' % file_path):
        # print(dirs)
        for echo in dirs:
            # print(echo)
            try:
                with open('%s\\%s\\%s.cmac-prev' % (file_path, echo, echo), 'r', encoding='utf-8') as fp:
                    msg = fp.read()
                    mac_str = re.search(r'<Adapter slot="0".*>', msg).group()
                    mac = mac_str.split(' ')[3].split('=')[1].strip('"')
                    print(echo, ':', mac)
                    sql = 'INSERT INTO computer_list (file_path, computer_name, mac_address) values (%s, %s, %s)'
                    commit_sql(conn, sql, (file_path, echo, mac))
            except:
                pass
        break
    while True:
        titles = set()

        def foo(hwnd, mouse):
            if win32gui.IsWindow(hwnd) and win32gui.IsWindowEnabled(hwnd) and win32gui.IsWindowVisible(hwnd):
                titles.add(win32gui.GetWindowText(hwnd))
        win32gui.EnumWindows(foo, 0)
        lt = [t for t in titles if t]
        lt.sort()
        virtual_count = 0
        for t in lt:
            result = PATTERN.findall(t)
            if result:
                virtual_count += 1
        # pids = psutil.pids()
        # process_count = 0
        # for pid in pids:
        #     p = psutil.Process(pid)
        #     if p.name() == 'CrystalMac.exe':
        #         process_count += 1
        #         # print('pid-%s, pname-%s' % (pid, p.name()))
        # virtual_count = process_count // 3
        open_count = TARGET_NUM - virtual_count
        if open_count > 0:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sql = 'SELECT * from computer_list where state=0 order by id limit %s'
            all_open_info = fetch_all_sql(conn, sql, open_count)
            if all_open_info:
                print(current_time, '目标数量:', TARGET_NUM, '当前运行数量:',
                      virtual_count, '即将开启数量:', open_count)
                for open_info in all_open_info:
                    file_path = open_info['file_path']
                    computer_name = open_info['computer_name']
                    mac_address = open_info['mac_address']
                    p = subprocess.Popen('C:\\Program Files\\DoVirt\\CrystalMac\\CrystalMac.exe %s\\%s\\%s.cmac' % (
                        file_path, computer_name, computer_name), shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    print('Satrt %s!' % computer_name)
                    sql = 'UPDATE computer_list set state=1 where computer_name=%s'
                    commit_sql(conn, sql, computer_name)
                    time.sleep(1)
                    sql = 'UPDATE email_info set open_machine_times=open_machine_times+1 where register_pp_mac=%s'
                    commit_sql(conn, sql, mac_address)
                    time.sleep(9)
            else:
                print('暂无未使用机器!重新运行未完成注册机器!')
                sql = 'SELECT * from email_info where open_machine_times<3 and created_paypal_account<3 and emailIsUsed=1 and register_pp_mac!="-" order by id desc limit %s'
                try_again_account = fetch_all_sql(conn, sql, open_count)
                if try_again_account:
                    print(current_time, '目标数量:', TARGET_NUM, '当前运行数量:',
                          virtual_count, '即将开启数量:', open_count)
                    for echo in try_again_account:
                        register_pp_mac = echo['register_pp_mac']
                        sql = 'SELECT * from computer_list where mac_address=%s'
                        machine_info = fetch_one_sql(
                            conn, sql, register_pp_mac)
                        if machine_info:
                            file_path = machine_info['file_path']
                            computer_name = machine_info['computer_name']
                            p = subprocess.Popen('C:\\Program Files\\DoVirt\\CrystalMac\\CrystalMac.exe %s\\%s\\%s.cmac' % (
                                file_path, computer_name, computer_name), shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                            print('Satrt %s!' % computer_name)
                            sql = 'UPDATE email_info set open_machine_times=open_machine_times+1 where register_pp_mac=%s'
                            commit_sql(conn, sql, register_pp_mac)
                            time.sleep(10)
                else:
                    print('No machine!')
                    break
        time.sleep(180)


def delete_machine(conn):
    sql = 'SELECT id, register_pp_mac from email_info where created_paypal_account=3 and emailIsUsed=1 and pc_is_deleted=0'
    all_done_computer = fetch_all_sql(conn, sql)
    if all_done_computer:
        for done_computer in all_done_computer:
            id_num = done_computer['id']
            mac_address = done_computer['register_pp_mac']
            sql = 'SELECT * from computer_list where mac_address=%s and state=1'
            computer_info = fetch_one_sql(conn, sql, mac_address)
            if computer_info:
                file_path = computer_info['file_path']
                file_name = computer_info['computer_name']
                path = '%s\\%s' % (file_path, file_name)
                shutil.rmtree(path)
                print('%s Deleted!' % file_name)
                sql = 'UPDATE email_info set pc_is_deleted=1 where id=%s'
                commit_sql(conn, sql, id_num)
    sql1 = 'SELECT * from computer_list where state=1 and mac_address not in (SELECT register_pp_mac from email_info)'
    all_done_computer1 = fetch_all_sql(conn, sql1)
    if all_done_computer1:
        for done_computer1 in all_done_computer1:
            id_num1 = done_computer1['id']
            mac_address1 = done_computer1['mac_address']
            file_path1 = done_computer1['file_path']
            file_name1 = done_computer1['computer_name']
            path1 = '%s\\%s' % (file_path1, file_name1)
            shutil.rmtree(path1)
            print('%s Deleted!' % file_name1)
            sql = 'DELETE from computer_list where id=%s'
            commit_sql(conn, sql, id_num1)
    sql2 = 'SELECT * from email_info where emailIsUsed=9 and register_pp_mac!="-" and pc_is_deleted=0'
    all_done_computer2 = fetch_all_sql(conn, sql2)
    if all_done_computer2:
        for done_computer2 in all_done_computer2:
            id_num2 = done_computer2['id']
            mac_address2 = done_computer2['register_pp_mac']
            sql = 'SELECT * from computer_list where mac_address=%s and state=1'
            computer_info2 = fetch_one_sql(conn, sql, mac_address2)
            if computer_info2:
                file_path2 = computer_info2['file_path']
                file_name2 = computer_info2['computer_name']
                path2 = '%s\\%s' % (file_path2, file_name2)
                shutil.rmtree(path2)
                print('%s Deleted!' % file_name2)
                sql = 'UPDATE email_info set pc_is_deleted=1 where id=%s'
                commit_sql(conn, sql, id_num2)
    sql3 = 'SELECT * from email_info where open_machine_times=3 and created_paypal_account<3 and register_pp_mac!="-" and pc_is_deleted=0'
    all_done_computer3 = fetch_all_sql(conn, sql3)
    if all_done_computer3:
        for done_computer3 in all_done_computer3:
            id_num3 = done_computer3['id']
            mac_address3 = done_computer3['register_pp_mac']
            sql = 'SELECT * from computer_list where mac_address=%s and state=1'
            computer_info3 = fetch_one_sql(conn, sql, mac_address3)
            if computer_info3:
                file_path3 = computer_info3['file_path']
                file_name3 = computer_info3['computer_name']
                path3 = '%s\\%s' % (file_path3, file_name3)
                try:
                    shutil.rmtree(path3)
                    print('%s Deleted!' % file_name3)
                    sql = 'UPDATE email_info set pc_is_deleted=1 where id=%s'
                    commit_sql(conn, sql, id_num3)
                except:
                    pass


def commit_sql(conn, sql, data=None):
    cursor = conn.cursor()
    cursor.execute(sql, data)
    conn.commit()
    cursor.close()


def fetch_all_sql(conn, sql, data=None):
    cursor = conn.cursor()
    cursor.execute(sql, data)
    results = cursor.fetchall()
    cursor.close()
    return results


def fetch_one_sql(conn, sql, data=None):
    cursor = conn.cursor()
    cursor.execute(sql, data)
    result = cursor.fetchone()
    cursor.close()
    return result


if __name__ == '__main__':
    main()
