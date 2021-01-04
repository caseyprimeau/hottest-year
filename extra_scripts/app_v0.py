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
import calendar
import requests
import pandas as pd
import numpy as np
import dash
import copy
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import plotly.graph_objs as go
import plotly.figure_factory as ff
import colorlover as cl

daily_variance = 0

def get_market_data():
    ####get PredictIt market data from API
    response = requests.get('https://www.predictit.org/api/marketdata/markets/6234/')
    data = response.json()
    return data

def get_nasa_monthly():
    ###get csv file with nasa monthly global average temperature anomaly
    url = 'https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv'
    #url = 'nasa_monthly.csv'
    df = pd.read_csv(url)
    
    ###remove header, promote first row to column headers
    new_header = df.iloc[0]
    df = df[1:]
    df.columns = new_header
    return df

def get_nws_daily():
    ###get csv file from national weather service containing global daily temperatures 
    day = date.today()
    day = day - datetime.timedelta(days=2)
    filename = "daily_summary_" + day.strftime("%Y%m%d") + "_v2.csv"
    url = 'ftp://ftp.cpc.ncep.noaa.gov/cadb_v2/daily/' + day.strftime("%Y") + '/' + day.strftime("%m")+'/' + filename
    df = pd.read_csv(url, dtype={'stn_id': str})
    return df
    #ftp://ftp.cpc.ncep.noaa.gov/cadb_v2/daily/2020/10/daily_summary_20201030_v2.csv
    #ftp://ftp.cpc.ncep.noaa.gov/cadb_v2/docs/CADB_Daily_v2_Output_Documentation.pdf

def get_columns_for_table(df):
    ###generic function to get column names from dataframe for use in dash tables
    dt_cols = []
    for col in df.columns:
        dt_cols.append({"name":str(col), "id":str(col)})
    return dt_cols

def get_normals():
    ###import historical normals file
    day = date.today()
    day = day - datetime.timedelta(days=1)    
    loc = "merged_daily_normals_tavg.csv"
    df = pd.read_csv(loc, dtype={'stn_id': str})
    ###filter historical normals file down to current day before join w/ CY daily temperature
    ismonth = df['month']==int(day.strftime("%m"))
    dfmonth = df[ismonth]
    isday = dfmonth['day']==int(day.strftime("%d"))
    dfday = dfmonth[isday]
    return dfday

def compare_daily_normal(comparedf):
    ###drop unneeded columns from joined df
    comparedf = comparedf[['stn_id', 'date','month','day','tmax', 'tmin', 'tavg']]

    ###get daily average
    global daily_variance
    comparedf['dailyavg'] = (comparedf.tmax + comparedf.tmin)/2

    ###drop extreme outliers (bad data), create variance column
    comparedf = comparedf[comparedf['dailyavg'].abs() < 70]
    comparedf = comparedf[comparedf['tavg'].abs() < 70]
    comparedf['variance'] = (comparedf.dailyavg-comparedf.tavg)
    daily_variance = comparedf['variance'].mean()
    return comparedf

def save_daily_variance():
    ###check if last row of daily variance record is today, if not append daily variance
    global daily_variance
    day = date.today()
    day = day - datetime.timedelta(days=1) 
    day = day.strftime('%Y%m%d')    
    csvdf = pd.read_csv('daily_variance.csv')
    csvdf = csvdf.tail(1)
    try:
        if (csvdf.at[0,'date'] != day):
            todaydata = [[day, daily_variance]]
            newrow = pd.DataFrame(todaydata, columns = ['date', 'daily_variance'])
            newrow.to_csv('daily_variance.csv', mode='a', header=False, index=False)
        else:
            print('daily variance is already written')
    except:
        print('didnt write to daily variance')

def variance_calendar():
    ###dummydata: To create the heatmap Calendar
    variancedf = pd.read_csv('daily_variance.csv')
    variancedf.columns = ["date", "daily_variance"]
    pp_array = list(variancedf.daily_variance)
    date_string_array = list(variancedf.date)
    ##Initialize the Calendar Object. For more information, please read the calendar module library. https://docs.python.org/2/library/calendar.html
    day = date.today()
    year =  int(day.strftime("%Y")) 
    month = int(day.strftime("%m")) 
    calendar_object=calendar.Calendar()
    days1 = calendar_object.monthdatescalendar(year,month)
    if (len(days1) >5):
        y=['Week 1','Week 2','Week 3','Week 4','Week 5', 'Week 6']
        days=[[None]*7,[None]*7,[None]*7,[None]*7,[None]*7,[None]*7]
    else:
        y=['Week 1','Week 2','Week 3','Week 4','Week 5']
        days=[[None]*7,[None]*7,[None]*7,[None]*7,[None]*7]

    for rows_number, rows in enumerate(days1):
        for time_index, time in enumerate(rows):
            print("rows Number")
            print(rows_number)
            print("rows")
            print(rows)
            print("Time index")
            print(time_index)
            days[rows_number][time_index] = time.day


    ###In terms of the color gradients/color scales. Please the read the doc. https://plot.ly/python/colorscales/
    colorscale = [[0,'rgb(255,255,255)'],[0.25,'rgb(255,255,255)'],[0.25,'rgb(0,191,255)'],[0.5,'rgb(255,0,0)'],[0.5,'rgb(231,124,17)'], [0.75,'rgb(255,255,0)' ],[0.75,'rgb(0,254,0)'],[1,'rgb(255,0,0)']]
    num = len(pp_array)
    day_numbers= len(date_string_array)
    ###In python, values are passed by reference. Make a copy so it won't change the initial list. 

    dates_list = [datetime.datetime.strptime(date, '%Y-%m-%d').date() for date in date_string_array]  ##Convert date string objects to datetime objects
    color_array=copy.deepcopy(days1)
    textinfo = copy.deepcopy(days1)

    x=['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    y=y[::-1]   ##REVERSE THE lists order

    ### Assign the value into specific day.
    for rows_number, rows in enumerate(days1):
        for time_index, time in enumerate(rows):
            for i in range(day_numbers):
                if dates_list[i] == time:
                    if float(pp_array[i]) < 0 and float(pp_array[i]) >=-10:
                        color_array[rows_number][time_index] = 1
                        textinfo[rows_number][time_index] ='Variance: '+str(pp_array[i])
                        break
                    if float(pp_array[i]) < 2 and float(pp_array[i]) >=0:
                        color_array[rows_number][time_index] = 2
                        textinfo[rows_number][time_index]= 'Variance:'+str(pp_array[i])
                        break
                    if float(pp_array[i]) >=2:
                        color_array[rows_number][time_index] = 3
                        textinfo[rows_number][time_index] = 'Variance: '+str(pp_array[i])
                        break
            else:
                color_array[rows_number][time_index] =0
                textinfo[rows_number][time_index] = 'Data is not available yet'

    ## Z values indicate the color of date'cells.
    z = color_array[::-1]
    days = days[::-1]
    textinfo = textinfo[::-1]

    ## Plot the heatmap calendar
    pt = ff.create_annotated_heatmap(z, x=x, y=y, annotation_text=days, colorscale=colorscale, font_colors=['black'], hoverinfo='text', text = textinfo)  ##Figure
    pt.layout.title = datetime.datetime.now().strftime("%B")
    calendarfig = go.Figure(data=pt, layout=calendar_layout())
    return calendarfig

def calendar_layout():
    cal_layout = go.Layout(
    autosize=False,
    width=700,
    height=450,
    margin=go.Margin(
        l=150,
        r=160,
        b=50,
        t=100,
        pad=3
        ),
        xaxis=dict(
        title='Week',
        showgrid=False,
        titlefont=dict(
            size=12,
        ),),
    )
    return cal_layout

def main():
    external_stylesheets = ['https://codepen.io/anon/pen/mardKv.css']

    ####market data load - calls api every time
    market_data = get_market_data()
    lastPrice = market_data['contracts'][0]['lastTradePrice']
    buyYesPrice = market_data['contracts'][0]['bestBuyYesCost']
    buyNoPrice = market_data['contracts'][0]['bestBuyNoCost']

    ###load and prepare global monthly
    monthlydf = get_nasa_monthly()
    monthlydf = monthlydf.iloc[::-1] #flip order of years
    ###drop seasonal columns of means table
    i = 0
    while i < 5:
        monthlydf = monthlydf[monthlydf.columns[:-1]]
        i = i +1

    ###compare daily national weather service temperatures to historical normal on this date
    dailydf = get_nws_daily()
    ###dailydf = pd.read_csv('daily_summary_20201031_v2.csv')
    normaldf = get_normals()
    comparedf = pd.merge(dailydf, normaldf, on='stn_id') #merge daily with normals
    comparedf = compare_daily_normal(comparedf)
    save_daily_variance()

    
    ###**** dash ****

    app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
    
    app.layout = html.Div(children=[
        html.H1(children='Will this be the hottest year on record?'),
        
        html.Div(children='''
        latest price: $ 
        ''' + str(lastPrice)),
    
        html.Div(children='''
        daily variance: 
        '''+ str(round(daily_variance,2)) + chr(176)),

        dcc.Graph(id = 'my-graph', figure = variance_calendar()),

        dash_table.DataTable(
            columns=get_columns_for_table(comparedf),
            data=comparedf.to_dict('records')
        ),

        html.Div(children='''
        global-mean monthly, seasonal, and annual means: 
        '''),

        dash_table.DataTable(
            columns=get_columns_for_table(monthlydf),
            data=monthlydf.to_dict('records'),
            style_as_list_view=True
        )
    
    #eof
    ])
    
    app.run_server(debug=True)    

if __name__ == "__main__":
    main()

    