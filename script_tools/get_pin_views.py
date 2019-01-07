import json
import os
import time
import datetime
from requests import Session
import pymysql


def my_get(param):
    sess = Session()
    millis = str(round(time.time() * 1000))
    url = 'https://www.pinterest.com/_ngjs/resource/UserResource/get/?source_url=%2F' + param + '%2F&data=%7B%22options%22%3A%7B%22isPrefetch%22%3Afalse%2C%22username%22%3A%22' + \
        param + '%22%2C%22field_set_key%22%3A%22profile%22%7D%2C%22context%22%3A%7B%7D%7D&_=' + millis
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Referer': 'https://www.pinterest.com/',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-APP-VERSION': '79d3456',
        'X-Pinterest-AppState': 'background',
        'X-Requested-With': 'XMLHttpRequest',
        'Cookie': 'G_ENABLED_IDPS=google; _b="ATllpRenVvhF6IE9smXlwWU0Q6ams71wkYrWnR7y1OFyRQ425kP0DURZkBPXsp2ZkGc="; fba=True; cm_sub=denied; _pinterest_cm=TWc9PSZHUVhMN0FWZGo4OEJpL2JkdjRXUmxGbk1oQ2tuOFQ5bTVRV0EvNGVZVkp1RHJMYjc5V1QxV1kzd0cwUFk3VXRCSmppdllySjhDdVRZWkZwOVlHdDVtaVZrVXpSS285KzVVNXg2WjZpeEVkOU9oRTBzQVRZdkc3YzJEcmRqb3NmQSZTNEk5aFBHZGNqVEVGVEYrN1dja1hCb3BkdUE9; _pinterest_referrer="http://127.0.0.1:8000/show/pin/"; _routing_id="71f53e1d-08e9-4cdb-b0be-b900e4edd951"; sessionFunnelEventLogged=1; _auth=1; csrftoken=kQ7Bhlv7N6X8Rkfhdf294WJ4SdjtQhuK; _pinterest_sess="TWc9PSY2TlcrU0toWFFLYnBpNWJ2YjE2Ni9iUktsOXRHU3Exak41UW5BaTBxY3JaS0UxWmRad2ZjZWF0Y2ZSc0s1bFNTM0hhdWcveDJRT2ViREQ0bUQrZWhVV1ZUU210MnhIQXlGTHIzQjRBOUE5MW1rUkJmTVdQdHlER1NSNVVVeHorTVpHbG55LzZYUkIzOE52ZmdXOUlTQjRER1MxbWlyckpYWVFlOC9nR0xhb3JwZWl4TEhqSkNtL2pFNlE5WFNhR1hrajFwelNzeXpaMGQxU1FlUWhLT0JIMGxlbDk4VnVRY09WdU8raGZpVmthSnNka1M0SStmM1lhditId0V0M2U2UlhPTGtPN1ZaQjNOMlFPdjkrS0l6ckNxbk9pRGFHNDJqSGlzU2V5VmVlSm5IalJYOGhSQXNJVjR0eWFKcmN5ZTdKSzYrckdWQnRaR2g0S0F2YlUra28vL3QrL2RKYTl2d2pRMWFSUnJDQkxYbDRsaWpiamRydWxHbG16eUFjdXpEZnd5eXQwT2JHZk9KQlJCd3NGWGVUblFrb1FxTllCMXZjSnVwQXpwNG5UdEcwc3FQN25ya09BMFRCUmN3TTZ3MjZjSWk3UElrdlhaWk9qbDJTYVFFcDltTExYeDZKV3Z5eVN6eHdHaU85RXNWWnMrWHZkbVlWOVFOM3NwZWdTbzZ0ZndSQXpZUDFBVWovVWhWVk0vemwyckpVbzVVcG5XNXZFUHd5ZUtIWFBrRTBQeXRHVHN5UUFETGUzSHVnemJLWFZ2ekIxV1NBWjhQTzJ1M2RuODlRTk9GSjc3UjlXZ1hTTUlVRkxqQndud01kS2JoYXJvTndvNGRNRmNSRVcwVTdCQk14WUZweFZIdkpVeHI1bXVPMnVydFNhRVdmOHZzRGI4WVluY1laOEV6dklTYXovTEVveWpHNGpTUDB0QVlQRjh6ZW9pM0dWQW45bTlob3RjVFQ3M2cxN2NDVmpFdUFxaHVxM1dmYVhad3ZPS1VNVGxqc1VVRENjcjhuK2p6dDlrUTMzb1pDQUdMeEN1SmJhYnFVdFptUkVXeFJYOVhES29SMmZPZFFHMHo1aVd5SDRGM2VjS0NqWHdLSDZXSExzdVpkR3h2QmFIWGo0ajMvdjFCVXZTaG90aTRFK2NFRFV3YnBqNHR5VT0mMmdrbXlEK3FQUzVhaXRXb0ovUHRLQ1B4Z0tRPQ=="; bei=false; _fbp=fb.1.1546845271512.1961545300',
        'X-Pinterest-ExperimentHash': '120d398e7e86e4172479b7c6e77086fedb43f58581c96b9a37f41324931719d605d9a64a766b693370f56bf6e6da4d852d144c36d7b528c9ce993e759a3c76a5'
    }
    html = sess.get(url, headers=headers)
    return html.text


def get_user_list(conn):
    param_list = []
    sql = "SELECT * from yyc_domain_to_user"
    cursor = conn.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    for param in results:
        if param['user'] != None:
            param_list.append((param['user']).strip())
    cursor.close()
    return param_list


def main():
    conn = pymysql.connect(host='loaclhost', port=3306,
                           user='root', password='******',
                           db='yyc_admin', charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    conn1 = pymysql.connect(host='loaclhost', port=3306,
                            user='root', password='******',
                            db='pinterest', charset='utf8mb4',
                            cursorclass=pymysql.cursors.DictCursor)
    current_time = datetime.datetime.now().strftime('%Y_%m_%d')
    cursor = conn.cursor()
    try:
        cursor.execute(
            'alter table yyc_domain_to_user add views_%s int(11)' % current_time)
        conn.commit()
        print('新建字段：', 'views_' + current_time)
    except:
        pass
    params = get_user_list(conn)
    for param in params:
        param = param.strip()
        html = my_get(param)
        all_url_json = json.loads(html)
        # bookmarks = all_url_json['resource']['options']['bookmarks'][0]
        datalist = all_url_json['resource_response']['data']
        if datalist != None:
            viewers = datalist['profile_reach']
            print(param, ':', viewers)
            cursor.execute('update yyc_domain_to_user set views_%s=%s where user="%s"' % (
                current_time, viewers, param))
            conn.commit()
    print('######### 数据获取完毕！ ##########')


if __name__ == '__main__':
    main()
