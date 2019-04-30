import os
import re
import pymysql


def main():
    conn = pymysql.connect(host='localhost', port=3306,
                           user='pp2', password='123456',
                           db='auto_info', charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    for root, dirs, files in os.walk('0410'): 
        # 当前目录路径
        print(root)  
        # 当前路径下所有子目录 
        # print(dirs) 
        # 当前路径下所有非目录子文件
        # print(files)  
        for echo in dirs:    
            with open('0410\\%s\\%s.cmac-prev' % (echo, echo), 'r', encoding='utf-8') as fp:
                msg = fp.read()
                mac_str = re.search(r'<Adapter slot="0".*>', msg).group()
                mac = mac_str.split(' ')[3].split('=')[1].strip('"')
                print(echo, ':', mac)
                sql = 'INSERT INTO computer_info (virtual, mac_address) values (%s, %s)'
                commit_sql(conn, sql, (echo, mac))


def commit_sql(conn, sql, data=None):
    cursor = conn.cursor()
    cursor.execute(sql, data)
    conn.commit()
    cursor.close()


if __name__ == '__main__':
    main()