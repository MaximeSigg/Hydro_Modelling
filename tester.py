import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Our model modules
from Modules.snow_module import snow_module
from Modules.interception_module import interception_module
from Modules.storage_module1 import storage_module                   #called storage_module1 (WITH THE 1)
from Modules.discharge_module import discharge_module
from Modules.calibration_g4 import calibration_module

#Load CAMELS observed and simulated data
catchment_obs = pd.read_csv('Datasets/CAMELS_CH_obs_based_2469.csv')
catchment_sim = pd.read_csv('Datasets/CAMELS_CH_sim_based_2469.csv')

###########  CALIBRATION RUN


# We do a first calibration run, to choose the best mp, Tpbase, mf and T_t for the snow and melt module
# With the best mp, Tpbase, mf and T_T, we calibrate k and Smax for our simulated discharge.
# This is done for the period 1982-01-01 and 2000-12-31, and validated against the 2001-01-01 onwards.
# Another period can be manually selected in the calibration_module function.

best_snow, best_k, best_Smax = calibration_module(catchment_obs,catchment_sim)