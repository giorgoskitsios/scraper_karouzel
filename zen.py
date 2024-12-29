import time
import gspread
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from google.oauth2.service_account import Credentials
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

from google.oauth2.service_account import Credentials

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

sheet_id = ""
sheet_name = "Zen"
workbook = client.open_by_key(sheet_id)
sheet = workbook.worksheet(sheet_name)

# Specify the expected unique headers
expected_headers = ["URL Προιόντος", "availability", "availability_update"]


data = sheet.get_all_records(expected_headers=expected_headers)

# Convert to Pandas DataFrame
df = pd.DataFrame(data)
columns_to_keep = ["URL Προιόντος", "availability", "availability_update"]
df_filtered = df[columns_to_keep]

# Print the DataFrame
print(df_filtered)

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

filtered_df = df[["availability", "availability_update"]]
print(filtered_df)

# Convert the filtered dataframe to a 2D list
values = [["availability", "availability_update"]] + filtered_df.values.tolist()
print(values)

sheet.update(values, f"L1:M{len(values)}")
print("Google Sheet file updated.")
