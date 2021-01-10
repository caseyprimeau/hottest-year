"""
Temperature Anomaly Dashboard

**Will NASA find 2020’s global average temperature highest on record?**
https://www.predictit.org/markets/detail/6234/

Official yearly measurement: 
https://data.giss.nasa.gov/gistemp/graphs/graph_data/Global_Mean_Estimates_based_on_Land_and_Ocean_Data/graph.txt

"""

import pdb

import requests
import pandas as pd
import numpy as np
import datetime
from datetime import date
from pathlib import Path
import copy
import flask
import calendar
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_auth
import plotly.express as px
import plotly.graph_objs as go
import plotly.figure_factory as ff
import colorlover as cl
import infos
from colormap import rgb2hex

def get_market_data():
    ####get PredictIt market data from API
    response = requests.get('https://www.predictit.org/api/marketdata/markets/6234/')
    data = response.json()
    return data

def monthly_anomaly_fig(full_anomaly):
    monthly_anomaly = full_anomaly
    i = 0
    while i < 6:  ###isolate monthly columns
        monthly_anomaly = monthly_anomaly[monthly_anomaly.columns[:-1]]
        i = i +1
    monthly_anomaly.set_index('Year', inplace=True)
    month_list = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    #colors = px.colors.sequential.Jet
    #pdb.set_trace()
    monthly_anomaly_fig = go.Figure()
    for i in range(0, len(monthly_anomaly)):
        line_name = str(monthly_anomaly.iloc[i].name)
        monthly_anomaly_fig.add_trace(go.Scatter(y=monthly_anomaly.iloc[i], x=month_list, name=line_name, line_color=colorize_row(monthly_anomaly.iloc[i])))#, line_color=colordf.loc[int(line_name)][1]))
    monthly_anomaly_fig.update_layout(
        xaxis = dict(
        autorange=True,
        rangemode="normal",
        type = 'category',
        tick0 = 0,
    )
    )

    return monthly_anomaly_fig

#def seasonal_anomaly_fig(full_anomaly):
#    ###load and prepare seasonal df
#
#    seasonal_anomaly = full_anomaly
#    seasonal_anomaly.drop(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec', 'J-D','D-N'], axis=1)
#
#    seasonal_anomaly.set_index('Year', inplace=True)
#    season_list = ['']
#    colors = px.colors.qualitative.Plotly
#    seasonal_anomaly_fig = go.Figure()
#    
#    for i in range(0, len(seasonal_anomaly)):
#        line_name = seasonal_anomaly.iloc[i].name
#        seasonal_anomaly_fig.add_trace(go.Scatter(y=seasonal_anomaly.iloc[i], x=season_list, name=str(line_name), line_color=colors))

def colorize_row(row):
    #above .6-red, above .1-orange, above 0-yellow, above -.21- green, below -.21 teal
    if row.name in(2021, 2020):
        return '#FAFF00'
    if row.mean() > 0.6:
        return '#FF0000'
    elif 0.6 >= row.mean() > 0.1:
        return '#ef7f1c'
    elif 0.1 >= row.mean() > 0.0:
        return '#96ce48'      
    elif 0 >= row.mean() > -0.21:
        return '#64ad7f'
    elif -0.21>= row.mean():
        return '#6d9d95'            
    else:
        return'#FFFFFF'

server = flask.Flask('app')
app = dash.Dash('app', assets_folder='static', server=server)
auth = dash_auth.BasicAuth(
    app,
    infos.VALID_USERNAME_PASSWORD_PAIRS
)

app.index_string = infos.analytics_string
app.title = 'Will this be the hottest year on record?'

####predictit market data load - calls api every time
lastPrice = get_market_data()['contracts'][0]['lastTradePrice']

###load csv datasets
home_dir = str(Path.home())
yearly_landocean = pd.read_csv(home_dir + '/data/nasa_landocean_yearly.csv') #yearly nasa land-ocean temperature index
nosmooth_landocean = yearly_landocean[yearly_landocean.columns[:-1]].nlargest(150, 'No_Smoothing')
#smoothed_landocean = yearly_landocean.drop('No_Smoothing',1).nlargest(10, 'Lowess(5)')

full_anomaly = pd.read_csv(home_dir + '/data/gistemp_monthly.csv') #nasa anomaly data used for monthly, seasonal

#pdb.set_trace()
app.layout = html.Div(children=[
    html.H1('Will this be the hottest year on record?'),
    html.Div([
        html.Div(html.H3([dcc.Link('PredictIt Market', target="_blank", href="https://www.predictit.org/markets/detail/6234/Will-NASA-find-2020%E2%80%99s-global-average-temperature-highest-on-record"), 
        html.Br(),
        '''
        Latest Price (Yes): $ 
        ''' 
        + str(lastPrice)]), className="eight columns"
        ),
        html.Div(
            [html.Label('Yearly Temperature Anomaly', style={'fontWeight':'500', 'textAlign':'center'}), 
                dash_table.DataTable(
                columns=[{"name": "Year", "id":"Year"}, {"name": "Land-Sea Temperature Index (Unsmoothed)", "id":"No_Smoothing"}],
                data=nosmooth_landocean.to_dict('records'),
                style_as_list_view=False,
                style_table={
                    'overflowY': 'scroll',
                    'height': '250px',
                },
                style_cell={'textAlign':'center'},
                style_cell_conditional=[
                {'if': {'id': 'Year'},
                'width': '50%'},
                {'if': {'id': 'No_Smoothing'},
                'width': '50%'}]
            )],className="four columns")
    ], className="row"),
    html.Br(),
    html.Div(
        dcc.Graph(
            id='anomaly',
            figure=monthly_anomaly_fig(full_anomaly).
                update_layout(title="Monthly Temperature Anomaly 1880-Present", 
                              title_x=0.5,
                              paper_bgcolor="white",
                              plot_bgcolor="lightgrey",
                              margin=dict(l=0,r=0,b=20,t=40,pad=10))
        )),
#end of dash
])

if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0')




    
