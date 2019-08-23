import pymysql
from dbconnection import op_commit


conn = pymysql.connect(host='localhost',
                       port=3306,
                       user='root',
                       password='123456',
                       db='pinterest',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
ip_list = []
with open('ips-static.txt', 'r', encoding='utf-8') as fp:
    while True:
        line = fp.readline()
        ip = line.split('-')[-1].split(':')[0]
        print(ip)
        if ip:
            ip_a = ip.split('.')[0]
            ip_b = ip.split('.')[1]
            ip_c = ip.split('.')[2]
            try:
                sql = 'INSERT INTO ips (ip, a_segment, b_segment, c_segment) VALUES (%s, %s, %s, %s)'
                op_commit(conn, sql, (ip, ip_a, ip_b, ip_c))
            except:
                pass
        else:
            break

conn.close()
print('End')