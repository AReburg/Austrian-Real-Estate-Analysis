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
import numpy as np
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



def get_commission(raw):
    if raw is None:
        return 'No broker commission'
    elif raw.find('keine') > 0 or raw.find('frei') > 0 or raw.find('nein') > 0 or raw.find('Fixpreis') > 0 or raw == 'NaN':
        return 'No broker commission'
    else:
        return 'Broker commission'

def get_geo_data(selector, source='online'):
    """ Load Austrian geojson
     counties["features"][0]['properties']['iso']
    https://github.com/ginseng666/GeoJSON-TopoJSON-Austria/blob/master/2021/simplified-99.9/laender_999_geo.json """
    if selector == 'gemeinden':
        if source == 'online':
            link = 'https://raw.githubusercontent.com/ginseng666/GeoJSON-TopoJSON-Austria/master/2021/simplified-99.5/gemeinden_995_geo.json'
            with urlopen(link, encoding='utf8') as response:
                counties = json.load(response)
        else:
            with open("./data/gemeinden_999_geo.json", encoding='utf8') as a:
                counties = json.load(a)
    elif selector == 'bezirk':
        if source == 'online':
            link = 'https://raw.githubusercontent.com/ginseng666/GeoJSON-TopoJSON-Austria/master/2021/simplified-99.9/bezirke_999_geo.json'
            with urlopen(link, encoding='utf8') as response:
                counties = json.load(response)
        else:
            with open("./data/bezirke_999_geo.json", encoding='utf8') as a:
                counties = json.load(a)
    elif selector == 'laender':
        if source == 'online':
            link = 'https://raw.githubusercontent.com/ginseng666/GeoJSON-TopoJSON-Austria/master/2021/simplified-99.9/laender_999_geo.json'
            with urlopen(link, encoding='utf8') as response:
                counties = json.load(response)
        else:
            with open("./data/laender_999_geo.json", encoding='utf8') as a:
                counties = json.load(a)
    return counties


def load_data():
    # load lookup data
    df_lookup = pd.read_csv(r'laender_lookup.csv', sep=';')
    df_lookup_l = pd.read_csv(r'counties_lookup.csv', sep=';', encoding='latin1')

    # Load data from db
    con = sqlite3.connect("./db/real_estate.sqlite")
    df = pd.read_sql_query("SELECT * FROM RealEstate", con)
    con.close()

    # Set dtypes of the dataframe
    df['Type'] = df['Type'].astype('category', errors='ignore')
    df['plz'] = df.plz.fillna(0).astype("int64", errors='ignore')

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
    df['commission'] = df['Makler'].apply(get_commission)
    return df


def make_graph(df, sel='gemeinden'):
    geo_data = get_geo_data(sel, source='offline')
    feat_key = ''
    locations = ''
    hover_name = ''
    hover_data = []
    if sel == 'gemeinden':
        feat_key = "properties.iso"
        locations = "cc"
        hover_name = 'plz'
        hover_data = ['plz', 'bezirk', 'county', 'cc', 'price', 'commission']
    elif sel == 'laender':
        feat_key = "properties.name"
        locations = "county"
        hover_name = "county"
        hover_data = ['price', 'commission']
    elif sel == 'bezirk':
        feat_key = "properties.name"
        locations = "bezirk"
        hover_name = "bezirk"
        hover_data = ['bezirk', 'county', 'price', 'commission']
    fig = px.choropleth_mapbox(df, geojson=geo_data, locations=locations,
                               featureidkey=feat_key, color="price",
                               hover_name = hover_name,
                               hover_data = hover_data,
                               color_continuous_scale="Viridis",
                               range_color=(df['price'].mean()*(1-0.3), df['price'].mean()*(1+0.3)),
                               mapbox_style="carto-positron",
                               zoom=7, center = {"lat": 47.809490, "lon": 13.055010},
                               opacity=0.25,
                               labels={'price':'price'}
                              )
    fig.update_layout(margin={"r":10,"t":30,"l":40,"b":10})
    fig.show()


def calc_comm(raw):
    # todo: erstes if noch "falsch"
    if len(raw.value_counts()) < 2:
        return raw.value_counts()[0]
    else:
        return round(raw.value_counts()[0]/(raw.value_counts()[0]+raw.value_counts()[1]), 1)


def manipulate_data(df, sel='gemeinden'):
    df2 = df.copy()
    if sel == 'gemeinden':
        df2 = df2.groupby(['cc'], as_index=False).agg({'price':'mean', 'bezirk':'first', 'plz':'first', 'county':'first', 'commission':calc_comm})
    elif sel == 'laender':
        df2 = df2.groupby(['county'], as_index=False).agg({'price': 'mean', 'plz': 'first', 'commission' : calc_comm})
    elif sel == 'bezirk':
        df2 = df2.groupby(['bezirk'], as_index=False).agg({'price': 'mean', 'county': 'first', 'commission' : calc_comm})
    df2['price'] = df2['price'].round(0)
    return df2

df = load_data()
res = 'bezirk'  # bezirk, laender
df2 = manipulate_data(df, res)
print(df2.head(10))
make_graph(df2, res)

