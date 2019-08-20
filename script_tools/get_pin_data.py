import os
import sys
import json
import time
import queue
import pymysql
import datetime
import threading
from requests import Session
from DBUtils.PooledDB import PooledDB


q = queue.Queue()


POOL = PooledDB(creator=pymysql,
                mincached=100,
                host='localhost',
                user='root',
                passwd='123456',
                db='pin_data',
                port=3306,
                charset="utf8")


POOL1 = PooledDB(creator=pymysql,
                 mincached=1,
                 maxcached=3,
                 host='localhost',
                 user='root',
                 passwd='123456',
                 db='pinterest',
                 port=3306,
                 charset="utf8")


def get_list():
    conn = POOL1.connection()
    sql = "SELECT * FROM account WHERE state<9"
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(sql)
    results = cursor.fetchall()
    for param in results:
        if param['home_page']:
            q.put((param['home_page']).split('/')[-2].strip())
    conn.close()
    print('总数量：', q.qsize())


def my_get(param, headers, sess):
    millis = str(round(time.time() * 1000))
    url = 'https://www.pinterest.com/resource/UserPinsResource/get/?source_url=%2F' + param + '%2Fpins%2F&data=%7B%22options%22%3A%7B%22is_own_profile_pins%22%3Afalse%2C%22username%22%3A%22' + \
        param + '%22%2C%22field_set_key%22%3A%22grid_item%22%2C%22pin_filter%22%3Anull%7D%2C%22context%22%3A%7B%7D%7D&_=' + millis
    html = sess.get(url, headers=headers)
    return html.text


def main():
    run_flag = 1
    sess = Session()
    while q.qsize() > 0:
        thread_name = threading.current_thread().getName()
        millis = str(round(time.time() * 1000))
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
            'Referer': 'https://www.pinterest.com/',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-APP-VERSION': 'd21ec39',
            'X-Pinterest-AppState': 'active',
            'X-Requested-With': 'XMLHttpRequest'
        }
        param = q.get()
        if param:
            param = param.strip()
            try:
                html = my_get(param, headers, sess)
            except:
                q.put(param)
                run_flag = 0
            if run_flag == 1:
                all_url_json = json.loads(html)
                print(thread_name, '开始获取数据！')
                bookmarks = all_url_json['resource']['options']['bookmarks'][0]
                datalist = all_url_json['resource_response']['data']
                if datalist:
                    parse_data(param, datalist)
                continue_spider(sess, headers, millis, bookmarks, param, 1)
    print(thread_name, '######### 数据获取完毕！ ##########')


def continue_spider(sess, headers, millis, bookmarks, param, count):
    run_flag = 1
    url = 'https://www.pinterest.com/resource/UserPinsResource/get/?source_url=%2F' + param + '%2Fpins%2F&data=%7B%22options%22%3A%7B%22bookmarks%22%3A%5B%22' + bookmarks + '%22%5D%2C%22is_own_profile_pins%22%3Afalse%2C%22username%22%3A%22' + param + '%22%2C%22field_set_key%22%3A%22grid_item%22%2C%22pin_filter%22%3Anull%7D%2C%22context%22%3A%7B%7D%7D&_=' + str(
        millis)
    try:
        html = my_get(param, headers, sess)
    except:
        q.put(param)
        run_flag = 0
    if run_flag == 1:
        all_url_json = json.loads(html)
        bookmarks = all_url_json['resource']['options']['bookmarks'][0]
        datalist = all_url_json['resource_response']['data']
        if count < 10 and datalist != None:
            if len(datalist) > 0:
                print('第' + str(count) + '次循环取数据')
                parse_data(param, datalist)
                count += 1
                continue_spider(sess, headers, millis, bookmarks, param, count)


def parse_data(param, datalist):
    for datastr in datalist:
        user_home_page = 'https://www.pinterest.com/' + param
        pic_id = datastr['id']
        link = datastr['link']
        if link:
            domain = link.split('/')[2].lstrip('www.')
        else:
            domain = ''
            link = ''
        url = 'https://www.pinterest.com/pin/' + \
            str(pic_id) + '/'
        created_at_us_time = datastr['created_at'].replace(
            ", ", " ").rstrip('+0000').strip()[4:]
        time_format = datetime.datetime.strptime(
            created_at_us_time, '%d %b %Y %H:%M:%S')
        created_at = time_format.strftime('%Y-%m-%d %H:%M:%S')
        repin_count = datastr['repin_count']
        try:
            imgsaves = datastr['aggregated_pin_data']['aggregated_stats']['saves']
        except Exception as e:
            imgsaves = '0'
        conn = POOL.connection()
        cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)
        try:
            cursor.execute("""INSERT INTO pin_daily_data (user, user_home_page, created_at, repin_count, imgsaves, url, link, domain) values(
                %s, %s, %s, %s, %s, %s, %s, %s)""", (param, user_home_page, created_at, repin_count, imgsaves, url, link, domain))
        except:
            cursor.execute("""UPDATE pin_daily_data set user_home_page=%s, created_at=%s, repin_count=%s, imgsaves=%s, 
                link=%s, domain=%s where user=%s and url=%s""", (user_home_page, created_at, repin_count, imgsaves, link, domain, param, url))
        conn.commit()
        conn.close()


if __name__ == '__main__':
    get_list()
    for i in range(100):
        threading.Thread(target=main).start()
