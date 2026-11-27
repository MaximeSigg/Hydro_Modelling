'''
--------------------------------------------------------------------
                    FINAL EXERCISE
             MAIN SCRIPT: Final model simulation for Kander-Hondrich catchment
 Authors: Antonia Schibbe, Jordi Fornés Mengual, Maxime Siggen
-------------------------------------------------------------------
 Description: In this exercise we build up on all the previous exercises to obtain
 our final model for the Kander-Hondrich catchment. We use the best parameters
 estimated previously. The novelty is the inclusion of different elevation bands
 to account for different temperatures.
-------------------------------------------------------------------
'''



import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent      # .../Hydro_Modelling
sys.path.append(str(ROOT))

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Our model modules
from Modules.cal_val_g5 import calibration_module_g5


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


best_snow, best_k, best_Smax = calibration_module_g5(CAL_START, CAL_END, VAL_START,
                                                  mp_list, Tpbase_list,mf_list, T_T_list,
                                                  k_list, Smax_list,
                                                  catchment_obs, catchment_sim)
#%% small plot to  see how it works (takes more time, because of elevation bands)
from Modules.cal_val_g5 import nse

from Modules.snow_module_elevation_gr5 import snow_module_elevation
from Modules.interception_module import interception_module
from Modules.storage_module1 import storage_module
from Modules.discharge_module import discharge_module

# ---- Plot discharge: observed vs modelled (3 years) ----

# Apply the snow module with calibrated parameters
df = snow_module_elevation(catchment_obs, **best_snow)

# Apply the remaining modules
df = interception_module(df, catchment_sim)
df = storage_module(df, k=best_k, Smax=best_Smax, initial_storage=0)
df = discharge_module(df)

# Select the 3-year period
df['date'] = pd.to_datetime(df['date'])
plot_start = '2005-01-01'
plot_end = '2007-12-31'

period = (df['date'] >= plot_start) & (df['date'] <= plot_end)

# Calculate NSE for this period
Q_obs = df.loc[period, 'discharge_spec(mm/d)']
Q_mod = df.loc[period, 'Q_tot_discharge_(mm/d)']

nse_value = nse(Q_obs, Q_mod)

# Plot
plt.figure(figsize=(12, 4))

plt.plot(df.loc[period, 'date'], Q_obs, label='Observed', color='black')
plt.plot(df.loc[period, 'date'], Q_mod, label='Modelled', color='red')

plt.title(f'Discharge: observed vs modelled (NSE = {nse_value:.2f})')
plt.ylabel('Discharge (mm/d)')
plt.xlabel('Date')
plt.legend()
plt.grid(alpha=0.3)
plt.tight_layout()
plt.show()