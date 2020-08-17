import os
import re
import json
import random
import pymysql
import configparser

from urllib.parse import quote

from dbconnection import op_select_one
from dbconnection import op_select_all
from dbconnection import op_commit


def main():
    page_num_start = int(input(
        'Enter the starting image folder number for the data to be generated:'))
    page_num_end = int(input(
        'Enter the end image folder number for the data to be generated:'))
    domain_list = []
    with open('./domain.txt', 'r', encoding='utf-8') as fp:
        domains = fp.readlines()
        for d in domains:
            domain_list.append(d.strip())
    domain_list_length = len(domain_list)

    conf = 'config.ini'
    conf_conn = configparser.ConfigParser()
    conf_conn.read(conf, encoding='utf-8')
    pro_info_items = conf_conn.items('mysql_pro_info')
    pro_info_items = dict(pro_info_items)
    wdweb_items = conf_conn.items('mysql_wdweb')
    wdweb_items = dict(wdweb_items)
    pro_info_conn = pymysql.connect(host='localhost',
                                    port=3306,
                                    db=pro_info_items['db'],
                                    user=pro_info_items['user'],
                                    password=pro_info_items['password'],
                                    charset='utf8mb4',
                                    cursorclass=pymysql.cursors.DictCursor)

    wdweb_conn = pymysql.connect(host='localhost',
                                 port=3306,
                                 db=wdweb_items['db'],
                                 user=wdweb_items['user'],
                                 password=wdweb_items['password'],
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    count = 0
    for page_num in range(page_num_start, page_num_end + 1):

        domain = domain_list[count]
        sql = 'SELECT products_model FROM products WHERE products_status=1'
        results = op_select_all(wdweb_conn, sql)
        if results:
            for res in results:

                products_model = res['products_model']
                sql = 'SELECT pro_model, category, pro_desc_simple, main_tag, other_tag FROM products WHERE pro_model=%s'
                result = op_select_one(pro_info_conn, sql, products_model)
                if result:

                    pro_model = result['pro_model']
                    category = result['category']
                    pro_desc_simple = result['pro_desc_simple']
                    new_title = ''
                    main_tag = result['main_tag']
                    main_tag = json.loads(main_tag)
                    other_tag = result['other_tag']
                    other_tag_list = json.loads(other_tag)
                    main_tag_1 = random.choice(main_tag)
                    new_title += re.sub('dress', '', main_tag_1,
                                        flags=re.IGNORECASE).strip()

                    if not os.path.exists(os.path.join('..', 'images', 'pinimg', str(page_num), '%s.jpg' % pro_model)):
                        print('Image not find!')
                        continue

                    if len(other_tag_list) >= 2:
                        for _ in range(2):
                            other_tag_1 = random.choice(other_tag_list)
                            new_title += '-' + \
                                re.sub('dress', '', other_tag_1,
                                       flags=re.IGNORECASE).strip()
                            other_tag_list.remove(other_tag_1)

                    else:
                        other_tag_1 = random.choice(other_tag_list)
                        new_title += '-' + \
                            re.sub('dress', '', other_tag_1,
                                   flags=re.IGNORECASE).strip()
                        other_tag_list.remove(other_tag_1)
                    new_title = ((new_title + '-Dress')
                                 ).replace(' ', '-').lower()
                    media = 'https://www.%s/images/pinimg/%s/%s.jpg' % (
                        domain, page_num, pro_model)
                    media_real_path = '/images/pinimg/%s/%s.jpg' % (page_num, pro_model)
                    url_title = new_title + '-p-' + \
                        str(int(products_model.replace('P', '')))
                    url = 'https://www.%s/%s.html' % (domain, url_title)

                    if len(pro_desc_simple) > 450:
                        pro_desc_simple = pro_desc_simple[:450] + '...'
                    for _ in range(2):
                        pro_desc_simple += ' #' + \
                            (random.choice(main_tag)).replace(
                                ' ', '').replace('-', '')
                    pro_desc_simple += ' #' + \
                        (category).replace(' ', '').replace('-', '')

                    url_encode = quote(url, 'utf-8')
                    media_encode = quote(media, 'utf-8')
                    description_encode = quote(
                        pro_desc_simple, 'utf-8')
                    pin_url = "https://www.pinterest.com/pin/create/link/?url=%s&media=%s&description=%s" % (
                        url_encode, media_encode, description_encode)

                    sql = 'SELECT savelink FROM pin_upload WHERE save_image=%s'
                    r = op_select_one(pro_info_conn, sql, media_real_path)
                    if r:
                        print('Data duplication!')
                        continue

                    else:
                        sql = 'INSERT INTO pin_upload(savelink, saveboard, save_image, belong_web) VALUES (%s, %s, %s, %s)'
                        op_commit(pro_info_conn, sql,
                                  (pin_url, category, media_real_path, domain))
                        print(media_real_path, 'finished!')

            count += 1
            if count >= domain_list_length:
                count = 0


if __name__ == '__main__':
    main()