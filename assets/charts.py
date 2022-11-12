import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from pathlib import Path
import geojson
import logging
from assets.data_wrangling import GeoData
data = GeoData()

cwd = Path().resolve()
token = open(os.path.join(Path(cwd), 'assets', '.mapbox_token')).read()


def get_pie_chart(df):
    """ generates the pie chart with the three main genres of the categories """
    fig = go.Figure(data=[go.Pie(values=df.genre.value_counts().to_list(), labels=df.genre.unique(), textinfo='label',
                                      insidetextorientation='radial', hole=.25, marker_colors=night_colors)])
    fig.update_layout(legend_font_size=14, font=dict(family="Open Sans"))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.update(layout_showlegend=False)
    fig.update_traces(marker=dict(line=dict(color='#9c9c9c', width=1.5)))
    fig.update_traces(opacity=0.7)
    return fig

def aggregate_data(df, group='', agge='', rename=''):
    """ function to group, aggregate and rename the dataframe """
    df = df.groupby([group]).agg(agge)
    df.columns = df.columns.droplevel(0)
    df.columns = rename
    df.reset_index(drop=True, inplace=True)
    return df


def heatmap_airbnb_prices(df, title=''):
    """
    interesting: https://stackoverflow.com/questions/71104827/plotly-express-choropleth-map-custom-color-continuous-scale
    """
    districts = get_geo_data()
    k = aggregate_data(df, 'neighbourhood', {'neighbourhood': ['first'], 'price': ['median']}, \
                       rename=['district', 'median'])
    k['median'] = k['median'].astype('category')
    k.sort_values(by='median', ascending=False, inplace=True)
    dfz = k.groupby(['median']).agg({'median': ['first']})
    dfz.columns = dfz.columns.droplevel(0)
    dfz.columns = ['price']
    dfz.reset_index(drop=True, inplace=True)
    dfz.sort_values(by='price', ascending=False, inplace=True)
    dfz = dfz['price'].tolist()
    dicts = {}
    farbe = px.colors.cyclical.IceFire[0:len(dfz)]
    for i, j in zip(dfz, farbe):
        dicts[i] = f'{i} $'
    cols = k['median'].map(dicts)

    fig = px.choropleth_mapbox(k, geojson=districts, locations=k['district'], featureidkey="properties.name",
                               color=cols,
                               title=title,
                               color_discrete_sequence=farbe,
                               # color_discrete_sequence=px.colors.qualitative.Prism,
                               labels={'median': 'price per night'},
                               mapbox_style="open-street-map", zoom=10, center={"lat": 48.210033, "lon": 16.363449},
                               opacity=0.60)
    fig.add_scattermapbox(
        lat=df['latitude'].tolist(),
        lon=df['longitude'].tolist(),
        mode='markers',
        showlegend=False,
        marker_size=3,
        marker_color='#F3F5F6',
        opacity=0.3,
        hoverinfo='skip'
    )
    fig.update_layout(mapbox_style="light", mapbox_accesstoken=token)
    fig.update_layout(legend={"title": "price per night"})
    fig.update_layout(font=dict(family="Helvetica"))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


def heatmap_airbnb_listings(df, title=''):
    """
    https://plotly.com/python/builtin-colorscales/
    """
    districts = get_geo_data()
    agg = df.groupby('neighbourhood').agg(nr_listings = ('id', 'count')).reset_index().sort_values('nr_listings', ascending=False)
    agg['ratio'] = 100 * agg['nr_listings'] / agg['nr_listings'].sum()
    agg['nr_listings'] = agg['nr_listings'].astype('category')
    agg.sort_values(by='nr_listings', ascending = False, inplace=True)
    fig = px.choropleth_mapbox(agg, geojson=districts, locations=agg['neighbourhood'], featureidkey="properties.name",
                               color_discrete_sequence=px.colors.cyclical.IceFire, #px.colors.sequential.Plasma_r, #px.colors.qualitative.Dark24,
                               color=agg['nr_listings'],
                               #color=agg['ratio'],
                               title=title,
                               labels={'nr_listings':'Nr. of listings'},
        mapbox_style="open-street-map", zoom=10, center = {"lat": 48.210033, "lon": 16.363449}, opacity=0.30)
    neighbourhood = agg['neighbourhood'].tolist()
    nr = agg['nr_listings'].tolist()
    for i,trace in enumerate (fig.data):
        trace.update(name=f'{nr[i]} / {neighbourhood[i]}')
    #fig.for_each_trace(lambda t: t.update(name = newnames[t.name]))
    fig.update_layout(mapbox_style="light", mapbox_accesstoken=token)
    fig.update_layout(font=dict(family="Helvetica"))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    #fig.update_layout(autosize=False,width=700,height=500)
    return fig


def get_category_chart(df):
    """generates the bar chart of the category distribution from the "direct" genre """
    direct_cate = df[df.genre == 'direct']
    direct_cate_counts = (direct_cate.mean(numeric_only=True) * direct_cate.shape[0]).sort_values(ascending=False)
    direct_cate_names = list(direct_cate_counts.index)

    fig = px.bar(x=[i.replace("_", " ").title() for i in direct_cate_names], y=direct_cate_counts)
    # fig.update_traces(marker_color=night_colors[0], marker_line_color='#9c9c9c', marker_line_width=1, opacity=0.7)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    fig.update_layout(xaxis={'visible': True, 'showticklabels': True})
    fig.update_layout(yaxis={'visible': True, 'showticklabels': True})
    fig.update_yaxes(tickfont=dict(family='Helvetica', color='#9c9c9c'),
                     title_font_color='#9c9c9c', mirror=True,
                     ticks='outside', showline=True, gridwidth=1, gridcolor='#4c4c4c')
    fig.update_xaxes(tickfont=dict(family='Helvetica', color='#9c9c9c'),
                     title_font_color='#9c9c9c', mirror=True,
                     ticks='outside', showline=True, gridwidth=1, gridcolor='#4c4c4c')
    fig.update_layout(yaxis_title=None, xaxis_title=None)
    return fig


def blank_fig():
    """ returns a black fig without any content. """
    fig = go.Figure(go.Scatter(x=[], y=[]))
    fig.update_layout(template=None)
    fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
    fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
    return fig


def get_main_chart(dfx):
    try:
        # Define color sets of paintings
        night_colors = ['rgb(56, 75, 126)', 'rgb(18, 36, 37)', 'rgb(34, 53, 101)']

        if dfx is None:
            d = {'restaurant': 0, 'cafe': 0, 'bar': 0, 'station': 0, 'biergarten': 0, 'fast_food': 0, 'pub': 0,
                 'nightclub': 0, 'theatre': 0, 'university': 0}
            df = pd.DataFrame(data=d, index=[0])
            df1_transposed = df.T
            """ generates the horizontal bar chart with the categories """
        else:
            df1_transposed = dfx.T
        df1_transposed.rename({0: 'value'}, inplace=True, axis=1)
        df1_transposed['feature'] = df1_transposed.index
        fig = px.bar(df1_transposed, x='value', y='feature', orientation='h')
        fig.update_layout(hovermode=False)
        # fig.update_layout(xaxis={'visible': False, 'showticklabels': True},
        #                  yaxis={'visible': False, 'showticklabels': True})
        fig.update_yaxes(title='', visible=True, showticklabels=True)
        fig.update_xaxes(title='', visible=True, showticklabels=True)
        fig.update_yaxes(tickfont=dict(size= 10, family='Helvetica', color='#9c9c9c'),
                         title_font_color='#9c9c9c',
                         ticks='outside', showline=True, gridwidth=1, gridcolor='#4c4c4c')
        fig.update_layout(font_family="Helvetica")
        if dfx is None:
            fig.update_xaxes(range=[0, 10])
        fig.update_traces(marker_color=night_colors[0], marker_line_color='#9c9c9c', opacity=0.7)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        fig.update_layout(autosize=True,height=300,margin_pad=0)
        fig.update_layout(margin={"r":0,"t":20,"l":0,"b":0})
        return fig
    except:
        fig = go.Figure(go.Scatter(x=[0], y=[0]))
        fig.update_layout(template=None)
        fig.update_xaxes(showgrid=False, showticklabels=False, zeroline=False)
        fig.update_yaxes(showgrid=False, showticklabels=False, zeroline=False)
        return fig


def get_geo_data():
    """ load geojson data """
    cwd = Path().resolve()
    with open(os.path.join(Path(cwd), 'data', 'geojson', 'vienna.geojson'), encoding='utf-8') as fp:
        counties = geojson.load(fp)
    return counties


def heatmap_airbnb(df, title=''):
    """ """
    districts = get_geo_data()
    agg = df.groupby('neighbourhood').agg(nr_listings=('id', 'count')).reset_index().sort_values('nr_listings',
          ascending=False)
    agg['ratio'] = 100 * agg['nr_listings'] / agg['nr_listings'].sum()
    fig = px.choropleth_mapbox(agg, geojson=districts, locations=agg['neighbourhood'],
                               featureidkey="properties.name", color=agg['ratio'],
                               title=title,
                               mapbox_style="open-street-map", zoom=10, center={"lat": 48.210033, "lon": 16.363449},
                               opacity=0.40)

    fig.add_scattermapbox(
        lat=df['latitude'].tolist(),
        lon=df['longitude'].tolist(),
        mode='markers',
        # text=texts,
        marker_size=2,
        marker_color='#F3F5F6',
        opacity=0.9
    )
    fig.update_layout(mapbox_style="light", mapbox_accesstoken=token)
    fig.update_layout(
            font=dict(family="Open Sans"),
            coloraxis_colorbar_title='$/night',
            legend_font_size=14
            )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    fig.update_yaxes(linewidth=1, linecolor='LightGrey', gridwidth=1, gridcolor='LightGrey', mirror=True,
                     ticks='outside', showline=True)
    return fig


def bar_airbnb(df):
    """generates the bar chart of the category distribution from the "direct" genre """
    night_colors = ['rgb(56, 75, 126)', 'rgb(18, 36, 37)', 'rgb(34, 53, 101)']
    agg = df.groupby('neighbourhood').agg(nr_listings = ('id', 'count')).reset_index().sort_values('nr_listings', ascending=False)
    agg['ratio'] = 100 * agg['nr_listings'] / agg['nr_listings'].sum()

    fig = px.bar(x=agg['neighbourhood'].tolist(), y=agg['ratio'])
    fig.update_traces(marker_color=night_colors[0], marker_line_color='#9c9c9c', marker_line_width=1, opacity=0.7)
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})

    fig.update_layout(xaxis={'visible': True, 'showticklabels': True})
    fig.update_layout(yaxis={'visible': True, 'showticklabels': True})
    fig.update_yaxes(tickfont=dict(family='Helvetica', color='#9c9c9c'),
                     title_font_color='#9c9c9c', mirror=True,
                     ticks='outside', showline=True, gridwidth=1, gridcolor='#4c4c4c')
    fig.update_xaxes(tickfont=dict(family='Helvetica', color='#9c9c9c'),
                     title_font_color='#9c9c9c', mirror=True,
                     ticks='outside', showline=True, gridwidth=1, gridcolor='#4c4c4c')
    fig.update_layout(yaxis_title=None, xaxis_title=None)
    return fig


def get_price_chart(df, feat_key, locations, selector, hover_name, hover_data, opacity):
    fig = px.choropleth_mapbox(df, geojson=data.get_geo_data(selector, source='offline'), locations=locations,
                               featureidkey=feat_key, color="price_sqrt",
                               color_continuous_scale="Viridis",
                               range_color=(df['price_sqrt'].quantile(0.25), df['price_sqrt'].quantile(0.75)),
                               # mapbox_style="open-street-map",
                               mapbox_style="carto-positron",
                               hover_data=hover_data,
                               hover_name=hover_name, zoom=6, center={"lat": 47.809490, "lon": 13.055010},
                               opacity=opacity,
                               )
    fig.update_layout(font=dict(family="Open Sans"), coloraxis_colorbar_title='€/m²')
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig