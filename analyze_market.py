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

import numpy as np


def gkz(a):
    try:
        arr = np.where(a==df_lookup['plz'], a, 999)
        return arr
    except IndexError:
        return None


def get_geo_data(selector, source='online'):
    """ Load Austrian geojson
     counties["features"][0]['properties']['iso']
    https://github.com/ginseng666/GeoJSON-TopoJSON-Austria/blob/master/2021/simplified-99.9/laender_999_geo.json """
    if selector == 'gemeinden':
        if source == 'online':
            link = 'https://raw.githubusercontent.com/ginseng666/GeoJSON-TopoJSON-Austria/master/2021/simplified-99.5/gemeinden_995_geo.json'
            with urlopen(link) as response:
                counties = json.load(response)
        else:
            with open("./data/gemeinden_999_geo.json") as a:
                counties = json.load(a)
    elif selector == 'bezirk':
        if source == 'online':
            link = 'https://raw.githubusercontent.com/ginseng666/GeoJSON-TopoJSON-Austria/master/2021/simplified-99.9/bezirke_999_geo.json'
            with urlopen(link) as response:
                counties = json.load(response)
        else:
            with open("./data/bezirke_999_geo.json") as a:
                counties = json.load(a)
    elif selector == 'laender':
        if source == 'online':
            link = 'https://raw.githubusercontent.com/ginseng666/GeoJSON-TopoJSON-Austria/master/2021/simplified-99.9/laender_999_geo.json'
            with urlopen(link) as response:
                counties = json.load(response)
        else:
            with open("./data/laender_999_geo.json") as a:
                counties = json.load(a)

    return counties


def load_data():
    # load lookup data
    df_lookup = pd.read_csv(r'laender_lookup.csv', sep=';')
    df_lookup_l = pd.read_csv(r'counties_lookup.csv', sep=';')

    # Load data from db
    con = sqlite3.connect("./db/real_estate.sqlite")
    df = pd.read_sql_query("SELECT * FROM RealEstate", con)
    con.close()

    # Set dtypes of the dataframe
    df['Type'] = df['Type'].astype('category', errors='ignore')
    df['plz'] = df.plz.fillna(0).astype("int64", errors='ignore')
    # print(df['count'].head())
    df_lookup['plz'] = df_lookup.plz.astype("int64")
    df_lookup['cc'] = df_lookup.cc.astype("int64")
    df_lookup_l['county'] = df_lookup_l.bundesland.astype("category")
    df_lookup_l['bezirk'] = df_lookup_l.bezirk.astype("category")
    df_lookup_l['plz'] = df_lookup_l.plz.astype("int64")
    df['price'] = df['price'].fillna(0)#.astype('int', errors='ignore')
    df['price'] = pd.to_numeric(df['price'], errors='coerce')

    # merge dataframem with lookup table
    df = df.merge(df_lookup[['plz','cc']], on=['plz'])
    df = df.merge(df_lookup_l[['plz','county', 'bezirk']], on=['plz'])
    #df_new['cc'] = df_new['cc'].fillna(0).astype('int', errors='ignore')
    #df_new['cc'] = df_new['cc'].astype('str', errors='ignore')
    # df = df.groupby('cc', as_index=False)
    #df.price = df.price.mean()
    #print(df['plz'])
    # print(df.price)
    return df


def make_graph(df, geo_data, sel='gemeinden'):
    feat_key = ''
    locations = ''
    if sel == 'gemeinden':
        feat_key = "properties.iso"
        locations = "cc"
    elif sel == 'laender':
        feat_key = "properties.name"
        locations = "county"
    elif sel == 'bezirk':
        feat_key = "properties.name"
        locations = "bezirk"
    fig = px.choropleth_mapbox(df, geojson=geo_data, locations=locations,
                               featureidkey=feat_key, color="price",
                               #hover_name = 'plz',
                               hover_data = ['price'], #'county' 'cc',
                               color_continuous_scale="Viridis",
                               range_color=(df['price'].mean()*(1-0.3), df['price'].mean()*(1+0.3)),
                               mapbox_style="carto-positron",
                               zoom=6, center = {"lat": 47.809490, "lon": 13.055010},
                               opacity=0.25,
                               labels={'price':'price'}
                              )
    fig.update_layout(margin={"r":10,"t":30,"l":40,"b":10})
    fig.show()


def manipulate_data(df, sel='gemeinden'):
    # print(f"{df['price'].mean()}")
    #f['plz'] = df['plz'].astype('category', errors='ignore')
    #df['count'] = df['cc'].value_counts()
    #print(df['count'])
    df2 = df.copy()
    #print(df2.columns)
    # print(df.groupby(['cc'], as_index=False).groups.keys())
    # print(df.groupby(['cc'], as_index=False)['price'].mean())
    if sel == 'gemeinden':
        df2 = df2.groupby(['cc'], as_index=False).agg({'price': 'mean', 'plz': 'first', 'county': 'first'})
    elif sel == 'laender':
        df2 = df2.groupby(['county'], as_index=False).agg({'price': 'mean', 'plz': 'first'})
    elif sel == 'bezirk':
        df2 = df2.groupby(['bezirk'], as_index=False).agg({'price': 'mean', 'county': 'first'})
    df2['price'] = df2['price'].round(0)
    return df2

df = load_data()
res = 'bezirk'  # bezirk, laender
df2 = manipulate_data(df, res)
geo_data = get_geo_data(res, source='offline')
make_graph(df2, geo_data, res)
