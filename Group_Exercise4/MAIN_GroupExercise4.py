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

ROOT = Path(__file__).resolve().parent.parent      # .../Hydro_Modelling
sys.path.append(str(ROOT))

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Our model modules
from Modules.cal_val_g4 import calibration_module


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


best_snow, best_k, best_Smax = calibration_module(CAL_START, CAL_END, VAL_START,
                                                  mp_list, Tpbase_list,mf_list, T_T_list,
                                                  k_list, Smax_list,
                                                  catchment_obs, catchment_sim)


