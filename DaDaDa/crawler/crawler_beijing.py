import math

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import html2text
import requests
import json
import time
import pandas as pd

if __name__ == '__main__':
    options = webdriver.ChromeOptions()
    # the local position of chrome
    options.binary_location = "your_local_chrome"
    driver = webdriver.Chrome(options=options)
    url = 'https://webs.bjidex.com/#/login'
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'input#username')))


    username = driver.find_element(By.CSS_SELECTOR, 'input#username')
    password = driver.find_element(By.CSS_SELECTOR, 'input#password')

    username.send_keys("username")
    password.send_keys("password")

    time.sleep(5)
    login_button = driver.find_element(By.CSS_SELECTOR, 'button.login-btn')
    login_button.click()

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.index_btns__2TayV')))

    item_num = driver.find_element(By.CSS_SELECTOR, 'div.index_btns__2TayV>div:nth-child(2)>span').text
    print(item_num)
    item_num = int(item_num)

    result = []
    page_num = math.ceil(item_num / 10)
    for i in range(item_num):
        cur_num = i + 1
        page_num = math.ceil(cur_num / 10)
        if page_num > 1:
            jump_page = driver.find_element(By.CSS_SELECTOR, 'div.icos-ant-pagination-options-quick-jumper input')
            jump_page.send_keys(page_num)
            jump_page.send_keys(Keys.ENTER)
            time.sleep(1)

        # forward
        item_list = driver.find_elements(By.CSS_SELECTOR, 'div.index_detailbtn__cy0GH')
        item = item_list[i % 10]
        item.click()
        time.sleep(2)
        # get the main content

        current_url = driver.current_url
        title = driver.find_element(By.CSS_SELECTOR, 'span.detail_name__1sJwp').text
        description = driver.find_element(By.CSS_SELECTOR, 'div.detail_desc__SNzVf').text
        area = driver.find_element(By.CSS_SELECTOR, 'div.detail_field__3fZOc>div:nth-child(1)>span:nth-child(2)').text
        type = driver.find_element(By.CSS_SELECTOR, 'div.detail_field__3fZOc>div:nth-child(2)>span:nth-child(2)').text
        offer_type = driver.find_element(By.CSS_SELECTOR, 'div.detail_field__3fZOc>div:nth-child(3)>span:nth-child(2)').text
        try:
            price = driver.find_element(By.CSS_SELECTOR, 'span.detail_refprice__1j2Gr').text
        except Exception:
            price = ""
            pass
        company_name = driver.find_element(By.CSS_SELECTOR, 'div.detail_compty__1jbIs>span').text


        h = html2text.HTML2Text()

        element = driver.find_element(By.CSS_SELECTOR, 'div.icos-ant-tabs-tab-btn:first-child')
        id = element.get_attribute('id')
        # id = 'rc-tabs-x-tab-x', we need 'x', x is a num
        id_num = id.split('-')[2]

        button_prefix = 'rc-tabs-' + id_num +  '-tab-'
        # print(button_prefix)
        info_prefix = 'rc-tabs-' + id_num + '-panel-'
        # print(info_prefix)

        try:
            detail_button = driver.find_element(By.CSS_SELECTOR, 'div#' + button_prefix + '1')
            detail_button.click()
            time.sleep(1)

            detail = driver.find_element(By.CSS_SELECTOR, 'div#' + info_prefix + '1')
            # get the original html
            detail_html = detail.get_attribute('innerHTML')
            # convert html to text
            detail = h.handle(detail_html)
        except Exception:
            detail = ""
            pass

        try:
            data_item_button = driver.find_element(By.CSS_SELECTOR, 'div#' + button_prefix + '2')
            data_item_button.click()
            time.sleep(1)

            data_item = driver.find_element(By.CSS_SELECTOR, 'div#' + info_prefix + '2')
            dimension = data_item.find_elements(By.CSS_SELECTOR, 'tbody>tr')
            dimension = len(dimension) - 1
            # data_item_html = data_item.get_attribute('innerHTML')
            # data_item = h.handle(data_item_html)
        except Exception:
            data_item = ""
            pass

        try:
            limit_button = driver.find_element(By.CSS_SELECTOR, 'div#' + button_prefix + '3')
            limit_button.click()
            time.sleep(1)

            limit = driver.find_element(By.CSS_SELECTOR, 'div#' + info_prefix + '3')
            limit_html = limit.get_attribute('innerHTML')
            limit = h.handle(limit_html)
        except Exception:
            limit = ""
            pass

        result.append([current_url, title, description, area, type, offer_type, price, company_name, detail, dimension, limit])
        # print(title, description, area, type, offer_type, price, detail, data_item, limit, directory)
        # api_url = 'https://webs.bjidex.com/api/dstp/data-asset-server/data-product/get-data-product?' + current_url.split('?')[1]
        # print(api_url)
        #
        # response = requests.get(api_url, verify=False)
        # data = response.json()
        # print(data)

        # backward
        driver.back()
        time.sleep(1)

    result = pd.DataFrame(result, columns=['url', 'title', 'description', 'area', 'type', 'offer_type', 'price', 'company_name', 'detail', 'dimension', 'limit'])
    result.to_csv('./beijing.csv', index=False)







