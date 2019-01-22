import csv
import xlrd
import pymysql


def csv_to_db(conn):
    cursor = conn.cursor()
    csv_file = csv.reader(open("***.csv", 'r'))
    print(csv_file)
    for echo in csv_file:
        print(echo)
        try:
            cursor.execute(
                'INSERT INTO account (email, pw, port, setting_other) values (%s, %s, %s, %s)',
                (echo[0], echo[1], echo[2], 100))
            conn.commit()
        except:
            conn.rollback()
    cursor.close()
    conn.close()


def txt_to_db(conn):
    cursor = conn.cursor()
    with open('***.txt', 'r', encoding='utf-8') as fp:
        file = fp.readlines()
    for echo in file:
        account = echo.strip().split('----')
        print(account)
        try:
            cursor.execute(
                'INSERT INTO account (email, pw, setting_other) values (%s, %s, %s)',
                (account[0].strip(), account[1].strip() + '2018', 100))
            conn.commit()
        except:
            conn.rollback()
    cursor.close()
    conn.close()


def xls_to_db(conn):
    cursor = conn.cursor()
    data = xlrd.open_workbook('pin账号.xls')
    table = data.sheets()[0]
    nrows = table.nrows
    num = 1
    for i in range(nrows):
        if i < 1:
            continue
        row = table.row_values(i)
        mac_adress = row[5].replace(':', '').strip()
        print('email', row[1], 'pwd', row[2], 'email_pwd', row[7],
              'domain', row[4], 'mac_adress', mac_adress, 'vpn', row[6])
        cursor.execute(
            'INSERT INTO account (email, pw, email_pwd, domain, mac_adress, vpn, action_computer, belong) values (%s, %s, %s, %s, %s, %s, %s, %s)',
            (row[1], row[2], row[7], row[4], mac_adress, row[6], 'chensm' + str(num), 'chensm'))
        conn.commit()
        if num == 1:
            input()
        num += 1
    cursor.close()
    conn.close()


def choice_text():
    conn = pymysql.connect(host='localhost', port=3306,
                           user='root', password='1234562',
                           db='new_pin', charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    conn1 = pymysql.connect(host='localhost', port=3306,
                            user='root', password='123456',
                            db='storenvy', charset='utf8mb4',
                            cursorclass=pymysql.cursors.DictCursor)
    conn2 = pymysql.connect(host='localhost', port=3306,
                            user='root', password='123456',
                            db='pin_login_system', charset='utf8mb4',
                            cursorclass=pymysql.cursors.DictCursor)
    choice_num = int(input('''选择读取的文本格式！
1: csv
2: txt
3: xls''' + '\n'))
    if choice_num == 1:
        csv_to_db(conn)
    elif choice_num == 2:
        txt_to_db(conn)
    elif choice_num == 3:
        xls_to_db(conn2)


if __name__ == '__main__':
    choice_text()
