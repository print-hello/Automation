import pymysql
import random
import xlrd
import random


def main():
    conn = pymysql.connect(host='localhost', port=3306,
                           user='root', password='123456',
                           db='walmartmoneycard', charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    cursor = conn.cursor()
    data = xlrd.open_workbook('1000ssn02.xlsx')
    table = data.sheets()[0]
    nrows = table.nrows
    for i in range(nrows):
        # if i < 1:
        #     continue
        row = table.row_values(i)
        try:
            firstname = row[0].split(' ')[0].strip()
            lastname = row[0].split(' ')[-1].strip()
            socialnumber = row[5].replace('-', '').strip()
            print(firstname, lastname, socialnumber)
            birthdate = row[7]
            birthdate_1 = birthdate.split('/')[0].zfill(2)
            birthdate_2 = birthdate.split('/')[1].zfill(2)
            birthdate_3 = birthdate.split('/')[2]
            birthdate = birthdate_1 + birthdate_2 + birthdate_3
            address = row[1]
            city = row[2]
            state = row[3]
            zip_num = str(row[4]).zfill(5)
            mobilenumber = phone_num(conn, city, state)
            pinnumber = pin_number()
            sql = 'INSERT INTO register_info5 (firstname, lastname, address, city, state, zip, socialnumber, birthdate, mobilenumber, pinnumber) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
            commit_sql(conn, sql, (firstname, lastname, address, city, state,
                                   zip_num, socialnumber, birthdate, mobilenumber, pinnumber))
        except Exception as e:
            pass


def fetch_one_sql(conn, sql, data=None):
    cursor = conn.cursor()
    cursor.execute(sql, data)
    result = cursor.fetchone()
    cursor.close()
    return result


def fetch_all_sql(conn, sql, data=None):
    cursor = conn.cursor()
    cursor.execute(sql, data)
    results = cursor.fetchall()
    cursor.close()
    return results


def commit_sql(conn, sql, data=None):
    cursor = conn.cursor()
    cursor.execute(sql, data)
    conn.commit()
    cursor.close()


def phone_num(conn, city, state):
    random_str = ''
    sql = 'SELECT * from area_code_table where city=%s'
    res = fetch_one_sql(conn, sql, city)
    if res:
        area_code = res['area_code']
        random_str += area_code
    else:
        sql = 'SELECT * from area_code_table where abb_state=%s order by RAND() limit 1'
        res = fetch_one_sql(conn, sql, state)
        if res:
            area_code = res['area_code']
            random_str += area_code
        else:
            random_str += '682'
    for i in range(7):
        ch = str((random.randrange(0, 9)))
        random_str += ch
    # print(random_str)
    return random_str


def pin_number():
    random_str = ''
    ch = str((random.randrange(1, 9)))
    random_str += ch
    for i in range(3):
        ch = str((random.randrange(0, 9)))
        random_str += ch
    # print(random_str)
    return random_str


if __name__ == '__main__':
    main()
