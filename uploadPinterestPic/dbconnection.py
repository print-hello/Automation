import pymysql


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