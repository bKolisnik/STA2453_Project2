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

#the daily case changes by phu csv total column is the the number of new cases since yesterday it is new positive cases + new resolved cases + new deaths



phu_data_rolling = pd.read_csv('Ontario_PHU.csv')
ontario_daily = pd.read_csv('Ontario_status.csv')
df = pd.read_csv('recent_phu.csv')

#functions to compute necessary values for dashboard
ontario_daily.loc[:,'new_positive'] = ontario_daily['Confirmed Positive'].diff()
ontario_daily.loc[:,'new_cases']= ontario_daily['Total Cases'].diff()
ontario_daily.loc[:,'new_resolved']= ontario_daily['Resolved'].diff()
ontario_daily.loc[:,'new_death']= ontario_daily['Deaths'].diff()

today = ontario_daily.loc[ontario_daily['Reported Date']==ontario_daily['Reported Date'].max(),:]
active_cases = int(today['Confirmed Positive'])
total_cases = int(today['Total Cases'])
total_deaths = int(today['Deaths'])
total_recoveries = int(today['Resolved'])

new_positive_today = int(today['new_positive'])
new_recovered_today = int(today['new_resolved'])
new_deaths_today = int(today['new_death'])

if(new_positive_today < 0):
    new_positive_today = 0

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

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

### HTML components go here, control the heights using h classes with percent of screen height
app.layout = dbc.Container(
    [
        dbc.Row(dbc.Col(html.H1("Ontario COVID-19 Tracker"))),
        dbc.Row(
            [
                dbc.Col(dbc.Card(
                    dbc.CardBody(
                        [dbc.Row([dbc.Col([html.H4("New Cases Today", className="card-title"),
                            html.H1(str(new_positive_today)),
                            ], width=6),
                            dbc.Col([html.H4("Total Cases", className="card-title"),
                            html.H1(str(total_cases)),
                            ], width=6)
                        ])
                            
                        ]
                    ),
                    style={'text-align':'center'},outline=True),md=6, width=6),
                dbc.Col(dbc.Card(
                    dbc.CardBody(
                        [dbc.Row([dbc.Col([html.H4("Deaths Today", className="card-title"),
                            html.H1(str(new_deaths_today)),
                            ], width=6),
                            dbc.Col([html.H4("Total Deaths", className="card-title"),
                            html.H1(str(total_deaths)),
                            ], width=6)
                        ])
                            
                        ]
                    ),
                    style={'text-align':'center'},outline=True),md=6, width=6),
            ]),
        dbc.Row(
            [
                dbc.Col(dbc.Card(
                    dbc.CardBody(
                        [dbc.Row([dbc.Col([html.H4("Recovered Today", className="card-title"),
                            html.H1(str(new_recovered_today)),
                            ], width=6),
                            dbc.Col([html.H4("Total Recovered", className="card-title"),
                            html.H1(str(total_recoveries)),
                            ], width=6)
                        ])
                            
                        ]
                    ),
                    style={'text-align':'center'},outline=True),md=6, width=6),
                dbc.Col(dbc.Card(
                    dbc.CardBody(
                        [dbc.Row([dbc.Col([html.H4("Tested Today", className="card-title"),
                            html.H1("N/A"),
                            ], width=6),
                            dbc.Col([html.H4("Total Tested", className="card-title"),
                            html.H1("N/A"),
                            ], width=6)
                        ])
                            
                        ]
                    ),
                    style={'text-align':'center'},outline=True),md=6, width=6),
            ]),
        dbc.Row(
            [
                dbc.Col(id="phu-zone",md=6, width=6),
                dbc.Col(dcc.Graph(id='ontario-map',figure=fig),id="map-box",md=6,width=6),
            ],
            align="center",
        className="h-75"),
        dbc.Row(
            [
            ],
            align="center",
        className="h-25"),

    ],
    fluid=True,
    style={"height":"100vh"}
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