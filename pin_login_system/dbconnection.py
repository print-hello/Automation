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