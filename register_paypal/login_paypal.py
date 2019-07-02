import time
from selenium import webdriver
from util import explicit_wait


def login_paypal(driver, email, paypal_pwd):
    input_email_XP = '//input[@id="email"]'
    input_email_flag = explicit_wait(
        driver, "VOEL", [input_email_XP, "XPath"], 15, False)
    if input_email_flag:
        driver.find_element_by_xpath(input_email_XP).send_keys(email)
        time.sleep(1)
        try:
            driver.find_element_by_id('btnNext').click()
        except:
            pass
        input_password_XP = '//input[@id="password"]'
        explicit_wait(driver, "VOEL", [input_password_XP, "XPath"])
        driver.find_element_by_xpath(input_password_XP).send_keys(paypal_pwd)
        time.sleep(1)
        driver.find_element_by_id('btnLogin').click()
        time.sleep(3)
        try:
            driver.find_element_by_xpath(
                '//p[@class="secondaryLink"]/a').click()
            time.sleep(3)
        except:
            pass

        home_element_XP = '//a[text()="Summary"]'
        home_element_flag = explicit_wait(
            driver, "VOEL", [home_element_XP, "XPath"], 10, False)
        if home_element_flag:
            login_flag = 1
        else:
            login_flag = 0
    else:
        login_flag = 0

    return login_flag
