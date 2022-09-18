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
from os.path import basename

def predict_time_to_cure(location, model, enter_date, strength):

    # Checking weather forecast for London
    # location = Point(51.5072, -0.1276, 30)

    #====================================================Prediction Arc======================================================================
    # Inputs used for carrying prediction
    # models = pd.read_csv('models.csv')
    # enter_date = '2022-09-18'

    models = pd.read_csv(model)

    #temperature_cement = 20
    # y = 40
    y = strength

    pred_date_temp = str(enter_date).split('-')
    pred_date_temp = list(map(int, pred_date_temp))
    pred_date = datetime(pred_date_temp[0], pred_date_temp[1], pred_date_temp[2])
    pred_date_1 = datetime(pred_date_temp[0], pred_date_temp[1], pred_date_temp[2]+1)
    data_pred = Daily(location, pred_date, pred_date_1)
    data_pred = data_pred.fetch()

    out_temp_pred = data_pred.iloc[0, 0]
    precipitation = data_pred.iloc[0,3]
    wind_speed = data_pred.iloc[0,5]
    pressure = data_pred.iloc[0,8]

    time_passed = (y - (models['intercept'].mean() + out_temp_pred*models['outside_temp'].mean() + precipitation*models['precipitation'].mean()+wind_speed*models['wind_speed'].mean()+pressure*models['pressure'].mean()))/(models['time_passed'].mean())
    #time_passed = (y - (models['intercept'].mean() + out_temp_pred*models['outside_temp'].mean() + precipitation*models['precipitation'].mean()+wind_speed*models['wind_speed'].mean()+pressure*models['pressure'].mean()))/(models['time_passed'].mean())

    return time_passed