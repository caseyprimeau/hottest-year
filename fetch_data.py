import pdb
import datetime
from datetime import date
import requests
import pandas as pd


def gistemp_monthly_anomaly():
    url = 'https://data.giss.nasa.gov/gistemp/tabledata_v4/GLB.Ts+dSST.csv'
    df = pd.read_csv(url)
    df.to_csv('source_data/gistemp_monthly.csv')
    df = pd.read_csv('source_data/gistemp_monthly.csv')
    ###remove header, promote first row to column headers
    new_header = df.iloc[0]
    df = df[1:]
    df.columns = new_header
    df = df.iloc[::-1] #flip order of rows
    #pdb.set_trace()
    df.to_csv('source_data/gistemp_monthly.csv', index=False)


def nasa_landocean(): 
    url = 'https://data.giss.nasa.gov/gistemp/graphs/graph_data/Global_Mean_Estimates_based_on_Land_and_Ocean_Data/graph.txt'
    df = pd.read_csv(url, sep='\s+', header=None)

    df = df.drop([0,1,3]) #remove formatting rows
    df = df[df.columns[:-1]]
    df = df.reset_index(drop=True)
    new_header = df.iloc[0]
    df = df[1:]
    df.columns = new_header
    df = df.iloc[::-1] #flip order of rows
    df.to_csv('source_data/nasa_landocean_yearly.csv', index=False)


def main():
    gistemp_monthly_anomaly()
    nasa_landocean()
    print('made fetch happen')

if __name__ ==  "__main__":
    main()