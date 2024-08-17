import math

import requests
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
    options.binary_location = "E:\chrome\chrome-win64\chrome.exe"
    driver = webdriver.Chrome(options=options)

    # use edge
    # edge_path = r'E:\msedgedriver.exe'

    # options = webdriver.EdgeOptions()
    # options.add_argument('--headless')
    # driver = webdriver.Edge(options=options)
    # driver = webdriver.Edge()

    url = 'https://nidts.chinadep.com/ep-hall?search=&dataType=&type=list&sectorName=&firstSubSectorName=&pageSize=10&pageNum=1&order=&corpus='
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button.btn-next')))
    api_prefix = 'https://nidts.chinadep.com/daep/broker/product/visitor/detail?'
    h = html2text.HTML2Text()
    result = []

    count = 0
    while True:
        item_list = driver.find_elements(By.CSS_SELECTOR, 'div.product-card')
        num = len(item_list)
        for i in range(num):
            count += 1
            temp_list = driver.find_elements(By.CSS_SELECTOR, 'div.product-card')

            try:
            # first move to the element
                ActionChains(driver).move_to_element(temp_list[i]).perform()
                time.sleep(3)
                # click
                detail_button = driver.find_element(By.CSS_SELECTOR, 'div.product-card__mask')
                detail_button.click()
                time.sleep(3)

                cur_url = driver.current_url
                info = driver.find_elements(By.CSS_SELECTOR, 'div.product-pec>div:nth-child(2) div.el-descriptions-item__container')
            except Exception:
                print(count)
                url = 'https://nidts.chinadep.com/ep-hall?search=&dataType=&type=list&sectorName=&firstSubSectorName=&pageSize=10&pageNum=' + str(math.ceil(count / 10)) + '&order=&corpus='
                print(url)
                driver.get(url)
                time.sleep(3)
                continue

            try:
                print(len(info))
                title = list_time = series_name = company_name = industry = data_type = product_type = None
                description = keyword = update_frequency = coverage = storage = storage_incr = dimension = None
                for cur_info in info:
                    label = cur_info.find_element(By.CSS_SELECTOR, 'span.el-descriptions-item__label').text
                    content = cur_info.find_element(By.CSS_SELECTOR, 'span.el-descriptions-item__content').text
                    if label == '产品名称':
                        title = content
                    elif label == '挂牌日期':
                        list_time = content
                    elif label == '系列名称':
                        series_name = content
                    elif label == '供方名称':
                        company_name = content
                    elif label == '应用板块':
                        industry = content
                    elif label == '数据主题':
                        data_type = content
                    elif label == '产品类型':
                        product_type = content
                    elif label == '产品描述':
                        description = content
                    elif label == '关键词':
                        keyword = content
                    elif label == '更新频率':
                        update_frequency = content
                    elif label == '覆盖范围':
                        coverage = content
                    elif label == '存储大小':
                        storage = content
                    elif label == '增量存储大小':
                        storage_incr = content
                    elif label == '底层数据维度':
                        dimension = content
                    else:
                        pass

                use_case = driver.find_element(By.CSS_SELECTOR, 'div.use-case')
                use_case = h.handle(use_case.get_attribute('innerHTML'))

                # price = driver.find_element(By.CSS_SELECTOR, 'div.product-price')
                # price = h.handle(price.get_attribute('innerHTML'))
                # print(price)

                result.append([title, list_time, series_name, company_name, industry, data_type, product_type, description, keyword,
                               update_frequency, coverage, storage, storage_incr, dimension, use_case, cur_url])
            except Exception:
                print(cur_url)
                pass


            time.sleep(3)
            driver.back()
            time.sleep(3)

        next_button = driver.find_element(By.CSS_SELECTOR, 'button.btn-next')
        if next_button.get_attribute('disabled') == 'true':
            break
        next_button.click()

    # result = pd.DataFrame(result, columns=['title', 'description', 'url', 'industry', 'keyword', 'update_frequency', 'coverage', 'dataStore', 'dataStore_incr', 'data_dim', 'use_case', 'main_content',
    #                                        'price', 'company_name', 'sector_name', 'series_name', 'data_type', 'data_from', 'listed_time', 'update_time'])
    # result = pd.DataFrame(result, columns=['title', 'list_data', 'series_name', 'company_name', 'industry', 'data_type', 'product_type', 'description', 'keyword', 'update_frequency', 'coverage', 'storage', 'storage_incr', 'dimension', 'use_case', 'url'])
    result = pd.DataFrame(result, columns=['title', 'list_time', 'series_name', 'company_name', 'industry', 'data_type', 'product_type', 'description',
                                           'keyword', 'update_frequency', 'coverage', 'storage', 'storage_incr', 'dimension', 'use_case', 'url'])
    result.to_csv('./shanghai.csv', index=False)
