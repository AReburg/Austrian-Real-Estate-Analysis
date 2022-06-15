from time import sleep
import random
import logging
import os
from fake_useragent import UserAgent
from nordvpn_switcher import initialize_VPN,rotate_VPN,terminate_VPN

from datetime import datetime
from bs4 import BeautifulSoup
from collections import OrderedDict
import sqlite3
import requests
import urllib
import re
import anonym
import pandas as pd
dirname = os.path.dirname(__file__)
from requests_html import AsyncHTMLSession

class AdvertaisementNotAvailableError(Exception):
    pass

class RequestsError(Exception):
    pass

area_input = ['Argentina','Denmark','Switzerland','Finland','Chile','Brazil','Austria','Portugal','Serbia','Germany','France','Hungary','Spain']
#response = s.get('https://www.whatismyip.com/de/', headers=headers, proxies=prox)
#so = BeautifulSoup(response.text, 'html.parser')
#print(so.find('span', {'id': 'geo'}))

real_estate_db = 'real_estate.sqlite'
svg = """<svg class="createSvgIcon__SvgIcon-sc-1vebdtk-0 dHnWPw" height="1em" pointer-events="none" viewbox="0 0 24 24" width="1em" xmlns="http://www.w3.org/2000/svg"><path d="M21.71 5.29a1 1 0 0 0-1.42 0L9 16.58l-5.28-5.29a1 1 0 0 0-1.41 1.41l6 6a1 1 0 0 0 1.42 0l12-12a1 1 0 0 0-.02-1.41Z" fill="currentColor"></path></svg>"""
from requests_html import HTMLSession
opt = 3 #3 best
# settings = initialize_VPN(save=1,area_input=['complete rotation'])
# rotate_VPN(settings)

def make_driver():
    opt = Options()
    ua = UserAgent()
    path = f'{os.path.join(os.path.dirname(__file__))}\chromedriver.exe'
    opt.add_argument(f'user-agent={ua.random}')
    driver = webdriver.Chrome(service = Service(path), options=opt)
    return driver

if opt==1:
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

    driver = make_driver()
elif opt==2:
    session = AsyncHTMLSession ()
elif opt == 3:
    s = requests.Session()



prox = ''
headers = ''
while True:
    try:
        ua = UserAgent()
        headers = {"User-Agent": ua.random, 'Cache-Control': 'no-cache'}
        if opt ==1:
            print("selenium option 1")
        elif opt== 2:
            print("html session")
        elif opt == 3:
            print(f"""{s.get("https://api.ipify.org/?format=json", headers=headers).json()['ip']}, {headers}""") #, proxies=prox
        break
    except:
        sleep(1)


def innerHTML(element):
    """Returns the inner HTML of an element as a UTF-8 encoded bytestring"""
    return element.encode_contents()


def get_additional_apartment_details(soup, url):
    """ Get price data etc. """
    title = []
    value = []

    """ get real estate price """
    title.append('price')
    try:
        price = innerHTML(soup.find('span', {'data-testid': 'contact-box-price-box-price-value-0'})).decode("utf-8")
        pattern = re.compile(r'\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?')
        try:
            res = pattern.findall(price)[0]
            value.append(float(res.replace('.', '').replace(',', '.')))
        except (IndexError, AttributeError) as e:
            value.append(price)
    except:
        value.append(None)


    title.append('scrape_date')
    now = datetime.now()
    value.append("{}.{}.{} {}:{}".format(now.day, now.month, now.year, now.hour, now.minute))

    title.append('type')
    if url.find('eigentumswohnung') > 0:
        value.append('condominium')
    elif url.find('mietwohnungen') > 0:
        value.append('rented flat')
    elif url.find('haus-kaufen') > 0:
        value.append('single-family home')
    else:
        value.append(None)

    """ Retail agency """
    try:
        title.append('makler')
        value.append(innerHTML(
            soup.find('span', {'data-testid': 'price-information-freetext-attribute-value-0'})).decode("utf-8"))
    except (IndexError, AttributeError) as e:
        value.append(None)

    """ additional information retail agent """
    try:
        title.append('zusatz')
        value.append(innerHTML(
            soup.find('span', {'data-testid': 'price-information-freetext-attribute-value-1'})).decode("utf-8"))
    except (IndexError, AttributeError) as e:
        value.append(None)

    """ last change of the inserat """
    title.append('last_change_date')
    try:
        last_change = innerHTML(soup.find('span', {'data-testid': 'ad-detail-ad-edit-date-top'})).decode("utf-8")
        value.append(re.findall(r'(\d{2}.\d{2}.\d{4})', last_change)[0])
    except (IndexError, AttributeError) as e:
        value.append(None)

    """ title of the inserat """
    title.append('title')
    try:
        value.append(innerHTML(soup.find('h1', {'data-testid': 'ad-detail-header'})).decode("utf-8"))
    except (IndexError, AttributeError) as e:
        value.append(None)

    """ code number = unique identifier"""
    title.append('code')
    try:
        willhaben_code = innerHTML(soup.find('span', {'data-testid': 'ad-detail-ad-wh-code-top'})).decode("utf-8")
        value.append(re.findall(r'(\d{9})', willhaben_code)[0])
    except (IndexError, AttributeError) as e:
        value.append(None)

    title.append('url')
    value.append(url)

    """ location of the real estate """
    title.append('location')
    try:
        location = innerHTML(soup.find('div', {'data-testid': 'object-location-address'})).decode("utf-8")
        value.append(location)
    except (IndexError, AttributeError) as e:
        value.append(None)

    """ area code of the real estate """
    title.append('plz')
    # source: https://stackoverflow.com/questions/16348538/python-regex-for-int-with-at-least-4-digits
    pattern = re.compile(r"(?<!\d)\d{4,7}(?!\d)")
    try:
        plz = pattern.findall(location)[0]
        value.append(plz)
    except:
        value.append(None)
    [title, value] = get_details(soup, title, value)
    return [title, value]


def get_apartment_details(url):
    """Get all the details of the apartment. """
    #response = s.get(url, headers=headers, timeout=(3.05, 27))
    if opt ==2:
        import asyncio
        #response = session.get(url, headers=headers)
        #await session.get(url).result().arender()
        asyncio.run(session.get(url).result().arender())
        #response.html.render()  # this call executes the js in the page
    elif opt == 3:
        try:
            response = s.get(url, headers=headers, timeout=10)
        except requests.exceptions.ReadTimeout:
            raise RequestsError("Timeout error")

    sleep(0.5)


    soup =''
    if opt ==1:
        driver.get(url)
        sleep(3)
        if driver.current_url != url:
            raise AdvertaisementNotAvailableError(driver.current_url)
        """
        try:
            expired = soup.find('span', {'class': 'Text-sc-10o2fdq-0 cqMSJQ'})
        except Exception:
            raise AdvertaisementNotAvailableError(driver.current_url) """

        speed = 12
        current_scroll_position, new_height = 0, 1
        while current_scroll_position <= new_height:
            current_scroll_position += speed
            driver.execute_script("window.scrollTo(0, {});".format(current_scroll_position))
            new_height = driver.execute_script("return document.body.scrollHeight")
        sleep(0.5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        print(soup)
    elif opt==2:
        soup = BeautifulSoup(response.html.raw_html, 'html.parser')
    elif opt==3:
        rand = random.choices([0, 1], weights=(1, 100), k=1)
        if rand[0] == 0:
            # source: https://stackoverflow.com/questions/23816139/clear-cookies-from-requests-python
            s.cookies.clear()
            print("cookies cleared.")
        if response.url != url:
            raise AdvertaisementNotAvailableError(response.url)
        soup = BeautifulSoup(response.text, 'html.parser')


    # print(soup)
    [title, value] = get_additional_apartment_details(soup, url)
    results = OrderedDict()
    results['columns'] = title
    results['values'] = value
    if response.url != url:
        raise AdvertaisementNotAvailableError(response.url)
    return results


def get_details(soup, title, value):
    try:
        titles = soup.find_all('span', {'class': 'Text-sc-10o2fdq-0 jnPJDV'})
        for i in titles:
            try:
                title.append(innerHTML(i).decode("utf-8"))
            except:
                title.append(None)
        values = soup.find_all('div', {'data-testid': 'attribute-value'})
        for i in values:
            try:
                if innerHTML(i).decode("utf-8") == svg:
                    value.append("yes")
                else:
                    value.append(innerHTML(i).decode("utf-8"))
            except Exception as e:
                print(e)
                value.append(None)
        return [title, value]
    except IndexError:
        return [title, value]


def _translate_umlauts(s):
    """Translate a string into ASCII. source: http://stackoverflow.com/a/2400577/152439
    https://charbase.com/00f6-unicode-latin-small-letter-o-with-diaeresis """
    trans = {"\xe4" : "ae", "\xfc" : "ue", "\xf6" : "oe", "\xdf" : "ss"}
    patt = re.compile("|".join(trans.keys()))
    return patt.sub(lambda x: trans[x.group()], s)


def write_to_db(params):
    con = sqlite3.connect(os.path.join(dirname + '\db', real_estate_db))
    cur = con.cursor()
    create_table = (f'''CREATE TABLE IF NOT EXISTS RealEstate (scrape_date DATE, code text UNIQUE)''')
    cur.execute(create_table)

    columns = [_translate_umlauts(re.sub("[(/)]", "", i[1]).lower()) for i in cur.execute('PRAGMA table_info(RealEstate)')]
    #columns = [re.sub(" ", "_", i[1]) for i in columns]
    params['columns'] = [_translate_umlauts(re.sub("[(/)]", "", i).lower()) for i in params['columns']]
    # this step is just needed for teilmoebliert/ möbliert!!!!
    params['columns'] = [re.sub(" ", "_", i) for i in params['columns']]

    for idx,i in enumerate(params['columns']):
        if i not in columns:
            cur.execute(f'ALTER TABLE RealEstate ADD COLUMN {i} TEXT')
            rows = list(cur.execute(f'SELECT {i} FROM RealEstate'))
            con.commit()

    query_sign = ''.join(['?' if i == len(params['columns'])-1 else '?, ' for i in range(len(params['columns']))])
    cols = ''.join([i if i == params['columns'][-1] else i+', ' for i in params['columns']])


    """ write to db only if:
    1) the code is new
    2) the code is the same and last_change is different
    """
    sqlite_insert_with_param1 = f"""INSERT OR IGNORE INTO RealEstate ({cols}) VALUES ({query_sign}) ON CONFLICT(code) DO UPDATE SET last_change_date=excluded.last_change_date"""
    sqlite_insert_with_param2 = f"""INSERT OR UPDATE INTO RealEstate ({cols}) VALUES ({query_sign});"""
    sqlite_insert_with_param3 = f"""INSERT INTO RealEstate  ({cols}) VALUES ({query_sign});"""
    data_tuple = tuple(params['values'])
    cur.execute(sqlite_insert_with_param1, data_tuple)
    con.commit()
    con.close()


def run():
    con2 = sqlite3.connect(os.path.join(dirname + '\db', 'scrape2.sqlite'))
    cur2 = con2.cursor()
    cur2.execute(f"""SELECT * FROM scrape;""")
    rows = cur2.fetchall()
    fails = 0
    for idx, row in enumerate(rows):
        try:
            res = get_apartment_details(row[0])
            if res['values'][0] != None:
                try:
                    write_to_db(res)
                    cur2.execute(f"""DELETE FROM scrape WHERE url='{row[0]}';""")
                    con2.commit()
                    print(f"{idx}/{len(rows)}, price: {res['values'][0]}, col: {res['columns']}, val: {res['values']}{len(res['columns'])}")
                except sqlite3.OperationalError:
                    print("sqlite3.OperationalError. This are the col and values:")
                    print(
                        f"{idx}/{len(rows)}, price: {res['values'][0]}, col: {res['columns']}, val: {res['values']}{len(res['columns'])}")
                    pass
            else:
                if fails > 1:
                    settings = initialize_VPN(save=1, area_input=random.choices(area_input))
                    rotate_VPN(settings)
                    fails = 0
                else:
                    print(f"{idx}/{len(rows)}, Not possible to mine: {row[0]}")
                    print(
                        f"{idx}/{len(rows)}, price: {res['values'][0]}, col: {res['columns']}, val: {res['values']}{len(res['columns'])}")
                    fails += 1
                    pass
            rand = random.choices([0, 1], weights=(1, 1000), k=1)
            try:
                if rand[0] == 0:
                    print("rotate vpn")
                    #rotate_VPN()
            except:
                pass

        except AdvertaisementNotAvailableError as e:
            print(f"{idx}/{len(rows)}, AdvertaisementNotAvailableError: {row[0]} | {e}")
            cur2.execute(f"""DELETE FROM scrape WHERE url='{row[0]}';""")
            con2.commit()
            pass
        except RequestsError:
            settings = initialize_VPN(save=1, area_input=random.choices(area_input))
            rotate_VPN(settings)





run()