"""
Temperature Anomaly Dashboard

**Will NASA find 2020’s global average temperature highest on record?**
https://www.predictit.org/markets/detail/6234/

Official yearly measurement: 
https://data.giss.nasa.gov/gistemp/graphs/graph_data/Global_Mean_Estimates_based_on_Land_and_Ocean_Data/graph.txt
"""

import requests
import datetime
from datetime import date
from pathlib import Path
import pandas as pd
import numpy as np
import sqlite3
import flask
import dash
import dash_table
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
import dash_auth
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objs as go
import infos, secret

### Load CSV datasets - prepared daily by fetch_data.py
home_dir = str(Path.home())
yearly_landocean = pd.read_csv(home_dir + '/data/nasa_landocean_yearly.csv') #yearly nasa land-ocean temperature index
full_anomaly = pd.read_csv(home_dir + '/data/gistemp_monthly.csv') #nasa anomaly data used for monthly, seasonal
full_anomaly.set_index('Year', inplace=True)
moyhu_data = pd.read_csv(home_dir + '/data/moyhu_monthly.csv')

#======================================
#   Dash                              
#======================================
server = flask.Flask('app')
app = dash.Dash('app', assets_folder='static', server=server)

app.index_string = secret.analytics_string
app.title = 'Will this be the hottest year on record?'

app.layout = html.Div(children=[
    html.H1('Will this be the hottest year on record?'),
    html.Div([
        html.Div(
            [html.H2(dcc.Link('2020 PredictIt Market', target="_blank", href="https://www.predictit.org/markets/detail/6234/Will-NASA-find-2020%E2%80%99s-global-average-temperature-highest-on-record",
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
            html.H3("PredictIt did not run this market in 2021, unfortunately"),
            dcc.Interval(   #performs refresh action for price 
                id='interval-component',
                interval=60*1000,
                n_intervals=0),
        ], className="seven columns"),
        html.Div(
            [html.Label('Annual Temperature Anomaly', id='dummy-label',style={'textAlign':'center','fontSize':16}), 
            dash_table.DataTable(
                columns=[{"name": "Rank", "id":"Rank"}, 
                        {"name": "Year", "id":"Year"}, 
                        {"name": "Temperature Index", "id":"No_Smoothing"}],
                data=yearly_landocean.to_dict('records'),
                style_header={'backgroundColor': 'rgb(30, 30, 30)', 'color': 'white', 'padding-right':10 },                
                style_as_list_view=True,
                style_table={
                    'overflowY':'scroll',
                    'height':'150px',
                    'fontSize':16,
                    'padding':5},
                style_cell={'textAlign':'center',         
                            'backgroundColor': '#F2F2F2',
                            'color': 'black'},
                style_cell_conditional=[
                {'if': { 'filter_query': '{Rank} = 1'},
                'color': 'red'},
                {'if': {'id': 'Rank'},
                'width': '50%'},
                {'if': {'id': 'Year'},
                'width': '40%'},
                {'if': {'id': 'No_Smoothing'},
                'width': '10%'}]
            )],style={'backgroundColor':'#FFFFFF','padding-left':15,'padding-right':15, 'padding-top': 0, 'padding-bottom':'10px', 'marginLeft': '10px', 'marginRight': '10px', 'marginTop': '20px'}
            ,className="five columns")
    ], className="row"),
    html.Br(),
    html.Div([
        html.H3(['NASA GISTEMP ', html.Img(id='expand-nasa', n_clicks=0 )]),
        dbc.Collapse([
            dbc.Card(dbc.CardBody(dcc.Markdown(infos.nasa_gistemp, dangerously_allow_html=True))),
            html.Br()],
            id='nasa-container')
        ], style={"margin-left": "5px"}),
    html.Div(
        dcc.Graph(
            id='showdown-scatter',)),
    html.Br(),        
    html.Div([
        html.Label(
            id='monthly-anomaly-label',
            style={'textAlign':'center','fontSize':16,}),
        dcc.RangeSlider(
            id='year-slider',
            min=1880,
            max=2021,
            value=[1900,2021]),
        dcc.Graph(
            id='anomaly-scatter',),
    ], style={'backgroundColor':'#FFFFFF'}),
    html.Br(),
    html.Div([
        html.Div([
            html.H3(['TempLS ', html.Img(id='expand-templs', n_clicks=0 )]),
            dbc.Collapse([
                dbc.Card(dbc.CardBody(dcc.Markdown(infos.templs, dangerously_allow_html=True))),
                html.Br()],
                id='templs-container')
            ], style={"margin-left": "5px"}),
        html.Div([
        dcc.Dropdown(
            id='templs-dropdown',
            options=[
                {'label':'TempLSgrid',          'value':'TempLSgrid'},
                {'label':'TempLSinfill',        'value':'TempLSinfill'},
                {'label':'TempLSLOESS',         'value':'TempLSLOESS'},
                {'label':'TempLSmesh',          'value':'TempLSmesh'},
                {'label':'TempLSgrid_adj',      'value':'TempLSgrid_adj'},
                {'label':'TempLSinfill_adj',    'value':'TempLSinfill_adj'},
                {'label':'TempLSLOESS_adj',     'value':'TempLSLOESS_adj'},
                {'label':'TempLSmesh_adj',      'value':'TempLSmesh_adj'},
                {'label':'TempLS_SST',          'value':'TempLS_SST'},
                {'label':'TempLS_La',           'value':'TempLS_La'},
            ],
            value ='TempLSgrid',
            style={'fontSize':20, 'width':300}
            )], className="row"),
        dcc.Graph(
            id='templs-plot',
            style={'textAlign':'center','fontSize':16}),
        ]),
    html.Br(),
    html.P('This is not investment advice.'),
    html.Footer(html.P(dcc.Link('Casey Primeau', target="_blank", href="https://caseyprimeau.com/")),
    style={'textAlign': 'right', 'backgroundColor':'#e6e6e6'})
###end of dash layout
])
#======================================

def colorize_line(row):
    #above .6-red, above .1-orange, above 0-yellow, above -.21- green, below -.21 teal
    if row.name in(2020, 2016):
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

def colorize_marker(value):
    #above .6-red, above .1-orange, above 0-yellow, above -.21- green, below -.21 teal
    if value > 0.6:
        return '#FF0000'
    elif 0.6 >= value > 0.1:
        return '#ef7f1c'
    elif 0.1 >= value > 0.0:
        return '#96ce48'      
    elif 0 >= value > -0.21:
        return '#64ad7f'
    elif -0.21>= value:
        return '#6d9d95'            
    else:
        return'#FFFFFF'

### Callbacks
@app.callback(Output('live-update-text', 'children'),
              Input('interval-component', 'n_intervals'))
def get_market_data(n):
    #~Call PredictIt API, Return last price
    response = requests.get('https://www.predictit.org/api/marketdata/markets/6234/')
    data = response.json()
    return data['contracts'][0]['lastTradePrice']


@app.callback(Output('24h-update-text', 'children'),
              Input('interval-component', 'n_intervals'))
def get_24hr_change(n):
    #~24 hr change data load - from sqlite db
    with sqlite3.connect('/home/casey/data/hottest.db') as conn:
        cur = conn.cursor()
        current_price = cur.execute("SELECT price FROM price ORDER BY rowid DESC LIMIT 1").fetchall()
        ### python-provided filter version for performance test:
        #yesterday_price = cur.execute("SELECT price FROM price WHERE strftime('%Y-%m-%d %H:%M',datetime) LIKE datetime(strftime('%Y-%m-%d %H:%M'," + current_price[0][0]+ ",'-1 hour'));").fetchall()

        ### subquery version for performance test:
        yesterday_price = cur.execute("SELECT price FROM price WHERE strftime('%Y-%m-%d %H:%M',datetime) LIKE (SELECT strftime('%Y-%m-%d %H:%M',datetime(datetime,'-1 day')) FROM price ORDER BY rowid DESC LIMIT 1);").fetchall()
        try:
            result = ' $' + str(round(current_price[0][0] - yesterday_price[0][0],2))
        except:
            result = 'Unavailable'
        return result

@app.callback(Output('nasa-container', 'is_open'),
            Output('expand-nasa', 'src'),
            Input('expand-nasa', 'n_clicks'),
            State('nasa-container','is_open'))
def toggle_nasa_info(n, is_open):
    if(n):
        if (is_open == True) :
            is_open = False
            return is_open, app.get_asset_url('chevron-down.svg')
        else:
            is_open = True
            return is_open, app.get_asset_url('chevron-up.svg')
    is_open =False
    return is_open, app.get_asset_url('chevron-down.svg')

@app.callback(Output('showdown-scatter', 'figure'),
                Input('dummy-label', 'value'))
def showdown_scatter(value):
    #~Input: full monthly_anomaly df. Output: current year (hardcoded) vs. reigning champions  
    month_list = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    monthly_anomaly = full_anomaly
    showdown_scatter_fig = go.Figure()
    for i in range(0, len(monthly_anomaly)):
        line_name = str(monthly_anomaly.iloc[i].name)
        if (line_name =='2022'):
            showdown_scatter_fig.add_trace(go.Scatter(y=monthly_anomaly.iloc[i], x=month_list, name=line_name, marker_symbol='line-ns', line_color=colorize_line(monthly_anomaly.iloc[i]) ))
        if (line_name in('2016', '2020')):
            showdown_scatter_fig.add_trace(go.Scatter(y=monthly_anomaly.iloc[i], x=month_list, name=line_name, marker_symbol='circle-open-dot', line_color="#000000"))#colorize_line(monthly_anomaly.iloc[i]) ))

    showdown_scatter_fig.update_layout(
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
    return showdown_scatter_fig


@app.callback(Output('monthly-anomaly-label', 'children'),
                Input('year-slider', 'value'))
def update_monthly_anomaly_title(value):
    title =f"Monthly Temperature Anomaly {value[0]}-{value[1]}"
    return title


@app.callback(Output('anomaly-scatter', 'figure'),
              [Input('year-slider', 'value')])      
def monthly_anomaly_fig(value):
    #~Input: full monthly_anomaly df, Output: 1880-Present scatter plot  
    monthly_anomaly = full_anomaly
    month_list = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    monthly_anomaly_fig = go.Figure()
    include_range = reversed(range(value[0],value[1]+1))
    for each in include_range:
        monthly_anomaly_fig.add_trace(
            go.Scatter(
            y=monthly_anomaly.loc[each], 
            x=month_list, 
            name=str(monthly_anomaly.loc[each].name), 
            line_color=colorize_line(monthly_anomaly.loc[each]),
            marker_symbol='line-ns'            
            ))
    monthly_anomaly_fig.update_layout(
        paper_bgcolor="white",
        plot_bgcolor="#F2F2F2",
        margin=dict(l=20,r=40,b=20,t=0,pad=10),
        yaxis = dict(showgrid=False),
        xaxis = dict(
            range=[0,11],
            showgrid=True),
        legend = dict(bordercolor='#F2F2F2', borderwidth=1, x = 1.02),    
            )   
    return monthly_anomaly_fig

@app.callback(Output('templs-container', 'is_open'),
            Output('expand-templs', 'src'),
            Input('expand-templs', 'n_clicks'),
            State('templs-container','is_open'))
def toggle_templs_info(n, is_open):
    if(n):
        if (is_open == True):
            is_open = False
            return is_open, app.get_asset_url('chevron-down.svg')
        else:
            is_open = True
            return is_open, app.get_asset_url('chevron-up.svg')
    return not is_open, app.get_asset_url('chevron-up.svg')

@app.callback(Output('templs-plot', 'figure'),
                Input('templs-dropdown', 'value'))
def monthly_tempLS_fig(value):
    #~Input: TempLS df, dropdown seletion, Output: TempLS plot
    templs_fig = px.scatter(moyhu_data, x="Year", y=value, trendline="lowess")
    templs_fig.update_layout(
        title="TempLS | " + value,
        title_x=0.5,
        paper_bgcolor="white",
        plot_bgcolor="#F2F2F2",
        
        margin=dict(l=0,r=20,b=30,pad=0),
        xaxis_title="",
        yaxis_title="",
        yaxis = dict(showgrid=False),
        xaxis = dict(showgrid=True))
    templs_fig.update_traces(marker=dict(color=moyhu_data.groupby(moyhu_data.Year.astype(str).str[:4])[value].transform('mean').apply(colorize_marker).tolist()))
    return templs_fig 


if __name__ == '__main__':
    app.run_server(debug=False, host='0.0.0.0')