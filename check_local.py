import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd

USERNAME="054989280"
PASSWORD="51872"

service = Service('./chromedriver.exe')
driver = webdriver.Chrome(service=service)

driver.get('https://www.zencollection.gr')
time.sleep(1)

login = driver.find_element(By.XPATH, '/html/body/header/div[2]/div[4]/div[2]/a')
login.click()
time.sleep(1)
username = driver.find_element(By.XPATH, '//*[@id="glblgn"]/div/form/div[1]/input')
username.send_keys(USERNAME)
password = driver.find_element(By.XPATH, '//*[@id="glblgn"]/div/form/div[2]/input')
password.send_keys(PASSWORD)
button = driver.find_element(By.XPATH, '//*[@id="glblgn"]/div/form/button')
button.click()

file_name = "output_test.xlsx"

df = pd.read_excel(file_name)

def check_availability_and_update(df, column_name):
    try:
        for index, row in df.iterrows():
            url = row.get(column_name, None)

            if pd.notna(url):
                print(f"Opening URL: {url}")
                driver.get(url)
                try:
                    WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '/html/body/header/div[2]/div[3]/a/img')))
                except TimeoutException:
                    print("Page load timed out or expected element not found.")

                if "Σε απόθεμα" in driver.page_source:
                    print("In stock")
                    if df.loc[index, 'availability'] != "In stock":
                        df.loc[index, 'availability_update'] = "Yes"
                        df.loc[index, 'availability'] = "In stock"
                    else:
                        df.loc[index, 'availability_update'] = ""
                else:
                    print("Out of stock")
                    if df.loc[index, 'availability'] != "Out of stock":
                        df.loc[index, 'availability_update'] = "Yes"
                        df.loc[index, 'availability'] = "Out of stock"
                    else:
                        df.loc[index, 'availability_update'] = ""
            else:
                print(f"Skipping invalid URL at index {index}")

    finally:
        driver.quit()
        print("All URLs have been processed.")

    return df

df = check_availability_and_update(df, "URL Προιόντος")

df.to_excel(file_name, index=False)
print("Excel file updated.")
