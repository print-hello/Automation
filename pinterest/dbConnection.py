import pymysql

def readOneSQL(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchone()
    cur.close()
    return result

def readAllSQL(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)
    results = cur.fetchall()
    cur.close()
    return results
    
def writeSQL(conn, sql):
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    cur.close()