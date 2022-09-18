# This script gets the coefficients of the variables of the multivariable linear regression problem based on fused data of the 
# sensors and weather and saves them to a .csv file.

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

# Site ID and Weather to fetch latest model
location = Point(42.361145, -71.057083, 10)
site_id = '189'

#===========================================================================================================================
dataset_directory= os.path.join(os.path.join("CD_data_x_Converge","Converge"),"site_")
pours = glob.glob(os.path.join(os.path.join(str(dataset_directory)+str(site_id),"site_"+str(site_id)+"_data"),"*.csv"))

models = pd.DataFrame(columns=['pour_id','intercept','time_passed','temperature','outside_temp','precipitation','wind_speed','pressure'])
i = 0
for file in pours:
    pour_id = basename(file).split('.')[0] #'L00M-Pour-3_2945177719211557035'
    dataset_directory= os.path.join(os.path.join("CD_data_x_Converge","Converge"),"site_")
    df = pd.read_csv(os.path.join(os.path.join(str(dataset_directory)+str(site_id),"site_"+str(site_id)+"_data"),str(pour_id)+".csv"))
    if len(df)>=240:
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

        # TODO: While time has proper deltas over delta strength, the weather data stays pretty much
        # constant over delta strengths. Drying speed is a function of a constant weather condition, 
        # and nearly not a delta when using Linear Regression.

        # Enviromental changes over several days are nearly not present if packed in a linear regression model. 
        # The temperature change apart from day/night and special occassions is very low. Therefore, apart from
        # a constant k(T,p, ...) as function of the environmental data, the regression model can not do too much.
        # A more complex model should be used which takes into account intermediate (large) changes of environmental
        # data. In this case, at least hourly updates are necessary. 
        
        model = LinearRegression()
        model.fit(x, y)
        print(model.coef_)
        print("Equation for the model is: Y = "+str(model.intercept_)+" + "+str(model.coef_[0])+"*time_passed + "+str(model.coef_[1])+"*outside_temp_avg + "+str(model.coef_[2])+"*precipitation + "+str(model.coef_[3])+"*wind_speed + "+str(model.coef_[4])+"*pressure")
        
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

# TODO: Why is the discrepancy between the coefficients of each single dataset so large? Not sure if taking mean 
# works properly in this case. Did we check if data is suitable for linear regression?

print(models.head())
print("Equation for the model is: Y = "+str(models['intercept'].mean())+" + "+str(models['time_passed'].mean())+"*time_passed + "+str(models['outside_temp'].mean())+"*outside_temperature + "+str(models['precipitation'].mean())+"*precipitation + "+str(models['wind_speed'].mean())+"*wind_speed + "+str(models['pressure'].mean())+"*pressure")
#print("Equation for the model is: Y = "+str(models['intercept'].mean())+" + "+str(models['time_passed'].mean())+"*time_passed + "+str(models['temperature'].mean())+"*cement_temperature + "+str(models['outside_temp'].mean())+"*outside_temp_avg + "+str(models['precipitation'].mean())+"*precipitation + "+str(models['wind_speed'].mean())+"*wind_speed + "+str(models['pressure'].mean())+"*pressure")
models.to_csv('models.csv')

'''
#======================Visualization=========================================================================
import pandas as pd
import matplotlib.pyplot as plt
from sklearn import linear_model

######################################## Data preparation #########################################

file = 'https://aegis4048.github.io/downloads/notebooks/sample_data/unconv_MV_v5.csv'
df = pd.read_csv(file)

X = df['Por'].values.reshape(-1,1)
y = df['Prod'].values

################################################ Train #############################################

ols = linear_model.LinearRegression()
model = ols.fit(X, y)
response = model.predict(X)

############################################## Evaluate ############################################

r2 = model.score(X, y)

############################################## Plot ################################################

plt.style.use('default')
plt.style.use('ggplot')

fig, ax = plt.subplots(figsize=(8, 4))

ax.plot(X, response, color='k', label='Regression model')
ax.scatter(X, y, edgecolor='k', facecolor='grey', alpha=0.7, label='Sample data')
ax.set_ylabel('Gas production (Mcf/day)', fontsize=14)
ax.set_xlabel('Porosity (%)', fontsize=14)
ax.text(0.8, 0.1, 'aegis4048.github.io', fontsize=13, ha='center', va='center',
         transform=ax.transAxes, color='grey', alpha=0.5)
ax.legend(facecolor='white', fontsize=11)
ax.set_title('$R^2= %.2f$' % r2, fontsize=18)

fig.tight_layout()
'''