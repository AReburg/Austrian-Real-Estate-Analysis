from time import sleep
import random
import logging
import os
from time import time
from collections import OrderedDict
from datetime import datetime
import sqlite3
import requests
from bs4 import BeautifulSoup
import urllib
import re
import helpers

if __name__ == '__main__':

    graz_apartment_links = helpers.get_all_urls()
    print(graz_apartment_links)
    for url in graz_apartment_links:
        params = helpers.get_apartment_details(url)
        helpers.write_to_db(params)
