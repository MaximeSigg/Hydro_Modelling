# test_calibration.py
import time
import pandas as pd

from Modules.cal_val_g4 import calibration_module

# Load CAMELS observed and simulated data
obs = pd.read_csv('Datasets/CAMELS_CH_obs_based_2469.csv')
sim = pd.read_csv('Datasets/CAMELS_CH_sim_based_2469.csv')

# Quick checks on the input before running
print('obs shape:', obs.shape, '| sim shape:', sim.shape)
needed = ['date', 'swe(mm)', 'discharge_spec(mm/d)', 'precipitation(mm/d)', 'temperature_mean(degC)']
print('missing columns in obs:', [c for c in needed if c not in obs.columns])
print('missing PET in sim:', 'pet_sim(mm/d)' not in sim.columns)

# Run the calibration
t0 = time.time()
best_snow, best_k, best_Smax = calibration_module(obs, sim)
