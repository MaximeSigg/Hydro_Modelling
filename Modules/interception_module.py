'''
SNOW MODULE: Interception function

This function  implements the snow/rain separation from the precipitation data.
We use the equation from Magnusson et. al., 2024
'''
import numpy as np
import pandas as pd

def interception_module(observed, simulated, Icept_threshold=1):
    """Adds to the table: PET, Interception, Throughfall, Evaporation of interception,
    Unloading, net rainfall and PET left for transpiration."""
    '''Parameters:
            -----------
            observed : pandas.DataFrame
                Must contain 'Rainfall_modelled(mm/d)' (output of snow_module)
            simulated : pandas.DataFrame
                Same structure as observed, must contain 'pet(mm/d)'
            Icept_threshold : float
                Maximum interception per day (mm/d)'''

    df = observed.copy()

    rain = df['Rainfall_modelled(mm/d)']
    pet = simulated['pet_sim(mm/d)']

    df['PET_sim(mm/d)'] = pet
    df['Icept_modelled(mm/d)'] = np.minimum(rain, Icept_threshold)
    df['Throughfall_modelled(mm/d)'] = rain - df['Icept_modelled(mm/d)']
    df['Evap_icept(mm/d)'] = np.minimum(pet, df['Icept_modelled(mm/d)'])
    df['Unloading(mm/d)'] = df['Icept_modelled(mm/d)'] - df['Evap_icept(mm/d)']
    df['Rain_net(mm/d)'] = df['Throughfall_modelled(mm/d)'] + df['Unloading(mm/d)']

    # PET left for transpiration after interception has used its share
    df['PET_transpiration(mm/d)'] = pet - df['Evap_icept(mm/d)']

    return df