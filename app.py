"""
Temperature Anomaly Dashboard

**Will NASA find 2020’s global average temperature highest on record?**
https://www.predictit.org/markets/detail/6234/

Official yearly measurement: 
https://data.giss.nasa.gov/gistemp/graphs/graph_data/Global_Mean_Estimates_based_on_Land_and_Ocean_Data/graph.txt
"""

import pdb

import requests
import datetime
from datetime import date
from pathlib import Path
import copy
import pandas as pd
import numpy as np
import sqlite3
import flask
import calendar
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import dash_auth
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objs as go
import plotly.figure_factory as ff
import colorlover as cl
import infos
from colormap import rgb2hex

def loess_plot(moyhu_data):
    lowess_fig = px.scatter(moyhu_data, x="Year", y="TempLSLOESS", trendline="lowess")
    lowess_fig.update_layout(
        title="TempLS LOESS Trend",
        title_x=0.5)
    return lowess_fig 

def showdown_scatter(monthly_anomaly):
    #takes full monthly_anomaly csv  df, produces current year vs. reigning champion  
    month_list = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    monthly_anomaly_fig = go.Figure()
    for i in range(0, len(monthly_anomaly)):
        line_name = str(monthly_anomaly.iloc[i].name)
        if line_name in ('2016', '2020', '2021'):
            monthly_anomaly_fig.add_trace(go.Scatter(y=monthly_anomaly.iloc[i], x=month_list, name=line_name, marker_symbol='line-ns', line_color=colorize_row(monthly_anomaly.iloc[i]) ))
    monthly_anomaly_fig.update_layout(
        title="Current Year vs. Standing Record", 
        title_x=0.5,
        height=200,
  
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F2F2F2",
        margin=dict(l=10,r=25,b=20,t=40,pad=10),
        yaxis = dict(showgrid=False),
        xaxis = dict(
            range=[0,11],
            showgrid=False,))
    return monthly_anomaly_fig


def colorize_row(row):
    #above .6-red, above .1-orange, above 0-yellow, above -.21- green, below -.21 teal
    if row.name in(2021, 2020):
        return '#800080'
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

###load csv datasets
home_dir = str(Path.home())
yearly_landocean = pd.read_csv(home_dir + '/data/nasa_landocean_yearly.csv') #yearly nasa land-ocean temperature index
full_anomaly = pd.read_csv(home_dir + '/data/gistemp_monthly.csv') #nasa anomaly data used for monthly, seasonal
full_anomaly.set_index('Year', inplace=True)
moyhu_data = pd.read_csv(home_dir + '/data/moyhu_monthly.csv')
###
#======================================
#   Dash                              
#======================================
server = flask.Flask('app')
app = dash.Dash('app', assets_folder='static', server=server)
#auth = dash_auth.BasicAuth(
#    app,
#    infos.VALID_USERNAME_PASSWORD_PAIRS
#)

app.index_string = infos.analytics_string
app.title = 'Will this be the hottest year on record?'

app.layout = html.Div(children=[
    html.H1('Will this be the hottest year on record?'),
    html.Div([
        html.Div(
            [html.H2(dcc.Link('PredictIt Market', target="_blank", href="https://www.predictit.org/markets/detail/6234/Will-NASA-find-2020%E2%80%99s-global-average-temperature-highest-on-record",
            title="""The global temperature Annual Average Anomaly for 2020 shall be greater than that for all prior recorded and published years, as rounded to the nearest hundredth of a degree, according to the first-published such data on NASA's Global Climate Change website."""
            )),
            html.H3(
                [html.Div('Latest Price (Yes): $', style={"margin-left": "0px"}),
                html.Div(id='live-update-text')], className="row"
                ),
            html.H3(
                [html.Div('24 Hour Change:', style={"margin-right": "10px", "margin-left": "0px"}),
                html.Div(id='24h-update-text')], className="row"
                ),
            dcc.Interval(
                id='interval-component',
                interval=60*1000,
                n_intervals=0),
        ], className="seven columns"),
        html.Div(
            [
            html.Label('Annual Average Temperature Anomaly', style={'textAlign':'center','fontSize':16}), 
            dash_table.DataTable(
                columns=[{"name": "Year", "id":"Year"}, 
                        {"name": "Land-Sea Temperature Index", 
                        "id":"No_Smoothing"}],
                data=yearly_landocean.to_dict('records'),
                style_as_list_view=False,
                style_table={
                    'overflowY': 'scroll',
                    'height': '250px',
                    'fontSize':14,
                    'padding':5},
                style_cell={'textAlign':'center'},
                style_cell_conditional=[
                {'if': {'id': 'Year'},
                'width': '50%'},
                {'if': {'id': 'No_Smoothing'},
                'width': '50%'}]
            )],style={'backgroundColor':'#FFFFFF','padding-left':15,'padding-right':15, 'padding-top': 0, 'marginLeft': '10px', 'marginTop': '20px'},className="five columns")
    ], className="row"),
    html.Br(),
    html.Div(
        dcc.Graph(
            id='showdown',
            figure=showdown_scatter(full_anomaly)
        )),
    html.Br(),        
    html.Div([
        html.Label(
            id='anomaly-label',
            style={'textAlign':'center','fontSize':16,}),
        dcc.RangeSlider(
            id='year-slider',
            min=1880,
            max=2020,
            value=[1900,2020]),
        dcc.Graph(
            id='anomaly-scatter',),
    ], style={'backgroundColor':'#FFFFFF'}),
    html.Br(),
    html.Div(
        dcc.Graph(
            id='moyhu_plot',
            figure=loess_plot(moyhu_data)
        )),
    html.Br(),        

###end of dash
])

###callbacks
@app.callback(Output('anomaly-label', 'children'),
                Input('year-slider', 'value'))
def update_label(value):
    title =f"Monthly Temperature Anomaly {value[0]}-{value[1]}"
    return title


@app.callback(Output('anomaly-scatter', 'figure'),
              [Input('year-slider', 'value')])      
def monthly_anomaly_fig(value):
    #takes full monthly_anomaly csv  df, produces 1880-Present scatter plot  
    monthly_anomaly = full_anomaly
    month_list = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    monthly_anomaly_fig = go.Figure()
    #monthly_anomaly.at[2010, 'Jan']
    include_range = reversed(range(value[0],value[1]+1))
    for each in include_range:
        monthly_anomaly_fig.add_trace(
            go.Scatter(
            y=monthly_anomaly.loc[each], 
            #pdb.set_trace()
            #y=[monthly_anomaly.at[each]]
            x=month_list, 
            name=str(monthly_anomaly.loc[each].name), 
            line_color=colorize_row(monthly_anomaly.loc[each]),
            marker_symbol='line-ns'            
            ))
        #monthly_anomaly_fig.add_trace(go.Scatter(y=monthly_anomaly.iloc[i], x=month_list, name=str(monthly_anomaly.iloc[i].name), line_color=colorize_row(monthly_anomaly.iloc[i])))
    monthly_anomaly_fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="#F2F2F2",
        #width=800,
        margin=dict(l=20,r=40,b=20,t=0,pad=10),
        yaxis = dict(showgrid=False),
        xaxis = dict(
            range=[0,11],
            showgrid=False),
        legend = dict(bordercolor='#F2F2F2', borderwidth=1, x = 1.02),    
            )
    #figure=monthly_anomaly_fig(full_anomaly)        
    return monthly_anomaly_fig

@app.callback(Output('live-update-text', 'children'),
              Input('interval-component', 'n_intervals'))
def get_market_data(n):
    ####get PredictIt market data from API
    response = requests.get('https://www.predictit.org/api/marketdata/markets/6234/')
    data = response.json()
    return data['contracts'][0]['lastTradePrice']

@app.callback(Output('24h-update-text', 'children'),
              Input('interval-component', 'n_intervals'))
def get_24hr_change(n):
    #### 24 hr change data load - from sqlite db
    with sqlite3.connect('/home/casey/data/hottest.db') as conn:
        cur = conn.cursor()
        current_price = cur.execute("SELECT price FROM price ORDER BY rowid DESC LIMIT 1").fetchall()
        ###python-provided filter version for performance test:
        #yesterday_price = cur.execute("SELECT price FROM price WHERE strftime('%Y-%m-%d %H:%M',datetime) LIKE datetime(strftime('%Y-%m-%d %H:%M'," + current_price[0][0]+ ",'-1 hour'));").fetchall()

        ###subquery version for performance test:
        yesterday_price = cur.execute("SELECT price FROM price WHERE strftime('%Y-%m-%d %H:%M',datetime) LIKE (SELECT strftime('%Y-%m-%d %H:%M',datetime(datetime,'-1 day')) FROM price ORDER BY rowid DESC LIMIT 1);").fetchall()
        try:
            result = ' $' + str(round(current_price[0][0] - yesterday_price[0][0],2))
        except:
            result = 'Unavailable'
        return result


if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0')


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
