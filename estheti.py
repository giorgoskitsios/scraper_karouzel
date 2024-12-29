import time
import gspread
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from google.oauth2.service_account import Credentials
import pandas as pd

USERNAME="30-96-0281"
PASSWORD="30-96-0281"

service = Service('./chromedriver.exe')
driver = webdriver.Chrome(service=service)

driver.get('https://www.eurolamp.gr')
time.sleep(1)

login = driver.find_element(By.XPATH, '//*[@id="usermenu"]/li[5]/a')
login.click()
time.sleep(1)
username = driver.find_element(By.XPATH, '//*[@id="cphBodyTop_cphWebPartsTop_cphBody_lgnB2B_UserName"]')
username.send_keys(USERNAME)
password = driver.find_element(By.XPATH, '//*[@id="cphBodyTop_cphWebPartsTop_cphBody_lgnB2B_Password"]')
password.send_keys(PASSWORD)
button = driver.find_element(By.XPATH, '//*[@id="cphBodyTop_cphWebPartsTop_cphBody_btnLogin"]')
button.click()

from google.oauth2.service_account import Credentials

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(creds)

sheet_id = ""
sheet_name = "Estheti"
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
                    EC.presence_of_element_located((By.XPATH, '//*[@id="form1"]/div[7]/div[2]/div[2]/div[1]/div[6]/div')))
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

sheet.update(values, f"K1:L{len(values)}")
print("Google Sheet file updated.")
