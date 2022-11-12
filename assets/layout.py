from dash import dcc, html
import pandas as pd
from assets import charts
import logging
# import dash_bootstrap_components as dbc
import dash_dangerously_set_inner_html
import dash_bootstrap_components as dbc

def layout(app, df):

    layout = html.Div([
        # left half of the web page
        html.Div([
            html.Div([html.Img(src=app.get_asset_url('logo.png'), height='21 px', width='auto')],
                     className='col-2', style={'align-items': 'center', 'padding-top': '1%', 'height': 'auto'}),
            html.Div(dash_dangerously_set_inner_html.DangerouslySetInnerHTML(
                """
                <h2>AUSTRIAN HOUSING MARKET</h2>
                A machine learning pipline has been established, where OSM features are used for price modelling. These features include
                the count of restaurants, bars, cafes, subway station tourist destinations etc. within a walking distance.  
                However, this model ist just a case study how OpenStreetMap features can be used together with other property types,
                such as accommodation capacity and other property features.<br/>
                <br/>
                The data has been pre-processed and is available <a href="https://github.com/AReburg/Airbnb-Price-Prediction/", target="_blank">
                here</a>. All the data manipulation and the modelling steps
                are described in this 
                <a href="https://github.com/AReburg/", target="_blank">jupyter notebook</a>.
                <br/><br/>""")),
            html.Div([dcc.Dropdown(
                ["rented flat", "single family home", 'condo'],
                placeholder="Select geospatial resolution", id='property_type', value="rented flat",
            )], className='Select-value'),

            html.P("Select geospatial resolution:"),
            html.Div([dcc.Dropdown(
                ["municipal", "district", 'state'],
                placeholder="Select geospatial resolution", id='resolution', value="district",
            )], className='Select-value'),
            html.P(""),
            html.P(""),
            ], className='four columns div-user-controls'),

        # right half of the web page
        html.Div([
            html.Div([dcc.Graph(id="graph", figure={}, config={'displayModeBar': False})]),
            html.Br(),
            html.Br(),
        ], className='eight columns div-for-charts bg-grey')
    ])
    return layout

