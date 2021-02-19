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
import numpy as np
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
# COVID-19 Ontario ICU Data
df_ICU = get_data_from_url('https://data.ontario.ca/dataset/8f3a449b-bde5-4631-ada6-8bd94dbc7d15/resource/e760480e-1f95-4634-a923-98161cfb02fa/download/region_hospital_icu_covid_data.csv')
# COVID-19 Ontario Vaccine Data
df_Vaccine = get_data_from_url('https://raw.githubusercontent.com/ccodwg/Covid19Canada/master/timeseries_prov/vaccine_administration_timeseries_prov.csv')
# COVID-19 Ontario Age and Gender Data
df_age_gender = get_data_from_url('https://data.ontario.ca/dataset/f4112442-bdc8-45d2-be3c-12efae72fb27/resource/455fd63b-603d-4608-8216-7d8647f43350/download/conposcovidloc.csv')
#COVID-19 Testing Centers
df_testing_centre = get_data_from_url('https://data.ontario.ca/dataset/covid-19-assessment-centre-locations/resource/c60993bb-3988-4648-9be9-398dee480514/download/assessment_centre_locations.csv')

#modify testing centres to only contain currently active testing centres
df_testing_centre = df_testing_centre.loc[df_testing_centre['active']=='Yes']
df_testing_centre = df_testing_centre.loc[(df_testing_centre['latitude'].isna()==False)&(df_testing_centre['longitude'].isna()==False)]
df_testing_centre['longitude'] = pd.to_numeric(df_testing_centre['longitude'].str.strip())
df_testing_centre.loc[df_testing_centre['phone'].isna(),'phone'] = 'N/A'


# modify gender feature to only contain female, male and other
df_age_gender.Client_Gender = df_age_gender.Client_Gender.replace(
    {'FEMALE': 'FEMALE', 'MALE': 'MALE', 
    'UNSPECIFIED': 'OTHER', 
    'GENDER DIVERSE': 'OTHER'})

# drop the missing age group and 
df_age_gender = df_age_gender.loc[df_age_gender.Age_Group != 'UNKNOWN']
df_age_gender.Age_Group.dropna(inplace = True)
# change age group names
df_age_gender.Age_Group = df_age_gender.Age_Group.replace(
    {'<20': '0-19', '20s': '20-29', '30s': '30-39',
    '40s': '40-49', '50s': '50-59', '60s': '60-69',
    '70s': '70-79', '80s': '80-89', '90s': '90-99'})

# only keep case report date, gender and age
df_age_gender = df_age_gender[['Case_Reported_Date', 'Age_Group', 'Client_Gender']]
df_age_only = df_age_gender[['Case_Reported_Date', 'Age_Group']]

# create bar plots of total cases, cases by age groups, cases by exposure:
df_age_gender_date = df_age_gender[['Case_Reported_Date', 'Age_Group', 'Client_Gender']]
bar_df = df_age_gender_date.groupby('Case_Reported_Date')['Client_Gender'].agg(['count'])
bar_df.reset_index(inplace = True)
# ax = plt.subplot(111)
# ax.bar(pd.to_datetime(bar_df.iloc[:, 0]), bar_df.iloc[:, 1], width=10)
# ax.xaxis_date()
# plt.show()

fig_bar1 = px.bar(x= pd.to_datetime(bar_df.iloc[:, 0]), y= bar_df.iloc[:, 1])
fig_bar1.update_layout(
    title="",
    xaxis_title="Case Reported Date",
    yaxis_title="Number of reported cases")
fig_bar1.update_traces(hovertemplate='Date: %{x} <br>Count: %{y}', selector=dict(type='bar'))

age_bar_df = df_age_gender_date.groupby(['Case_Reported_Date', 'Age_Group'])['Client_Gender'].agg(['count'])
age_bar_df.reset_index(inplace = True)
age_bar_df['Age_Group'] = age_bar_df['Age_Group'].astype(object)
fig_bar2 = px.bar(x= pd.to_datetime(age_bar_df['Case_Reported_Date']), y= age_bar_df['count'], color = age_bar_df['Age_Group'])
fig_bar2.update_layout(
    title="",
    xaxis_title="Case Reported Date",
    yaxis_title="Number of reported cases",
    legend_title_text='Age Group')
fig_bar2.update_traces(hovertemplate='Date: %{x} <br>Count: %{y}', selector=dict(type='bar'))

gender_bar_df = df_age_gender_date.groupby(['Case_Reported_Date', 'Client_Gender'])['Client_Gender'].agg(['count'])
gender_bar_df.reset_index(inplace = True)
fig_bar3 = px.bar(x= pd.to_datetime(gender_bar_df['Case_Reported_Date']), y= gender_bar_df['count'], color = gender_bar_df['Client_Gender'])
fig_bar3.update_layout(
    title="",
    xaxis_title="Case Reported Date",
    yaxis_title="Number of reported cases",
    legend_title_text='Gender')
fig_bar3.update_traces(hovertemplate='Date: %{x} <br>Count: %{y}', selector=dict(type='bar'))

# compute total count groupby age and gender
df_age_gender = df_age_gender.groupby(by=['Age_Group', 'Client_Gender']).count()
df_age_gender = df_age_gender.groupby(level = 0).apply(lambda x: 100 * x / float(x.sum()))
df_age_gender.reset_index(inplace = True)
# compute total count groupby age
df_age_only = df_age_only.groupby(by=['Age_Group']).count()
df_age_only = df_age_only.apply(lambda x: 100 * x / float(x.sum()))
df_age_only.reset_index(inplace = True)
# merge the df_age_gender and df_age_only
df_age_gender = df_age_gender.merge(df_age_only, on = 'Age_Group')
# compute the distribution of age and gender
df_age_gender['percent'] = df_age_gender['Case_Reported_Date_x'] * df_age_gender['Case_Reported_Date_y']/100

fig_age_gender = px.bar(df_age_gender, x="percent", y="Age_Group", color="Client_Gender", 
             labels={'percent':'Proportion (%)', 'Age_Group': 'Age Group (years)',
                    'Client_Gender': 'Gender'})




#phu_data_rolling = pd.read_csv('Ontario_PHU.csv')
#ontario_daily = pd.read_csv('Ontario_status.csv')
df = phu_data_rolling.groupby('PHU_NAME')['FILE_DATE'].max().reset_index()
df = df.merge(phu_data_rolling, on = ['PHU_NAME', 'FILE_DATE'])
df.reset_index(inplace=True, drop=True)
#Needed for plotting phu bars
phu_dict_list = [{'label':name, 'value':name} for name in phu_data_rolling['PHU_NAME'].unique() if name is not np.nan]
phu_dict_list.append({'label':'ONTARIO','value':'ONTARIO'})

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
                           # color='positive_rate',
                           #color_continuous_scale="purpor",
                           labels={'positive_rate': 'COVID-19 Positive Rate %',
                                   'PHU_NAME': 'Public Health Unit'})
fig_positive_rate.update_layout(margin=dict(l=0))
fig_positive_rate.update_traces(marker_color="#7289da")
## compute the ICU cases by different region
df_ICU_ONTARIO = df_ICU.groupby('date')['date', 'ICU'].agg('sum')
df_ICU_ONTARIO.reset_index(inplace = True)

# get icu dropdown list
icu_dict_list = [{'label':name, 'value':name} for name in df_ICU['oh_region'].unique()]
icu_dict_list.append({'label':'ONTARIO','value':'ONTARIO'})


fig_ICU = go.Figure(data=[go.Scatter(
    x=df_ICU_ONTARIO.date,
    y=df_ICU_ONTARIO.ICU,
    name="ONTARIO",
    line=dict(color="#7289da"))])
fig_ICU.update_layout(
    xaxis_title="Date",
    yaxis_title="ICU")



## compute Ontario Vaccine Administration
df_Vaccine = df_Vaccine.loc[df_Vaccine['province'] == 'Ontario']
df_Vaccine['date_vaccine_administered']= pd.to_datetime(df_Vaccine['date_vaccine_administered'], dayfirst = True)
df_Vaccine.reset_index(inplace = True, drop = True)
fig_Vaccine = px.line(df_Vaccine, x = 'date_vaccine_administered', y = 'avaccine', 
              labels={
                  'date_vaccine_administered': 'Date',
                  'avaccine': 'Vaccine Administered'
              })
fig_positive_rate.update_layout(margin=dict(r=0))

#functions to compute necessary values for dashboard
### necessary global variables
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
###

###Bar plot for phu data
colors = ['#d9534f','#5cb85c','#7289da']

phu_bar = go.Figure(data=[go.Bar(
    x=['Active', 'Recovered', 'Deaths'],
    y=[active_cases, total_recoveries, total_deaths],
    marker_color=colors # marker color can be a single color value or an iterable
)])
#phu_bar.update_layout(title_text='Number of cases in Ontario')


with open("Ministry_of_Health_Public_Health_Unit_Boundary Simplified.json") as f:
    boundary_data = json.load(f)


fig = px.choropleth_mapbox(df, geojson=boundary_data, featureidkey='properties.PHU_ID', 
                           locations='PHU_NUM', color='ACTIVE_CASES',
                           color_continuous_scale="purpor",
                           #color_continuous_scale="agsunset",
                           range_color=(0, 4000),
                           mapbox_style="carto-positron",
                           zoom=4, center = {"lat": 48.31, "lon": -84.73},
                           opacity=0.5,
                           labels={'PHU_NUM': 'PHU Number'},
                           hover_data = ['PHU_NAME']
                          )

#fig2 = px.scatter_geo(df_testing_centre, lat='latitude', lon='longitude', hover_name='location_name', hover_data=['PHU','phone','website'])
#fig.add_scattergeo()
fig2 = px.scatter_mapbox(df_testing_centre,lat='latitude',lon='longitude',
                         hover_name='location_name',hover_data=['phone','website'],
                         mapbox_style="carto-positron",zoom=4, center = {"lat": 48.31, "lon": -84.73})
fig.add_trace(fig2.data[0])

'''
fig = px.choropleth(df, geojson=boundary_data, featureidkey='properties.PHU_ID', 
                           locations='PHU_NUM', color='ACTIVE_CASES',
                           color_continuous_scale="purpor",
                           #color_continuous_scale="agsunset",
                           range_color=(0, 4000),
                           scope='north america', center = {"lat": 48.31, "lon": -84.73},
                           labels={'PHU_NUM': 'PHU Number'},
                           hover_data = ['PHU_NAME']
)'''
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, dragmode=False)

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

### HTML components go here, control the heights using h classes with percent of screen height ##########
app.layout = dbc.Container(
    [
        dbc.Row(dbc.Col(html.H1("Ontario COVID-19 Tracker"))),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(dbc.Card(
                    dbc.CardBody(
                        [dbc.Row([dbc.Col([html.H4("New Cases Today", className="card-title"),
                            html.H1('{:,}'.format(new_positive_today)),
                            ], width=6),
                            dbc.Col([html.H4("Total Cases", className="card-title"),
                            html.H1('{:,}'.format(total_cases)),
                            ], width=6)
                        ])
                            
                        ]
                    ),
                    style={'text-align':'center',
                           'margin-top': '10px',
                           'margin-bottom': '5px',
                           'margin-left': '15px'},outline=True),md=6, width=6),
                dbc.Col(dbc.Card(
                    dbc.CardBody(
                        [dbc.Row([dbc.Col([html.H4("Deaths Today", className="card-title"),
                            html.H1('{:,}'.format(new_deaths_today)),
                            ], width=6),
                            dbc.Col([html.H4("Total Deaths", className="card-title"),
                            html.H1('{:,}'.format(total_deaths)),
                            ], width=6)
                        ])
                            
                        ]
                    ),
                    style={'text-align':'center',
                           'margin-top': '10px',
                           'margin-bottom': '5px',
                           'margin-right': '15px'},outline=True),md=6, width=6),
            ]),
        dbc.Row(
            [
                dbc.Col(dbc.Card(
                    dbc.CardBody(
                        [dbc.Row([dbc.Col([html.H4("Recovered Today", className="card-title"),
                            html.H1('{:,}'.format(new_recovered_today)),
                            ], width=6),
                            dbc.Col([html.H4("Total Recovered", className="card-title"),
                            html.H1('{:,}'.format(total_recoveries)),
                            ], width=6)
                        ])
                            
                        ]
                    ),
                    style={'text-align':'center',
                           'margin-top': '10px',
                           'margin-bottom': '5px',
                           'margin-left': '15px'},outline=True),md=6, width=6),
                dbc.Col(dbc.Card(
                    dbc.CardBody(
                        [dbc.Row([dbc.Col([html.H4("Tests Completed Today", className="card-title"),
                            html.H1('{:,}'.format(tests_today)),
                            ], width=6),
                            dbc.Col([html.H4("Total Tests Completed", className="card-title"),
                            html.H1('{:,}'.format(total_tests)),
                            ], width=6)
                        ])
                            
                        ]
                    ),
                    style={'text-align':'center',
                           'margin-top': '10px',
                           'margin-bottom': '5px',
                           'margin-right': '15px'}, outline=True),md=6, width=6),
            ]),

        # main choropleth map
        dbc.Row(html.H3("Ontario COVID-19 Active Cases and Test Locations")),
        dbc.Row(
            dbc.Col(dcc.Graph(id='ontario-map',figure=fig),id="map-box"),
            style={'text-align':'center',
                           'margin-top': '10px',
                           'margin-bottom': '10px',
                           'margin-left': '20px',
                           'margin-right': '10px'}),
        # Cases and ICU plots
        dbc.Row(
            [
                dbc.Col(dbc.Card(
                    dbc.CardBody(
                        [dbc.Row([dbc.Col(html.H5('Number of Cases in'),md=4,width=3),
                                  dbc.Col(dcc.Dropdown(
                    options=phu_dict_list,
                    value='ONTARIO',
                    clearable=False,
                id="phu_dropdown"),md=8,width=9, align = "start")], align="start", form=True),
                         dbc.Row([dbc.Col(dcc.Graph(id='phu-bar',figure=phu_bar),id="phu-zone")])
                         ]
                    ),
                    style={'text-align': 'start',
                           'margin-top': '20px',
                           'margin-bottom': '5px',
                           'margin-left': '15px'}, outline=True), md=6, width=6),
                dbc.Col(dbc.Card(
                    dbc.CardBody(
                        [dbc.Row([dbc.Col(dcc.Dropdown(
                    options=icu_dict_list,
                    value='ONTARIO',
                    clearable=False,
                id="icu_dropdown"),md=4,width=4, align = "start"),
                            dbc.Col(html.H5('COVID-19 ICU Cases'),md=6,width=8)], align="start", form=True),
                         dbc.Row([dbc.Col(dcc.Graph(id='covid19-icu',figure=fig_ICU),id="line-box")])
                         ]
                    ),
                    style={'text-align': 'start',
                           'margin-top': '20px',
                           'margin-bottom': '5px',
                           'margin-right': '15px'}, outline=True), md=6, width=6),
            ]),

        # Age and Gender plots
        dbc.Row(
            [
                dbc.Col(dbc.Card(
                    dbc.CardBody(
                        [dbc.Row([dbc.Col(html.H5('COVID-19 Cases in Ontario by Reporting Date'))], align="start"),
                         dbc.Row([dbc.Col(dcc.Dropdown(
                                      options=[
                                          {'label': 'Total Cases', 'value': 'all'},
                                          {'label': 'by Age Group', 'value': 'age'},
                                          {'label': 'by Gender', 'value': 'gender'}
                                      ],
                                      value='all',
                                      clearable=False,
                                      id="dropdown"), md=4, width=4, align = "start")

                         ], align="start"),
                         dbc.Row([dbc.Col(dcc.Graph(id='covid19-casebar',figure=fig_bar1),id="ovid19-casebar")])
                         ]
                    ),
                    style={'text-align': 'start',
                           'margin-top': '20px',
                           'margin-bottom': '5px',
                           'margin-left': '15px'}, outline=True), md=6, width=6),
                dbc.Col(dbc.Card(
                    dbc.CardBody(
                        [dbc.Row([dbc.Col(html.H5('Age and Gender Distribution of COVID-19 Cases in Ontario'))]),
                         dbc.Row([dbc.Col(dcc.Graph(id='covid19-ageGender',figure=fig_age_gender),id="ageGender-box")])
                         ]
                    ),
                    style={'text-align': 'start',
                           'margin-top': '20px',
                           'margin-bottom': '5px',
                           'margin-right': '15px',
                           'height': '35rem'}, outline=True), md=6, width=6),
            ]),

        # dbc.Row(
        #     [
        #         dbc.Col(dbc.Row([dbc.Col(html.H4('Number of Cases in '),md=6,width=6),dbc.Col(dcc.Dropdown(
        #             options=phu_dict_list,
        #             value='ONTARIO',
        #             clearable=False,
        #         id="phu_dropdown"),md=6,width=6)],align="center"),md=6, width=6),
        #         dbc.Col(html.H4("Ontario COVID-19 Active Cases and Test Locations"),md=6,width=6),
        #     ],
        #     align="center"),
        # dbc.Row(
        #     [
        #         dbc.Col(dcc.Graph(id='phu-bar',figure=phu_bar),id="phu-zone",md=6, width=6),
        #         dbc.Col(dcc.Graph(id='ontario-map',figure=fig),id="map-box",md=6,width=6),
        #     ],
        #     align="center",
        # className="h-75"),
#         dbc.Row(
#             [
#             ],
#             align="center",
#         className="h-25"),
        
        # Ontario ICU and Positive Rate
        dbc.Row(
            [
                dbc.Col(dbc.Card(
                    dbc.CardBody(
                        [dbc.Row([dbc.Col(html.H5('PHU Ranked by COVID-19 Positive Rate'))]),
                         dbc.Row([dbc.Col(dcc.Graph(id='covid19-positive',figure=fig_positive_rate),id="bar-box")])
                         ]
                    ),
                    style={'text-align': 'start',
                           'margin-top': '20px',
                           'margin-bottom': '5px',
                           'margin-left': '15px'}, outline=True), md=6, width=6),
                dbc.Col(dbc.Card(
                    dbc.CardBody(
                        [dbc.Row([dbc.Col(html.H5('Ontario Daily Vaccine Administration'))], align="start"),
                         dbc.Row([dbc.Col(dcc.Graph(id='covid19-vaccine',figure=fig_Vaccine),id="vaccine-box")])
                         ]
                    ),
                    style={'text-align': 'start',
                           'margin-top': '20px',
                           'margin-bottom': '5px',
                           'margin-right': '15px'}, outline=True), md=6, width=6),
            ]),
#         dbc.Row(
#             [   # Vaccine
#                 dbc.Col(dcc.Graph(id='covid19-vaccine',figure=fig_Vaccine),id="vaccine-box",md=5,width=6),
#                 # COVID-19 Positive Rate by Public Health Unit
#                 dbc.Col(dcc.Graph(id='covid19-positive',figure=fig_positive_rate),id="bar-box",md=7,width=6),
#             ],
#             align="start", form=True,
#         className="h-95"),
        
        # Ontario Vaccine Administration and age and gender distribution
        # dbc.Row(
        #     [   # Vaccine
        #         # dbc.Col(dcc.Graph(id='covid19-vaccine',figure=fig_Vaccine),id="vaccine-box",md=0,width=0),
        #         # age and gender distribution
        #         #dbc.Col(dcc.Graph(id='covid19-ageGender',figure=fig_age_gender),id="ageGender-box",md=6,width=6),
        #     ],
        #     align="center",
        # className="h-95"),

        # dbc.Row(
        #     [
        #         dbc.Col([html.H6("Filter"),dcc.Dropdown(
        #             options=[
        #                 {'label': 'None', 'value': 'all'},
        #                 {'label': 'Age', 'value': 'age'},
        #                 {'label': 'Gender', 'value': 'gender'}
        #             ],
        #             value='all',
        #             clearable=False,
        #         id="dropdown")],md=1,width=1),
        #         dbc.Col(dcc.Graph(id='covid19-casebar',figure=fig_bar1),id="covid19-casebar",md=6,width=6),
        #     ],
        #     align="center",
        # className="h-95"),

    ],
    fluid=True,
    style={"height":"100vh"}
)

@app.callback(
    Output('phu-bar', 'figure'),
    [Input('phu_dropdown', 'value')])
def update_phu_bar(value):
    #too many plots to precompute. Compute plot dynamically  
    if value is not None:            
        if value=='ONTARIO':
            phu_bar.update_layout(
                margin=dict(t=50))
            return phu_bar
        else:
            #compute new plot
            phu_df = phu_data_rolling.loc[phu_data_rolling['PHU_NAME']==value]
            phu_df = phu_df.loc[phu_df['FILE_DATE'] == phu_df['FILE_DATE'].max()]
            phu_bar2 = go.Figure(data=[go.Bar(
                x=['Active', 'Recovered', 'Deaths'],
                y=[int(phu_df['ACTIVE_CASES']), int(phu_df['RESOLVED_CASES']), int(phu_df['DEATHS'])],
                marker_color=colors
            )])
            phu_bar2.update_layout(
                margin=dict(t=50), yaxis_range=[0,100000])
            return phu_bar2
    return phu_bar

# ICU Scatter Plot
@app.callback(
    Output('covid19-icu', 'figure'),
    [Input('icu_dropdown', 'value')])
def update_icu_scatter(value):
    color_dict = {'CENTRAL': "#7f8bf5", 'TORONTO': "#445bab",
                 'WEST': "#0fba7c", 'EAST': "#4b9cfc", 'NORTH': "#d461f2"}

    #too many plots to precompute. Compute plot dynamically  
    if value is not None:            
        if value=='ONTARIO':
            fig_ICU.update_layout(
                margin=dict(t=50))
            return fig_ICU
        else:
            #compute new plot
            df_ICU_temp= df_ICU.loc[df_ICU.oh_region == value]
            icu_temp = go.Figure(data=[go.Scatter(
                x=df_ICU_temp.date,
                y=df_ICU_temp.ICU,
                name=value,
                line=dict(color=color_dict[value]))])
            
            icu_temp.update_layout(
                margin=dict(t=50), yaxis_range=[0,450])
            icu_temp.update_layout(
                xaxis_title="Date",
                yaxis_title="ICU")
            return icu_temp
    return icu_temp



@app.callback(
    Output('covid19-casebar', 'figure'),
    [Input('dropdown', 'value')])
def update_figure(value):    
    if value is not None:            
        if value=='all':
            fig_bar1.update_layout(
                margin=dict(t=20))
            return fig_bar1
        elif value=='age':
            fig_bar2.update_layout(
                margin=dict(t=20))
            return fig_bar2
        else:
            fig_bar3.update_layout(
                margin=dict(t=20))
            return fig_bar3
    return fig_bar1

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
    # debug=True
    app.run_server(debug=True)
