'''
SNOW MODULE: SNOW/RAIN SEPARATION FUNCTION

This function  implements the snow/rain separation from the precipitation data. 
We use the equation from Magnusson et. al., 2024
'''

import numpy as np
import pandas as pd

#catchment = pd.read_csv('CAMELS_CH_obs_based_2469.csv')

def snow_module(catchment,Tpbase = 2,mp = 1,mf = 3,T_T = 2):
    """Add to table : Snowfall, Rainfall, Melt, SWE et Actual_melt."""
    '''Parameters:
            -----------
            df : pandas.DataFrame
                Must contain 'precipitation(mm/d)' and 'temperature_mean(degC)'
            tp_base : float
                Threshold temperature for rain/snow separation (°C)
            mp : float
                Mixed-precipitation factor
            mf : float
                Melt factor (mm/°C/day)
            t_t : float
                Threshold temperature for snowmelt (°C)
            initial_swe : float
                Initial snow water equivalent at t=0 (mm)'''

    df = catchment.copy()

    df['Snowfall_modelled(mm/d)'] = ( df['precipitation(mm/d)'] / (1+np.exp((df['temperature_mean(degC)']- Tpbase)*mp)))
    df['Rainfall_modelled(mm/d)'] = df['precipitation(mm/d)'] - df['Snowfall_modelled(mm/d)']
    df['Melt_modelled(mm/d)'] = ((df['temperature_mean(degC)'] - T_T).clip(lower=0) * mf)   

    storage = 0
    SWE = []
    actual_melt = []

    for snowfall, melt in zip(df['Snowfall_modelled(mm/d)'],
                                df['Melt_modelled(mm/d)']):
            storage = storage + snowfall

            melt = min(storage, melt)
            storage = storage - melt               

            SWE.append(storage)
            actual_melt.append(melt)

    df['SWE_modelled(mm)'] = SWE                             #useful for the personal exercice 2
    df['Actual_melt(mm/d)'] = actual_melt                    #useful for the group exercice 3 (because we need the melt)
    return df


