from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import time
import json

url = "https://cloud.google.com/translate/docs/languages"


driver = webdriver.Firefox()
driver.get(url)


time.sleep(1)

soup = BeautifulSoup(driver.page_source, features="html.parser")

language = soup.find("div", {"class": "devsite-table-wrapper"})

table = language.find('table')
table_rows = table.find_all('tr')

data = {}

key = 0
for tr in table_rows:
    td = tr.find_all('td')

    row = [i.text for i in td]

    if len(row) != 0:
        data[key] = row

    key += 1

print(data)
# with open('read.json', "w") as outfile:
#     json.dump(data, outfile)
