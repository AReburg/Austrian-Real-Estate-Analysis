#-----------------------------------------------------------------------------------------------------------------------
# Scrape willhaben real estate data
#
# pipreqs C:\Users\klara\Documents\GitHub\WillhabenScrape
# pip3 freeze > requirements.txt  # Python3

# Scraping Austrian real estate properties from Willhaben
# Date: 06.03.2022
# Links:
## https://stackoverflow.com/questions/16248723/how-to-find-spans-with-a-specific-class-containing-specific-text-using-beautiful
# https://stackoverflow.com/questions/8112922/beautifulsoup-innerhtml
# https://www.regextester.com/99555
# https://regex101.com/r/hByf5o/1
# https://www.sqlite.org/lang_update.html
# \b[0-9]{1,3}(,[0-9]{3})*(\.[0-9]+)?\b|\.[0-9]+\b
# \b\d{1,3}(.\d{3})*(\.[0-9]+)?\b|\,[0-9]+\b
# https://www.regextester.com/99555
# https://www.reddit.com/r/learnpython/comments/tf3929/my_career_path_going_from_zero_experience_to_a_sr/
# # url = "https://www.willhaben.at/iad/immobilien/eigentumswohnung/eigentumswohnung-angebote?&rows=5&areaId=601&parent_areaid=6"
#     soupString = str(soup)
#     #post_code = re.search('post_code":"(.*?)"', soupString)
#     #price = re.search('price":"(.*?)"', soupString)
#     #rooms = re.search('rooms":"(.*?)"', soupString)
#     #print("This is apartment in " + post_code.group(1) + ", with " + rooms.group(1) + " rooms, price is " + price.group(1) + ".")
#     # spans = soup.find_all('span', {'class' : 'Text-sc-10o2fdq-0 bZUXUD'})
#     #
#-----------------------------------------------------------------------------------------------------------------------
from time import sleep
import random
import logging
import os
#from nordvpn_switcher import initialize_VPN, rotate_VPN, terminate_VPN
from time import time
from collections import OrderedDict
from datetime import datetime
import sqlite3
import requests
from bs4 import BeautifulSoup
import urllib
import re

dirname = os.path.dirname(__file__)
real_estate_db = 'real_estate.sqlite'
area_postal_codes = 'area_codes.json'
headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36"}
svg = """<svg class="createSvgIcon__SvgIcon-sc-1vebdtk-0 fKmYTO" height="1em" pointer-events="none" viewbox="0 0 24 24" width="1em" xmlns="http://www.w3.org/2000/svg"><path d="M21.71 5.29a1 1 0 0 0-1.42 0L9 16.58l-5.28-5.29a1 1 0 0 0-1.41 1.41l6 6a1 1 0 0 0 1.42 0l12-12a1 1 0 0 0-.02-1.41Z" fill="currentColor"></path></svg>"""

bundesland = ['oberoesterreich']#, 'steiermark', 'salzburg', 'wien', 'vorarlberg', 'burgenland', 'niederoesterreich',
            #  'kaernten', 'tirol']
wohnung = ['eigentumswohnung', 'mietwohnungen']
end_page = 4
rows_shown = 4



def remove_umlaut(string):
    """ Removes umlauts from strings and replaces them with the letter+e convention
    """
    u = 'ü'.encode()
    U = 'Ü'.encode()
    a = 'ä'.encode()
    A = 'Ä'.encode()
    o = 'ö'.encode()
    O = 'Ö'.encode()
    ss = 'ß'.encode()

    string = string.encode()
    string = string.replace(u, b'ue')
    string = string.replace(U, b'Ue')
    string = string.replace(a, b'ae')
    string = string.replace(A, b'Ae')
    string = string.replace(o, b'oe')
    string = string.replace(O, b'Oe')
    string = string.replace(ss, b'ss')

    string = string.decode('utf-8')
    return string


def innerHTML(element):
    """Returns the inner HTML of an element as a UTF-8 encoded bytestring"""
    return element.encode_contents()


def get_additional_apartment_details(soup, url):
    title = []
    value = []
    try:
        price = innerHTML(soup.find('span', {
            'class': 'Text-sc-10o2fdq-0 PriceInformationAttributesBox___StyledText-sc-1a44msw-0 dZQwG iuZZCU'})).decode(
            "utf-8")
        value.append(price)
    except:
        value.append(None)
        pass
    title.append('Preis')
    title.append('scrape_date')
    now = datetime.now()
    scrape_date = "{}.{}.{} {}:{}".format(now.day, now.month, now.year, now.hour, now.minute)
    value.append(scrape_date)

    title.append('Type')
    if url.find('eigentumswohnung'):
        value.append('Eigentumswohnung')
    elif url.find('mietwohnung'):
        value.append('Mietwohnung')

    try:
        makler = innerHTML(
            soup.find('span', {'data-testid': 'price-information-freetext-attribute-value-0'})).decode("utf-8")
        title.append('Makler')
        value.append(makler)
    except AttributeError as error:
        pass
    try:
        zusatz = innerHTML(
            soup.find('span', {'data-testid': 'price-information-freetext-attribute-value-1'})).decode("utf-8")
        title.append('Zusatz')
        value.append(zusatz)
    except AttributeError as error:
        pass

    last_change = innerHTML(soup.find('span', {'data-testid': 'ad-detail-ad-edit-date-top'})).decode("utf-8")
    change = re.findall(r'(\d{2}.\d{2}.\d{4})', last_change)
    title.append('LetzteAenderung')
    value.append(change[0])

    header_title = innerHTML(soup.find('h1', {'data-testid': 'ad-detail-header'})).decode("utf-8")
    title.append('Header')
    value.append(header_title)

    willhaben_code = innerHTML(soup.find('span', {'data-testid': 'ad-detail-ad-wh-code-top'})).decode("utf-8")
    code = re.findall(r'(\d{9})', willhaben_code)[0]
    title.append('WillhabenCode')
    value.append(code)
    title.append('Url')
    value.append(url)

    object_standort = innerHTML(soup.find('div', {'data-testid': 'object-location-address'})).decode("utf-8")
    title.append('ObjektStandort')
    value.append(object_standort)

    return [title, value]


def get_apartment_details(url):
    """Get all the details of the appartment. """
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    [title, value] = get_additional_apartment_details(soup, url)

    results = OrderedDict()
    results['columns'] = title
    results['values'] = value
    return results
    """
    debug = False
    spans = soup.find_all('span', {'class': 'Text-sc-10o2fdq-0 bZUXUD'})
    value_span = soup.find_all('div', {'data-testid': 'attribute-value'})
    print(f"{len(spans)}, {len(value_span)}")
    print(f"{spans}, \n{value_span}")
    for i in spans:
        # title.append(re.sub('[^A-Za-z0-9]+', '', innerHTML(i).decode("utf-8")))
        without_umlaute = helpers.remove_umlaut(innerHTML(i).decode("utf-8"))
        title.append(re.sub('[^A-Za-z0-9]+', '', without_umlaute))


    for i in value_span:
        if innerHTML(i).decode("utf-8") == svg:
            value.append("True")
        elif innerHTML(i).decode("utf-8").find(' m²')>0:
            val = innerHTML(i).decode("utf-8").split(' m²')[0]
            value.append(val)
        else:
            value.append(helpers.remove_umlaut(innerHTML(i).decode("utf-8")))

    if debug:
        try:
            for idx,j in enumerate(title):
                val = value[idx]
                # print(f"{j}: {val}")
        except IndexError as error:
            pass
        """

def get_all_urls():
    """ Get all urls initially. Afterwards for each url the data is scraped."""
    apartment_links = []
    for land in bundesland:
        for wohnungs_typ in wohnung:
            for i in range(1,end_page):
                url = (f'https://www.willhaben.at/iad/immobilien/{wohnungs_typ}/{land}?rows={rows_shown}&page={i}')
                # print(url)
                response = requests.get(url, headers=headers)
                soup = BeautifulSoup(response.text, 'html.parser')
                for link in soup.find_all('a'):
                    url2 = link.get('href')
                    # print(url)
                    if url2 != "#" and url2 != None and url2.startswith((f"/iad/immobilien/d/{wohnungs_typ}/{land}")):
                        apartment_links.append("https://www.willhaben.at" + url2)
    return apartment_links


def write_to_db(params):
    print(f"col: {params['columns']}, {len(params['columns'])}")
    print(f"val: {params['values']}, {len(params['values'])}")
    con = sqlite3.connect(os.path.join(dirname + '\db', real_estate_db))
    cur = con.cursor()
    create_table = (f'''CREATE TABLE IF NOT EXISTS RealEstate (scrape_date DATE, WillhabenCode text)''')
    cur.execute(create_table)

    columns = [i[1] for i in cur.execute('PRAGMA table_info(RealEstate)')]

    for idx,i in enumerate(params['columns']):
        if i not in columns:
            cur.execute(f'ALTER TABLE RealEstate ADD COLUMN {i} TEXT')
            rows = list(cur.execute(f'SELECT {i} FROM RealEstate'))
            # print(f'{i}  {rows}')
            con.commit()
    query = ''
    for idx, i in enumerate(params['columns']):
        if idx == len(params['columns'])-1:
            query = query+ '?'
        else:
            query = query + '?, '
    col = ''
    for idx, i in enumerate(params['columns']):
        if idx == len(params['columns']) - 1:
            col = col + f'{i}'
        else:
            col = col + f'{i}, '

    sqlite_insert_with_param = f"""INSERT OR IGNORE INTO RealEstate  ({col}) VALUES ({query});"""
    data_tuple = tuple(params['values'])
    # print(f"{sqlite_insert_with_param}")
    # print(f"{data_tuple}")
    cur.execute(sqlite_insert_with_param, data_tuple)
    con.commit()
    con.close()
