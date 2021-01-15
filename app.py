# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd

import json
import pandas as pd
import io
import requests


df = pd.read_csv('recent_phu.csv')

with open("Ministry_of_Health_Public_Health_Unit_Boundary Simplified.json") as f:
    phu_data = json.load(f)

fig = px.choropleth_mapbox(df, geojson=phu_data, featureidkey='properties.PHU_ID', locations='PHU_NUM', color='ACTIVE_CASES',
                           color_continuous_scale="Viridis",
                           range_color=(0, 4000),
                           mapbox_style="carto-positron",
                           zoom=4, center = {"lat": 48.31, "lon": -84.73},
                           opacity=0.5,
                           labels={'PHU_NUM': 'PHU Number'}
                          )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
fig.show()

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    dcc.Graph(
        id='ontario-map',
        figure=fig
    )
])

if __name__ == '__main__':
    app.run_server(debug=True)