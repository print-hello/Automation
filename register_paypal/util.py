from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
import uuid
import os
import re


def explicit_wait(driver, track, ec_params, timeout=35, notify=True):
    if not isinstance(ec_params, list):
        ec_params = [ec_params]

    # find condition according to the tracks
    if track == "VOEL":
        elem_address, find_method = ec_params
        ec_name = "visibility of element located"

        find_by = (By.XPATH if find_method == "XPath" else
                   By.CSS_SELECTOR if find_method == "CSS" else
                   By.CLASS_NAME)
        locator = (find_by, elem_address)
        condition = EC.visibility_of_element_located(locator)

    elif track == "TC":
        expect_in_title = ec_params[0]
        ec_name = "title contains '{}' string".format(expect_in_title)

        condition = EC.title_contains(expect_in_title)

    elif track == "SO":
        ec_name = "staleness of"
        element = ec_params[0]
        condition = EC.staleness_of(element)

    # generic wait block
    try:
        wait = WebDriverWait(driver, timeout)
        result = wait.until(condition)

    except:
        if notify is True:
            print(
                "Timed out with failure while explicitly waiting until {}!\n"
                .format(ec_name))
        return False

    return result


def get_mac():
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    mac_address = ''.join([mac[e:e + 2] for e in range(0, 11, 2)])
    mac_address = mac_address.upper()
    # print(mac_address)

    return mac_address


def modify_port(proxifier_path, proxifier_file):
    filenames = os.listdir(proxifier_path)
    for filename in filenames:
        with open(proxifier_path + '\\' + filename, 'r', encoding='utf-8') as fp:
            info = fp.read()
    port_str = re.search(r'<Port>\d*</Port>', info).group()
    print(port_str)
    with open(proxifier_file, 'r', encoding='utf-8') as f1, open('%s.bak' % proxifier_file, 'w', encoding='utf-8') as f2:
        for line in f1:
            f2.write(re.sub(r'<Port>\d*</Port>', port_str, line))
    os.remove(proxifier_file)
    os.rename('%s.bak' % proxifier_file, proxifier_file)