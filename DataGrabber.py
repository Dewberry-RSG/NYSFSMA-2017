# -*- coding: utf-8 -*-
"""
Created on Thu Feb  2 16:16:29 2017

@author: slawler
"""

import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime
from collections import OrderedDict
import matplotlib.pyplot as plt
  
# Start date (year, month, day)
y0, m0 ,d0 = 1900, 1, 1         
y1, m1 ,d1 = 2020, 1, 1    
  
#USGS parameter
flow = "00060"  
stage = "00065"

# Create Datetime Objects
start     = datetime(y0, m0, d0,0)    
stop      = datetime(y1, m1 ,d1,0) 


def GetTidePrediction(gage, start, stop):   
    #--NOAA API https://tidesandcurrents.noaa.gov/api/
    datum     = "msl"   #"NAVD"                  #Datum
    units     = "english"                         #Units
    time_zone = "lst_ldt"                         #Time Zone
    fmt       = "json"                            #Format
    url       = 'http://tidesandcurrents.noaa.gov/api/datagetter'
    product   = 'predictions'                     #Product
    
    noaa_time_step = '6T'
    noaa = pd.DataFrame()
    gages = dict()
    
    t0     = start.strftime('%Y%m%d %H:%M')
    t1     = stop.strftime('%Y%m%d %H:%M')
    api_params = {'begin_date': t0, 'end_date': t1,
                'station': gage,'product':product,'datum':datum,
                'units':units,'time_zone':time_zone,'format':fmt,
                'application':'web_services' }
        
    pred=[];t=[]

    r = requests.get(url, params = api_params)
    jdata =r.json()
    
    for j in jdata['predictions']:
        t.append(str(j['t']))
        pred.append(str(j['v']))

    colname = str(gage)    
    noaa[colname]= pred
    noaa[colname] = noaa[colname].astype(float)
      
    idx = pd.date_range(start,periods = len(noaa.index), freq=noaa_time_step)   
    noaa = noaa.set_index(idx)  
    print('We have Predictions ' , gage) 
    return noaa 

def GetTideObservation(gage, start, stop):   
    #--NOAA API https://tidesandcurrents.noaa.gov/api/
    datum     = "msl"   #"NAVD"                  #Datum
    units     = "english"                         #Units
    time_zone = "lst_ldt"                         #Time Zone
    fmt       = "json"                            #Format
    url       = 'http://tidesandcurrents.noaa.gov/api/datagetter'
    product   = 'hourly_height'                     #Product
    
    noaa_time_step = '60T'
    noaa = pd.DataFrame()
    gages = dict()
    
    t0     = start.strftime('%Y%m%d %H:%M')
    t1     = stop.strftime('%Y%m%d %H:%M')
    api_params = {'begin_date': t0, 'end_date': t1,
                'station': gage,'product':product,'datum':datum,
                'units':units,'time_zone':time_zone,'format':fmt,
                'application':'web_services' }
        
    pred=[];t=[]

    r = requests.get(url, params = api_params)
    jdata =r.json()
    
    for j in jdata['data']:
        t.append(str(j['t']))
        pred.append(str(j['v']))
    
    colname = str(gage)    
    noaa[colname]= pred
    noaa[colname] = noaa[colname].astype(float)
         
    idx = pd.date_range(start,periods = len(noaa.index), freq=noaa_time_step)   
    noaa = noaa.set_index(idx)  
    print('We have Observations ' , gage) 
    return noaa

    
def Get_USGS_Instant(gage, parameter, start, stop):  
               
    dformat    = "json"                                  # Data Format  
    url        = 'http://waterservices.usgs.gov/nwis/iv' # USGS API
    
    # Format Datetime Objects for USGS API
    first    =  datetime.date(start).strftime('%Y-%m-%d')
    last     =  datetime.date(stop).strftime('%Y-%m-%d') 
    

    # Ping the USGS API for data
    params = OrderedDict([('format',dformat),('sites',gage),('startDT',first), 
                ('endDT',last), ('parameterCD',parameter)])  
    
    r = requests.get(url, params = params) 
    print("\nRetrieved Data for USGS Gage: ", gage)
    data = r.content.decode()
    d = json.loads(data)
    mydict = dict(d['value']['timeSeries'][0])

    if params['parameterCD'] == '00060':
        obser = "StreamFlow"
    else:
        obser = "Stage"
        
    # Great, We can pull the station name, and assign to a variable for use later:
    SiteName = mydict['sourceInfo']['siteName']
    print('\n', SiteName)
    
    
    # After reveiwing the JSON Data structure, select only data we need: 
    tseries = d['value']['timeSeries'][0]['values'][0]['value'][:]
    
    # Create a Dataframe, format Datetime data,and assign numeric type to observations
    df = pd.DataFrame.from_dict(tseries)
    df.index = pd.to_datetime(df['dateTime'],format='%Y-%m-%d{}%H:%M:%S'.format('T'))

    df.value = pd.to_numeric(df.value)
    
    # Get Rid of unwanted data, rename observed data
    df = df.drop('dateTime', 1)
    df = df.rename(columns = {'value':obser})
    return df    

def Get_Peaks(gage):  
    url = 'https://nwis.waterdata.usgs.gov/ny/nwis/peak?site_no={}&agency_cd=USGS&format=rdb'.format(gage)
    df = pd.read_csv(url, skiprows=64, sep = '\t')
    df.drop(0, axis=0, inplace=True)
    y = df['peak_va'].astype(float)
    x = df['peak_dt']
    x = pd.to_datetime(x, format= '%Y-%m-%d')
    y.index = x
    return y     

def StageFlowPlotter(df_q, df_s, start, stop):
    df_q  = df_q[start:stop]
    df_s = df_s[start:stop]

    x = df_q.index
    y1 = df_q['StreamFlow']
    y2 = df_s['Stage']

    fig, ax1 = plt.subplots()
    ax1.set_ylabel(y1.name, color='r')    
    ax1.plot(x, y1, 'r')
    ax1.set_xlabel('Time')

    ax2 = ax1.twinx()
    ax2.plot(x, y2, 'b')
    ax2.set_ylabel('Stage', color='b')
    ax2.tick_params('y', colors='b')

    fig.autofmt_xdate()
    ax1.grid()


def Q_to_Stage(usgs_gage_id):
    url = r'https://waterdata.usgs.gov/nwisweb/get_ratings?site_no={}&file_type=exsa'.format(usgs_gage_id)
    cols = ['INDEP', 'SHIFT','DEP','STOR']
    usgs_data = pd.read_csv(url, skiprows = 38, sep = '\t', names = cols)

    poly_order = 3
    xs = np.array(usgs_data['DEP'])
    ys = np.array(usgs_data['INDEP'])

    coefs    = np.polyfit(xs,ys,poly_order)
    polynomial = np.poly1d(coefs) 
    
    return polynomial

def GetPKFQ(gage):
    url = 'https://nwis.waterdata.usgs.gov/ny/nwis/peak?site_no={}&agency_cd=USGS&format=hn2'.format(gage)
    pkf = pd.read_csv(url)
    pkf.to_csv('return_periods\\{}.pkf'.format(gage), sep='\t', index=False)
    print('{} Data Saved in return_periods'.format(gage))


def Get_USGS_Daily(gage):  
    url = 'https://waterdata.usgs.gov/nwis/dv?cb_00060=on&format=rdb&site_no={}&referred_module=sw&period=&begin_date=1900-01-01&end_date=2020-01-01'.format(gage)
    df = pd.read_csv(url, skiprows=64, sep = '\t')
    df.drop(0, axis=0, inplace=True)
    y = df['peak_va'].astype(float)
    x = df['peak_dt']
    x = pd.to_datetime(x, format= '%Y-%m-%d')
    y.index = x
    return y  


def GotoUSGS(state):
    url = 'https://waterdata.usgs.gov/nwis/uv?referred_module=sw&state_cd={}&site_tp_cd=OC&site_tp_cd=OC-CO&site_tp_cd=ES&site_tp_cd=LK&site_tp_cd=ST&site_tp_cd=ST-CA&site_tp_cd=ST-DCH&site_tp_cd=ST-TS&format=station_list'.format(state)
    return url

def GotoNOAA():
    url = 'https://tidesandcurrents.noaa.gov/stations.html?type=Water+Levels'
    return url    

def GetURL(gage):
    url = 'https://waterdata.usgs.gov/nwis/dv?cb_00060=on&format=rdb&site_no={}&referred_module=sw&period=&begin_date=1900-03-23&end_date=2020-03-23'.format(gage)
    return url

def plotsingle(df1, df4, df5, Tides_Only, order):
    df = df1[['datetime', 'Stage']].copy()
    df.set_index('datetime', inplace=True)
    df = df.ix[start_plot:stop_plot]
    x1 = df.index
    y1 = df['Stage'].resample('6T').mean()
    interpolated = y1.interpolate(method='cubic', order=order)

    fig, ax1 = plt.subplots()
    ax1.set_ylabel('Stage: Tidal', color='black')    
    ax1.plot(df4.index, df4[Tides_Only], 'r')
    ax1.plot(df5.index, df5[Tides_Only], 'b')

    ax1.set_xlabel('Time')
    fig.autofmt_xdate()
    axes = plt.gca()
    axes.grid()

    ax2 = ax1.twinx()
    ax2.plot(interpolated, 'black')
    ax2.set_ylabel('Stage: Fluvial', color='black')  
    axes.set_xlim([df4.index[0],df4.index[-1]])

def plotmultiple(df1, df2, df3, df4, df5, df1_name, df2_name, df3_name, Tides_Only,order, start_plot, stop_plot):
    f, (ax_1, ax_2, ax_3) = plt.subplots(3, sharex=True, sharey=True)
    df = df1[['datetime', 'Stage']].copy()
    df.set_index('datetime', inplace=True)
    df = df.ix[start_plot:stop_plot]
    x1 = df.index
    y1 = df['Stage'].resample('6T').mean()
    interpolated = y1.interpolate(method='cubic', order=2)


    ax_1.set_ylabel('{}'.format(Tides_Only), color='black')     
    ax_1.plot(df4.index, df4[Tides_Only], 'r')
    ax_1.plot(df5.index, df5[Tides_Only], 'b')
    ax_1a = ax_1.twinx()
    ax_1a.plot(interpolated, 'black')
    ax_1a.set_ylabel('{}'.format(df1_name), color='black') 


    df = df2[['datetime', 'Stage']].copy()
    df.set_index('datetime', inplace=True)
    df = df.ix[start_plot:stop_plot]
    x1 = df.index
    y1 = df['Stage'].resample('6T').mean()
    interpolated = y1.interpolate(method='cubic', order=2)


    ax_2.set_ylabel('{}'.format(Tides_Only), color='black')     
    ax_2.plot(df4.index, df4[Tides_Only], 'r')
    ax_2.plot(df5.index, df5[Tides_Only], 'b')
    ax_2a = ax_2.twinx()
    ax_2a.plot(interpolated, 'black')
    ax_2a.set_ylabel('{}'.format(df2_name), color='black')  


    #--df3
    df = df2[['datetime', 'Stage']].copy()
    df.set_index('datetime', inplace=True)
    df = df.ix[start_plot:stop_plot]
    x1 = df.index
    y1 = df['Stage'].resample('6T').mean()
    interpolated = y1.interpolate(method='cubic', order=2)


    ax_3.set_ylabel('{}'.format(Tides_Only), color='black')    
    ax_3.plot(df4.index, df4[Tides_Only], 'r')
    ax_3.plot(df5.index, df5[Tides_Only], 'b')
    ax_3a = ax_3.twinx()
    ax_3a.plot(interpolated, 'black')
    ax_3a.set_ylabel('{}'.format(df3_name), color='black')  
    
    
    f.autofmt_xdate()
    plt.tight_layout(pad=0.4, w_pad=0.5, h_pad=1.0)
    #axes = f.gca()
    #axes.set_xlim([df4.index[0],df4.index[-1]])
    #axes.grid()