import xlrd
from DBPools import OPMysql


DB_NAME = 'data_content_587'

def get_domain():
    domain_list = []
    data = xlrd.open_workbook('domain.xlsx')
    table = data.sheets()[0]
    nrows = table.nrows
    num = 1
    for i in range(nrows):
        row = table.row_values(i)
        domain = row[0].strip()
        domain_list.append(domain)

    return domain_list


def main():
    MYSQLINFO = {
        "host": 'localhost',
        "user": 'root',
        "passwd": '123456',
        "db": 'pin_link_data',
        "port": 3306,
        "charset": 'utf8mb4'
    }
    domain_list = get_domain()
    conn = OPMysql(MYSQLINFO)
    sql = 'SELECT count(1) as allcount FROM %s' % DB_NAME
    all_data_count = conn.op_select_one(sql)['allcount']
    print('发布数据总量:', all_data_count)

    domain_count = len(domain_list)
    print('域名数量:', domain_count)

    domain_info_num = all_data_count // domain_count
    print('每个域名分配数据数量:', domain_info_num)

    for t in range(domain_count):
        if t > 0:
            start_num = t * domain_info_num + 2
        else:
            start_num = t * domain_info_num + 1

        end_num = (t + 1) * domain_info_num + 1
        print(start_num, '--->', end_num)

        sql = 'UPDATE %s SET domain="%s", savebuttonlink=REPLACE(savebuttonlink, "yaohaowang.top", "%s") WHERE id BETWEEN %d AND %d' % (DB_NAME, 'https://' + domain_list[t], domain_list[t], start_num, end_num)
        conn.op_commit(sql)

    conn.dispose()


if __name__ == '__main__':
    main()