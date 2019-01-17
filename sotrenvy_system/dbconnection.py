import pymysql


def read_one_sql(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchone()
    cur.close()
    return result


def read_all_sql(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)
    results = cur.fetchall()
    cur.close()
    return results


def write_sql(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()


def distribution_data(conn, database, ip):
    now_time = datetime.datetime.today()
    # 清除历史遗留IP数据
    history_time = now_time - datetime.timedelta(hours=1)
    sql = ("update `%s` set ip='#' where state=0 and ip_time<'%s' ") % (
        database, history_time)
    commit_sql(conn, sql)
    # 给当前IP分配数据
    sql = ("update `%s` set ip='%s' , ip_time='%s'  where state=0 and ip='#' ORDER BY RAND() LIMIT 10 ") % (
        database, ip, now_time)
    commit_sql(conn, sql)
    # 取得分配的数量
    sql = ("select * from `%s` where ip='%s' and state=0 ") % (database, ip)
    results = results_sql(conn, sql)
    distribution_num = 0
    for rows in results:
        distribution_num += 1
    return distribution_num
