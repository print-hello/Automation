import time
import json
from util import explicit_wait


def login(driver, login_url, account_id, email, pwd, cookie):
    # if cookie:
    #     login_state = cookie_login(driver, login_url, cookie)
    # else:
    #     login_state = 0

    # if login_state == 0:
    driver.get(login_url)
    if driver.page_source.find('This site can’t be reached') > -1:
        login_state = 2
        print('Net error!')
        return login_state
    elif driver.page_source.find("This page isn’t working") > -1:
        login_state = 2
        print('Net error!')
        return login_state
    else:
        input_email_XP = '//input[@id="email"]'
        input_email_flag = explicit_wait(driver, "VOEL", [input_email_XP, "XPath"], 15, False)
        if input_email_flag:
            driver.find_element_by_xpath(input_email_XP).send_keys(email)
            time.sleep(1)
            driver.find_element_by_name("password").send_keys(pwd)
            time.sleep(1)
            driver.find_element_by_xpath("//form//button").click()
            # login_success_XP = '//div[@class="pinWrapper"]'
            login_success_XP = '//div[text()="Home"]'
            login_success_flag = explicit_wait(driver, "VOEL", [login_success_XP, "XPath"], 15, False)
            if login_success_flag:
                login_state = 11
            else:
                reset_passwd_XP = '//button[@aria-label="Reset password"]'
                reset_passwd_flag = explicit_wait(driver, "VOEL", [reset_passwd_XP, "XPath"], 5, False)
                if reset_passwd_flag:
                    print('Error code: 9')
                    login_state = 9
                elif driver.page_source.find('The email you entered does not belong to any account.') > -1:
                    print('Error code: 66')
                    login_state = 66
                elif driver.page_source.find('Your account has been suspended') > -1:
                    print('Error code: 99')
                    login_state = 99
                else:
                    login_state = 0
        else:
            login_state = 0

    return login_state


def cookie_login(driver, login_url, cookie):
    driver.get(login_url)
    print('Cookie login...')
    # clear cookies, To prevent the automatic login to other accounts
    driver.delete_all_cookies()
    time.sleep(2)
    try:
        cookies = json.loads(cookie)
        for coo in cookies:
            coo.pop('domain')
            driver.add_cookie(coo)
        driver.refresh()
    except Exception as e:
        print('The cookies is invalid. You are trying to login')
        login_state = 0
        return login_state

    login_success_XP = '//div[@class="pinWrapper"]'
    login_success_flag = explicit_wait(driver, "VOEL", [login_success_XP, "XPath"], 15, False)
    if login_success_flag:
        login_state = 1
    else:
        login_state = 0

    return login_state


def get_coo(driver):
    cookie = driver.get_cookies()
    cookie = json.dumps(cookie)

    return cookie