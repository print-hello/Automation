import time
import selenium
from util import explicit_wait
from receiveEmail import get_confirm_url


def login_yahoo(driver, email, email_pwd, paypal_pwd, step_flag, paypal_type):
    time.sleep(5)
    paypal_confirm_url = get_confirm_email(email, email_pwd)
    if not paypal_confirm_url and paypal_type == 1:
        print('Not email url, Send again!')
        paypal_confirm_url = paypal_personal_send_email_again(driver, step_flag)
    elif not paypal_confirm_url and paypal_type == 2:
        print('Not email url, Send again!')
        paypal_confirm_url = paypal_here_send_email_again(driver, step_flag)
    if paypal_confirm_url:
        js = 'window.open("%s");' % paypal_confirm_url
        driver.execute_script(js)
        windows = driver.window_handles
        # Gets the new page handle
        driver.switch_to.window(windows[1])
        time.sleep(3)
        step_flag = activate(driver, email, paypal_pwd, step_flag)
    else:
        step_flag = 0

    return step_flag


def paypal_personal_send_email_again(driver, step_flag):
    print('Send email again!')
    try:
        driver.find_element_by_xpath('//div[@class="myAccount"]/a').click()
        time.sleep(3)
    except:
        pass
    email_flag_XP = '//a[@data-name="confirm_your_email"]'
    email_flag_exist = explicit_wait(driver, "VOEL", [email_flag_XP, "XPath"], 30, False)
    if email_flag_exist:
        email_flag = driver.find_element_by_xpath(email_flag_XP)
        (ActionChains(driver)
         .move_to_element(email_flag)
         .click()
         .perform())

        click_send_button_XP = '//button[@id="js_unconfirmedEmail"]'
        click_send_button_flag = explicit_wait(driver, "VOEL", [click_send_button_XP, "XPath"], 30, False)
        if click_send_button_flag:
            click_send_button = driver.find_element_by_xpath(click_send_button_XP)
            (ActionChains(driver)
             .move_to_element(click_send_button)
             .click()
             .perform())
        else:
            driver.refresh()
            click_send_button_XP = '//button[@id="js_unconfirmedEmail"]'
            click_send_button_flag = explicit_wait(driver, "VOEL", [click_send_button_XP, "XPath"], 30, False)
            if click_send_button_flag:
                click_send_button = driver.find_element_by_xpath(click_send_button_XP)
                (ActionChains(driver)
                 .move_to_element(click_send_button)
                 .click()
                 .perform())
            else:
                step_flag = 0
        if step_flag == 1:
            time.sleep(10)
            paypal_confirm_url = get_confirm_email(email, email_pwd)
    else:
        step_flag = 0

    return paypal_confirm_url


def paypal_here_send_email_again(driver, step_flag):
    driver.get('https://www.paypal.com/businessprofile/settings/email')
    email_edit_XP = '//span[@class="links"]//a[1]'
    email_edit_flag = explicit_wait(driver, "VOEL", [email_edit_XP, "XPath"], 10, False)
    if email_edit_flag:
        driver.find_element_by_xpath(email_edit_XP).click()
        email_confirm_XP = '//a[@class="confirm"]'
        email_confirm_flag = explicit_wait(driver, "VOEL", [email_confirm_XP, "XPath"], 10, False)
        if email_confirm_flag:
            driver.find_element_by_xpath(email_confirm_XP).click()
            time.sleep(5)
            paypal_confirm_url = get_confirm_email(email, email_pwd)
        step_flag = 0
    else:
        step_flag = 0

    return paypal_confirm_url


def login_gmail(driver, conn, email, email_pwd, paypal_pwd, recovery_email):
    js = 'window.open("https://accounts.google.com/ServiceLogin?continue=https%3A%2F%2Fmail.google.com%2Fmail%2F&service=mail&sacu=1&rip=1");'
    driver.execute_script(js)
    windows = driver.window_handles
    # Gets the new page handle
    driver.switch_to.window(windows[1])
    time.sleep(3)
    if driver.page_source.find('This site can’t be reached') > -1:
        print('Net Error!')
        driver.refence()
        time.sleep(5)
    try:
        # element = WebDriverWait(driver, 10).until(
        #     EC.presence_of_element_located((By.ID, 'identifierId')))
        # element.send_keys(email)
        driver.find_element_by_id('identifierId').send_keys(email)
        time.sleep(1)
        driver.find_element_by_id('identifierNext').click()
        time.sleep(5)
    except Exception as e:
        pass
    try:
        driver.find_element_by_name('password').send_keys(email_pwd)
        driver.find_element_by_id('passwordNext').click()
        time.sleep(3)
        error_info = driver.find_element_by_xpath(
            '//div[@class="GQ8Pzc"]')
        if error_info:
            print('Password error!')
    except Exception as e:
        pass
    try:
        time.sleep(5)
        element1 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//li[@class="C5uAFc"]/div')))
        element1.click()
        time.sleep(3)
        element2 = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'identifierId')))
        element2.send_keys(recovery_email)
        driver.find_element_by_xpath(
            '//div[@class="qhFLie"]/div').click()
    except Exception as e:
        pass
    try:
        element3 = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="N4lOwd"]')))
        time.sleep(3)
        driver.find_element_by_xpath(
            '//div[@class="yKBrKe"]/div').click()
    except Exception as e:
        pass
    try:
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="tbyFuf"]//a[2]')))
        element.click()
        time.sleep(3)
    except Exception as e:
        pass
    try:
        driver.find_element_by_xpath(
            '//button[@name="welcome_dialog_next"]').click()
        time.sleep(2)
        driver.find_element_by_xpath('//button[@name="ok"]').click()
        time.sleep(2)
    except:
        pass
    try:
        email_element = driver.find_elements_by_xpath(
            '//div[@class="yW"]//span[@name="service@paypal.com"]')
        email_element[0].click()
        time.sleep(3)
    except:
        pass
    while True:
        link_element = ''
        try:
            link_element = driver.find_element_by_xpath(
                '//a[text()="Confirm My Email"]')
        except:
            pass
        if link_element:
            link_element.click()
            time.sleep(5)
            break
    windows = driver.window_handles
    # Gets the new page handle
    driver.switch_to.window(windows[2])
    time.sleep(3)
    activate(driver, email, paypal_pwd, created_flag)


def activate(driver, email, paypal_pwd, step_flag):
    input_password_XP = '//input[@id="password"]'
    input_password_flag = explicit_wait(
        driver, "VOEL", [input_password_XP, "XPath"], 30, False)
    if input_password_flag:
        time.sleep(8)
        driver.find_element_by_xpath(input_password_XP).send_keys(paypal_pwd)
        time.sleep(1)
        driver.find_element_by_xpath('//button[@id="btnLogin"]').click()
        time.sleep(1)
        not_now_button_XP = '//p[@class="secondaryLink"]/a'
        not_now_button_flag = explicit_wait(
            driver, "VOEL", [not_now_button_XP, "XPath"], 10, False)
        if not_now_button_flag:
            not_now_button = driver.find_element_by_xpath(not_now_button_XP)
            (ActionChains(driver)
             .move_to_element(not_now_button)
             .click()
             .perform())
        else:
            try_times = 0
            while True:
                msg_code = ''
                try:
                    msg_code = driver.find_element_by_xpath(
                        '//form/div[1]/p').text
                except:
                    pass
                if msg_code == 'Your email is all set!':
                    # Not now
                    driver.find_element_by_xpath(
                        '//button[@id="/appData/action"]').click()
                    break
                else:
                    try_times += 1
                    time.sleep(3)
                if try_times > 5:
                    step_flag = 0
                    break
    else:
        step_flag = 0

    return step_flag