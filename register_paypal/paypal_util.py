from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
import win32api
import win32gui
import win32con
import time
from util import explicit_wait


def paypal_personal_page_one():
    input_firstname_XP = '//input[@id="paypalAccountData_firstName"]'
    input_firstname_flag = explicit_wait(
        driver, "VOEL", [input_firstname_XP, "XPath"], 20, False)
    if input_firstname_flag:
        driver.find_element_by_xpath(input_firstname_XP).send_keys(firstname)
        time.sleep(1)
        driver.find_element_by_id(
            'paypalAccountData_lastName').send_keys(lastname)
        time.sleep(1)
        driver.find_element_by_id(
            'paypalAccountData_email').send_keys(email)
        time.sleep(1)
        driver.find_element_by_id(
            'paypalAccountData_password').send_keys(paypal_pwd)
        time.sleep(2)
        # 确认密码
        try:
            driver.find_element_by_id(
                'paypalAccountData_confirmPassword').send_keys(paypal_pwd)
            time.sleep(1)
        except:
            pass
        try:
            error_code = driver.find_element_by_xpath(
                '//form//p/span').text
            print(error_code)
        except:
            pass
        if error_code == 'It looks like you already signed up. Log in to your account.':
            print('Already signed up')
            sql = 'UPDATE email_info set created_paypal_account=-1 where email=%s'
            commit_sql(conn, sql, email)
            step_flag = 0
        else:
            driver.find_element_by_xpath(
                '//div[@class="btnGrp"]/button').click()
            step_flag = 1
    else:
        step_flag = 0

    return step_flag


def paypal_personal_page_two():
    input_address_XP = '//div[@data-label-content="Street address"]//input'
    input_address_flag = explicit_wait(
        driver, "VOEL", [input_address_XP, "XPath"], 20, False)
    if input_address_flag:
        driver.find_element_by_xpath(input_address_XP).send_keys(address)
        time.sleep(1)
        driver.find_element_by_id(
            'paypalAccountData_city').send_keys(city)
        time.sleep(1)
        Select(driver.find_element_by_id(
            "paypalAccountData_state")).select_by_value(state)
        time.sleep(1)
        driver.find_element_by_id(
            'paypalAccountData_zip').send_keys(zip_num)
        time.sleep(1)
        driver.find_element_by_id(
            'paypalAccountData_phone').send_keys(phone_num)
        time.sleep(1)
        driver.find_element_by_xpath(
            '//div[@class="signupCheckBox"]//label').click()
        time.sleep(1)
        driver.find_element_by_xpath(
            '//div[@class="btnGrp"]/button').click()
        time.sleep(5)
        info_error = ''
        try:
            info_error = driver.find_element_by_xpath(
                '//div[@class="notification"]//span').text
        except:
            pass
        if info_error:
            step_flag = 0
            print('Info Error!')
            sql = 'UPDATE email_info set emailIsUsed=9 where email=%s'
            commit_sql(conn, sql, email)
        else:
            step_flag = 1
            sql = 'UPDATE email_info set paypal_pwd=%s, created_paypal_account=1 where email=%s'
            commit_sql(conn, sql, (paypal_pwd, email))
            created_flag = 1
            try_set_up = 0
            while True:
                set_up_profile = ''
                try:
                    set_up_profile = driver.find_element_by_xpath(
                        '//a[@name="notnow"]')
                except:
                    pass
                if set_up_profile:
                    set_up_profile.click()
                    time.sleep(3)
                    break
                else:
                    try_set_up += 1
                    time.sleep(3)
                if try_set_up > 2:
                    break
    else:
        step_flag = 0


def bind_card_in_normal_process():
    # 绑卡
    # if created_flag == 1 and step_flag == 1:
    #     if login_separately == 1:
    #         login_flag = login_paypal(driver, email, paypal_pwd)
    #         if login_flag == 1:
    #             created_flag = link_card(
    #                 driver, conn, email, card_num, expiration_date, card_csc)
    #             login_separately = 0
    #     else:
    next_step_page_XP = '//div[@class="formLink "]//button'
    next_step_page_flag = explicit_wait(
        driver, "VOEL", [next_step_page_XP, "XPath"], 15, False)
    if next_step_page_flag:
        next_step_page = driver.find_element_by_xpath(next_step_page_XP)
        (ActionChains(driver)
         .move_to_element(next_step_page)
         .click()
         .perform())
        step_flag = 1
    else:
        step_flag = 0

    if step_flag == 1:
        input_cardNumber_XP = '//input[@id="cardData_cardNumber"]'
        input_cardNumber_flag = explicit_wait(
            driver, "VOEL", [input_cardNumber_XP, "XPath"], 15, False)
        if input_cardNumber_flag:
            driver.find_element_by_xpath(
                input_cardNumber_XP).send_keys(card_num)
            time.sleep(1)
            driver.find_element_by_id(
                'cardData_expiryDate').send_keys(expiration_date)
            time.sleep(1)
            driver.find_element_by_id(
                'cardData_csc').send_keys(card_csc)
            time.sleep(1)
            driver.find_element_by_xpath(
                '//div[@class="btnGrp"]/button').click()
            time.sleep(5)
            while True:
                end_flag = ''
                try:
                    end_flag = driver.find_element_by_xpath(
                        '//form//h1').text
                    print(end_flag)
                except:
                    pass
                if end_flag == 'Your account’s ready to use! Shop, send money, and more with PayPal':
                    sql = 'UPDATE email_info set created_paypal_account=2 where email=%s'
                    commit_sql(conn, sql, email)
                    time.sleep(1)
                    created_flag = 2
                    print('Successful!')
                    step_flag = 1
                    break
                else:
                    time.sleep(3)
        else:
            step_flag = 0


def link_card(driver, conn, email, card_num, expiration_date, card_csc, created_flag=1):

    link_button_XP = '//a[@id="bankCardLinkBankOrCard"]'
    explicit_wait(driver, "VOEL", [link_button_XP, "XPath"])
    link_button = driver.find_element_by_xpath(link_button_XP)
    (ActionChains(driver)
     .move_to_element(link_button)
     .click()
     .perform())

    link_card_XP = '//a[@data-name="addCard"]'
    explicit_wait(driver, "VOEL", [link_card_XP, "XPath"])
    link_card = driver.find_element_by_xpath(link_card_XP)
    (ActionChains(driver)
     .move_to_element(link_card)
     .click()
     .perform())

    next_element_XP = '//a[@data-name="linkManually"]'
    explicit_wait(driver, "VOEL", [next_element_XP, "XPath"])
    next_element = driver.find_element_by_xpath(next_element_XP)
    (ActionChains(driver)
     .move_to_element(next_element)
     .click()
     .perform())

    cardNumber_XP = '//input[@id="cardNumber"]'
    explicit_wait(driver, "VOEL", [cardNumber_XP, "XPath"])
    driver.find_element_by_xpath(cardNumber_XP).send_keys(card_num)
    time.sleep(1)
    driver.find_element_by_id('expDate').send_keys(expiration_date)
    time.sleep(1)
    driver.find_element_by_id('verificationCode').send_keys(card_csc)
    time.sleep(1)
    driver.find_element_by_name('detailsSubmit').click()
    time.sleep(5)
    try:
        driver.find_element_by_xpath(
            '//a[@data-name="addCardDone"]').click()
        time.sleep(2)
        sql = 'UPDATE email_info set created_paypal_account=2 where email=%s'
        commit_sql(conn, sql, email)
        time.sleep(1)
        created_flag = 2
        driver.find_element_by_xpath('//a[text()="Summary"]').click()
        time.sleep(3)
    except:
        pass

    return created_flag


def confirm_identity(conn, driver, email, confirm_info_id, confirm_user, confirm_pwd, routing_number, account_number, confirm_type):
    next_step = 1
    search_bank_link_text = 0
    accountNumberLast4 = account_number[-4:]
    click_bank_link_XP = '//a[@id="bankCardLinkBankOrCard"]'
    explicit_wait(driver, "VOEL", [click_bank_link_XP, "XPath"])
    click_bank_link = driver.find_element_by_xpath(click_bank_link_XP)
    (ActionChains(driver)
     .move_to_element(click_bank_link)
     .click()
     .perform())

    add_bank_link_XP = '//a[@data-name="addBank"]'
    explicit_wait(driver, "VOEL", [add_bank_link_XP, "XPath"])
    add_bank_link = driver.find_element_by_xpath(add_bank_link_XP)
    (ActionChains(driver)
     .move_to_element(add_bank_link)
     .click()
     .perform())

    click_bank_logo_XP = '//a[@name="manualAddBank"]'
    explicit_wait(driver, "VOEL", [click_bank_logo_XP, "XPath"])
    click_bank_logo = driver.find_element_by_xpath(click_bank_logo_XP)
    (ActionChains(driver)
     .move_to_element(click_bank_logo)
     .click()
     .perform())

    input_routing_XP = '//input[@name="routingNumberGroup"]'
    explicit_wait(driver, "VOEL", [input_routing_XP, "XPath"])
    if confirm_type == 'Savings':
        time.sleep(3)
        # driver.find_element_by_xpath('//label[@for="savingsRadioBtn"]').click()
        driver.find_element_by_xpath('//input[@id="savingsRadioBtn"]').click()
    time.sleep(2)
    driver.find_element_by_xpath(input_routing_XP).send_keys(routing_number)
    time.sleep(1)

    # Account Number
    driver.find_element_by_name('accountNumberInput').send_keys(account_number)
    time.sleep(1)
    add_bank_button_XP = '//button[@name="addBank"]'
    explicit_wait(driver, "VOEL", [add_bank_button_XP, "XPath"])
    add_bank_button = driver.find_element_by_xpath(add_bank_button_XP)
    (ActionChains(driver)
     .move_to_element(add_bank_button)
     .click()
     .perform())
    time.sleep(5)
    try:
        driver.find_element_by_xpath(add_bank_button_XP).click()
    except:
        pass
    security_check = ''
    error_msg = ''
    try:
        security_check = driver.find_element_by_xpath(
            '//div[@class="challengesSection"]//h1').text
    except:
        pass
    time.sleep(2)
    try:
        error_msg = driver.find_element_by_xpath('//form/div[1]/p').text
    except:
        pass
    if security_check == 'Quick security check':
        sql = 'UPDATE email_info set confirm_identity=9 where email=%s'
        commit_sql(conn, sql, email)
        next_step = 0
    elif error_msg:
        try:
            driver.find_element_by_name('addBank').click()
        except:
            pass
    if next_step == 1:
        pending_confirm_button_XP = '//button[@name="pendingConfirmBank"]'
        pending_confirm_button_state = explicit_wait(
            driver, "VOEL", [pending_confirm_button_XP, "XPath"], 10, False)
        if pending_confirm_button_state:
            pending_confirm_button = driver.find_element_by_xpath(
                pending_confirm_button_XP)
            (ActionChains(driver)
             .move_to_element(pending_confirm_button)
             .click()
             .perform())

            view_bank_button_XP = '//a[@data-name="viewBank"]'
            explicit_wait(driver, "VOEL", [view_bank_button_XP, "XPath"])
            view_bank_button = driver.find_element_by_xpath(
                view_bank_button_XP)
            (ActionChains(driver)
             .move_to_element(view_bank_button)
             .click()
             .perform())

            confirm_instantly_XP = '//a[@name="confirmInstantly"]'
            explicit_wait(driver, "VOEL", [confirm_instantly_XP, "XPath"])
            confirm_instantly = driver.find_element_by_xpath(
                confirm_instantly_XP)
            (ActionChains(driver)
             .move_to_element(confirm_instantly)
             .click()
             .perform())
        else:
            user_pwd_confirm_XP = '//div[@class="confirmBank-confirmInstantly"]/a'
            user_pwd_confirm_flag = explicit_wait(
                driver, "VOEL", [user_pwd_confirm_XP, "XPath"], 5, False)
            if user_pwd_confirm_flag:
                user_pwd_confirm = driver.find_element_by_xpath(
                    user_pwd_confirm_XP)
                (ActionChains(driver)
                 .move_to_element(user_pwd_confirm)
                 .click()
                 .perform())

        input_user_XP = '//form/div/div[1]/input'
        input_user_flag = explicit_wait(
            driver, "VOEL", [input_user_XP, "XPath"], 30, False)
        if input_user_flag:
            driver.find_element_by_xpath(input_user_XP).send_keys(confirm_user)
            time.sleep(1)
            driver.find_element_by_xpath(
                '//form/div/div[3]/input').send_keys(confirm_pwd)
            time.sleep(1)
            driver.find_element_by_name('continue').click()
        else:
            next_step = 0

        if next_step == 1:
            choice_account_number_XP = '//label[@for="accountNumber-%s"]' % accountNumberLast4
            confirm_last_step = explicit_wait(
                driver, "VOEL", [choice_account_number_XP, "XPath"], 150, False)
            if confirm_last_step:
                choice_account_number = driver.find_element_by_xpath(
                    choice_account_number_XP)
                (ActionChains(driver)
                 .move_to_element(choice_account_number)
                 .click()
                 .perform())
                time.sleep(1)
                driver.find_element_by_name('continue').click()
                search_bank_link_text = 1
            else:
                try:
                    driver.find_element_by_name('continue').click()
                except:
                    pass
                choice_account_number_XP = '//label[@for="accountNumber-%s"]' % accountNumberLast4
                confirm_last_step = explicit_wait(
                    driver, "VOEL", [choice_account_number_XP, "XPath"], 150, False)
                if confirm_last_step:
                    choice_account_number = driver.find_element_by_xpath(
                        choice_account_number_XP)
                    (ActionChains(driver)
                     .move_to_element(choice_account_number)
                     .click()
                     .perform())
                    time.sleep(1)
                    try:
                        driver.find_element_by_name('continue').click()
                        search_bank_link_text = 1
                    except:
                        pass
        # print(search_bank_link_text)
        if search_bank_link_text == 1:
            confirm_success_XP = '//h2[text()="Bank linked!"]'
            success_flag = explicit_wait(
                driver, "VOEL", [confirm_success_XP, "XPath"], 20, False)
            if success_flag:
                sql = 'UPDATE email_info set confirm_identity=1, confirm_type=%s, confirmAccountNumber=%s where email=%s'
                commit_sql(conn, sql, (confirm_type, account_number, email))
                print('Confirm Successsful!')
                sql = 'UPDATE paypal_confirm_info set used=2 where id=%s'
                commit_sql(conn, sql, confirm_info_id)
            # else:
                # print('Change back to the state!')
                # sql = 'UPDATE paypal_confirm_info set used=0 where id=%s'
                # commit_sql(conn, sql, confirm_info_id)


def paypal_here_page_one(driver,
                         step_flag,
                         firstname,
                         lastname,
                         email,
                         paypal_pwd, 
                         login_with_input_box=False):
    if login_with_input_box:
        sign_or_log_XP = '//button[@id="pphLoginButton"]'
        step_flag = 2
    else:
        sign_or_log_XP = '//a[text()="Sign Up"]'
    sign_or_log_flag = explicit_wait(
        driver, "VOEL", [sign_or_log_XP, "XPath"], 15, False)
    if sign_or_log_flag:
        driver.find_element_by_xpath(sign_or_log_XP).click()
        if step_flag == 1:
            input_firstname_XP = '//input[@id="firstName"]'
            input_firstname_flag = explicit_wait(
                driver, "VOEL", [input_firstname_XP, "XPath"], 15, False)
            if input_firstname_flag:
                driver.find_element_by_xpath(
                    input_firstname_XP).send_keys(firstname)
                time.sleep(1)
                driver.find_element_by_xpath(
                    '//input[@id="lastName"]').send_keys(lastname)
                time.sleep(1)
                driver.find_element_by_xpath(
                    '//input[@id="email"]').send_keys(email)
                time.sleep(1)
                driver.find_element_by_xpath(
                    '//input[@id="password"]').send_keys(paypal_pwd)
                time.sleep(1)
                driver.find_element_by_xpath(
                    '//button[@id="continueButton"]').click()
            else:
                step_flag = 0
    else:
        step_flag = 0

    return step_flag


# 选择 Individual 页面
def paypal_here_page_two(driver,
                         name,
                         address,
                         city,
                         full_state,
                         zip_num,
                         birthdate,
                         phone_num,
                         ssn):
    choice_individual_XP = '//form//div[@id="businessType"]/div'
    choice_individual_flag = explicit_wait(
        driver, "VOEL", [choice_individual_XP, "XPath"], 10, False)
    if choice_individual_flag:
        choice_individual = driver.find_element_by_xpath(choice_individual_XP)
        (ActionChains(driver)
         .move_to_element(choice_individual)
         .click()
         .perform())
        time.sleep(2)
        win32api.keybd_event(40, 0, 0, 0)
        win32api.keybd_event(40, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(1)
        win32api.keybd_event(13, 0, 0, 0)
        win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(1)
        input_business_name_XP = '//input[@id="businessLegalName"]'
        input_business_name_flag = explicit_wait(
            driver, "VOEL", [input_business_name_XP, "XPath"], 5, False)
        if input_business_name_flag:
            driver.find_element_by_xpath(
                input_business_name_XP).send_keys(name)
            time.sleep(1)
            driver.find_element_by_xpath(
                '//input[@id="merchantCategoryCode"]').send_keys("women")
            win32api.keybd_event(40, 0, 0, 0)
            win32api.keybd_event(40, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(1)
            win32api.keybd_event(13, 0, 0, 0)
            win32api.keybd_event(13, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(1)
            # driver.find_element_by_xpath(
            #     '//form//div[@id="businessAverageMonthlyVolume"]').click()
            # time.sleep(1)
            # driver.find_element_by_xpath(
            #     '//ul[@id="businessAverageMonthlyVolume-menu"]//li[text()="Up to USD $4,999"]').click()
            # time.sleep(1)
            driver.find_element_by_xpath(
                '//input[@label="Street address"]').send_keys(address)
            time.sleep(1)
            driver.find_element_by_xpath(
                '//input[@label="City"]').send_keys(city)
            time.sleep(1)
            driver.find_element_by_xpath(
                '//*[@id="homeAddress"]/div[4]/div').click()
            time.sleep(1)
            driver.find_element_by_xpath(
                '//li[text()="%s"]' % full_state).click()
            time.sleep(1)
            driver.find_element_by_xpath(
                '//input[@label="ZIP code"]').send_keys(zip_num)
            time.sleep(1)
            driver.find_element_by_xpath(
                '//input[@id="dateOfBirth"]').send_keys(birthdate)
            time.sleep(1)
            driver.find_element_by_xpath(
                '//input[@id="mobilePhoneNumber"]').send_keys(phone_num)
            time.sleep(1)
            driver.find_element_by_xpath('//input[@id="ssn"]').send_keys(ssn)
            time.sleep(1)
            driver.find_element_by_xpath(
                '//label[input[@id="agreementAccepted"]]').click()
            time.sleep(1)
            driver.find_element_by_xpath(
                '//button[@id="newUserSubmitButton"]').click()
            here_success_text_XP = '''//p[text()="You're ready to go."]'''
            here_success_text_flag = explicit_wait(
                driver, "VOEL", [here_success_text_XP, "XPath"], 8, False)
            if here_success_text_flag:
                here_success = 1
            else:
                here_false_XP = '//a[text()="Summary"]'
                here_false_flag = explicit_wait(
                    driver, "VOEL", [here_false_XP, "XPath"], 3, False)
                if here_false_flag:
                    here_success = 0
        else:
            here_success = -1
    else:
        here_success = -1

    return here_success