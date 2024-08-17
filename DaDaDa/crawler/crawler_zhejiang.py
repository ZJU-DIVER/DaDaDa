import math
import traceback

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

    url = 'https://ditm.zjdex.com/data-service/index'
    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.el-pagination')))
    h = html2text.HTML2Text()
    result = []

    count = 0
    while True:
        item_list = driver.find_elements(By.CSS_SELECTOR, 'div.product-container>div.container')
        main_window = driver.current_window_handle
        num = len(item_list)
        for i in range(num):
            count += 1
            try:
                item_list[i].click()
                driver.switch_to.window(driver.window_handles[-1])

                WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.title-container')))
                time.sleep(3)
                # get the main content
                cur_url = driver.current_url
                title = driver.find_element(By.CSS_SELECTOR, 'div.intro-content-header>div.title-container').text
                data_type = driver.find_element(By.CSS_SELECTOR, 'div.tag').text
                click_times = driver.find_element(By.CSS_SELECTOR, 'div.view-container').text
                description = driver.find_element(By.CSS_SELECTOR, 'div.des').text
                price = driver.find_element(By.CSS_SELECTOR, 'div.price>span.number-container').text
                deal_times = driver.find_element(By.CSS_SELECTOR, 'div.deal-container>span.deal-content').text

                print(title, data_type, click_times, price, deal_times)
                header_num = len(driver.find_elements(By.CSS_SELECTOR, 'div.tabs-header-item-title'))

                api_info = None
                for j in range(header_num):
                    header_list = driver.find_elements(By.CSS_SELECTOR, 'div.tabs-header-item-title')
                    header_type = header_list[j].text
                    header_list[j].click()
                    time.sleep(1)
                    if header_type == '商品概况':
                        product_info = driver.find_elements(By.CSS_SELECTOR, 'div.basic-information-content div.item-content')
                        version = product_info[0].text
                        product_type = product_info[1].text

                        datasource_info = driver.find_elements(By.CSS_SELECTOR, 'div.data-source-content div.item-container')
                        category = classification = management = update_frequency = None
                        sample_time = data_size = data_form = None
                        for info in datasource_info:
                            label = info.find_element(By.CSS_SELECTOR, 'div.item-label').text
                            content = info.find_element(By.CSS_SELECTOR, 'div.item-content').text
                            print(label, content)
                            if label == '数据分类':
                                category = content
                            elif label == '数据分级信息':
                                classification = content
                            elif label == '公共管理属性':
                                management = content
                            elif label == '更新频率':
                                update_frequency = content
                            elif label == '数据采集周期':
                                sample_time = content
                            elif label == '数据量':
                                data_size = content
                            elif label == '数据形态':
                                data_form = content
                            else:
                                pass
                    elif header_type == '功能介绍':
                        detail_description = driver.find_element(By.CSS_SELECTOR, 'div.return-example-content')
                        detail_description = h.handle(detail_description.get_attribute('innerHTML'))
                    elif header_type == '商品价格':
                        price_type = driver.find_element(By.CSS_SELECTOR, 'div.api-doc-content')
                        price_type = h.handle(price_type.get_attribute('innerHTML'))
                    elif header_type == 'API文档':
                        api_info = driver.find_element(By.CSS_SELECTOR, 'div.api-doc-content')
                        api_info = h.handle(api_info.get_attribute('innerHTML'))
                    else:
                        pass

                result.append([title, data_type, click_times, description, price, deal_times, version, product_type, category,
                               classification, management, update_frequency, sample_time, data_size, data_form, detail_description, price_type, api_info, cur_url])

                driver.close()
                driver.switch_to.window(main_window)
                time.sleep(3)
            except Exception as e:
                # print the cause of the Exception
                traceback.print_exc()
                print(count)
                driver.close()
                driver.switch_to.window(main_window)
                time.sleep(3)
                continue

        next_button = driver.find_element(By.CSS_SELECTOR, 'button.btn-next')
        if next_button.get_attribute('disabled') == 'true':
            break
        next_button.click()
        time.sleep(3)

    result = pd.DataFrame(result, columns=['title', 'data_type', 'click_times', 'description', 'price', 'deal_times', 'version', 'product_type', 'category',
                               'classification', 'management', 'update_frequency', 'sample_time', 'data_size', 'data_form', 'detail_description', 'price_type', 'api_info', 'cur_url'])
    result.to_csv('./zhejiang.csv', index=False)

