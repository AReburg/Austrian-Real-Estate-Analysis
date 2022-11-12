from pathlib import Path
from dash.dependencies import Output, Input
import dash_bootstrap_components as dbc
cwd = Path().resolve()
from assets.data_wrangling import GeoData
from assets import charts
from dash import dcc, html
data = GeoData()
import numpy as np
import pandas as pd
import logging
from assets.data_wrangling import GeoData
data = GeoData()



def register_callbacks(app, dfx):
    dfi = dfx.copy()

    @app.callback(
        Output("graph", "figure"),
        [Input("property_type", "value"), Input("resolution", "value")])
    def display_choropleth(property_type, resolution):
        """ selector specifies the geographic resolution """

        dfi['count'] = np.nan
        feat_key = ''
        locations = ''
        hover_data = ''
        opacity = 0.55

        if property_type == 'rented flat':
            dfj = dfi[(dfi['type'].str.contains('rented flat', na = False)) & (dfi['rooms'] < 6)].copy()
        elif property_type == 'condo':
            dfj = dfi[(dfi['type'].str.contains('condominium', na = False))].copy()
        elif property_type == 'single family home':
            dfj = dfi[(dfi['type'].str.contains('single-family home', na = False))].copy()


        if resolution == 'municipal':
            feat_key = "properties.iso"
            locations = "GKZ"
            hover_data = ["GKZ", "Bezirk", "Bundesland", "count"]
            hover_name = "GKZ"
            text = {'price': 'mean', 'price_sqrt': 'mean', 'Bezirk': 'first', 'Bundesland': 'first', 'count': 'size'}

        elif resolution == 'district':
            feat_key = "properties.name"
            locations = "Bezirk"
            hover_data = ["Bundesland", "Bezirk", "count"]
            hover_name = "Bezirk"
            text = {'price': 'mean', 'price_sqrt': 'mean', 'Bundesland': 'first', 'count': 'size'}

        elif resolution == 'state':
            feat_key = "properties.name"
            locations = "Bundesland"
            hover_data = ["Bundesland", "count"]
            hover_name = "Bundesland"
            text = {'price': 'mean', 'price_sqrt': 'median', 'count': 'size'}

        d = dfj.groupby([locations], as_index=False).agg(text)
        return charts.get_price_chart(d, feat_key, locations, resolution, hover_name, hover_data, opacity)

