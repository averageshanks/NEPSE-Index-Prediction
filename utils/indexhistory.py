import time
import datetime
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

# url
path = "https://www.sharesansar.com/index-history-data"
driver = webdriver.Chrome()
driver.maximize_window()

driver.get(path)

starting_date = driver.find_element(
    By.XPATH, '//input[@class="form-control datepicker"and @name="fromDate"]'
)
end_date = driver.find_element(
    By.XPATH, '//input[@class="form-control datepicker"and @name="toDate"]'
)

from_date = datetime.datetime(2016, 1, 1).date()
to_date = datetime.datetime.now().date()

print(from_date, to_date)

starting_date.clear()
starting_date.send_keys(str(from_date))
end_date.clear()
end_date.send_keys(str(end_date))


search = driver.find_element(By.XPATH, '//button[@class="btn btn-org"]')
search.click()


select = driver.find_element(By.XPATH, '//select[@name="myTable_length"]')
select.send_keys("50")

time.sleep(3)


table = driver.find_element(By.XPATH, "//table[@class]")
table_header = table.find_element(By.TAG_NAME, "thead")
each_row = table_header.find_elements(By.TAG_NAME, "th")
header = [i.text.replace("\n", "") for i in each_row]

df = pd.DataFrame(columns=header)

starting_index = 1
next = driver.find_element(By.XPATH, '//a[@class="paginate_button next"]')
paginate_buttons = driver.find_elements(By.XPATH, '//a[@class="paginate_button "]')

index = [j.text.replace("\n", "") for j in paginate_buttons]
last_index = int(index[-1])


while starting_index <= last_index:
    table_content = driver.find_element(By.XPATH, "//table[@class]")
    table_data = table_content.find_element(By.TAG_NAME, "tbody")
    data = table_data.find_elements(By.TAG_NAME, "tr")

    for i in data:
        each_row = i.find_elements(By.TAG_NAME, "td")
        ind_data = [j.text.replace("\n", "") for j in each_row]
        if len(ind_data) != len(header):  # Ensure row length matches header length
            ind_data.extend(
                [float("nan")] * (len(header) - len(ind_data))
            )  # Fill missing values with NaN
        df.loc[len(df)] = ind_data

    if starting_index != last_index:
        next = driver.find_element(By.XPATH, '//a[@class="paginate_button next"]')
        next.click()

    print(starting_index)
    starting_index += 1
    time.sleep(2)


df.to_csv("Historic Index Data.csv")
driver.quit()
