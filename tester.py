import pandas as pd
from Modules.calibration_module import calibration_module
from Modules.snow_module import snow_module
from Modules.interception_module import interception_module
from Modules.storage_module1 import storage_module                   #called storage_module1 (WITH THE 1)
from Modules.discharge_module import discharge_module


obs = pd.read_csv('Datasets/CAMELS_CH_obs_based_2469.csv')
sim = pd.read_csv('Datasets/CAMELS_CH_sim_based_2469.csv')


best, bestk, bestSmax = calibration_module(obs, sim)

print(best, bestk, bestSmax)