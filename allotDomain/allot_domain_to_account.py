from DBPools import OPMysql


MYSQLINFO = {
    "host": 'localhost',
    "user": 'root',
    "passwd": '123456',
    "db": 'pinterest',
    "port": 3306,
    "charset": 'utf8mb4'
}


conn = OPMysql(MYSQLINFO)

sql = 'SELECT * FROM domain WHERE state=0'
all_domain = conn.op_select_all(sql)
if all_domain:
    for i in all_domain:
        domain = i['domain']

        sql = 'SELECT * FROM account WHERE state=1 AND home_page!="" AND upload_web="-" AND id>2573 ORDER BY RAND() LIMIT 1'
        r = conn.op_select_one(sql)
        if r:
            email = r['email']
            sql = 'UPDATE account SET upload_web=%s, setting_num=6 WHERE email=%s'
            conn.op_commit(sql, (domain, email))
            print(email, ': Domain name added!')
            sql = 'UPDATE domain SET state=1 WHERE domain=%s'
            conn.op_commit(sql, domain)

else:
    print('No assigned domain name!')

conn.dispose()