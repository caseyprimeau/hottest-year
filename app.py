"""
Temperature Anomaly Dashboard

**Will NASA find 2020’s global average temperature highest on record?**
https://www.predictit.org/markets/detail/6234/

Official yearly measurement: 
https://data.giss.nasa.gov/gistemp/graphs/graph_data/Global_Mean_Estimates_based_on_Land_and_Ocean_Data/graph.txt


"""
import pdb
import datetime
from datetime import date
import requests
import pandas as pd
import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objs as go


def get_market_data():
    response = requests.get('https://www.predictit.org/api/marketdata/markets/6234/')
    data = response.json()
    return data

def get_nasa_monthly():
    #url = 'https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv'
    url = 'nasa_monthly.csv'
    df = pd.read_csv(url)
    
    #remove header, promote first row to column headers
    new_header = df.iloc[0]
    df = df[1:]
    df.columns = new_header
    return df

def get_nws_daily():
    #ftp://ftp.cpc.ncep.noaa.gov/cadb_v2/docs/CADB_Daily_v2_Output_Documentation.pdf
    day = date.today()
    day = day - datetime.timedelta(days=2)
    filename = "daily_summary_" + day.strftime("%Y%m%d") + "_v2.csv"
    url = 'ftp://ftp.cpc.ncep.noaa.gov/cadb_v2/daily/' + day.strftime("%Y") + '/' + day.strftime("%m")+'/' + filename
    df = pd.read_csv(url)
    return df
    #ftp://ftp.cpc.ncep.noaa.gov/cadb_v2/daily/2020/10/daily_summary_20201030_v2.csv

def get_columns_for_nasa_table(df):
    dt_cols = []
    for col in df.columns:
        dt_cols.append({"name":str(col), "id":str(col)})
    return dt_cols

def get_normals():
    day = date.today()
    day = day - datetime.timedelta(days=2)    
    loc = "merged_daily_normals_tavg.csv"
    df = pd.read_csv(loc)
    ismonth = df['month']==int(day.strftime("%m"))
    dfmonth = df[ismonth]
    isday = dfmonth['day']==int(day.strftime("%d"))
    dfday = dfmonth[isday]
    return dfday

def main():
    external_stylesheets = ['https://codepen.io/anon/pen/mardKv.css']

    #####market data load - calls api every time
    #market_data = get_market_data()
    #lastPrice = market_data['contracts'][0]['lastTradePrice']
    #buyYesPrice = market_data['contracts'][0]['bestBuyYesCost']
    #buyNoPrice = market_data['contracts'][0]['bestBuyNoCost']

    #load and prepare global monthly
    monthlydf = get_nasa_monthly()
    monthlydf = monthlydf.iloc[::-1] #flip order of years
    #drop season  columns of means table
    i = 0
    while i < 5:
        monthlydf = monthlydf[monthlydf.columns[:-1]]
        i = i +1

    #dailydf = get_nws_daily()
    dailydf = pd.read_csv('daily_summary_20201030_v2.csv')
    normaldf = get_normals()
    comparedf = pd.merge(dailydf, normaldf, on='stn_id') #not many results
    pdb.set_trace()

    #**** dash ****

    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    app.layout = html.Div(children=[
        html.H1(children='Will this be the hottest year on record?'),
        
        html.Div(children='''
        market data: 
        '''),
    
        html.Div(children='''
        global-mean monthly, seasonal, and annual means: 
        '''),

        dash_table.DataTable(
            columns=get_columns_for_nasa_table(monthlydf),
            data=monthlydf.to_dict('records')
        )
    
    #eof
    ])
    
    app.run_server(debug=True)    

if __name__ == "__main__":
    main()

    