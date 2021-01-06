"""
Temperature Anomaly Dashboard

**Will NASA find 2020’s global average temperature highest on record?**
https://www.predictit.org/markets/detail/6234/

Official yearly measurement: 
https://data.giss.nasa.gov/gistemp/graphs/graph_data/Global_Mean_Estimates_based_on_Land_and_Ocean_Data/graph.txt

"""

#import pdb
import flask
import datetime
from datetime import date
import calendar
import requests
import pandas as pd
import numpy as np
import dash
import copy
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_auth
import plotly.express as px
import plotly.graph_objs as go
import plotly.figure_factory as ff
import colorlover as cl
import infos


def get_market_data():
    ####get PredictIt market data from API
    response = requests.get('https://www.predictit.org/api/marketdata/markets/6234/')
    data = response.json()
    return data

def load_gistemp_monthly_anomaly():
    ###get csv file with nasa monthly global average temperature anomaly
    file = 'source_data/gistemp_monthly.csv'
    df = pd.read_csv(file)
    return df

def load_nasa_yearly_landocean():
    file = 'source_data/nasa_landocean_yearly.csv'
    df = pd.read_csv(file)
    return df

def monthly_anomaly_fig(full_anomaly):
    monthly_anomaly = full_anomaly
    i = 0
    while i < 6:  ###isolate monthly columns
        monthly_anomaly = monthly_anomaly[monthly_anomaly.columns[:-1]]
        i = i +1

    monthly_anomaly.set_index('Year', inplace=True)
    month_list = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    colors = px.colors.qualitative.Plotly
    monthly_anomaly_fig = go.Figure()
    #pdb.set_trace()
    for i in range(0, len(monthly_anomaly)):
        line_name = str(monthly_anomaly.iloc[i].name)
        monthly_anomaly_fig.add_trace(go.Scatter(y=monthly_anomaly.iloc[i], x=month_list, name=line_name))
    return monthly_anomaly_fig

def seasonal_anomaly_fig(full_anomaly):
    ###load and prepare seasonal df

    seasonal_anomaly = full_anomaly
    seasonal_anomaly.drop(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec', 'J-D','D-N'], axis=1)

    seasonal_anomaly.set_index('Year', inplace=True)
    season_list = ['']
    colors = px.colors.qualitative.Plotly
    seasonal_anomaly_fig = go.Figure()
    
    for i in range(0, len(seasonal_anomaly)):
        line_name = seasonal_anomaly.iloc[i].name
        seasonal_anomaly_fig.add_trace(go.Scatter(y=seasonal_anomaly.iloc[i], x=season_list, name=str(line_name)))



    #pdb.set_trace()

###********************* dash ***************************************

#app.scripts.config.serve_locally = True

app = dash.Dash(__name__, assets_folder='static')
auth = dash_auth.BasicAuth(
    app,
    infos.VALID_USERNAME_PASSWORD_PAIRS
)

#optional, overrides Dash html default including google analytics string
app.index_string = infos.analytics_string

application = app.server

####predictit market data load - calls api every time
market_data = get_market_data()
lastPrice = market_data['contracts'][0]['lastTradePrice']

###load pre-fetched datasets
full_anomaly = load_gistemp_monthly_anomaly() #nasa anomaly data used for monthly, seasonal
yearly_landocean = load_nasa_yearly_landocean() #yearly nasa land-ocean temperature index
nosmooth_landocean = yearly_landocean[yearly_landocean.columns[:-1]].nlargest(10, 'No_Smoothing')
smoothed_landocean = yearly_landocean.drop('No_Smoothing',1).nlargest(10, 'Lowess(5)')

app.layout = html.Div(children=[
    html.H1('Will this be the hottest year on record?'),
    html.Div([
        html.Div(html.H3(['[PredictIt Logo]', html.Br(),'''
        Latest Price (Yes): $ 
        ''' + str(lastPrice)]), className="six columns"
        ),
        html.Div([dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in nosmooth_landocean.columns],
            data=nosmooth_landocean.to_dict('records'),
            style_as_list_view=False
            )],className="eight columns")
    ], className="row"),
    html.Br(),
    html.Div(
        dcc.Graph(
            id='anomaly',
            figure=monthly_anomaly_fig(full_anomaly)
        )),
#end of dash
])

if __name__ == '__main__':
    application.run(debug=True, port=8080)




    