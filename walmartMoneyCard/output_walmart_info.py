import pymysql
import datetime
import os
from dbconnection import fetch_one_sql, fetch_all_sql, commit_sql


os.makedirs('./walmartCardInfo/', exist_ok=True)
current_time = datetime.datetime.now().strftime("%Y-%m-%d")
conn = pymysql.connect(host='172.16.253.100', port=3306,
                       user='root', password='123456',
                       db='walmartmoneycard', charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
sql = 'SELECT * from email_info where emailIsUsed=1 and is_output=0'
all_info = fetch_all_sql(conn, sql)
for echo in all_info:
    email = echo['email']
    email_pwd = echo['email_pwd']
    user = echo['user']
    user_pwd = echo['user_pwd']
    bankRoutingNumber = echo['bankRoutingNumber']
    directDepositAccountNumber = echo['directDepositAccountNumber']
    temporaryCardNumber = echo['temporaryCardNumber']
    expirationData = echo['expirationData']
    securityCode = echo['securityCode']
    register_info_id = echo['register_info_id']
    answer_1 = echo['answer_1']
    answer_2 = echo['answer_2']
    answer_3 = echo['answer_3']
    sql = 'SELECT * from register_info where id=%s'
    prosonal_info = fetch_one_sql(conn, sql, register_info_id)
    if prosonal_info:
        firstname = prosonal_info['firstname']
        lastname = prosonal_info['lastname']
        address = prosonal_info['address']
        city = prosonal_info['city']
        state = prosonal_info['state']
        zip_ = prosonal_info['zip']
        socialnumber = prosonal_info['socialnumber']
        birthdate = prosonal_info['birthdate']
        birthdate = birthdate
        mobilenumber = prosonal_info['mobilenumber']
        pinnumber = prosonal_info['pinnumber']
        with open('walmartCardInfo\\%s.txt' % email, 'w', encoding='utf-8') as fp:
            fp.write('''SN: %s: %s: %s: %s: %s: %s: %s: %s

----------------------------------------------------------------------------------------------------------


----------------------------------------------------------------------------------------------------------


----------------------------------------------------------------------------------------------------------
Bank Routing Number: %s, Direct Deposit Account Number: %s

Temporary Card Number: %s
Expiration Date: %s
3-Digit Security Code: %s

ID: %s----%s

密保: %s, %s, %s
----------------------------------------------------------------------------------------------------------
mail: %s----%s''' % (
                firstname, lastname, address, city, state, zip_, socialnumber, birthdate, bankRoutingNumber, directDepositAccountNumber, temporaryCardNumber, expirationData, securityCode, user, user_pwd, answer_1, answer_2, answer_3, email, email_pwd))
conn.close()
