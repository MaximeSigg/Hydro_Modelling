'''
Calibration Module:
Function to tune the parameters for the snow/rain separation and for the linear flowerpot model.
Model is applied to CAMELS observed data, and the calibration is done with the simulated discharge
from CAMELS.
'''

import itertools
import numpy as np
import pandas as pd

try:
  from Modules.discharge_module import discharge_module
  from Modules.interception_module import interception_module
  from Modules.snow_module import snow_module
  from Modules.storage_module1 import storage_module
except ModuleNotFoundError:
  from discharge_module import discharge_module
  from interception_module import interception_module
  from snow_module import snow_module
  from storage_module1 import storage_module


def nse(o, m):
    return 1 - np.sum((o - m) ** 2) / np.sum((o - o.mean()) ** 2)


def kge(o, m):
    r = np.corrcoef(o, m)[0, 1]
    alpha = m.std() / o.std()
    beta = m.mean() / o.mean()
    return 1 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)


def calibration_module(obs, sim):

    obs.index = sim.index = pd.to_datetime(obs['date'])

    # ---- Step 1: snow parameters (mean of NSE and KGE of SWE) ----
    mp_list = [1, 1.5, 2, 3]                       # mp < 1: unrealistically wide transition
    Tpbase_list = [-0.5, 0, 0.5, 1, 1.5, 2, 2.5]
    mf_list = [1, 2, 3, 4, 5, 6, 7]                # literature range
    T_T_list = [-2, -1, 0, 1, 2]

    has_swe = obs['swe(mm)'].notna()
    swe_obs = obs.loc[has_swe, 'swe(mm)']

    results = []
    for mp, Tp, mf, TT in itertools.product(mp_list, Tpbase_list, mf_list, T_T_list):
        df = snow_module(obs, Tpbase=Tp, mp=mp, mf=mf, T_T=TT)
        swe_mod = df.loc[has_swe, 'SWE_modelled(mm)']

        nse_swe = nse(swe_obs, swe_mod)
        kge_swe = kge(swe_obs, swe_mod)
        score = (nse_swe + kge_swe) / 2
        if np.isnan(score):                        # e.g. no snow at all -> KGE undefined
            score = -np.inf

        results.append((score, mp, Tp, mf, TT, nse_swe, kge_swe))
    results.sort(reverse=True)

    print('\nSNOW PARAMETERS: top 5 by mean of NSE and KGE of SWE')
    print(f"{'rank':>4} | {'mp':>5} | {'Tpbase':>7} | {'mf':>5} | {'T_T':>5} | {'NSE':>7} | {'KGE':>7} | {'score':>7}")
    print('-' * 68)
    for i, r in enumerate(results[:5], 1):
        print(f"{i:>4} | {r[1]:>5g} | {r[2]:>7g} | {r[3]:>5g} | {r[4]:>5g} | {r[5]:>7.3f} | {r[6]:>7.3f} | {r[0]:>7.3f}")
    best_snow = dict(mp=results[0][1], Tpbase=results[0][2], mf=results[0][3], T_T=results[0][4])

    # ---- Step 2: k and Smax (mean of NSE and KGE of discharge) ----
    df = snow_module(obs, **best_snow)             # snow and interception do not depend on k, Smax
    df = interception_module(df, sim)

    k_list = [0.01, 0.02, 0.03, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3]
    Smax_list = [50, 100, 200, 300, 500, 750, 1000]

    Q_obs = obs['discharge_spec(mm/d)']
    cal = (obs.index >= '1983-01-01') & (obs.index <= '2009-12-31')   # 1981+1982 = spin-up
    val = obs.index >= '2010-01-01'

    results = []
    for k, Smax in itertools.product(k_list, Smax_list):
        d = discharge_module(storage_module(df, k=k, Smax=Smax, initial_storage=0))
        Q_mod = d['Q_tot_discharge_(mm/d)']

        nse_cal, kge_cal = nse(Q_obs[cal], Q_mod[cal]), kge(Q_obs[cal], Q_mod[cal])
        nse_val, kge_val = nse(Q_obs[val], Q_mod[val]), kge(Q_obs[val], Q_mod[val])

        results.append(((nse_cal + kge_cal) / 2, k, Smax, nse_cal, kge_cal, nse_val, kge_val))
    results.sort(reverse=True)

    print('\nLINEAR RESERVOIR: top 5 by mean of NSE and KGE (calibration period)')
    print(f"{'rank':>4} | {'k':>6} | {'Smax':>6} | {'NSE cal':>8} | {'KGE cal':>8} | {'score':>7} | {'NSE val':>8} | {'KGE val':>8}")
    print('-' * 80)
    for i, r in enumerate(results[:5], 1):
        print(f"{i:>4} | {r[1]:>6g} | {r[2]:>6g} | {r[3]:>8.3f} | {r[4]:>8.3f} | {r[0]:>7.3f} | {r[5]:>8.3f} | {r[6]:>8.3f}")

    best_k = results[0][1]
    best_Smax = results[0][2]

    print('\nSELECTED PARAMETERS')
    print(f"  mp = {best_snow['mp']:g}, Tpbase = {best_snow['Tpbase']:g}, "
          f"mf = {best_snow['mf']:g}, T_T = {best_snow['T_T']:g}")
    print(f"  k = {best_k:g}, Smax = {best_Smax:g}")

    return best_snow, best_k, best_Smax