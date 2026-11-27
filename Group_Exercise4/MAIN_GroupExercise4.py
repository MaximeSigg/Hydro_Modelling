'''
--------------------------------------------------------------------
                        GROUP EXERCISE 4
             MAIN SCRIPT: Parameter estimation for Kander - Hondrich Catchment
 Authors: Antonia Schibbe, Jordi Fornés Mengual, Maxime Siggen
-------------------------------------------------------------------
 Description: For this exercise we estimate the parameters of the lumped daily model
 for the Kander - Hondrich catchment (CAMELS-CH ID 2469), which consists of a snow,
 an interception, storage and discharge module. We do the evaluation of the parameters
 based on different statistical parameters such as NSE. nash-log, bias and KGE.

 The statistical assessment is done for a calibration and a validation period. All parameters
 are calibrated at once (first the snow module parameters, and then the discharge parameters
 from the flowerpot model k and Smax). For this reason, there is a dedicated script for studying
 the individual influence of each parameter - sensitivity.py
-------------------------------------------------------------------
'''

import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

ROOT = Path(__file__).resolve().parent.parent      # .../Hydro_Modelling
sys.path.append(str(ROOT))

# Our model modules
from Modules.cal_val_g4 import calibration_module_g4
from Modules.snow_module import snow_module
from Modules.interception_module import interception_module
from Modules.storage_module1 import storage_module                   #called storage_module1 (WITH THE 1)
from Modules.discharge_module import discharge_module
from Modules.calibration_module import calibration_module



#Load CAMELS observed and simulated data
catchment_obs = pd.read_csv(ROOT / 'Datasets' / 'CAMELS_CH_obs_based_2469.csv')
catchment_sim = pd.read_csv(ROOT / 'Datasets' / 'CAMELS_CH_sim_based_2469.csv')


#### TUNNABLE PARAMS

# ---- Periods (change here) ----
CAL_START = '1983-01-01'      # 1981+1982 = spin-up
CAL_END = '2009-12-31'
VAL_START = '2010-01-01'


# ---- Step 1: snow parameters (mean of NSE and KGE of SWE, calibration period) ----
mp_list = [1, 1.5, 2, 3]  # mp < 1: unrealistically wide transition
Tpbase_list = [-0.5, 0, 0.5, 1, 1.5, 2, 2.5]
mf_list = [1, 2, 3, 4, 5, 6, 7]  # literature range
T_T_list = [-2, -1, 0, 1, 2]

k_list = [0.01, 0.02, 0.03, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3]
Smax_list = [50, 100, 200, 300, 500, 750, 1000]


best_snow, best_k, best_Smax = calibration_module_g4(CAL_START, CAL_END, VAL_START,
                                                  mp_list, Tpbase_list,mf_list, T_T_list,
                                                  k_list, Smax_list,
                                                  catchment_obs, catchment_sim)


#Apply the different modules: CHOOSE BEST AND WORST CASE OF OUR MODEL

#1 Snow/rain separation module
df_snow_rain = snow_module(catchment_obs, Tpbase=best_snow['Tpbase'], mp=best_snow['mp'], mf=best_snow['mf'], T_T=best_snow['T_T'])
#2 Interception of rain
df_snow_rain_intercept = interception_module(df_snow_rain, catchment_sim, Icept_threshold=1)
#3 Storage module: evolution of storage, includes the linear flowerpot for the discharge.
df_storage = storage_module(df_snow_rain_intercept, k=best_k, Smax=best_Smax, initial_storage=0)
#4 Discharge module: adds discharge + overflow
df_discharge = discharge_module(df_storage)


### Plots
#Creating the plots discharge observed vs modelled and precipitation inverted

df_discharge['date'] = pd.to_datetime(df_discharge['date'])
df = df_discharge.set_index('date').sort_index()

# Find best and worst periods

window = pd.Timedelta(days=30)       # <-- length of the period
step = pd.Timedelta(days=1)          # <-- step of the search

results = []

start = df.index.min()               # to skip the spin-up, use: start = pd.Timestamp(CAL_START)

while start + window <= df.index.max():

    end = start + window
    d = df.loc[start:end]

    obs = d['discharge_spec(mm/d)']
    mod = d['Q_tot_discharge_(mm/d)']

    valid = obs.notna() & mod.notna()
    obs = obs[valid]
    mod = mod[valid]

    if len(obs) > 0.75 * window.days:          # at least 75% of the days with data

        denominator = sum((obs - obs.mean())**2)

        if denominator > 0:
            nse = 1 - sum((obs - mod)**2) / denominator
            results.append((nse, start, end))

    start = start + step

# Find best and worst periods
best = max(results, key=lambda x: x[0])
worst = min(results, key=lambda x: x[0])

print("Best period:", best)
print("Worst period:", worst)

# Use these periods for plotting
periods = [
    (best[1], best[2]),
    (worst[1], worst[2])
]
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
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=7))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))
    # --- Top Plot: Inverted Precipitation ---
    axp = ax.twinx()
    axp.bar(d.index, d['precipitation(mm/d)'], color='tab:blue', width=1.0)
    ax.set_title(f'{a:%Y-%m-%d} to {b:%Y-%m-%d}', fontsize=10)
    axp.set_ylim(pmax * 3, 0)
    axp.set_ylabel('Precip [mm/d]')

    handles = [plt.Line2D([], [], color='k'),
               plt.Line2D([], [], color='tab:red'),
               plt.Rectangle((0, 0), 1, 1, color='tab:blue')]
    fig.legend(handles, ['Observed discharge', 'Modelled discharge', 'Precipitation'],
               loc='lower center', ncol=3, frameon=False)
    fig.tight_layout(rect=(0, 0.07, 1, 1))

plt.show()


## Here you can choose any period from our model simulation

PERIODS = [
    ('Good Fit',   '2014-04-05', '2014-05-03'),     # <-- placeholder dates, change them
    ('Bad fit',     '2005-05-01', '2005-05-31'),     # <-- placeholder dates, change them
]



def nse_fn(o, m):
    return 1 - ((o - m) ** 2).sum() / ((o - o.mean()) ** 2).sum()

def kge_fn(o, m):
    r = np.corrcoef(o, m)[0, 1]
    alpha = m.std() / o.std()
    beta = m.mean() / o.mean()
    return 1 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)


my_periods = [(label, pd.Timestamp(a), pd.Timestamp(b)) for label, a, b in PERIODS]
pmax_my = max(df.loc[a:b, 'precipitation(mm/d)'].max() for _, a, b in my_periods)

for label, a, b in my_periods:
    d = df.loc[a:b]

    o, m = d['discharge_spec(mm/d)'], d['Q_tot_discharge_(mm/d)']
    ok = o.notna() & m.notna()
    nse_p, kge_p = nse_fn(o[ok], m[ok]), kge_fn(o[ok], m[ok])
    print(f'{label}: {a:%Y-%m-%d} to {b:%Y-%m-%d} | NSE = {nse_p:.2f} | KGE = {kge_p:.2f}')

    fig, ax = plt.subplots(figsize=(9, 4))

    # --- Bottom Plot: Observed vs Modelled Discharge ---
    ax.plot(d.index, d['discharge_spec(mm/d)'], color='k')
    ax.plot(d.index, d['Q_tot_discharge_(mm/d)'], color='tab:red')
    ax.set_ylabel('Discharge [mm/d]')
    ax.grid(True, linestyle=':', alpha=0.6)
    ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=7))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d %b'))

    # --- Top Plot: Inverted Precipitation ---
    axp = ax.twinx()
    axp.bar(d.index, d['precipitation(mm/d)'], color='tab:blue', width=1.0)
    axp.set_ylim(pmax_my * 3, 0)
    axp.set_ylabel('Precip [mm/d]')

    ax.set_title(f'{label}: {a:%Y-%m-%d} to {b:%Y-%m-%d}\nNSE = {nse_p:.2f}   |   KGE = {kge_p:.2f}',
                 fontsize=10)

    handles = [plt.Line2D([], [], color='k'),
               plt.Line2D([], [], color='tab:red'),
               plt.Rectangle((0, 0), 1, 1, color='tab:blue')]
    fig.legend(handles, ['Observed discharge', 'Modelled discharge', 'Precipitation'],
               loc='lower center', ncol=3, frameon=False)
    fig.tight_layout(rect=(0, 0.07, 1, 1))

plt.show()