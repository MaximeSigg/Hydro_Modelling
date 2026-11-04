'''
Calibration Module:
Function to tune the parameters for the snow/rain separation and for the linear flowerpot model.
Model is applied to CAMELS observed data, and the calibration is done with the simulated discharge
from CAMELS.
'''

import itertools
import numpy as np
import pandas as pd

from .snow_module import snow_module
from .interception_module import interception_module
from .storage_module1 import storage_module
from .discharge_module import discharge_module


def nse(o, m):
    return 1 - np.sum((o - m) ** 2) / np.sum((o - o.mean()) ** 2)


def calibration_module(obs, sim):

    obs.index = sim.index = pd.to_datetime(obs['date'])

    # ---- Step 1: snow parameters (RMSE of SWE) ----
    mp_list = [1, 1.5, 2, 3]                       # mp < 1: unrealistically wide transition
    Tpbase_list = [-0.5, 0, 0.5, 1, 1.5, 2, 2.5]
    mf_list = [1, 2, 3, 4, 5, 6, 7]                # literature range
    T_T_list = [-2, -1, 0, 1, 2]

    has_swe = obs['swe(mm)'].notna()
    swe_obs = obs.loc[has_swe, 'swe(mm)']

    results = []
    for mp, Tp, mf, TT in itertools.product(mp_list, Tpbase_list, mf_list, T_T_list):
        df = snow_module(obs, Tpbase=Tp, mp=mp, mf=mf, T_T=TT)
        rmse = np.sqrt(np.mean((df.loc[has_swe, 'SWE_modelled(mm)'] - swe_obs) ** 2))
        results.append((rmse, mp, Tp, mf, TT))
    results.sort()
    print('Best snow parameters (RMSE, mp, Tpbase, mf, T_T):')
    for r in results[:5]:
        print(np.round(r, 2))
    best_snow = dict(mp=results[0][1], Tpbase=results[0][2], mf=results[0][3], T_T=results[0][4])

    # ---- Step 2: k and Smax (NSE of discharge) ----
    df = snow_module(obs, **best_snow)             # snow and interception do not depend on k, Smax
    df = interception_module(df, sim)

    k_list = [0.01, 0.02, 0.03, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3]
    Smax_list = [50, 100, 200, 300, 500, 750, 1000]

    Q_obs = obs['discharge_spec(mm/d)']
    cal = (obs.index >= '1982-01-01') & (obs.index <= '2000-12-31')   # 1981 = spin-up
    val = obs.index >= '2001-01-01'

    results = []
    for k, Smax in itertools.product(k_list, Smax_list):
        d = discharge_module(storage_module(df, k=k, Smax=Smax, initial_storage=0))
        Q_mod = d['Q_tot_discharge_(mm/d)']
        results.append((nse(Q_obs[cal], Q_mod[cal]), nse(Q_obs[val], Q_mod[val]), k, Smax))
    results.sort(reverse=True)
    print('Best k, Smax (NSE calibration, NSE validation, k, Smax):')
    for r in results[:5]:
        print(np.round(r, 3))
    print('Selected:', best_snow, 'k =', results[0][2], 'Smax =', results[0][3])
    best_k = results[0][2]
    best_Smax = results[0][3]
    return best_snow, best_k, best_Smax

# best snow includes pest snow params stored as: {'mp': 2, 'Tpbase': 1.5, 'mf': 4, 'T_T': 0}
# results [0][2] is the best k param
# results[0][3]