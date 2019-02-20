import pymysql
import time
import socket
from selenium import webdriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By


options = webdriver.ChromeOptions()
options.add_argument('disable-infobars')
driver = webdriver.Chrome(chrome_options=options)
driver.maximize_window()
driver.get('https://accounts.google.com')
try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'identifierId')))
    element.send_keys('t3136921@gmail.com')
    driver.find_element_by_id('identifierNext').click()
except Exception as e:
    pass
try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//content//input[@name="password"]')))
    element.send_keys('HE7SPpWjqlzK')
    driver.find_element_by_id('passwordNext').click()
except Exception as e:
    print(e)
try:
    element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="N4lOwd"]')))
    if element.text == 'Protect your account':
        driver.find_elements_by_xpath('//div[@class="yKBrKe"]/div').click()
except Exception as e:
    pass
try:
    element = WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.XPATH, '//h1[@class="sfYUmb"]')))
    driver.find_element_by_xpath('//li[@class="C5uAFc"]/div').click()
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'identifierId')))
    element.send_keys('lee98930@gmail.com')
    driver.find_element_by_xpath('//div[@class="qhFLie"]/div').click()
except Exception as e:
    pass
if driver.page_source.find('Something went wrong') > -1:
    print('error')