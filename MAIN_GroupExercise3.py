'''
--------------------------------------------------------------------
                        GROUP EXERCISE 3
             MAIN SCRIPT: Flowerpot model for Kander - Hondrich Catchment
 Authors: Antonia Schibbe, Jordi Fornés Mengual, Maxime Siggen
-------------------------------------------------------------------
 Description: In this exercise we implement the flowerpot model for the
 Kander - Hondrich catchment. This script contains the basic functioning
 of our flowerpot model. The different functions can be found in the Modules
 folder. This script provides a basic plot comparison for the CAMELS discharge
 and our modelled discharge. For a further comparison with the MeteoSwiss station
 check the Group3_Station_Comparison.py script.
-------------------------------------------------------------------
'''

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Our model modules
from Modules.snow_module import snow_module
from Modules.interception_module import interception_module
from Modules.storage_module1 import storage_module                   #called storage_module1 (WITH THE 1)
from Modules.discharge_module import discharge_module
from Modules.calibration_module import calibration_module


#Load CAMELS observed and simulated data
catchment_obs = pd.read_csv('Datasets/CAMELS_CH_obs_based_2469.csv')
catchment_sim = pd.read_csv('Datasets/CAMELS_CH_sim_based_2469.csv')

###########  CALIBRATION RUN
# We do a first calibration run, to choose the best mp, Tpbase, mf and T_t for the snow and melt module
# With the best mp, Tpbase, mf and T_T, we calibrate k and Smax for our simulated discharge.
# This is done for the period 1982-01-01 and 2000-12-31, and validated against the 2001-01-01 onwards.
# Another period can be manually selected in the calibration_module function.

best_snow, best_k, best_Smax = calibration_module(catchment_obs,catchment_sim)

#Apply the different modules

#1 Snow/rain separation module
df_snow_rain = snow_module(catchment_obs,Tpbase = best_snow['Tpbase'],mp = best_snow['mp'],mf = best_snow['mf'],T_T = best_snow['T_T'])
#2 Interception of rain
df_snow_rain_intercept = interception_module(df_snow_rain, catchment_sim, Icept_threshold=1)
#3 Storage module: evolution of storage, includes the linear flowerpot for the discharge.
df_storage = storage_module(df_snow_rain_intercept, k=best_k, Smax=best_Smax, initial_storage = 0) # Change params
#4 Discharge module: adds discharge + overflow
df_discharge = discharge_module(df_storage)


### Plots
#Creating the plots discharge observed vs modelled and precipitation inverted

df_discharge['date'] = pd.to_datetime(df_discharge['date'])
df = df_discharge.set_index('date').sort_index()
periods = [('2013-10-01', '2014-09-30'), ('2005-10-01', '2006-09-30')]
pmax = max(df.loc[a:b, 'precipitation(mm/d)'].max() for a, b in periods)


for a, b in periods:
    d = df.loc[a:b]
    fig, ax = plt.subplots(figsize=(9, 4))

    # --- Bottom Plot: Observed vs Modelled Discharge ---
    ax.plot(d.index, d['discharge_spec(mm/d)'], color='k')
    ax.plot(d.index, d['Q_tot_discharge_(mm/d)'], color='tab:red')
    ax.set_ylabel('Discharge [mm/d]')
    ax.grid(True, linestyle=':', alpha=0.6)
    # Format date axis to show Year-Month
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))

    # --- Top Plot: Inverted Precipitation ---
    axp = ax.twinx()
    axp.bar(d.index, d['precipitation(mm/d)'], color='tab:blue', width=1.0)
    ax.set_title(f'{a} to {b}', fontsize=10)     # <-- new line
    axp.set_ylim(pmax * 3, 0)
    axp.set_ylabel('Precip [mm/d]')

    handles = [plt.Line2D([], [], color='k'),
               plt.Line2D([], [], color='tab:red'),
               plt.Rectangle((0, 0), 1, 1, color='tab:blue')]
    fig.legend(handles, ['Observed discharge', 'Modelled discharge', 'Precipitation'],
               loc='lower center', ncol=3, frameon=False)
    fig.tight_layout(rect=(0, 0.07, 1, 1))

plt.show()