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


def get_data_from_url(url):
    content = requests.get(url).content
    return pd.read_csv(io.StringIO(content.decode('utf-8')))

phu_data_rolling = get_data_from_url('https://data.ontario.ca/dataset/1115d5fe-dd84-4c69-b5ed-05bf0c0a0ff9/resource/d1bfe1ad-6575-4352-8302-09ca81f7ddfc/download/cases_by_status_and_phu.csv')
ontario_daily = get_data_from_url('https://data.ontario.ca/dataset/f4f86e54-872d-43f8-8a86-3892fd3cb5e6/resource/ed270bb8-340b-41f9-a7c6-e8ef587e6d11/download/covidtesting.csv')
# COVID-19 Testing Data
df_test = get_data_from_url('https://data.ontario.ca/dataset/a2dfa674-a173-45b3-9964-1e3d2130b40f/resource/07bc0e21-26b5-4152-b609-c1958cb7b227/download/testing_metrics_by_phu.csv')


#phu_data_rolling = pd.read_csv('Ontario_PHU.csv')
#ontario_daily = pd.read_csv('Ontario_status.csv')
current_date = max(phu_data_rolling['FILE_DATE'].unique())
df = phu_data_rolling.loc[phu_data_rolling['FILE_DATE'] == current_date]
df.reset_index(inplace=True, drop=True)


## compute the population in each Public Health Unit
# convert string to integer
df_test['test_volumes_7d_avg'] = df_test['test_volumes_7d_avg'].apply(lambda x: int(x.replace(',', '')))
df_test['DATE']= pd.to_datetime(df_test['DATE'], dayfirst = True)

current_date = max(df_test['DATE'].unique())
df_test_current = df_test.loc[df_test['DATE'] == current_date]
df_test_current.reset_index(inplace=True, drop=True)

# compute the population for each PHU
df_test_current['pop'] = (df_test_current['test_volumes_7d_avg'] / df_test_current['tests_per_1000_7d_avg']) * 1000

## compute the COVID-19 positive rate by Public Health Unit and generate bar plot
df = df.merge(df_test_current, left_on='PHU_NUM', right_on='PHU_num')
df['positive_rate'] = (df['ACTIVE_CASES']/df['pop']) * 100
df = df.sort_values(by = 'positive_rate')
fig_positive_rate = px.bar(df, x='positive_rate', y='PHU_NAME', height=700, 
                           labels={'positive_rate': 'COVID-19 Positive Rate %',
                                   'PHU_NAME': 'Public Health Unit'})



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
total_tests = int(ontario_daily['Total tests completed in the last day'].sum())

new_positive_today = int(today['new_cases'])
new_recovered_today = int(today['new_resolved'])
new_deaths_today = int(today['new_death'])
tests_today = int(today['Total tests completed in the last day'])

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
                        [dbc.Row([dbc.Col([html.H4("Tests Completed Today", className="card-title"),
                            html.H1(str(tests_today)),
                            ], width=6),
                            dbc.Col([html.H4("Total Tests Completed", className="card-title"),
                            html.H1(str(total_tests)),
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
#         dbc.Row(
#             [
#             ],
#             align="center",
#         className="h-25"),
        # COVID-19 Positive Rate by Public Health Unit
        dbc.Row(
            [
                #dbc.Col(id="phu-positive",md=0, width=0),
                dbc.Col(dcc.Graph(id='covid19-positive',figure=fig_positive_rate),id="bar-box",md=6,width=6),
            ],
            align="center",
        className="h-85")

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
    # port=8000, host='127.0.0.1'
    app.run_server(debug=True)
