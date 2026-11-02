'''
--------------------------------------------------------------------
                        GROUP EXERCISE 3
             Exercise 2a : Flowerpot model for Kander - Hondrich Catchment
 Authors: Antonia Schibbe, Jordi Fornés Mengual, Maxime Siggen
-------------------------------------------------------------------
 Description: In this exercise we implement the flowerpot model for the
 Kander - Hondrich catchment.
-------------------------------------------------------------------
'''

import pandas as pd
from Modules.snow_module import snow_module
from Modules.interception_module import interception_module
from Modules.storage_module1 import storage_module                   #called storage_module1 (WITH THE 1)
from Modules.discharge_module import discharge_module


catchment_obs = pd.read_csv('Datasets/CAMELS_CH_obs_based_2469.csv')
catchment_sim = pd.read_csv('Datasets/CAMELS_CH_sim_based_2469.csv')
df_snow_rain = snow_module(catchment_obs,Tpbase = 1.5,mp = 1,mf = 2,T_T = 2)

df_snow_rain_intercept = interception_module(df_snow_rain, catchment_sim, Icept_threshold=1)
df_storage = storage_module(df_snow_rain_intercept, initial_storage = 0)
df_discharge = discharge_module(df_storage)

#print(df_discharge)
print('hi, Im jordi')