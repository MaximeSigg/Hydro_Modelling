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


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

#Creating the plots discharge observed vs modelled and precipitation inverted
df_discharge['date'] = pd.to_datetime(df_discharge['date'])
df_year_2000 = df_discharge[
    (df_discharge['date'] >= '2005-10-01')
    & (df_discharge['date'] <= '2006-09-30')
]

fig, ax1 = plt.subplots(figsize=(10, 6))

# --- Top Plot: Inverted Precipitation ---
ax2 = ax1.twinx()
ax2.bar(df_year_2000['date'],
    df_year_2000['precipitation(mm/d)'],
    color='lightblue',
    label='Precipitation')
ax2.set_ylabel('Precip. [mm/d]')
ax2.invert_yaxis()  # Invert y-axis so rainfall hangs from top
ax2.set_ylim(df_year_2000['precipitation(mm/d)'].max() * 3.5, 0)

# --- Bottom Plot: Observed vs Modelled Discharge ---
# Note: Replace 'q_obs(mm/d)' with your exact column name for observed runoff
ax1.plot(df_year_2000['date'],
    df_year_2000['discharge_spec(mm/d)'],
    color='black',
    label='Observed Streamflow')
ax1.plot(df_year_2000['date'],
    df_year_2000['Q_tot_discharge_(mm/d)'],
    color='steelblue',
    linestyle='--',
    label='Modelled Streamflow')

ax1.set_xlabel('Date')
ax1.set_ylabel('Discharge [mm/d]')
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.legend()

# Format date axis to show Year-Month
ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))

plt.tight_layout()
plt.show()