import pymysql
import datetime
import os
from dbconnection import fetch_one_sql, fetch_all_sql, commit_sql


current_time = datetime.datetime.now().strftime("%Y-%m-%d")
os.makedirs('./walmartCardInfo%s/' % current_time, exist_ok=True)
conn = pymysql.connect(host='172.16.253.100', port=3306,
                       user='root', password='HmIIrwuDicIAKrtHvMP5j',
                       db='walmartmoneycard', charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)
sql = 'SELECT * from email_info where id>994 and emailIsUsed=1 and is_output=0'
all_info = fetch_all_sql(conn, sql)
for echo in all_info:
    email_id = echo['id']
    email = echo['email']
    email_pwd = echo['new_pwd']
    phone_num = echo['phone_num']
    recovery_email = echo['recovery_email']
    # recovery_email_pwd = echo['recovery_email_pwd']
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
        with open('walmartCardInfo%s\\%s.txt' % (current_time, email), 'w', encoding='utf-8') as fp:
            fp.write('''SN: %s: %s: %s: %s: %s: %s: %s: %s

----------------------------------------------------------------------------------------------------------

GV: %s----%s----%s
Recovery Email: %s

----------------------------------------------------------------------------------------------------------


----------------------------------------------------------------------------------------------------------
Bank Routing Number: %s, Direct Deposit Account Number: %s

Temporary Card Number: %s
Expiration Date: %s
3-Digit Security Code: %s

ID: %s----%s

密保: %s, %s, %s
----------------------------------------------------------------------------------------------------------
''' % (
    firstname, lastname, address, city, state, zip_, socialnumber, birthdate, email, email_pwd, phone_num, recovery_email, bankRoutingNumber, directDepositAccountNumber, temporaryCardNumber, expirationData, securityCode, user, user_pwd, answer_1, answer_2, answer_3))
    sql = 'UPDATE email_info set is_output=1 where id=%s'
    commit_sql(conn, sql, email_id)
conn.close()
