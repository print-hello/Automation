import pymysql
import configparser


conf = 'config.ini'
conf_conn = configparser.ConfigParser()
conf_conn.read(conf, encoding='utf-8')
items = conf_conn.items('mysql_wdweb')
items = dict(items)

conn = pymysql.connect(host='localhost',
                       port=3306,
                       db=items['db'],
                       user=items['user'],
                       password=items['password'],
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
cursor = conn.cursor()
cursor.execute('SELECT MAX(products_id) AS max_products_id FROM products_attributes')
result = cursor.fetchone()
if result:
    max_products_id = result['max_products_id']
    if not max_products_id:
        max_products_id = 0

cursor.execute('SELECT products_id FROM products WHERE products_id>%d' % int(max_products_id))
all_products = cursor.fetchall()
if all_products:
    for p in all_products:
        products_id = p['products_id']
        print('Add product %s attributes!' % products_id)
        cursor.execute('SELECT * FROM products_options_values_to_products_options')
        all_products_options = cursor.fetchall()
        if all_products_options:
            for i in all_products_options:
                options_id = i['products_options_id']
                options_values_id = i['products_options_values_id']

                cursor.execute('SELECT products_options_values_sort_order FROM products_options_values WHERE products_options_values_id=%s', options_values_id)
                r = cursor.fetchone()
                if r:
                    products_options_sort_order = r['products_options_values_sort_order']

                    cursor.execute('INSERT INTO products_attributes (products_id, options_id, options_values_id, price_prefix, products_options_sort_order, product_attribute_is_free, products_attributes_weight_prefix) VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                        (products_id, options_id, options_values_id, '+', products_options_sort_order, 1, '+'))
                    conn.commit()

cursor.close()
conn.close()