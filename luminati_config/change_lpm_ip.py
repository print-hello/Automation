import json
import pymysql
import datetime

from dbconnection import op_commit
from dbconnection import op_select_one
from dbconnection import op_select_all


json_data = {
    "_defaults": {
        "customer": "",
        "password": "",
        "token": "",
        "whitelist_ips": [
            "0.0.0.0/0"
        ],
        "www_whitelist_ips": [
            "173.208.185.10",
            "183.160.234.83"
        ]
    },
    "proxies": ""
}


def change_ip():
    conn = pymysql.connect(host='localhost',
                           port=3306,
                           user='root',
                           password='123456',
                           db='pinterest',
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    port_list = []
    sql = 'SELECT * FROM port_info WHERE state=2'
    results = op_select_all(conn, sql)
    if results:
        for res in results:
            port_in_sql = res['port']
            port_list.append(port_in_sql)
        print('更新 IP 库后已无法使用的端口', port_list)

    sql = 'SELECT * FROM account WHERE state=2 AND proxy_err_times>=3'
    server_results = op_select_all(conn, sql)
    if server_results:
        for server_res in server_results:
            server_port_in_sql = server_res['port']
            port_list.append(server_port_in_sql)

    if port_list:
        print('所有待更换 IP', port_list)
        for port in port_list:
            sql = 'SELECT * FROM port_info WHERE port=%s'
            port_info = op_select_one(conn, sql, port)
            if port_info:
                old_ip = port_info['ip']
                old_ip_a = old_ip.split('.')[0]
                old_ip_b = old_ip.split('.')[1]
                old_ip_c = old_ip.split('.')[2]

                sql = 'SELECT * FROM ips WHERE used=0 AND a_segment=%s AND b_segment=%s AND c_segment=%s ORDER BY RAND() LIMIT 1'
                get_new_ip = op_select_one(
                    conn, sql, (old_ip_a, old_ip_b, old_ip_c))
                if get_new_ip:
                    update_db(conn, get_new_ip, port, old_ip)

                else:
                    print('已无更多对应 C 段 IP, 获取同 B 段 IP！')
                    sql = 'SELECT * FROM ips WHERE used=0 AND a_segment=%s AND b_segment=%s ORDER BY RAND() LIMIT 1'
                    get_new_ip = op_select_one(conn, sql, (old_ip_a, old_ip_b))
                    if get_new_ip:
                        update_db(conn, get_new_ip, port, old_ip)

                    else:
                        print('已无更多对应 B 段 IP, 获取同 A 段 IP！')
                        sql = 'SELECT * FROM ips WHERE used=0 AND a_segment=%s ORDER BY RAND() LIMIT 1'
                        get_new_ip = op_select_one(conn, sql, old_ip_a)
                        if get_new_ip:
                            update_db(conn, get_new_ip, port, old_ip)

                        else:
                            print('已无更多对应 A 段 IP, 获取随机 IP！')
                            sql = 'SELECT * FROM ips WHERE used=0 ORDER BY RAND() LIMIT 1'
                            get_new_ip = op_select_one(conn, sql)
                            if get_new_ip:
                                update_db(conn, get_new_ip, port, old_ip)

        get_lpm_json(conn)

    else:
        print('暂无 IP 异常端口！')
    conn.close()


def update_db(conn, get_new_ip, port, old_ip):
    new_ip = get_new_ip['ip']
    sql = 'UPDATE port_info set ip=%s, state=1 where port=%s'
    op_commit(conn, sql, (new_ip, port))

    print('Old IP:', old_ip, '--->', 'New IP:', new_ip)
    sql = 'UPDATE ips SET used=1 WHERE ip=%s'
    op_commit(conn, sql, new_ip)

    try:
        sql = 'UPDATE ips SET used=2 WHERE ip=%s'
        op_commit(conn, sql, old_ip)
    except:
        pass

    try:
        sql = 'UPDATE account SET state=1 WHERE state=2 AND port=%s'
        op_commit(conn, sql, port)
    except:
        pass


def get_lpm_json(conn):
    sql = 'SELECT * FROM machine'
    proxy_account = op_select_all(conn, sql)
    if proxy_account:
        for i in proxy_account:
            proxy_ip = i['proxy_ip']
            customer = i['customer']
            customer_pwd = i['customer_pwd']
            zone = i['zone']

            sql = 'SELECT * FROM port_info WHERE zone=%s'
            config_in_sql = op_select_all(conn, sql, zone)
            
            proxies = []
            if config_in_sql:
                for conf in config_in_sql:
                    sql_port = conf['port']
                    sql_ip = conf['ip']
                    conf_proxies = {
                        "keep_alive": "true",
                        "max_requests": 0,
                        "secure_proxy": "true",
                        "zone": zone,
                        "password": customer_pwd,
                        "port": sql_port,
                        "session": "true",
                        "ip": sql_ip,
                        "pool_size": 1}
                    proxies.append(conf_proxies)

                with open('luminati.json(%s)' % proxy_ip, 'w', encoding='utf-8') as fp:
                    json_data['_defaults']["customer"] = customer
                    json_data['_defaults']["password"] = customer_pwd
                    json_data["proxies"] = proxies
                    json.dump(json_data, fp, indent=4)


if __name__ == '__main__':
    change_ip()
