import time
import datetime
from datetime import timedelta
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException, TimeoutException, ElementNotInteractableException

# Set up the Chrome WebDriver
driver = webdriver.Chrome()
driver.maximize_window()

# Open the URL
path = "https://www.sharesansar.com/today-share-price"
driver.get(path)

# Define start and end dates
starting_date = datetime.datetime(2024, 5, 15).date()
end_date = datetime.datetime.now().date()

# Find the table header and extract column names
try:
    table_content = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//table[@class="table table-bordered table-striped table-hover dataTable compact no-footer"]'))
    )
    table_rows = table_content.find_elements(By.TAG_NAME, "th")
    header = [i.text.replace('\n', '') for i in table_rows]
    header.append("Date")
    print("Header:", header)
except TimeoutException as e:
    print(f"Error loading table header: {e}")
    driver.quit()

# Initialize DataFrame
df = pd.DataFrame(columns=header)

# Function to attempt clicking the search button with retries
def click_search_button():
    retries = 5
    while retries > 0:
        try:
            search = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//button[@class="btn btn-org"]'))
            )
            time.sleep(2)
            search.click()
            return True
        except (ElementClickInterceptedException, TimeoutException, ElementNotInteractableException) as e:
            print(f"Error clicking search button: {e}. Retrying... ({5 - retries} retries left)")
            retries -= 1
            time.sleep(2)
    return False

# Loop through each date from starting_date to end_date
while starting_date <= end_date:
    try:
        # Select and clear the date input
        select_date = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@class="form-control datepicker"]'))
        )
        select_date.clear()
        select_date.send_keys(str(starting_date))
        
        # Attempt to click the search button
        if not click_search_button():
            print(f"Failed to click the search button for date: {starting_date}")
            starting_date += timedelta(days=1)
            continue
        
        # Wait for the table to update and re-locate the table elements
        WebDriverWait(driver, 10).until(EC.staleness_of(table_content))
        table_content = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//table[@class="table table-bordered table-striped table-hover dataTable compact no-footer"]'))
        )
        
        # Extract table data
        table_rows_1 = table_content.find_elements(By.TAG_NAME, "tr")[1:]
        for i in table_rows_1:
            data = i.find_elements(By.TAG_NAME, 'td')
            row = [j.text.replace("\n", "") for j in data]
            if len(row) != len(header):  # Ensure row length matches header length
                row.extend([float('nan')] * (len(header) - len(row) - 1))  # Fill missing values with NaN
            row.append(str(starting_date))
            df.loc[len(df)] = row
            

    except (NoSuchElementException, StaleElementReferenceException, TimeoutException) as e:
        print(f"An error occurred on {starting_date}: {e}")

    # Increment the date
    starting_date += timedelta(days=1)

# Save DataFrame to CSV
df.to_csv("Historic_Price_Data.csv", index=False)

# Close the browser
driver.quit()
