import json
import pymysql


conn = pymysql.connect(host='localhost',
                       port=3306,
                       user='root',
                       password='123456',
                       db='pinterest',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()
for port in range(26101, 27001):
    cursor.execute('SELECT * from ips where used=0 order by RAND() limit 1')
    result = cursor.fetchone()
    if result:
        ip = result['ip']
        print(ip)
        password = 'tc2n4yclk52h'
        zone = 'zone3'
        cursor.execute(
            'INSERT INTO port_info (port, ip, password, zone) values (%s, %s, %s, %s)', (port, ip, password, zone))
        conn.commit()
        cursor.execute('UPDATE ips set used=1 where ip=%s', ip)
        conn.commit()

cursor.close()
conn.close()
print('End')
