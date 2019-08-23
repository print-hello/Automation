import pymysql


def op_select_one(conn, sql, data=None):
    cursor = conn.cursor()
    cursor.execute(sql, data)
    result = cursor.fetchone()
    cursor.close()
    return result


def op_select_all(conn, sql, data=None):
    cursor = conn.cursor()
    cursor.execute(sql, data)
    results = cursor.fetchall()
    cursor.close()
    return results
    

def op_commit(conn, sql, data=None):
    cursor = conn.cursor()
    cursor.execute(sql, data)
    conn.commit()
    cursor.close()