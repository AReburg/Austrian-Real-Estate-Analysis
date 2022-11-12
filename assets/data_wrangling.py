import warnings
warnings.simplefilter(action='ignore')
import pandas as pd
import numpy as np
import geopandas as gpd
import requests
import os
import pickle
import osmnx as ox
import re
import json
import logging
from pathlib import Path
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon
from shapely.geometry.multipolygon import MultiPolygon
from shapely import wkt
from scipy import spatial
from urllib.request import urlopen

cwd = Path().resolve()


class GeoData():
    def __int__(self):
        print(" ")

    def calc_comm(self, raw):
        if len(raw.value_counts()) < 2:
            if raw.value_counts().index.tolist()[0] == True:
                return 1

            else:
                return 0
        else:
            # eq: broker comm./(broker comm. + no broker comm.)
            return round(raw.value_counts().sort_index(ascending=False)[1] /
                         (raw.value_counts().sort_index(ascending=False)[0] +
                          raw.value_counts().sort_index(ascending=False)[1]), 2)


    def format_title(self, title, subtitle=None, subtitle_font_size=14):
        """        """
        title = f'<b>{title}</b>'
        if not subtitle:
            return title
        subtitle = f'<span style="font-size: {subtitle_font_size}px;">{subtitle}</span>'
        return f'{title}<br>{subtitle}'


    def get_geo_data(self, selector, source='online'):
        """ Load Austrian geojson"""
        if selector == 'municipal':
            if source == 'online':
                link = 'https://raw.githubusercontent.com/ginseng666/GeoJSON-TopoJSON-Austria/master/2021/simplified-99.5/gemeinden_995_geo.json'
                with urlopen(link, encoding='utf8') as response:
                    counties = json.load(response)
            else:
                with open(os.path.join(Path(cwd), 'data', 'geojson', 'gemeinden_999_geo.json'), encoding='utf8') as a:
                    counties = json.load(a)
        elif selector == 'district':
            if source == 'online':
                link = 'https://raw.githubusercontent.com/ginseng666/GeoJSON-TopoJSON-Austria/master/2021/simplified-99.9/bezirke_999_geo.json'
                with urlopen(link, encoding='utf8') as response:
                    counties = json.load(response)
            else:
                with open(os.path.join(Path(cwd), 'data', 'geojson', 'bezirke_999_geo.json'), encoding='utf8') as a:
                    counties = json.load(a)
        elif selector == 'state':
            if source == 'online':
                link = 'https://raw.githubusercontent.com/ginseng666/GeoJSON-TopoJSON-Austria/master/2021/simplified-99.9/laender_999_geo.json'
                with urlopen(link, encoding='utf8') as response:
                    counties = json.load(response)
            else:
                with open(os.path.join(Path(cwd), 'data', 'geojson', 'laender_999_geo.json'), encoding='utf8') as a:
                    counties = json.load(a)
        return counties


    def import_data(self):
        """ import the airbnb data """
        return pd.read_csv('./data/data_fin.csv', sep=',', encoding='utf-8', index_col=False)