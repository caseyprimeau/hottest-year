import pdb
import datetime
from datetime import date
import requests
import pandas as pd
from pathlib import Path

home_dir = str(Path.home())

def gistemp_monthly_anomaly():
    url = 'https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv'
    df = pd.read_csv(url, header=1) #remove header
    df = df.iloc[::-1] #flip order of rows
    df = df.replace('***', '')
    for i in range(0,6):  ###isolate monthly columns
        df = df[df.columns[:-1]]
    df.to_csv(home_dir + '/data/gistemp_monthly.csv', index=False)


def nasa_yearly_landocean(): 
    url = 'https://data.giss.nasa.gov/gistemp/graphs/graph_data/Global_Mean_Estimates_based_on_Land_and_Ocean_Data/graph.txt'
    df = pd.read_csv(url, sep='\s+', header=2) #remove header
    df = df.drop([0,1,3]) #remove formatting rows
    df = df[df.columns[:-1]] #drop smoothing column
    df = df.reset_index(drop=True)
    df.sort_values(by='No_Smoothing', ascending=False, inplace=True)
    df.to_csv(home_dir + '/data/nasa_landocean_yearly.csv', index=False)

def moyhu_monthly():
    url = 'https://s3-us-west-1.amazonaws.com/www.moyhu.org/data/month/month.csv'
    df = pd.read_csv(url)
    df = df[df.columns[1:]]
    #df = df.drop([x for x in range(0,360)])
    #replace_dict ={
    #    '.04':'.01',
    #    '.12':'.02',
    #    '.21':'.03',
    #    '.29':'.04',
    #    '.37':'.05',
    #    '.46':'.06',
    #    '.54':'.07',
    #    '.62':'.08',
    #    '.71':'.09',
    #    '.79':'.10',
    #    '.87':'.11',
    #    '.96':'.12',
    #}
    #df['Year'] = df['Year'].astype(str).replace(replace_dict, regex=True)
    #pdb.set_trace()
    df['Year'] = df['Year'].astype(float)
    df.to_csv(home_dir + '/data/moyhu_monthly.csv', index=False)

def main():
    gistemp_monthly_anomaly()
    nasa_yearly_landocean()
    moyhu_monthly()
    print('made fetch happen')

if __name__ ==  "__main__":
    main()