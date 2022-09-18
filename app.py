import streamlit as st
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
from datetime import datetime, timedelta

# Inputs used for carrying prediction
# Checking weather forecast for London

st.header('ConGreat')
st.subheader('ConGreat is an online tool to predict time duration within which a pour can be carried out. The tool provides custom models for better planning and management of pouring practice in contruction site. We take into account weather and strength datasets from different sites to estimate ideal pouring time.')
st.caption('In case if the results show NaN values or ValueError, the weather data for that particular day/location was not available in the open source repository that we were using. However, this can be easily fixed by changing the weather forecast provider.')
st.caption('Please copy paste the latitude and longitude of cities through google search and retrain model')
st.caption('Please refresh the page after each run to avoid issues')

lat = st.number_input('Enter the Latitude', value = 51.5072)
lon = st.number_input('Enter the Longitude', value = -0.1276)
elev = st.number_input('Enter the Elevation', value = 30)
enter_date = st.text_input('Enter the Date', '2022-09-18')
strength = st.number_input('Enter the Strength of concrete for which time is to be estimated', value = 35)
number_of_pour = st.number_input('Enter the number of pours to be done', value = 35)

sites = glob.glob((os.path.join(os.path.join('CD_data_x_Converge','Converge'),'*')))
site_id = st.selectbox('Please Select the Site ID',(sites))

if st.button('Generate Model'):
    df = pd.DataFrame(columns=['lat', 'lon'])
    site_id = str(basename(site_id)).split('_')[-1]
    df.loc[0,'lat']=lat
    df.loc[0,'lon']=lon
    print(df)
    st.map(df)
    location = Point(lat, lon, elev)    
    #location = Point(51.5072, -0.1276, 30)

    #===========================================================================================================================
    dataset_directory= os.path.join(os.path.join("CD_data_x_Converge","Converge"),"site_")
    pours = glob.glob(os.path.join(os.path.join(str(dataset_directory)+str(site_id),"site_"+str(site_id)+"_data"),"*.csv"))

    models = pd.DataFrame(columns=['pour_id','intercept','time_passed','temperature','outside_temp','precipitation','wind_speed','pressure'])
    i = 0
    for file in pours:
        pour_id = basename(file).split('.')[0] #'L00M-Pour-3_2945177719211557035'
        dataset_directory= os.path.join(os.path.join("CD_data_x_Converge","Converge"),"site_")
        df = pd.read_csv(os.path.join(os.path.join(str(dataset_directory)+str(site_id),"site_"+str(site_id)+"_data"),str(pour_id)+".csv"))
        if len(df)>=270:
            df = df[df[' strength'] != ' ']

            # Set time period
            start_date_temp = str(str(df.iloc[0,0]).split(' ')[0]).split('/')
            end_date_temp = str(str(df.iloc[-1,0]).split(' ')[0]).split('/')

            start_date_temp = list(map(int, start_date_temp))
            end_date_temp = list(map(int, end_date_temp))

            start_date = datetime(start_date_temp[0], start_date_temp[1], start_date_temp[2])
            end_date = datetime(end_date_temp[0],end_date_temp[1],end_date_temp[2])

            #Get daily data for weather
            data = Daily(location, start_date, end_date)
            data = data.fetch()
            data = data.rename_axis("time").reset_index()
            data.rename(columns = {'time':'date'}, inplace = True)

            df[['date', 'time','timezone_1']] = df['time'].str.split(' ', 2, expand=True)
            df['date'] = df['date'].str.replace('/','-')
            df = df.drop([' timezone','timezone_1','time'], axis=1)
            df['date'] = df['date'].astype(str)
            data['date'] = data['date'].astype(str)
            df = pd.merge(df, data, on="date", how="left")
            df.insert(0, 'time_1', 20*df.index)
            df.rename(columns = {'time_1':'time'}, inplace = True)
            df['pres'] = df['pres']
            df = df[[' strength','time','tavg','prcp', 'wspd', 'pres']]
            df = df.dropna()
            print(df.head())

            x = df[['time','tavg','prcp', 'wspd', 'pres']]
            y = df[' strength']
            
            model = LinearRegression()
            model.fit(x, y)
            
            #print(model.coef_)
            #print("Equation for the model is: Y = "+str(model.intercept_)+" + "+str(model.coef_[0])+"*time_passed + "+str(model.coef_[1])+"*outside_temp_avg + "+str(model.coef_[2])+"*precipitation + "+str(model.coef_[3])+"*wind_speed + "+str(model.coef_[4])+"*pressure")
            
            models.loc[i,'pour_id'] = str(basename(file)).split('.')[0]
            models.loc[i,'intercept'] = model.intercept_
            models.loc[i,'time_passed'] = model.coef_[0]
            models.loc[i,'outside_temp'] = model.coef_[1]
            models.loc[i,'precipitation'] = model.coef_[2]
            models.loc[i,'wind_speed'] = model.coef_[3]
            models.loc[i,'pressure'] = model.coef_[4]
            
            i = i+1
            #print('intercept:', model.intercept_)
            #print('slope:', model.coef_)

    print(models.head())
    #st.code(models.head())
    print("Equation for the model is: Y = "+str(models['intercept'].mean())+" + "+str(models['time_passed'].mean())+"*time_passed + "+str(models['outside_temp'].mean())+"*outside_temperature + "+str(models['precipitation'].mean())+"*precipitation + "+str(models['wind_speed'].mean())+"*wind_speed + "+str(models['pressure'].mean())+"*pressure")
    st.subheader("Equation for the mean model is: ")
    st.code("Y = "+str(models['intercept'].mean())+" + "+str(models['time_passed'].mean())+"*time_passed + "+str(models['outside_temp'].mean())+"*outside_temperature + "+str(models['precipitation'].mean())+"*precipitation + "+str(models['wind_speed'].mean())+"*wind_speed + "+str(models['pressure'].mean())+"*pressure")
    #print("Equation for the model is: Y = "+str(models['intercept'].mean())+" + "+str(models['time_passed'].mean())+"*time_passed + "+str(models['temperature'].mean())+"*cement_temperature + "+str(models['outside_temp'].mean())+"*outside_temp_avg + "+str(models['precipitation'].mean())+"*precipitation + "+str(models['wind_speed'].mean())+"*wind_speed + "+str(models['pressure'].mean())+"*pressure")
    models.to_csv('models.csv')

if st.button('Estimate Pour Time'):
    df = pd.DataFrame(columns=['lat', 'lon'])
    df.loc[0,'lat']=lat
    df.loc[0,'lon']=lon
    st.map(df)
    location = Point(lat, lon, elev)
    #location = Point(51.5072, -0.1276, 30)
    models = pd.read_csv('models.csv')
    #enter_date = str(enter_date)
    y2 = strength
    y1 = strength-7
    #========================================================================================
    date_format = "%Y-%m-%d"
    today = datetime.today().strftime('%Y-%m-%d')
    a = datetime.strptime(enter_date, date_format)
    b = datetime.strptime(today, date_format)
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
        pred_date = datetime(2011, pred_date_temp[1], pred_date_temp[2])
        pred_date_1 = datetime(2011, pred_date_temp[1], pred_date_temp[2]+1)
        data_pred = Daily(location, pred_date, pred_date_1)
        data_pred = data_pred.fetch()
        out_temp_pred = data_pred.iloc[0,0]
        precipitation = data_pred.iloc[0,3]
        wind_speed = data_pred.iloc[0,5]
        pressure = data_pred.iloc[0,8]

        time_passed_1 = (y1 - (models['intercept'].mean() + out_temp_pred*models['outside_temp'].mean() + precipitation*models['precipitation'].mean()+wind_speed*models['wind_speed'].mean()+pressure*models['pressure'].mean()))/(models['time_passed'].mean())
        time_passed_2 = (y2 - (models['intercept'].mean() + out_temp_pred*models['outside_temp'].mean() + precipitation*models['precipitation'].mean()+wind_speed*models['wind_speed'].mean()+pressure*models['pressure'].mean()))/(models['time_passed'].mean())
        
        print(str(time_passed_1)+" to "+str(time_passed_2))
        pouring_dict = {1:"st",2:"nd",3:"rd",21:"st",22:"nd",23:"rd",31:"st",32:"nd",33:"rd"}
        for i in range(1,number_of_pour+1):
            if i in pouring_dict:
                st.subheader(str(i)+pouring_dict[i]+ " Pour will be finished within ")
                st.code(str((time_passed_1+i*time_passed_1)/(60*24))+" days to "+str((time_passed_2+i*time_passed_2)/(60*24))+" days")
            else:
                st.subheader(str(i) + "th " + "Pour will be finished within ")
                st.code(str((time_passed_1 + i * time_passed_1) / (60 * 24)) + " days to " + str(
                    (time_passed_2 + i * time_passed_2) / (60 * 24)) + " days")

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
        
        for i in range(1,number_of_pour+1):
            st.subheader(str(i)+" Pour will be finished within ")
            st.code(str((time_passed_1+i*time_passed_1)/(60*24))+" days to "+str((time_passed_2+i*time_passed_2)/(60*24))+" days")    