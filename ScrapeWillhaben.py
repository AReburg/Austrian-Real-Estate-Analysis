#-----------------------------------------------------------------------------------------------------------------------
# Scrape willhaben real estate data
#
# Scraping Austrian real estate properties from Willhaben
# Date: 06.03.2022
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
#-----------------------------------------------------------------------------------------------------------------------

vpn_rotation = True

dirname = os.path.dirname(__file__)
real_estate_db = 'real_estate.sqlite'
area_postal_codes = 'area_codes.json'



def printTime(start):
    end = time.time()
    duration = end - start
    if duration < 60:
        return "" + str(round(duration, 2)) + "s"
    else:
        mins = int(duration / 60)
        secs = round(duration % 60, 2)
        if mins < 60:
            return "" + str(mins) + "m " + str(secs) + "s"
        else:
            hours = int(duration / 3600)
            mins = mins % 60
            return "" + str(hours) + "h " + str(mins) + "m " + str(secs) + "s"



def get_apartment_details(url):
    fp = urllib.request.urlopen(url)
    mybytes = fp.read()
    mystr = mybytes.decode("ISO-8859-1")
    fp.close()
    soup = BeautifulSoup(mystr, 'html.parser')
    soupString = str(soup)
    post_code = re.search('post_code":"(.*?)"', soupString)
    price = re.search('price":"(.*?)"', soupString)
    rooms = re.search('rooms":"(.*?)"', soupString)
    print("This is apartment in " + post_code.group(1) + ", with " + rooms.group(1) + " rooms, price is " + price.group(
        1) + ".")


if __name__ == '__main__':

        con = sqlite3.connect(os.path.join(dirname + '\db', real_estate_db))
        cur = con.cursor()
        create_table = (
            f'''CREATE TABLE IF NOT EXISTS RealEstate (
            code int UNIQUE, \
            publish_date date, \
            closing_date date, \
            changing_date text, \
            title text, \
            area_code int, \
            location text,\
            living_area float, \
            room_count float, \
            price float)''')
        cur.execute(create_table)


        params = (
            1234, # inserate uid
            datetime.now(),
            datetime.now(),
            '01.01.2022',
            'This is the title',
            5020,
            'Salzburg',
            50.3,
            3, #rooms
            340000 # price
        )
        # https://stackoverflow.com/questions/3634984/insert-if-not-exists-else-update
        # https://stackoverflow.com/questions/418898/sqlite-upsert-not-insert-or-replace
        # check if uid already in db.
        #if cur.execute("SELECT EXISTS(SELECT 1 FROM RealEstate WHERE changing_date = '01.01.2022')").fetchone() == (1,):
        # response = self.connection.execute("SELECT EXISTS(SELECT 1 FROM invoices WHERE id=?)", (self.id, ))
        #response = cur.execute("SELECT EXISTS(SELECT 1 FROM RealEstate WHERE code =?)", (1234, ))
        cur.execute("SELECT code FROM RealEstate WHERE code =?", (1234,))
        if cur.fetchone():
            print("Found!")
        else:
            print("Not found...")

        execute = (f"""INSERT OR IGNORE INTO RealEstate VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""")
        cur.execute(execute, params)
        con.close()




#url = 'https://www.willhaben.at/iad/immobilien/eigentumswohnung/eigentumswohnung-angebote?sfId=09b56e0d-d01c-48fe-b70c-3007a032c6d9&isNavigation=true'
#area_id = '8020'
#for i in range(4):
#    url2 = f'{url}&page={i}&areaId={area_id}'
#    print(url2)
#import urllib.request
#user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
#headers={'User-Agent':user_agent,}
#url ='"https://www.willhaben.at/iad/immobilien/eigentumswohnung/eigentumswohnung-angebote?&rows=100&areaId=601&parent_areaid=6"'
#request=urllib.request.Request(url,None,headers)
#fp = urllib.request.Request(url,None,headers)

graz_apartment_links = []

url = "https://www.willhaben.at/iad/immobilien/eigentumswohnung/eigentumswohnung-angebote?&rows=100&areaId=601&parent_areaid=6"
#fp = urllib.request.urlopen(
#    )
#mybytes = fp.read()
#mystr = mybytes.decode("ISO-8859-1")
#fp.close()
#soup = BeautifulSoup(mystr, 'html.parser')

from requests_html import HTMLSession
session = HTMLSession()

def get_page(url):
    """ loads a webpage into a string """
    src = ''

    #req = urllib2.Request(url)
    r = session.get(url)
    t=  r.html.render()
    return r.html.html

    #response = requests.get(url)
    #return response.text


#soup = BeautifulSoup(, 'html.parser')
print(get_page(url))


for link in soup.find_all('a'):
    url = link.get('href')
    print(url)
    if url != "#" and url != None and url.startswith(("/iad/immobilien/d/eigentumswohnung/steiermark/graz/")):
        graz_apartment_links.append("https://www.willhaben.at" + url)

for url in graz_apartment_links:
    get_apartment_details(url)
    # print(url)