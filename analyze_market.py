from time import sleep
import random
import logging
import os
import pandas as pd
import plotly.express as px
from datetime import datetime
from bs4 import BeautifulSoup
from collections import OrderedDict
from urllib.request import urlopen
import json
import sqlite3
import requests
import urllib
import re


dirname = os.path.dirname(__file__)

""" load all Austrian area codes source: 
https://www.data.gv.at/katalog/dataset/rtr_postleitzahlen/resource/546e7e91-26aa-473c-9214-dbf528726128 
https://de.wikipedia.org/wiki/Amtlicher_Gemeindeschl%C3%BCssel
gemeinde liste: https://secure.umweltbundesamt.at/edm_portal/redaList.do;jsessionid=59B9C7B2CFD801671BD5A24791259EB0.edmportalnode01?seqCode=cwzqtv5r84nvpr&entireLsq=true
"""


def gkz(a):
    try:
        pattern = re.compile(r"(?<!\d)\d{4,7}(?!\d)")
        plz = pattern.findall(a)[0]
        return plz
    except IndexError:
        return None


def get_geo_data(selector):
    """ Load Austrian geojson
    https://github.com/ginseng666/GeoJSON-TopoJSON-Austria/blob/master/2021/simplified-99.9/laender_999_geo.json """
    if selector == 'gemeinden':
        link = 'https://raw.githubusercontent.com/ginseng666/GeoJSON-TopoJSON-Austria/master/2021/simplified-99.5/gemeinden_995_geo.json'
    elif selector == 'bezirke':
        link = 'https://raw.githubusercontent.com/ginseng666/GeoJSON-TopoJSON-Austria/master/2021/simplified-99.9/bezirke_999_geo.json'
    elif selector == 'laender':
        link = 'https://raw.githubusercontent.com/ginseng666/GeoJSON-TopoJSON-Austria/master/2021/simplified-99.9/laender_999_geo.json'

    with urlopen(link) as response:
        counties = json.load(response)
    return counties


def load_data():
    con = sqlite3.connect("./db/real_estate2.sqlite")
    df = pd.read_sql_query("SELECT * FROM RealEstate", con)
    con.close()
    df_lookup = pd.read_csv (r'laender_lookup.csv', sep = ';')
    print(df_lookup.cc)
    df_new = df

    df_new['plz']  = df['location'].apply(gkz)


    df_new['plz'] = df_new.plz.astype("int64")
    df_lookup['plz'] = df_lookup.plz.astype("int64")
    df_new= df_new.merge(df_lookup['cc'], how='outer', left_on='plz', right_on='cc')
    df_new['cc'] = df_new['cc'].fillna(0).astype('int', errors='ignore')
    df_new['cc'] = df_new['cc'].astype('str', errors='ignore')
    df_new['price'] = df_new['price'].fillna(0).astype('int', errors='ignore')
    plz_dat = pd.read_csv (r'plz.csv', sep = ';')

    # print(plz_dat)
    #df_new= df_new.merge(plz_dat, how='outer', left_on='plz', right_on=['bezirk', 'bundesland'])

    #df_new.groupby(df_new['cc']).mean()
    #print(df_new.head())
    #print(df_new['cc'])
    return df_new

def make_graph(df, geo_data):
    fig = px.choropleth_mapbox(df, geojson=geo_data, locations="cc",
                               featureidkey="properties.iso", color="price",
                               color_continuous_scale="Viridis",
                               range_color=(0, df['price'].max),
                               mapbox_style="carto-positron",
                               zoom=2, center = {"lat": 48.208176, "lon": 16.373819},
                               opacity=0.1
                               #labels={'price':'price'}
                              )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.show()


df = load_data()
geo_data = get_geo_data('gemeinden') # bezirke, laender
# make_graph(df, geo_data)

