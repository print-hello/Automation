import time
import socket
import datetime
import win32api
import win32gui
import win32con
import os
import queue
import pymysql
import requests
import json
from storenvy_description import storenvy_content
from dbconnection import write_sql, read_one_sql, read_all_sql, distribution_data
from upfile import select_upfilename_chrome
from selenium import webdriver
from selenium.webdriver.support.select import Select
from collections import deque
from selenium.webdriver import ActionChains


with open('config.txt', 'r', encoding='utf-8') as fp:
    all_info = fp.readlines()
    for res in all_info:
        res_flag = res.replace('\n', '')
        if res_flag.find('email=') > -1:
            EMAIL = res_flag.replace('email=', '')
        if res_flag.find('pwd=') > -1:
            PWD = res_flag.replace('pwd=', '')
        if res_flag.find('database=') > -1:
            DATABASE = res_flag.replace('database=', '')
        if res_flag.find('pic_num=') > -1:
            PIC_NUM = res_flag.replace('pic_num=', '')


def login_storenvy(driver):
    driver.maximize_window()
    driver.get("https://www.storenvy.com")
    print("login")
    driver.find_element_by_id("log_in").click()
    time.sleep(2)
    user_email_arr = driver.find_elements_by_id("user_email")
    user_email_arr[1].send_keys(EMAIL)
    user_password_arr = driver.find_elements_by_id("user_password")
    user_password_arr[1].send_keys(PWD)
    driver.find_element_by_id("login_submit").click()
    time.sleep(2)


def delete_product(driver):
    delete_flag = 0
    print("Delete this time")
    driver.execute_script("window.scrollTo(0, 0);")
    time.sleep(3)
    while True:
        try:
            driver.find_element_by_xpath(
                "//ul[@class='select']//li[3]").click()
            delete_flag = 1
            time.sleep(3)
        except:
            pass
        try:
            option = driver.switch_to_alert()
            time.sleep(1)
            option.accept()
            time.sleep(5)
        except:
            pass
        if delete_flag == 1:
            print('Successfully delete')
            break


def test_product(driver):
    product_description_value = driver.find_element_by_id(
        "product_description").get_attribute("value")
    if len(product_description_value) < 10:
        print("Description error, Delete product")
        delete_product(driver)
        time.sleep(4)
    pic_list_num_arr = driver.find_elements_by_xpath(
        "//ul[@id='product_photos']//li//a//img")
    if len(pic_list_num_arr) < 1:
        print("Picture error, Delete product")
        delete_product(driver)
        time.sleep(4)


def add_product():
    driver = webdriver.Chrome()
    hostname = socket.gethostname()
    conn = pymysql.connect(host='localhost', port=3306,
                           user='root', password='root',
                           db='opencartcpcj', charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)
    login_storenvy(driver)
    product_flag = 0
    next_step = 0
    while True:
        sql = "SELECT * from %s where state=1 and upload_computer='%s' and read_num<4 order by Id asc limit 1" % (
            DATABASE, hostname)
        mark_result = read_one_sql(conn, sql)
        if mark_result:
            next_step = 1
        else:
            sql = "SELECT * from %s where state=0 order by Id asc limit 1" % DATABASE
            result = read_one_sql(conn, sql)
            if result:
                next_step = 2
            else:
                print("Not data...")
                break
        if next_step == 1 or next_step == 2:
            product_flag = 1
            product_id = result["Id"]
            product_title = result["meta_title"]
            if len(product_title) > 140:
                product_title = product_title[0:150]
            set_new_title = requests.get(
                'http://www.pin.com/wangfei/GetTitleByStr.php?pwd=wangfeicode&str=%s' % product_title)
            new_title_res = set_new_title.text
            i = new_title_res.index('<')
            new_title = new_title_res[0:i]
            product_tag = new_title_res[0:i]
            try:
                product_price = result["sprice"]
                new_product_price = '%.2f' % (round(float(product_price)) / 2)
                product_image = result["images"]
                if next_step == 2:
                    sql = 'UPDATE %s set state=1, upload_computer="%s" where Id=%s' % (
                        DATABASE, hostname, product_id)
                    write_sql(conn, sql)
            except:
                product_flag = 0
                sql = 'UPDATE %s set state=4, upload_computer="-" where Id=%s' % (
                    DATABASE, product_id)
                write_sql(conn, sql)
                print('Data error!')
            sql = "UPDATE %s set read_num=read_num+1  where Id=%s " % (
                DATABASE, product_id)
            write_sql(conn, sql)
            if product_flag == 1:
                all_a_link_flag = driver.find_elements_by_xpath(
                    "//ul[@class='main-nav-dropdown']//a")
                for a_link in all_a_link_flag:
                    if a_link.get_attribute("text") == "Products":
                        web_http = a_link.get_attribute("href")
                driver.get(web_http)
                time.sleep(2)
                driver.find_element_by_xpath(
                    '//a[@id="btn_add_product"]').click()
                time.sleep(2)
                add_info(driver, conn, product_id, new_title,
                         product_tag, new_product_price, product_image)
                test_product(driver)


def add_info(driver, conn, product_id, new_title, product_tag, new_product_price, product_image):
    print("Start fill in info!")
    try:
        intercom_arr = driver.find_elements_by_xpath(
            "//a[@class='intercom-note-close']")
        if len(intercom_arr) > 0:
            for intercom_one in intercom_arr:
                intercom_one.click()
    except Exception as e:
        print(e)
    try:
        print("Title: ", new_title)
        driver.find_element_by_id("name").send_keys(new_title)
        print("Price: ", new_product_price)
        driver.find_element_by_id("price").send_keys(new_product_price)
        storenvy_class = "Women's--Dresses"
        storenvy_class_0 = ""
        storenvy_class_1 = ""
        storenvy_class_2 = ""
        storenvy_class_arr = storenvy_class.split("--")
        if len(storenvy_class_arr) > 0:
            storenvy_class_0 = storenvy_class_arr[0]
        if len(storenvy_class_arr) > 1:
            storenvy_class_1 = storenvy_class_arr[1]
        if len(storenvy_class_arr) > 2:
            storenvy_class_2 = storenvy_class_arr[2]
        if storenvy_class_0 != "":
            Select(driver.find_element_by_xpath(
                "//select[1]")).select_by_visible_text('' + storenvy_class_0 + '')
            time.sleep(1)
        flag_arr = driver.find_elements_by_xpath("//select")
        flag_num = 0
        for echo_flag in flag_arr:
            if flag_num == 1:
                if(storenvy_class_1 != ""):
                    Select(echo_flag).select_by_visible_text(
                        '' + storenvy_class_1 + '')
                    time.sleep(1)
            if flag_num == 2:
                if storenvy_class_2 != "":
                    Select(echo_flag).select_by_visible_text(
                        '' + storenvy_class_2 + '')
                    time.sleep(1)
            flag_num += 1
        print("Fill end!")
        web_url = driver.current_url
        web_url_arr = web_url.split("/")
        web_site_name = web_url_arr[2]
        submit_flag = 0
        print("Submit")
        while True:
            try:
                # driver.execute_script(
                #     "name_text = document.getElementById('edit-product-submit');" + "name_text.focus();")
                # time.sleep(1)
                product_submit = driver.find_element_by_xpath(
                    '//input[@name="commit"]')
                ActionChains(driver).move_to_element(product_submit).perform()
                product_submit.click()
                submit_flag = 1
            except:
                time.sleep(3)
            if submit_flag == 1:
                print('Submit success! Break loop!')
                break
        add_complete_info(driver, product_tag)
        upload_pic(driver, conn, product_id, product_image)
        print(new_title, "End!")
    except Exception as e:
        print(e)
        # product_class_storenvy_class=product_class.lower()
        # storenvy_class="Women's--Dresses"
        # if product_class_storenvy_class=="accessories":
        #     storenvy_class="Women's--Accessories"
        # if product_class_storenvy_class=="bags and purses":
        #     storenvy_class="Women's--Accessories--Bags, Purses & Wallets"
        # if product_class_storenvy_class=="bath and beauty":
        #     storenvy_class="Health & Beauty--Makeup"
        # if product_class_storenvy_class=="children":
        #     storenvy_class="Kids--Clothing"
        # if product_class_storenvy_class=="coats and jackets":
        #     storenvy_class="Women's--Outerwear--Coats & Jackets"
        # if product_class_storenvy_class=="crochet and knitting":
        #     storenvy_class="Women's--Outerwear"
        # if product_class_storenvy_class=="housewares":
        #     storenvy_class="Home--Decor"
        # if product_class_storenvy_class=="jewelry":
        #     storenvy_class="Jewelry--Body Jewelry"
        # if product_class_storenvy_class=="lingerie and nightwear":
        #     storenvy_class="Women's--Sleep & Intimates"
        # if product_class_storenvy_class=="men clothing":
        #     storenvy_class="Men's--Shirts"
        # if product_class_storenvy_class=="phone cases":
        #     storenvy_class="Tech--iphone & ipad Cases"
        # if product_class_storenvy_class=="shoes":
        #     storenvy_class="Women's--Shoes"
        # if product_class_storenvy_class=="socks and tights":
        #     storenvy_class="Women's--Sleep & Intimates--Socks & Tights"
        # if product_class_storenvy_class=="sweaters and cardigans":
        #     storenvy_class="Women's--Tops--Sweaters"
        # if product_class_storenvy_class=="swimwear and bikinis":
        #     storenvy_class="Women's--Swim"
        # if product_class_storenvy_class=="trousers and leggings":
        #     storenvy_class="Women's--Bottoms--Leggings"
        # if product_class_storenvy_class=="weddings":
        #     storenvy_class="Specialty--Wedding"
        # if product_class_storenvy_class=="women clothing":
        #     storenvy_class="Women's--Outerwear"
        # if product_class_storenvy_class=="women dresses":
        #     storenvy_class = "Women's--Dresses"
        # if product_class_storenvy_class=="women skirts":
        #     storenvy_class="Women's--Bottoms--Skirts"
        # if product_class_storenvy_class=="women tops":
        #     storenvy_class="Women's--Tops"
        # if product_class_storenvy_class=="dolls and miniatures":
        #     storenvy_class="Art--Designer Toys"
        # if product_class_storenvy_class=="everything else":
        #     storenvy_class="Specialty--Everything Else"
        # if product_class_storenvy_class=="holidays":
        #     storenvy_class="Home--Outdoor"
        # if product_class_storenvy_class=="paper craft":
        #     storenvy_class="Home--Stationery & Paper Goods"
        # if product_class_storenvy_class=="supplies":
        #     storenvy_class="Specialty--Supplies & Patterns"
        # if product_class_storenvy_class=="patterns":
        #     storenvy_class="Specialty--Supplies & Patterns"
        # if product_class_storenvy_class=="art and photography":
        #     storenvy_class="Art--Photography"


def add_complete_info(driver, product_tag):
    print("Add description!")
    product_description = storenvy_content()
    description_flag = 0
    while True:
        try:
            driver.execute_script(
                "name_text=document.getElementById('product_description');" + "name_text.focus();")
            driver.find_element_by_id(
                "product_description").send_keys('<p><b>' + product_tag + '</b></p>' + '\n' + product_description)
            time.sleep(3)
            description_flag = 1
        except:
            time.sleep(1)
        if description_flag == 1:
            break
    win32api.keybd_event(34, 0, 0, 0)
    win32api.keybd_event(34, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(3)
    print("Choice Labels")
    sale_flag = 0
    while True:
        try:
            driver.find_element_by_id("product_on_sale").click()
            time.sleep(1)
            sale_flag = 1
        except:
            time.sleep(3)
        if sale_flag == 1:
            print("Choice Labels success!, Break loop!")
            break
    print("Add tags: ", product_tag)
    if len(product_tag) > 55:
        product_tag = product_tag[0:54]
    tags_flag = 0
    while True:
        try:
            driver.find_element_by_id(
                "product_tag_list").send_keys(product_tag)
            tags_flag = 1
        except:
            time.sleep(3)
        if tags_flag == 1:
            print("tags add success! Break loop!")
            break
    time.sleep(3)
    save_flag = 0
    print("Save")
    while True:
        try:
            driver.execute_script(
                "name_text = document.getElementById('edit-product-submit');" + "name_text.focus();")
            driver.find_element_by_id('edit-product-submit').click()
            save_flag = 1
        except:
            pass
        if save_flag == 1:
            print("Save success! Break loop!")
            break
    # message_flag_save = 'Product was successfully saved.'
    # test_info(message_flag_save)
    print("Processing size!")
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    q = queue.Queue()
    if q.qsize() > 0:
        size_info = 1
    else:
        size_info = 0
    q.put("Choose an option")
    q.put("US 2")
    q.put("US 4")
    q.put("US 6")
    q.put("US 8")
    q.put("US 10")
    q.put("US 12")
    q.put("US 14")
    q.put("US 16")
    q.put("Custom Made(Add Note In Shopping Cart)")
    size_info_num = 0
    while q.qsize() > 0:
        size_flag = q.get()
        print(size_flag)
        if size_info_num == 0:
            driver.execute_script(
                "name_text = document.getElementById('btn_add_variant');" + "name_text.focus();")
            driver.find_element_by_id("btn_add_variant").click()
            time.sleep(3)
        driver.execute_script(
            "name_text = document.getElementById('variant_name');" + "name_text.focus();")
        driver.find_element_by_id("variant_name").send_keys(size_flag)
        driver.execute_script(
            "name_text = document.getElementById('variant_quantity');" + "name_text.focus();")
        driver.find_element_by_id("variant_quantity").send_keys('000')
        driver.execute_script(
            "name_text = document.getElementById('variant_full_quantity');" + "name_text.focus();")
        driver.find_element_by_id("variant_full_quantity").send_keys('00')
        time.sleep(1)
        driver.find_element_by_xpath('//div[@class="submit"]/input').click()
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        size_info_num += 1
    if size_info == 1:
        try:
            driver.find_element_by_xpath(
                "//form[@id='new_variant_form']//a").click()
            time.sleep(2)
            option = driver.switch_to_alert()
            time.sleep(1)
            option.accept()
        except Exception as e:
            pass


def upload_pic(driver, conn, product_id, product_image):
    win32api.keybd_event(33, 0, 0, 0)
    win32api.keybd_event(33, 0, win32con.KEYEVENTF_KEYUP, 0)
    win32api.keybd_event(33, 0, 0, 0)
    win32api.keybd_event(33, 0, win32con.KEYEVENTF_KEYUP, 0)
    time.sleep(3)
    img_file_num = 0
    success_flag = 0
    product_image_arr = product_image.split("*****")
    product_image_num = 0
    for product_one_num in product_image_arr:
        if product_one_num != "":
            product_image_num += 1
    for product_one in product_image_arr:
        if product_one != "":
            product_one = product_one.split("?")[0]
            img_name_class_flag = product_one.split('/')[-1]
            img_name_format = img_name_class_flag.split('.')[-1]
            if len(img_name_format) > 4:
                img_name_flag = product_one + ".jpg"
            else:
                img_name_flag = product_one
            if img_name_flag != ".jpg":
                img_http_domain_arr = img_name_flag.split("/")
                img_http_domain = "%s//%s/" % (
                    img_http_domain_arr[0], img_http_domain_arr[2])
                new_img_flag = "E:\\pic\\wwwroot\\%s\\" % PIC_NUM
                img_name_flag = img_name_flag.replace(
                    img_http_domain, new_img_flag)
                img_name_flag = img_name_flag.replace("/", "\\")
                print(img_name_flag)
                if os.path.exists(img_name_flag):
                    img_file_num = img_file_num + 1
                    select_upfilename_chrome(driver, img_name_flag)
                    if product_image_num == 1:
                        print("One picture, Skip!")
                    else:
                        if img_file_num == 1:
                            while True:
                                pic_list_num_arr = driver.find_elements_by_xpath(
                                    "//ul[@id='product_photos']//li//a//img")
                                print("Selected picture: ", img_file_num,
                                      " Was upload: ", len(pic_list_num_arr))
                                if len(pic_list_num_arr) == img_file_num:
                                    break
                                time.sleep(5)
                        else:
                            print("Not first picture, Dont wait!")
                            time.sleep(1)
                        success_flag = 1
                else:
                    print("File does not exist!")
                    success_flag = 0
                    time.sleep(3)
        if img_file_num == 5:
            break
    other_pic = 0
    if img_file_num > 0:
        if img_file_num < 4:
            img_file_num = img_file_num + 1
            add_default_pic = "E:\\pic\\wwwroot\\sizechart.jpg"
            select_upfilename_chrome(driver, add_default_pic)
            time.sleep(2)
            img_file_num = img_file_num + 1
            add_default_pic = "E:\\pic\\wwwroot\\celiangtu.jpg"
            select_upfilename_chrome(driver, add_default_pic)
            other_pic = 1
    else:
        success_flag = 0

    if success_flag == 1:
        now_time = datetime.datetime.today()
        sql = "UPDATE %s SET state=2, upload_computer='-', ip_time='%s' where Id=%s" % (
            DATABASE, now_time, product_id)
        write_sql(conn, sql)
        while True:
            pic_list_num_arr = driver.find_elements_by_xpath(
                "//ul[@id='product_photos']//li//a//img")
            print("Selected picture: ", img_file_num, " Was upload: ", len(pic_list_num_arr))
            if len(pic_list_num_arr) == img_file_num:
                break
            time.sleep(5)
        web_url = driver.current_url
        web_url_arr = web_url.split("/")
        web_site_name = web_url_arr[2].split(".")[0]
        web_class = "storenvy.com"
        product_id_storenvy = web_url_arr[5].split("-")[0]
        time.sleep(2)


if __name__ == '__main__':
    add_product()
