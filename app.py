import dash
import logging
from assets.layout import layout
from assets.data_wrangling import GeoData
from assets.callbacks import register_callbacks


data = GeoData()
df = data.import_data()
#model = data.get_model()
#region = data.get_region()

dash_app = dash.Dash(__name__)
dash_app.title = 'Austrian Price Prediction'
app = dash_app.server


dash_app.layout = layout(dash_app, df)
register_callbacks(dash_app, df)


if __name__ == "__main__":
    dash_app.run_server(debug=True)

