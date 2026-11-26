#%%
import pandas as pd
import numpy as np

elevation_bands = [
    (750, 0.0953),
    (1250, 0.2271),
    (1750, 0.2816),
    (2250, 0.2312),
    (2750, 0.1256),
    (3250, 0.0392)]
mean_elevation = 1854

def snow_module_elevation(catchment,
                Tpbase=1.5,
                mp=1,
                mf=2,
                T_T=2,
                lapse_rate=0.0060):
    """
    Calculate snowfall, rainfall, melt and SWE for different elevation bands.
    Results are weighted by the area fraction of each band.

    Parameters
    ----------
    catchment : pandas.DataFrame
        Must contain 'precipitation(mm/d)' and 'temperature_mean(degC)'.
    Tpbase : float
        Threshold temperature for rain/snow separation (°C).
    mp : float
        Mixed-precipitation factor.
    mf : float
        Melt factor (mm/°C/day).
    T_T : float
        Threshold temperature for snowmelt (°C).
    elevation_bands : list of tuples
        Elevation and area fraction of each band.
        Example: [(1000, 0.2), (1500, 0.5), (2000, 0.3)].
    mean_elevation : float
        Mean elevation of the catchment (m).
    lapse_rate : float
        Temperature decrease per metre of elevation (°C/m).
        Default = 0.006 °C/m (0.6 °C per 100 m).
    """

    df = catchment.copy()


    # Initialise catchment-wide results
    df['Snowfall_modelled(mm/d)'] = 0.0
    df['Rainfall_modelled(mm/d)'] = 0.0
    df['Melt_modelled(mm/d)'] = 0.0
    df['SWE_modelled(mm)'] = 0.0
    df['Actual_melt(mm/d)'] = 0.0

    # Calculate snow processes for each elevation band
    for elevation, area_fraction in elevation_bands:

        # Correct temperature according to elevation
        temperature = (
                df['temperature_mean(degC)']
                - lapse_rate * (elevation - mean_elevation)
        )

        # Snow/rain separation
        snowfall = (
                df['precipitation(mm/d)']
                / (1 + np.exp((temperature - Tpbase) * mp))
        )

        rainfall = df['precipitation(mm/d)'] - snowfall

        # Potential snowmelt
        melt_potential = (temperature - T_T).clip(lower=0) * mf

        # Calculate SWE separately for this elevation band
        storage = 0
        SWE = []
        actual_melt = []

        for date, snowfall_day, melt_day in zip(
                df['date'], snowfall, melt_potential):

            # Reset snow storage every 1 September
            if pd.to_datetime(date).month == 9 and pd.to_datetime(date).day == 1:
                storage = 0

            storage = storage + snowfall_day

            melt = min(storage, melt_day)
            storage = storage - melt

            SWE.append(storage)
            actual_melt.append(melt)

        # Weight results by the area fraction of this band
        df['Snowfall_modelled(mm/d)'] += snowfall * area_fraction
        df['Rainfall_modelled(mm/d)'] += rainfall * area_fraction
        df['Melt_modelled(mm/d)'] += melt_potential * area_fraction
        df['SWE_modelled(mm)'] += np.array(SWE) * area_fraction
        df['Actual_melt(mm/d)'] += np.array(actual_melt) * area_fraction

    return df

