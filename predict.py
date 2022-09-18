import pandas as pd
#from sklearn import linear_model
from sklearn.linear_model import LinearRegression
from datetime import datetime
import glob
import gc
import os
from meteostat import Point, Daily
import matplotlib.pyplot as plt
import numpy as np
from datetime import date
from os.path import basename

# Inputs used for carrying prediction
# Checking weather forecast for London
location = Point(42.361145, -71.057083, 10)
models = pd.read_csv('models.csv')
enter_date = '2022-03-25'
y1 = 30
y2 = 40
#========================================================================================
date_format = "%Y-%m-%d"
today = datetime.today().strftime('%Y-%m-%d')
a = datetime.strptime(enter_date, date_format)
b = datetime.strptime(today, date_format)
delta = b - a

if (b<=a):
    # Set time period
    #data = Daily(location, start, datetime.strptime(enter_date,date_format))
    #data = data.fetch()
    #data = data.rename_axis("time").reset_index()
    #data['time'] = data['time'].astype(str)
    #data[['year', 'month','day']] = data['time'].str.split('-', 2, expand=True)
    #data = data.drop(['time'],axis=1)
    print('Future Date selected')    
    pred_date_temp = str(enter_date).split('-')
    pred_date_temp = list(map(int, pred_date_temp))
    pred_date = datetime(2010, pred_date_temp[1], pred_date_temp[2])
    pred_date_1 = datetime(2010, pred_date_temp[1], pred_date_temp[2]+1)
    data_pred = Daily(location, pred_date, pred_date_1)
    data_pred = data_pred.fetch()
    out_temp_pred = data_pred.iloc[0,0]
    precipitation = data_pred.iloc[0,3]
    wind_speed = data_pred.iloc[0,5]
    pressure = data_pred.iloc[0,8]
    time_passed_1 = (y1 - (models['intercept'].mean() + out_temp_pred*models['outside_temp'].mean() + precipitation*models['precipitation'].mean()+wind_speed*models['wind_speed'].mean()+pressure*models['pressure'].mean()))/(models['time_passed'].mean())
    time_passed_2 = (y2 - (models['intercept'].mean() + out_temp_pred*models['outside_temp'].mean() + precipitation*models['precipitation'].mean()+wind_speed*models['wind_speed'].mean()+pressure*models['pressure'].mean()))/(models['time_passed'].mean())
    
    print(str(time_passed_1)+" to "+str(time_passed_2))

else:
    pred_date_temp = str(enter_date).split('-')
    pred_date_temp = list(map(int, pred_date_temp))
    pred_date = datetime(pred_date_temp[0], pred_date_temp[1], pred_date_temp[2])
    pred_date_1 = datetime(pred_date_temp[0], pred_date_temp[1], pred_date_temp[2]+1)
    data_pred = Daily(location, pred_date, pred_date_1)
    data_pred = data_pred.fetch()
    out_temp_pred = data_pred.iloc[0,0]
    precipitation = data_pred.iloc[0,3]
    wind_speed = data_pred.iloc[0,5]
    pressure = data_pred.iloc[0,8]
    time_passed_1 = (y1 - (models['intercept'].mean() + out_temp_pred*models['outside_temp'].mean() + precipitation*models['precipitation'].mean()+wind_speed*models['wind_speed'].mean()+pressure*models['pressure'].mean()))/(models['time_passed'].mean())
    time_passed_2 = (y2 - (models['intercept'].mean() + out_temp_pred*models['outside_temp'].mean() + precipitation*models['precipitation'].mean()+wind_speed*models['wind_speed'].mean()+pressure*models['pressure'].mean()))/(models['time_passed'].mean())
    #time_passed = (y - (models['intercept'].mean() + out_temp_pred*models['outside_temp'].mean() + precipitation*models['precipitation'].mean()+wind_speed*models['wind_speed'].mean()+pressure*models['pressure'].mean()))/(models['time_passed'].mean())

    print(str(time_passed_1)+" to "+str(time_passed_2))

