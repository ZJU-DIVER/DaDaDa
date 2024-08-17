from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import pandas as pd

if __name__ == '__main__':
    driver = webdriver.Chrome()
    url = 'https://www.gzdex.com.cn/market/list'
    driver.get(url)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'div.list-sort')))

    actions = ActionChains(driver)
    elements = driver.find_elements(By.CSS_SELECTOR, 'li.text-clip div')
    crawler_result = []

    for element in elements:
        actions.move_to_element(element).click().perform()
        time.sleep(5)
        # actions.move_by_offset(0,0).click().perform()
        move = driver.find_element(By.CSS_SELECTOR, 'div.bg-filter li:first-child')
        actions.move_to_element(move).click().perform()
        time.sleep(5)
        while True:
            # driver.find_element(By.CSS_SELECTOR, 'body').send_keys(Keys.SPACE)
            actions.send_keys(Keys.SPACE).perform()
            try:
                element = WebDriverWait(driver, 1).until(
                    EC.presence_of_element_located((By.XPATH, "//p[text()=' 加载完成 ']"))
                )
                break
            except Exception:
                continue

        products_div = driver.find_elements(By.CSS_SELECTOR, 'div.market-card')
        for product in products_div:
            title = product.find_element(By.CSS_SELECTOR, 'h3.title-text').text
            # first element is company, second is transaction record
            company = product.find_element(By.CSS_SELECTOR, 'div.title-info>span:nth-child(1)').text
            transaction_record = product.find_element(By.CSS_SELECTOR, 'div.title-info>span:nth-child(2)').text
            price = product.find_element(By.CSS_SELECTOR, 'div.card-rate p').text

            main = product.find_element(By.CSS_SELECTOR, 'div.card-main')
            description = main.find_element(By.CSS_SELECTOR, 'p.main-description').text

            data_type = main.find_element(By.CSS_SELECTOR, 'div.main-col:nth-child(1)>span:last-child').text
            use_type = main.find_element(By.CSS_SELECTOR, 'div.main-col:nth-child(2)>span:last-child').text
            create_time = main.find_element(By.CSS_SELECTOR, 'div.main-col:nth-child(3)').text

            # create_time = create_time[create_time.find('：') + 1:]
            # create_time get the content after the first space
            create_time = create_time[create_time.find(' ') + 1:]
            crawler_result.append([title, company, transaction_record, price, description, data_type, use_type, create_time])
            # print(crawler_result)

    crawler_result = pd.DataFrame(crawler_result, columns=['title', 'company', 'transaction_record', 'price', 'description', 'data_type', 'use_type', 'create_time'])
    crawler_result.to_csv('./guiyang.csv', index=False)