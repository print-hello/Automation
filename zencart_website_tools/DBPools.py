import pymysql
from DBUtils.PooledDB import PooledDB


class OPMysql:
    __pool = None

    def __init__(self, mysqlInfo):

        self.conn = OPMysql.getmysqlconn(mysqlInfo)
        self.cur = self.conn.cursor(cursor=pymysql.cursors.DictCursor)

    @staticmethod
    def getmysqlconn(mysqlInfo):
        if OPMysql.__pool is None:
            __pool = PooledDB(creator=pymysql,
                            mincached=1,
                            maxcached=3,
                            host=mysqlInfo['host'],
                            user=mysqlInfo['user'],
                            passwd=mysqlInfo['passwd'],
                            db=mysqlInfo['db'],
                            port=mysqlInfo['port'],
                            charset=mysqlInfo['charset'])
        return __pool.connection()

    def op_commit(self, sql, data=None):
        insert_num = self.cur.execute(sql, data)
        self.conn.commit()
        return insert_num

    def op_select_all(self, sql, data=None):
        self.cur.execute(sql, data)
        select_res = self.cur.fetchall()
        return select_res

    def op_select_one(self, sql, data=None):
        self.cur.execute(sql, data)
        select_res = self.cur.fetchone()
        return select_res

    def dispose(self):
        self.cur.close()
        self.conn.close()
