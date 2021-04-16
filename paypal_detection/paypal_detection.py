import os
import re
import time
import json
import requests
import zipfile
import datetime
import pymysql
from os.path import sep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options as Firefox_Options
from selenium.common.exceptions import UnexpectedAlertPresentException


def main():
    while True:
        have_data = 0
        execute_path = os.path.abspath('.')
        post_form_path = os.path.join(execute_path, 'post_form.html')

        conn = pymysql.connect(host='localhost', port=3306,
                               user='paypal_detection', password='******',
                               db='paypal_detection', charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
        cursor = conn.cursor()
        current_time = get_time()
        cursor.execute(
            'UPDATE running_time set last_run_time=%s where id=1', current_time)
        conn.commit()

        cursor.execute('SELECT * FROM paypal_info WHERE php_status=-1')
        sent_false = cursor.fetchall()
        if sent_false:
            for i in sent_false:
                post_info = {}
                paypal_id = i['id']
                paypal_email = i['paypal_email']
                php_status = i['php_status']
                sys = i['sys']
                post_info['paypal_email'] = i['paypal_email']
                post_info["status"] = int(i['paypal_status'])
                post_info["time"] = get_time()
                post2pp_system(conn, cursor, paypal_id, post_info, sys)

        cursor.execute(
            'SELECT * from paypal_info where py_status=0 order by id desc limit 1')
        paypal_info = cursor.fetchone()
        if paypal_info:
            have_data = 1

        else:
            cursor.execute(
                'SELECT * from paypal_info where dec_num<3 and paypal_status=-1 order by id desc limit 1')
            paypal_info = cursor.fetchone()
            if paypal_info:
                have_data = 1

            else:
                print('Not data, Wait 180s...')
                time.sleep(180)

        if have_data == 1:
            paypal_id = paypal_info['id']
            paypal_email = paypal_info['paypal_email']
            print(paypal_email, 'with id: ', paypal_id)
            paypal_url = paypal_info['url']
            dec_num = paypal_info['dec_num']
            sys = paypal_info['sys']
            browser = set_selenium_local_session(
                '127.0.0.1', 24000, False, None, 25,)
            detection_process(browser, execute_path, post_form_path, conn,
                              cursor, paypal_id, paypal_email, paypal_url, dec_num, sys)


def create_firefox_extension():
    ext_path = os.path.join(os.path.abspath('.'), 'firefox_extension')
    zip_file = os.path.join(os.path.abspath('.'), 'boot', 'extension.xpi')
    files = ["manifest.json", "content.js", "arrive.js"]

    with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED, False) as zipf:

        for file in files:
            zipf.write(ext_path + sep + file, file)

    return zip_file


def set_selenium_local_session(
    proxy_address,
    proxy_port,
    headless_browser,
    disable_image_load,
    page_delay,
):
    """Starts local session for a selenium server."""

    browser = None

    # set Firefox Agent to mobile agent
    user_agent = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 like Mac OS X) AppleWebKit/605.1.15 "
        "(KHTML, like Gecko) FxiOS/18.1 Mobile/16B92 Safari/605.1.15"
    )

    geckodriver_path = os.path.join(
        os.path.abspath('.'), 'boot', 'geckodriver.exe')

    firefox_options = Firefox_Options()

    if headless_browser:
        firefox_options.add_argument("-headless")

    firefox_profile = webdriver.FirefoxProfile()

    # disable notification
    # firefox_profile.set_preference('dom.webnotifications.enabled', False)

    # set English language
    firefox_profile.set_preference("intl.accept_languages", "en-US")
    firefox_profile.set_preference("general.useragent.override", user_agent)

    if disable_image_load:
        # permissions.default.image = 2: Disable images load,
        # this setting can improve pageload & save bandwidth
        firefox_profile.set_preference("permissions.default.image", 2)

    if proxy_address and proxy_port:
        firefox_profile.set_preference("network.proxy.type", 1)
        firefox_profile.set_preference("network.proxy.http", proxy_address)
        firefox_profile.set_preference(
            "network.proxy.http_port", int(proxy_port))
        firefox_profile.set_preference("network.proxy.ssl", proxy_address)
        firefox_profile.set_preference(
            "network.proxy.ssl_port", int(proxy_port))

    # mute audio while watching stories
    firefox_profile.set_preference("media.volume_scale", "0.0")

    # prevent Hide Selenium Extension: error
    firefox_profile.set_preference("dom.webdriver.enabled", False)
    firefox_profile.set_preference("useAutomationExtension", False)
    firefox_profile.set_preference("general.platform.override", "iPhone")
    firefox_profile.update_preferences()

    # prefer user path before downloaded one
    driver_path = geckodriver_path or get_geckodriver()
    browser = webdriver.Firefox(
        firefox_profile=firefox_profile,
        executable_path=driver_path,
        options=firefox_options,
    )

    # add extenions to hide selenium
    browser.install_addon(create_firefox_extension(), temporary=True)

    # converts to custom browser
    # browser = convert_selenium_browser(browser)

    browser.implicitly_wait(page_delay)

    # set mobile viewport (iPhone X)
    try:
        browser.set_window_size(375, 812)

    except UnexpectedAlertPresentException as exc:
        print(
            "Unexpected alert on resizing web browser!\n\t"
            "{}".format(str(exc).encode("utf-8"))
        )
        close_browser(browser, False, logger)

        return browser, "Unexpected alert on browser resize"

    print("Session started!")

    return browser


def detection_process(browser, execute_path, post_form_path, conn, cursor, paypal_id, paypal_email, paypal_url, dec_num, sys):
    refresh_status = refresh_sessions()
    if refresh_status:

        server_ip = '45.159.176.221'
        step_flag = 1
        try:
            browser.get("view-source:https://ip4.seeip.org/geoip")
            pre = browser.find_element_by_tag_name("pre").text
            current_ip_info = json.loads(pre)

            if (
                server_ip is not None
                and server_ip != current_ip_info["ip"]
            ):
                step_flag = 1

            else:
                print("- Internet Connection Status: error")
                step_flag = 0

        except Exception:
            print("- Internet Connection Status: error")
            step_flag = 0

        if step_flag == 1:
            try:
                browser.get(paypal_url)
                false_flag = 0
                email_input_box = '//input[@id="email"]'
                email_input_box_flag = explicit_wait(
                    browser, "VOEL", [email_input_box, "XPath"], 10, False)
                if email_input_box_flag:
                    false_flag = 0

                else:
                    false_flag = 1

                price_str = '//span[@class="ltrDisplay"]'
                price_str_flag = explicit_wait(
                    browser, "VOEL", [price_str, "XPath"], 10, False)
                current_time = get_time()

                if price_str_flag:
                    false_flag = 0

                else:
                    false_flag = 1

                if false_flag == 0:
                    print("Paypal is working...")
                    paypal_status = 1

                elif false_flag == 1:
                    print("Paypal doesn't work...")
                    paypal_status = -1

                dec_num += 1

                cursor.execute(
                    'UPDATE paypal_info set paypal_status=%s, py_status=1, py_time=%s, dec_num=%s where id=%s', (
                        paypal_status, current_time, dec_num, paypal_id))
                conn.commit()

                if paypal_status == 1 or dec_num == 3:
                    if dec_num == 3:
                        print('More than 3 times, send messages!')

                    php_status = 0
                    post_info = {}
                    post_info["paypal_email"] = paypal_email
                    post_info["status"] = paypal_status
                    post_info["time"] = get_time()
                    post2pp_system(conn, cursor, paypal_id, post_info, sys)

            except:
                try:
                    os.popen('taskkill /f /im firefox.exe')
                except:
                    pass

    else:
        pass

    browser.quit()
    time.sleep(1)
    try:
        os.popen('taskkill /f /im firefox.exe')
    except:
        pass


def post2pp_system(conn, cursor, paypal_id, post_info, sys):
    post_info = json.dumps(post_info)
    post_info = post_info.replace('"', r'\"')
    new_post_info = '"' + post_info + '"'
    new_post_data = '[' + new_post_info + ']'
    try:
        r = requests.post(
            "http://%s/api?user=root&word=root&data=%s" % (sys, new_post_data))
        r_json = json.loads(r.text)

        if r_json['status'] == 'success':
            print('Requests success!')
            php_status = 1

        else:
            php_status = -1

    except Exception:
        php_status = -1

    cursor.execute('UPDATE paypal_info set php_status=%s where id=%s', (
        php_status, paypal_id))
    conn.commit()


def get_time():
    current_time = (datetime.datetime.utcnow() +
                    datetime.timedelta(hours=8)).strftime("%Y-%m-%d %H:%M:%S")

    return current_time


def get_date():
    current_date = (datetime.datetime.utcnow() +
                    datetime.timedelta(hours=8)).strftime("%Y-%m-%d")

    return current_date


def refresh_sessions():
    r = requests.post('http://127.0.0.1:22999/api/refresh_sessions/24000')

    r = requests.get('http://127.0.0.1:22999/api/proxy_status/24000')
    port_status = r.json()
    if port_status['status'].lower() == 'OK'.lower():
        print('Proxy session is refresh!')
        return True

    else:
        return False


def explicit_wait(browser, track, ec_params, timeout=35, notify=True):
    if not isinstance(ec_params, list):
        ec_params = [ec_params]

    # find condition according to the tracks
    if track == "VOEL":
        elem_address, find_method = ec_params
        ec_name = "visibility of element located"

        find_by = (By.XPATH
                   if find_method == "XPath"
                   else By.CSS_SELECTOR
                   if find_method == "CSS"
                   else By.CLASS_NAME)
        locator = (find_by, elem_address)
        condition = EC.visibility_of_element_located(locator)

    elif track == "TC":
        expect_in_title = ec_params[0]
        ec_name = "title contains '{}' string".format(expect_in_title)

        condition = EC.title_contains(expect_in_title)

    elif track == "PFL":
        ec_name = "page fully loaded"

        def condition(browser): return browser.execute_script(
            "return document.readyState"
        ) in ["complete" or "loaded"]

    elif track == "SO":
        ec_name = "staleness of"
        element = ec_params[0]
        condition = EC.staleness_of(element)

    # generic wait block
    try:
        wait = WebDriverWait(browser, timeout)
        result = wait.until(condition)

    except:
        if notify is True:
            print(
                "Timed out with failure while explicitly waiting until {}!\n"
                .format(ec_name))
        return False

    return result


def modify_post_form(paypal_email, price, post_form_path):
    email_str = '<input type="hidden" name="business" value="%s">' % paypal_email
    price_str = '<input type="hidden" name="amount" value="%s">' % str(price)

    with open(post_form_path, 'r', encoding='utf-8') as f1, open('%s.bak' % post_form_path, 'w', encoding='utf-8') as f2:
        for line in f1:
            if 'name="business"' in line:
                line = re.sub(
                    r'<input type="hidden" name="business" value=".*">', email_str, line)
            if 'name="amount"' in line:
                line = re.sub(
                    r'<input type="hidden" name="amount" value=".*">', price_str, line)

            f2.writelines(line)

    os.remove(post_form_path)
    os.rename('%s.bak' % post_form_path, post_form_path)


if __name__ == '__main__':
    main()