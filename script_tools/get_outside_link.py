'''
Author: Vinter Wang
'''
import requests
from bs4 import BeautifulSoup
import pymysql
import datetime
import re
from lxml import etree
import threading
import queue
import time


q = queue.Queue()
CHOICE_STATUS = 0


def get_label():
    thread_name = threading.current_thread().getName()
    domain_list = get_domain()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
    }
    # link_list = ['https://burkeclan.com/index.php?route=forum/forum/view&post_id=23151&forum_id=16']
    while q.qsize() > 0:
        url = q.get()
        print(url)
        # print(page.content)
        # a = re.findall(r'''<a\b[^(>|<)]+\bhref=("|')([^("|')]*).(womentopdressdfsdafdsafdsas.comrg)([^("|')]*)("|')[^(>|<)]*>([\s\S]*?)</a>''', page.text)
        # print(a)
        try:
            page = requests.get(url, headers=headers)
            if page.status_code == 200:
                time.sleep(1)
                content = page.text
                page.close()
                href_list = []
                tree = etree.HTML(content)
                results = tree.xpath('//a')
                for res in results:
                    each = res.get('href')
                    try:
                        each_process = each.split('/')[2].lstrip("www").lstrip('.')
                        href_list.append(each_process)
                    except:
                        pass
                uniq_href_list = list((set(href_list)))
                for uniq_href in uniq_href_list:
                    if uniq_href in domain_list:
                        print(uniq_href)
                        write_db(url, 1)
                        break
                    else:
                        write_db(url)
        except Exception as e:
            pass
    print(thread_name, '######### 数据获取完毕！ ##########')


def conn():
    conn = pymysql.connect(host='localhost', port=3306,
                       user='root', password='123456',
                       db='link2', charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
    return conn


def get_domain():
    conn_flag = conn()
    cursor = conn_flag.cursor()
    cursor.execute('SELECT domain from li_post_domian_reference')
    results = cursor.fetchall()
    domain_list = []
    for res in results:
        domain = res['domain']
        domain_list.append(domain)
    cursor.close()
    conn_flag.close()
    return domain_list


def write_db(url, state=0):
    spider_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn_flag = conn()
    cursor = conn_flag.cursor()
    if CHOICE_STATUS == 0:
        if state == 0:
            cursor.execute(
                'UPDATE li_result set spider_time=%s where link=%s', (spider_time, url))
        elif state == 1:
            cursor.execute(
                'UPDATE li_result set status=1, spider_time=%s where link=%s', (spider_time, url))
    elif CHOICE_STATUS == 1:
        if state == 0:
            cursor.execute(
                'UPDATE li_result set last_status=0, last_spider_time=%s where link=%s', (spider_time, url))
        elif state == 1:
            cursor.execute(
                'UPDATE li_result set last_status=1, last_spider_time=%s where link=%s', (spider_time, url))
    conn_flag.commit()
    cursor.close()
    conn_flag.close()


def get_link():
    conn_flag = conn()
    cursor = conn_flag.cursor()
    if CHOICE_STATUS == 0:
        cursor.execute('SELECT link from li_result where status=0')
    elif CHOICE_STATUS == 1:
        cursor.execute('SELECT link from li_result where status=1')
    results = cursor.fetchall()
    for res in results:
        link = res['link']
        q.put(link)
    cursor.close()
    conn_flag.close()
    print('本次需要抓取的链接数量：', q.qsize())


if __name__ == '__main__':
    get_link()
    for i in range(100):
        threading.Thread(target=get_label).start()
