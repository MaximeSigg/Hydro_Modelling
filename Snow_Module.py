import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

catchment = pd.read_csv('C:/Users/maxim/OneDrive/Documents/4. Master_Bern/Hydro_Modelling/Projet_hydro_modelling/camels_ch/camels_ch/timeseries/observation_based/CAMELS_CH_obs_based_2469.csv')

##1. make new snowfall column, out of the equation we learned
Tpbase = 2                      ## upper limit for snowfall
mp = 1                          ## mixed-precip factor = 1

catchment['Snowfall_modelled(mm/d)'] = (
    catchment['precipitation(mm/d)'] / (1+np.exp(
        (catchment['temperature_mean(degC)']- Tpbase)*mp)
    )
)

##2. make new melt column
mf = 3                         ## means melt rate at 3mm/°Cday: the snow is considered between fresh and old
T_T = 2                        ## lower limit for rainfall

catchment['Melt_modelled(mm/d)'] = (
    (catchment['temperature_mean(degC)'] - T_T).clip(lower=0) * mf
)                                                                           # new column melt with the equation seen during the course


# 3. Calculate Snow Water Equivalent (SWE)
SWE = []                    ## create a new empty column
actual_melt = []
storage = 0                 # Initial snow storage (mm)

for snowfall, melt in zip(catchment['Snowfall_modelled(mm/d)'],
                          catchment['Melt_modelled(mm/d)']):
    storage = storage + snowfall

    melt = min(storage, melt)
    storage = storage - melt               

    SWE.append(storage)
    actual_melt.append(melt)

catchment['SWE_modelled(mm)'] = SWE                             #useful for the personal exercice 2
catchment['Actual_melt(mm/d)'] = actual_melt                    #useful for the group exercice 3 (because we need the melt)
