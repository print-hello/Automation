import json
import os
import time
import datetime
from requests import Session
import sys
import pymysql
import requests
import queue
import threading


q = queue.Queue()


def get_list():
    with open('user.txt', 'r', encoding='utf-8') as fp:
        params = fp.readlines()
    return params


def my_get(param, headers, sess):
    millis = str(round(time.time() * 1000))
    url = 'https://www.pinterest.com/_ngjs/resource/UserFollowersResource/get/?source_url=%2F' + param + \
        '%2Ffollowers%2F&data=%7B%22options%22%3A%7B%22bookmarks%22%3A%5B%22Pz9Nakl5TXpvek56a3pOVGd4TURZd01qQXpNVEkzT0RZNk9USXlNek0zTURVd01qWTBPREkxTWpJMk1GOUZ8ZjMwNTAxZjYwNWVhMjg1Y2I4MTE0NDk0MDViZTQ3NjQ2NjQ2NDZjZTc4ZGIyNmVkY2FmODdhZTIzZTY1YjIzYw%3D%3D%22%5D%2C%22isPrefetch%22%3Afalse%2C%22hide_find_friends_rep%22%3Atrue%2C%22username%22%3A%22' + param + '%22%7D%2C%22context%22%3A%7B%7D%7D&_=' + millis
    html = sess.get(url, headers=headers)
    return html.text


def main():
    thread_name = threading.current_thread().getName()
    sess = Session()
    millis = str(round(time.time() * 1000))
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Referer': 'https://www.pinterest.com/',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-APP-VERSION': 'd9d2e8e3',
        'X-Pinterest-AppState': 'background',
        'X-Requested-With': 'XMLHttpRequest',
        'cookie': 'G_ENABLED_IDPS=google; _b="ATllpRenVvhF6IE9smXlwWU0Q6ams71wkYrWnR7y1OFyRQ425kP0DURZkBPXsp2ZkGc="; fba=True; _auth=1; csrftoken=mLNyo5SqTXiUl3cGMfMcgq2AVK8XMemw; _pinterest_sess="TWc9PSZlTEh3KzR0T0RWNVJ1Uk9UeFIxTmhsVEtub0x0SWNmNExqSGdoY2Y3bThFTisydml5dm1aVTNpOHZ0Mnp6SG5idnNLcEs2Y3UxRUhOVXMzcmt1UmFjTzgrZ3JQYWRXNXZEKzV3Wm1xeUR5SC8xYlZOMzdNMXRGSjZkZVhUMDdGR3o5dE5pNm1NU2ppazVtL0pXYzBOeXZyYVN0cEVDQ01xYnhzTTdtaFY1YmpXaXFjVU1WRVNTSDg2NVZaQmFYTmM3eS9pdTM2ZWtJQTdhV25GR21SWGRWRkdsOHp4alZPMjhSTlhvVUdZTHFCNXUwMHd4c011cDVTZ2pCMExsck9pNjdhT3RaWDdnUlAvNldYcHIyYm1EMmV1alZHV1pkTHpRTmdTNTZ4a0pmYm9yN1FPSzZ5OW9YNjFFTlJlWVZPRVNJVFJ6dXhMNGJtZUhlUW15RlkvK2VIYUZZWUZoSHlmTEFxV0szU3RpQ0EvRlZRUk4rRkVzYzR4WXBSUmxoZFgrbFFETkVldVVzWGhHTkIrVDIzRURFS1hSSlZxaXRpRGZmQmJUNmxoK0NXK05pbis4d2Z5MnUyWW5QdVRCbXpaK0F0QWwzLy93b0ljMWxWNW1QT3B0bXdzTmUxUENVYXdrendUcXlJWER2VlpLaFhlZzlWbjlXeFpvRVdFQzErUHZpVXViSEVTTzQwVTZwSXBsK2ZPbWI3dGlnU2dkR01QYzFFcVR4bFlQMmZ0UXlzUjgxbUZTY1R1VWRqQmVHNGhTeEtxMFdpN1YwazkzVU9DcnpvTy9jWU55MGlXc2FBbTkvUUw4eVpzdndySmpBUndITllHbDIvNURUczQvVWJrak9VT2FPeWtsS25XSVhneFRFOTByZ2J0U1lrd0Z2dnUyall4M21WcHpKM1J4WkM4YVRsU2FJWjVCRENlQVp3ZU1LYWlGbXZjdk5MeWp6THlZMUtsWDUwdWhLS3JzbmI3aWpkdjNpZHRyK3ZnVE1wS1BxbGRLWStNQndhSzlBZDFrVDJwSFZNZXhCU2Z3Z3VzTDhPR1B1dWR4S0ptcDVMdVNFckVjODlybTJrMlViK1o5YXhwZGZ3Z3dSQzU3SmVYOFVHR2s2V2RnVTlWdDlPa2k3dm1uQ0dzUGlVQ0NEVTJtMlB6emtHQ0hBTT0mSWtoMU1LaGhWeTVGVHFZTlFFSFV2bS9FemxnPQ=="; cm_sub=denied; _routing_id="abec52c6-a5d1-4ab2-b13d-c89236eff849"; sessionFunnelEventLogged=1; _pinterest_referrer="http://172.16.252.123:8000/show/pin/"; bei=false; _fbp=fb.1.1546063606815.1861544321',
        'X-Pinterest-ExperimentHash': '53d83f88064b56237fedce86884b63453c35541612b5fa810740529ff44b0acf536a205044b85b41efe20547c47ed7d75ba9fc1de1de44a81eca514c5840e5c0'
    }
    print(thread_name, '开始获取数据！')
    params = get_list()
    for param in params:
        param = param.strip()
        print('来源：', param)
        html = my_get(param, headers, sess)
        all_url_json = json.loads(html)
        bookmarks = all_url_json['resource']['options']['bookmarks'][0]
        datalist = all_url_json['resource_response']['data']
        if datalist != None:
            for datastr in datalist:
                pic_url = datastr['image_xlarge_url']
                print(pic_url)
                q.put(pic_url)
            continue_spider(sess, millis, bookmarks, param, 1, q)
    print('######### 数据获取完毕！ ##########')
    print('图片总数量：', q.qsize())


def continue_spider(sess, millis, bookmarks, param, count, q):
    url = 'https://www.pinterest.com/_ngjs/resource/UserFollowersResource/get/?source_url=%2F' + param + '%2Ffollowers%2F&data=%7B%22options%22%3A%7B%22bookmarks%22%3A%5B%22' + \
        bookmarks + '%3D%3D%22%5D%2C%22isPrefetch%22%3Afalse%2C%22hide_find_friends_rep%22%3Atrue%2C%22username%22%3A%22' + \
        param + '%22%7D%2C%22context%22%3A%7B%7D%7D&_=' + str(millis)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Referer': 'https://www.pinterest.com/',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-APP-VERSION': 'd9d2e8e3',
        'X-Pinterest-AppState': 'background',
        'X-Requested-With': 'XMLHttpRequest',
        'cookie': 'G_ENABLED_IDPS=google; _b="ATllpRenVvhF6IE9smXlwWU0Q6ams71wkYrWnR7y1OFyRQ425kP0DURZkBPXsp2ZkGc="; fba=True; _auth=1; csrftoken=mLNyo5SqTXiUl3cGMfMcgq2AVK8XMemw; _pinterest_sess="TWc9PSZlTEh3KzR0T0RWNVJ1Uk9UeFIxTmhsVEtub0x0SWNmNExqSGdoY2Y3bThFTisydml5dm1aVTNpOHZ0Mnp6SG5idnNLcEs2Y3UxRUhOVXMzcmt1UmFjTzgrZ3JQYWRXNXZEKzV3Wm1xeUR5SC8xYlZOMzdNMXRGSjZkZVhUMDdGR3o5dE5pNm1NU2ppazVtL0pXYzBOeXZyYVN0cEVDQ01xYnhzTTdtaFY1YmpXaXFjVU1WRVNTSDg2NVZaQmFYTmM3eS9pdTM2ZWtJQTdhV25GR21SWGRWRkdsOHp4alZPMjhSTlhvVUdZTHFCNXUwMHd4c011cDVTZ2pCMExsck9pNjdhT3RaWDdnUlAvNldYcHIyYm1EMmV1alZHV1pkTHpRTmdTNTZ4a0pmYm9yN1FPSzZ5OW9YNjFFTlJlWVZPRVNJVFJ6dXhMNGJtZUhlUW15RlkvK2VIYUZZWUZoSHlmTEFxV0szU3RpQ0EvRlZRUk4rRkVzYzR4WXBSUmxoZFgrbFFETkVldVVzWGhHTkIrVDIzRURFS1hSSlZxaXRpRGZmQmJUNmxoK0NXK05pbis4d2Z5MnUyWW5QdVRCbXpaK0F0QWwzLy93b0ljMWxWNW1QT3B0bXdzTmUxUENVYXdrendUcXlJWER2VlpLaFhlZzlWbjlXeFpvRVdFQzErUHZpVXViSEVTTzQwVTZwSXBsK2ZPbWI3dGlnU2dkR01QYzFFcVR4bFlQMmZ0UXlzUjgxbUZTY1R1VWRqQmVHNGhTeEtxMFdpN1YwazkzVU9DcnpvTy9jWU55MGlXc2FBbTkvUUw4eVpzdndySmpBUndITllHbDIvNURUczQvVWJrak9VT2FPeWtsS25XSVhneFRFOTByZ2J0U1lrd0Z2dnUyall4M21WcHpKM1J4WkM4YVRsU2FJWjVCRENlQVp3ZU1LYWlGbXZjdk5MeWp6THlZMUtsWDUwdWhLS3JzbmI3aWpkdjNpZHRyK3ZnVE1wS1BxbGRLWStNQndhSzlBZDFrVDJwSFZNZXhCU2Z3Z3VzTDhPR1B1dWR4S0ptcDVMdVNFckVjODlybTJrMlViK1o5YXhwZGZ3Z3dSQzU3SmVYOFVHR2s2V2RnVTlWdDlPa2k3dm1uQ0dzUGlVQ0NEVTJtMlB6emtHQ0hBTT0mSWtoMU1LaGhWeTVGVHFZTlFFSFV2bS9FemxnPQ=="; cm_sub=denied; _routing_id="abec52c6-a5d1-4ab2-b13d-c89236eff849"; sessionFunnelEventLogged=1; _pinterest_referrer="http://172.16.252.123:8000/show/pin/"; bei=false; _fbp=fb.1.1546063606815.1861544321'
    }

    html = sess.get(url, headers=headers)
    all_url_json = json.loads(html.text)
    bookmarks = all_url_json['resource']['options']['bookmarks'][0]
    datalist = all_url_json['resource_response']['data']
    if count < 10 and datalist != None:
        if len(datalist) > 0:
            print('第' + str(count) + '次循环取数据')
            for datastr in datalist:
                pic_url = datastr['image_xlarge_url']
                print(pic_url)
                q.put(pic_url)
            count += 1
            continue_spider(sess, millis, bookmarks, param, count, q)


def download_pic(q):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
        'Referer': 'https://www.pinterest.com/',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-APP-VERSION': 'd9d2e8e3',
        'X-Pinterest-AppState': 'background',
        'X-Requested-With': 'XMLHttpRequest',
        'cookie': 'G_ENABLED_IDPS=google; _b="ATllpRenVvhF6IE9smXlwWU0Q6ams71wkYrWnR7y1OFyRQ425kP0DURZkBPXsp2ZkGc="; fba=True; _auth=1; csrftoken=mLNyo5SqTXiUl3cGMfMcgq2AVK8XMemw; _pinterest_sess="TWc9PSZlTEh3KzR0T0RWNVJ1Uk9UeFIxTmhsVEtub0x0SWNmNExqSGdoY2Y3bThFTisydml5dm1aVTNpOHZ0Mnp6SG5idnNLcEs2Y3UxRUhOVXMzcmt1UmFjTzgrZ3JQYWRXNXZEKzV3Wm1xeUR5SC8xYlZOMzdNMXRGSjZkZVhUMDdGR3o5dE5pNm1NU2ppazVtL0pXYzBOeXZyYVN0cEVDQ01xYnhzTTdtaFY1YmpXaXFjVU1WRVNTSDg2NVZaQmFYTmM3eS9pdTM2ZWtJQTdhV25GR21SWGRWRkdsOHp4alZPMjhSTlhvVUdZTHFCNXUwMHd4c011cDVTZ2pCMExsck9pNjdhT3RaWDdnUlAvNldYcHIyYm1EMmV1alZHV1pkTHpRTmdTNTZ4a0pmYm9yN1FPSzZ5OW9YNjFFTlJlWVZPRVNJVFJ6dXhMNGJtZUhlUW15RlkvK2VIYUZZWUZoSHlmTEFxV0szU3RpQ0EvRlZRUk4rRkVzYzR4WXBSUmxoZFgrbFFETkVldVVzWGhHTkIrVDIzRURFS1hSSlZxaXRpRGZmQmJUNmxoK0NXK05pbis4d2Z5MnUyWW5QdVRCbXpaK0F0QWwzLy93b0ljMWxWNW1QT3B0bXdzTmUxUENVYXdrendUcXlJWER2VlpLaFhlZzlWbjlXeFpvRVdFQzErUHZpVXViSEVTTzQwVTZwSXBsK2ZPbWI3dGlnU2dkR01QYzFFcVR4bFlQMmZ0UXlzUjgxbUZTY1R1VWRqQmVHNGhTeEtxMFdpN1YwazkzVU9DcnpvTy9jWU55MGlXc2FBbTkvUUw4eVpzdndySmpBUndITllHbDIvNURUczQvVWJrak9VT2FPeWtsS25XSVhneFRFOTByZ2J0U1lrd0Z2dnUyall4M21WcHpKM1J4WkM4YVRsU2FJWjVCRENlQVp3ZU1LYWlGbXZjdk5MeWp6THlZMUtsWDUwdWhLS3JzbmI3aWpkdjNpZHRyK3ZnVE1wS1BxbGRLWStNQndhSzlBZDFrVDJwSFZNZXhCU2Z3Z3VzTDhPR1B1dWR4S0ptcDVMdVNFckVjODlybTJrMlViK1o5YXhwZGZ3Z3dSQzU3SmVYOFVHR2s2V2RnVTlWdDlPa2k3dm1uQ0dzUGlVQ0NEVTJtMlB6emtHQ0hBTT0mSWtoMU1LaGhWeTVGVHFZTlFFSFV2bS9FemxnPQ=="; cm_sub=denied; _routing_id="abec52c6-a5d1-4ab2-b13d-c89236eff849"; sessionFunnelEventLogged=1; _pinterest_referrer="http://172.16.252.123:8000/show/pin/"; bei=false; _fbp=fb.1.1546063606815.1861544321',
        'X-Pinterest-ExperimentHash': '53d83f88064b56237fedce86884b63453c35541612b5fa810740529ff44b0acf536a205044b85b41efe20547c47ed7d75ba9fc1de1de44a81eca514c5840e5c0'
    }
    while True:
        thread_name = threading.current_thread().getName()
        print(thread_name, '正在下载！')
        os.makedirs('./image/', exist_ok=True)
        pic_url = q.get()
        if pic_url != 'https://s.pinimg.com/images/user/default_280.png':
            r = requests.get(pic_url, headers=headers)
            with open('./image/img%s.png' % pic_url[-10:-4], 'wb') as f:
                f.write(r.content)
        print('剩余图片数量：', q.qsize())
        if q.qsize() == 0:
            print(thread_name, '线程结束！')
            break


if __name__ == '__main__':
    main()
    for i in range(50):
        threading.Thread(target=download_pic, args=(q,)).start()
