# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select

import pandas as pd

driver = webdriver.Chrome()

years = {
	2013: 215,
	2014: 177,
	2015: 6,
	2016: 5,
	2017: 4,
	2018: 3,
	2019: 2,
	2020: 1,
	2021: 446,
	2022: 444,
	2023: 445}


headers = {
	'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
	'cookies': '__utmc77627408; ApplicationGatewayAffinityCORS=22109041979dfe0b8908cad8780e6956; ak_bmsc=01D22980D73091E444252539C17CCC7E~000000000000000000000000000000~YAAQFmbNF/jF/u2VAQAAaF0x9xtDCN8DVdjAS2mvbbMghUWvds2nwtVU12aq8c18nSWAtO2Ei+rYKEGqm6JwSC/gpOvBuyFENpk6f3FRxcGIEpcXjvB8QIHFD9jvjlmhDABcCqlPgyWi0Z4+wB+Ugi83c/LNVl1sMK6i3SDybzwl6uzUmCT/K0oOQROdO2B53/Nnci3vRZqjCkIJx8Els5hT8IxDaCyVpHs+R3GUMOmuEwTlVVkh+QIE83P/jk2EAxnNgmIYCUZvsUKSct1UAfO8uyj7qgz2ooHzMSzyjjOtkRnsJSWcfp4d/ZLfkfyjzB5lTEiM+UCQ5L1ZA5r6XWIfF9UMQFss43nZgVyAJE/s416oMGwJMy6qODMMoqeq7B+H68bkDNzuvq7w5g==; __utmc77627408; bm_sv=9D776724F32F1F38042BC32EEC671BC8~YAAQFmbNF/ogBu6VAQAACRlN9xvh788urwqaCSoCxjoBKfviqPvMMtJ+Wyd4EEhbH739Vjx9sBvETfXhbsugVXoebV+tLANdXJpWJfzOVNUb3iSzTxYxfZ3Tsx3YsNBAn4CtulC3nw9w/13FDd6clVJyv850Yny0iDb+qkGtfZh0FYET5hmFML5jj9/ei/DLevWP3/NAuA+HLPUsbcPFgA5yzlmudYuxVoKhwmp4FUr3GWIi29yns5LLe0fAuhXHS8gkHQ==~1'
	}

usda_recalls = []
for year, year_id in years.items():
	print(year)
	driver.get(f"https://www.fsis.usda.gov/fsis/api/recall/v/1?field_year_id={year_id}")	
	json_content = driver.find_element(By.TAG_NAME, 'pre').text
	df = pd.read_json(json_content)
	usda_recalls.append(df)
	
usda = pd.concat(usda_recalls)

usda.columns = [f.replace("field_","") for f in usda.columns]
	
usda.reset_index().to_parquet("usda_recalls.parquet")
	
	
