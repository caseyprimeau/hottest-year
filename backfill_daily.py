"""
Backfill Daily Temperature Variance CSV

start at beginning of the present month
for each day already passed:
    download daily temperature from national weather service
    join to normals table
    get daily variance
    save to csv

"""

import pdb
import datetime
from datetime import date
import calendar
import requests
import pandas as pd


def get_nws_daily(year, month, day):
    ###get csv file from national weather service containing global daily temperatures 
    datestring = year + month + str("{:02d}".format(day))
    filename = "daily_summary_" + datestring + "_v2.csv"
    url = 'ftp://ftp.cpc.ncep.noaa.gov/cadb_v2/daily/' + year + '/' + month+'/' + filename
    df = pd.read_csv(url, dtype={'stn_id': str})
    return df
    #ftp://ftp.cpc.ncep.noaa.gov/cadb_v2/daily/2020/10/daily_summary_20201030_v2.csv
    #ftp://ftp.cpc.ncep.noaa.gov/cadb_v2/docs/CADB_Daily_v2_Output_Documentation.pdf

def get_normals(month, day):
    ###import historical normals file
    loc = "merged_daily_normals_tavg.csv"
    df = pd.read_csv(loc, dtype={'stn_id': str})
    ###filter historical normals file down to current day before join w/ CY daily temperature
    ismonth = df['month']==int(month)
    dfmonth = df[ismonth]
    isday = dfmonth['day']==int(day)
    dfday = dfmonth[isday]
    return dfday

def compare_daily_normal(comparedf):
    ###drop unneeded columns from joined df
    comparedf = comparedf[['stn_id', 'date','month','day','tmax', 'tmin', 'tavg']]
    ###get daily average
    comparedf['dailyavg'] = (comparedf.tmax + comparedf.tmin)/2
    ###drop extreme outliers (bad data), create variance column
    comparedf = comparedf[comparedf['dailyavg'].abs() < 70]
    comparedf = comparedf[comparedf['tavg'].abs() < 70]
    comparedf['variance'] = (comparedf.dailyavg-comparedf.tavg)
    daily_variance = comparedf['variance'].mean()
    return daily_variance

def save_daily_variance(date, number):
    ### append daily variance
    try:
        todaydata = [[date, number]]
        newrow = pd.DataFrame(todaydata, columns = ['date', 'daily_variance'])
        newrow.to_csv('daily_variance.csv', mode='a', header=False, index=False)
    except:
        print('didnt write to daily variance')

def main():
    #get year and month
    year = date.today().strftime("%Y")
    month = date.today().strftime("%m")
    lastday = (date.today()-datetime.timedelta(days=1)).strftime("%d")

    getday = 1

    while (getday <= int(lastday)):
        dailydf = get_nws_daily(year, month, getday)
        normaldf = get_normals(month, getday)
        comparedf = pd.merge(dailydf, normaldf, on='stn_id') 
        getday_variance = compare_daily_normal(comparedf)
        save_daily_variance(year +'-'+ month + '-' + str("{:02d}".format(getday)),getday_variance)
        print(month+"-"+str("{:02d}".format(getday)))
        getday = getday + 1    
    print("done")

if __name__ == "__main__":
    main()

    