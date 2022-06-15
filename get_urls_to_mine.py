from time import sleep
from time import time
import random
import logging
import os
from fake_useragent import UserAgent
from datetime import datetime
from bs4 import BeautifulSoup
from collections import OrderedDict
import sqlite3
import requests
import urllib
import re
import anonym
import pandas as pd
import random
#---------------------
from selenium import webdriver
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.proxy import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.alert import Alert
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException

from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

use_sel = True


def make_driver():
    opt = Options()
    ua = UserAgent()
    path = f'{os.path.join(os.path.dirname(__file__))}\chromedriver.exe'
    opt.add_argument(f'user-agent={ua.random}')
    driver = webdriver.Chrome(service = Service(path), options=opt)
    return driver


def delete_cache(driver):
    # source: https://stackoverflow.com/questions/50456783/python-selenium-clear-the-cache-and-cookies-in-my-chrome-webdriver
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.keys import Keys

    driver.execute_script("window.open('');")
    sleep(2)
    driver.switch_to.window(driver.window_handles[-1])
    sleep(2)
    driver.get('chrome://settings/clearBrowserData') # for old chromedriver versions use cleardriverData
    sleep(2)
    actions = ActionChains(driver)
    actions.send_keys(Keys.TAB * 3 + Keys.DOWN * 3) # send right combination
    actions.perform()
    sleep(2)
    actions = ActionChains(driver)
    actions.send_keys(Keys.TAB * 4 + Keys.ENTER)
    actions.perform()
    sleep(5)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])




def get_all_urls(driver):
    dirname = os.path.dirname(__file__)
    bundesland = ['salzburg', 'vorarlberg', 'burgenland', 'steiermark', 'niederoesterreich', 'oberoesterreich', 'kaernten',
                  'tirol','wien'] #oberösterreich missing
    bundesland = ['kaernten']
    wohnung = ['eigentumswohnung']
#    random.shuffle(bundesland) 'mietwohnungen']#,
#    random.shuffle(wohnung)
    sleep(5)
    rows_per_page = 200
    page_start = 1
    page_end = 100

    """ Get all urls initially. Afterwards for each url the data is scraped."""
    i = 0
    driver.delete_all_cookies()
    delete_cache(driver)

    for land in bundesland:
        for wohnungs_typ in wohnung:
            final_page = False
            apartment_links = []
            for i in range(page_start, page_end):
                if final_page:
                    print(f"{land}, {wohnungs_typ}, {i} | {len(apartment_links)}")
                    driver.delete_all_cookies()
                    delete_cache(driver)
                    print("Cookies and cache has been deleted.")
                    break
                url = (f'https://www.willhaben.at/iad/immobilien/{wohnungs_typ}/{land}?rows={rows_per_page}&page={i}')
                print(url)
                i += 1
                driver.get(url)

                sleep(6)
                try:
                    driver.find_element(By.XPATH, "//button[@id='didomi-notice-disagree-button']").click()
                    sleep(10)
                except:
                    pass

                """Scrolling down to the bottom """
                speed = 8
                current_scroll_position, new_height = 0, 1
                while current_scroll_position <= new_height:
                    current_scroll_position += speed
                    driver.execute_script("window.scrollTo(0, {});".format(current_scroll_position))
                    new_height = driver.execute_script("return document.body.scrollHeight")

                if not use_sel:
                    response = s.get(url, headers=headers)
                    soup = BeautifulSoup(response.text, 'html.parser')
                else:
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                found = []
                for link in soup.find_all('a'):
                    url2 = link.get('href')
                    if url2 != "#" and url2 != None and url2.startswith((f"/iad/immobilien/d/{wohnungs_typ}/{land}")):
                        apartment_links.append("https://www.willhaben.at" + url2)
                        found.append(url2)

                        con = sqlite3.connect(os.path.join(dirname + '\db', 'scrape_kaernten_eigentum.sqlite'))
                        cur = con.cursor()
                        create_table = (
                            f'''CREATE TABLE IF NOT EXISTS scrape (url text UNIQUE)''')
                        cur.execute(create_table)
                        sqlite_insert_query = f"""INSERT OR IGNORE INTO scrape (url) VALUES
                                                 ('{"https://www.willhaben.at" + url2}');"""
                        cur.execute(sqlite_insert_query)
                        con.commit()
                        cur.close()
                print(f"{len(apartment_links)}")
                if len(found) <= 10: final_page = True

    return apartment_links


if __name__ == '__main__':
    start = time()
    driver = make_driver()
    get_all_urls(driver)
    print(f"{round(time()-start)} s")