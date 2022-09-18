import math
import os
import glob
import numpy as np
import pandas as pd
import streamlit as st
import predict_2 as pr


#import datetime


from os.path import basename
from meteostat import Point,Daily
from datetime import datetime,date,timedelta


st.title('Estimated Time for Cement to Dry up')

def time_passed(start_time,location ):


    loc = str(location).split(',')
    loc = list(map(float,loc))
    location = Point(loc[0], loc[1], loc[2])

    pred_date_temp = str(start_time).split('-')
    pred_date_temp = list(map(int, pred_date_temp))
    pred_date = datetime(pred_date_temp[0], pred_date_temp[1], pred_date_temp[2])
    pred_date_1 = datetime(pred_date_temp[0], pred_date_temp[1], pred_date_temp[2]+1)
    data_pred = Daily(location, pred_date, pred_date_1)
    data_pred = data_pred.fetch()

    out_temp_pred = data_pred.iloc[0,0]
    #print(out_temp_pred)
    precipitation = data_pred.iloc[0,3]
    if np.isnan(precipitation):
        precipitation=0
    #precipitation = 0 if precipitation == nan else precipitation
    #st.write('precipitation_1', precipitation)
    wind_speed = data_pred.iloc[0,5]
    pressure = data_pred.iloc[0,8]

    #temp_diff = float(temperature_cement)-out_temp_pred

    return out_temp_pred,precipitation,wind_speed,pressure


def predict_time_passed(out_temp_pred,precipitation,wind_speed,pressure,strength,models):
    #
    # model_intercept = 27.31090734824298
    # model_coef_0 =  0.0009408266941061254
    # model_coef_1 =  -1.159986681608001
    # model_coef_2  =  0.05708973224417882
    # model_coef_3 = -0.5426231309319686
    # model_coef_4 = 0.003207237186370504

    y1 = strength
    y2 = strength - 20

    time_passed_1 = (y1 - (
                models['intercept'].mean() + out_temp_pred * models['outside_temp'].mean() + precipitation * models[
            'precipitation'].mean() + wind_speed * models['wind_speed'].mean() + pressure * models[
                    'pressure'].mean())) / (models['time_passed'].mean())

    time_passed_2 = (y2 - (
            models['intercept'].mean() + out_temp_pred * models['outside_temp'].mean() + precipitation * models[
        'precipitation'].mean() + wind_speed * models['wind_speed'].mean() + pressure * models[
                'pressure'].mean())) / (models['time_passed'].mean())

    # time_passed = str(timedelta(seconds=time_passed))
    # x = time_passed.split(':')

    return  time_passed_1,time_passed_2


if __name__ =='__main__':

    location = st.text_input('Enter the location:', '51.5072,-0.1276,30')

    #visualization of the location on the map
    loc = location.split(',')
    loc = list(map(float,loc))
    data = {'lat':[loc[0]],'lon':[loc[1]]}
    df = pd.DataFrame(data)
    st.map(df)

    start_time = st.text_input('Starting Date for Construction:  ', '2022-09-18')
    no_pours = st.text_input('Number of Pour:','56')
    no_pours = int(no_pours)
    strength = st.text_input('Strength:  ', '28')
    strength = int(strength)
    site_id = st.text_input('Site Id:  ', '189')


    # the week of date you want to check
    check_date = datetime.strptime(start_time, "%Y-%m-%d").strftime("%V")
    #todays' week
    tday = date.today().strftime("%V")

    #check if the difference is withing two weeks
    diff = int(check_date)-int(tday)
    if diff>0 and diff<=2:
        st.write('the difference is within a week')
        #for num in no_pours:

        arr_for_table = []
        new_start_time = datetime.strptime(start_time, "%Y-%m-%d").timestamp()
        prev_start_time = datetime.strptime(start_time, "%Y-%m-%d").timestamp()
        time_to_cure = 0

        for number in range(0, no_pours):

            st.write("DEBUG")
            st.write(str(datetime.fromtimestamp(prev_start_time))[0:10])

            pr.predict_time_to_cure(loc, 'models.csv', str(datetime.fromtimestamp(prev_start_time))[0:10], strength)

            st.write(int(time_to_cure)*20*60)

            new_start_time = prev_start_time + math.ceil(((int(time_to_cure)*20)*60))

            arr_for_table.append([number, str(datetime.fromtimestamp(prev_start_time))[0:10],(time_to_cure/60/60/24), str(datetime.fromtimestamp(new_start_time))[0:10]])

            st.table(arr_for_table)

        st.write(str(arr_for_table))

        # st.write('**The Cement will Dry in:**')
        # #st.write( '*' +x[0] + '*', '*Hours*', x[1], '*Minutes*', x[2], '*Seconds*')
        # st.write('**The Prediction is Based on:**')
        # st.markdown("- Predicted")
        # st.markdown("- Time Difference")
        # st.markdown("- Precipitation")
        # st.markdown("- Wind Speed")
        # st.markdown("- Pressure")
        #
        # st.markdown('''
        # <style>
        # [data-testid="stMarkdownContainer"] ul{
        #     padding-left:40px;
        # }
        # </style>
        # ''', unsafe_allow_html=True)

    else:
        st.write('Currently we dont have predictions beyond two weeks')

st.write(':sunglasses:')

