# Run this app with `python app.py` and
# visit http://127.0.0.1:8050/ in your web browser.

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

import json
import pandas as pd
import io
import requests


df = pd.read_csv('recent_phu.csv')

with open("Ministry_of_Health_Public_Health_Unit_Boundary Simplified.json") as f:
    boundary_data = json.load(f)

fig = px.choropleth_mapbox(df, geojson=boundary_data, featureidkey='properties.PHU_ID', locations='PHU_NUM', color='ACTIVE_CASES',
                           color_continuous_scale="YlOrRd",
                           range_color=(0, 4000),
                           mapbox_style="carto-positron",
                           zoom=4, center = {"lat": 48.31, "lon": -84.73},
                           opacity=0.5,
                           labels={'PHU_NUM': 'PHU Number'},
                           hover_data = ['PHU_NAME']
                          )
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

'''
fig2 = go.Figure(go.Choroplethmapbox(geojson=boundary_data, locations=df['PHU_NUM'], featureidkey='properties.PHU_ID',z=df['ACTIVE_CASES'],
                                    colorscale="YlOrRd", zmin=0, zmax=4000,
                                    marker_opacity=0.5, marker_line_width=1,
                                    customdata=df[['PHU_NAME','DEATHS']],
                                    hovertemplate='<b>PHU Name: %{customdata[0]}</b><br>PHU Num: %{locations}<br>ACTIVE CASES: %{z}<br>DEATHS: %{customdata[1]}',))
fig2.update_layout(mapbox_style="carto-positron",
                  mapbox_zoom=4, mapbox_center = {"lat": 48.31, "lon": -84.73})
fig2.update_layout(margin={"r":0,"t":0,"l":0,"b":0})'''

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

### HTML components go here
app.layout = dbc.Container(
    [
        dbc.Row(dbc.Col(html.H1("Ontario COVID-19 Tracker"))),
        dbc.Row(
            [
                dbc.Col(id="phu-zone",md=0),
                dbc.Col(dcc.Graph(id='ontario-map',figure=fig),id="map-box",md=12),
            ],
            align="center",
        ),
        
    ],
    fluid=True,
)

'''

@app.callback(
    Output('ontario-map', 'figure'),
    [Input('ontario-map', 'clickData')])
def update_figure(clickData):    
    if clickData is not None:            
        location = clickData['points'][0]['location']

        if location not in selections:
            selections.add(location)
        else:
            selections.remove(location)
        
    return get_figure(selections)'''

if __name__ == '__main__':
    app.run_server(debug=True)