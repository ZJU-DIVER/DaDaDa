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

    url = 'https://www.cantonde.com/jydt.html#/list'
    driver.get(url)  # 将此处替换为你要爬取的网页URL
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.prj-sjjy-list')))
    h = html2text.HTML2Text()
    result = []

    count = 0
    while True:
        item_list = driver.find_elements(By.CSS_SELECTOR, 'div.prj-sjjy-list a')
        main_window = driver.current_window_handle
        num = len(item_list)
        for i in range(num):
            count += 1
            # temp_list = driver.find_elements(By.CSS_SELECTOR, 'div.prj-sjjy-list a')
            try:
                item_list[i].click()
                # 切换到新窗口（注意：新打开的窗口句柄会被添加到 window_handles 列表的最后）
                driver.switch_to.window(driver.window_handles[-1])

                WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'button.ant-modal-close')))
                # no need to login
                close_button = driver.find_element(By.CSS_SELECTOR, 'button.ant-modal-close')
                close_button.click()
                time.sleep(5)

                # get the main content
                cur_url = driver.current_url
                title = driver.find_element(By.CSS_SELECTOR, 'div.detail-head-title').text
                company_info = driver.find_element(By.CSS_SELECTOR, 'div.detail-head-sup-fl').text
                # test = company_name.split("：")
                # '公司名称：广州金控征信服务有限公司 |点击数：138', split company_time and clcik_times
                company_name = company_info.split('：')[1].split('|')[0].strip()
                click_time = int(company_info.split("：")[2])

                outline = driver.find_element(By.CSS_SELECTOR, 'div.detail-head-outline').text
                price = driver.find_element(By.CSS_SELECTOR, 'div.detail-head-num-money>span.money').text
                # application = driver.find_element(By.CSS_SELECTOR, 'table.detail-head-table>tr:first-child>td').text


                main_content = driver.find_elements(By.CSS_SELECTOR, 'div.ant-tabs-tabpane table.xm-tab')

                # test = main_content[0].get_attribute('innerHTML')

                introduction = main_content[0].find_elements(By.CSS_SELECTOR, 'td.xmtd2')
                application = introduction[0].text
                type = introduction[1].text
                subdivision_type = introduction[2].text
                target_user = introduction[3].text

                detail_description = main_content[1].text

                settlement_interval = main_content[-1].find_element(By.CSS_SELECTOR, 'td.xmtd2').text

                ###
                delivery = main_content[-2].find_elements(By.CSS_SELECTOR, 'tr')
                update_frequency = delivery_type = None
                # get all the tr
                for delivery_info in delivery:
                    text = delivery_info.find_element(By.CSS_SELECTOR, 'td.xmtd1').text
                    if text == '交付渠道':
                        delivery_type = delivery_info.find_element(By.CSS_SELECTOR, 'td.xmtd2').text
                    elif text == '更新频率':
                        update_frequency = delivery_info.find_element(By.CSS_SELECTOR, 'td.xmtd2').text

                result.append([title, company_name, click_time, outline, price, application, type, subdivision_type,
                               target_user, detail_description, settlement_interval, delivery_type, update_frequency, cur_url])
                # 关闭新窗口
                driver.close()
                # 切回到主窗口
                driver.switch_to.window(main_window)
                time.sleep(5)
            except Exception:
                print(Exception)
                print(count)
                # 关闭新窗口
                driver.close()
                # 切回到主窗口
                driver.switch_to.window(main_window)
                time.sleep(5)
                continue

        next_button = driver.find_element(By.CSS_SELECTOR, 'li.ant-pagination-next')
        if next_button.get_attribute('aria-disabled') == 'true':
            break
        next_button.click()
        time.sleep(5)

    result = pd.DataFrame(result, columns=['title', 'company_name', 'click_time', 'outline', 'price', 'application', 'type', 'subdivision_type',
                                 'target_user', 'detail_description', 'settlement_interval', 'delivery_type', 'update_frequency', 'cur_url'])
    result.to_csv('./guangzhou.csv', index=False)

