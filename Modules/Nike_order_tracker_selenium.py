from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time, os, zipfile
import urllib.request

def get_data(chromedriver_path):
    # Open a new Chrome window
    driver = webdriver.Chrome(chromedriver_path)

    # Navigate to Google.com
    driver.get("https://www.nike.com/orders")

    submit_cookies = driver.find_element(By.ID, 'hf_cookie_text_cookieAccept').click()

    order_number = driver.find_element(By.NAME, 'orderNumber').send_keys('C01159034092')
    order_email = driver.find_element(By.NAME, 'email').send_keys('Mart455@icloud.com')
    time.sleep(5)
    submit_data = driver.find_element(By.XPATH, '//*[@id="orders"]/div[1]/div/div/form/div/div/div/div[3]/button').click()
    time.sleep(5)
    try:
        tracking_number_1 = driver.find_element(By.XPATH, '//*[@id="order-detail-wrapper"]/div/div/div[1]/div[4]/div/div/div[3]/div[2]/div')
        tracking_number = driver.find_element(By.CSS_SELECTOR, 'nds-btn css-1cxnzw1 css-xxsqkh ex41m6f0 primary')#.get_attribute('href')
        print(tracking_number)
        print(tracking_number_1)

    except:
        print('No tracking number found')

try:
    chromedriver_path = os.path.join(os.getcwd(), 'chromedriver')
    get_data(chromedriver_path)

except:
    print('Chrome driver doesnt exit')