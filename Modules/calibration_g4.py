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

def nse_log(o, m):
    eps = 0.01 * o.mean()            # avoids log(0) on days with zero flow
    return 1 - np.sum((np.log(o + eps) - np.log(m + eps)) ** 2) / np.sum((np.log(o + eps) - np.log(o + eps).mean()) ** 2)

def bias(o, m):
    return 100 * np.sum(m - o) / np.sum(o)        # percent bias

def kge(o, m):
    r = np.corrcoef(o, m)[0, 1]
    alpha = m.std() / o.std()
    beta = m.mean() / o.mean()
    return 1 - np.sqrt((r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2)

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
        swe_mod = df.loc[has_swe, 'SWE_modelled(mm)']

        nse_swe = nse(swe_obs, swe_mod)
        nse_log_swe = nse_log(swe_obs, swe_mod)
        bias_swe = bias(swe_obs, swe_mod)
        kge_swe = kge(swe_obs, swe_mod)

        results.append(( mp, Tp, mf, TT, nse_swe, nse_log_swe, bias_swe, kge_swe))
    results.sort()
    print('Best snow parameters ( mp, Tpbase, mf, T_T, NSE, NSE_log, bias, KGE):')
    for r in results[:5]:
        print(np.round(r, 2))
    best_snow = dict(mp=results[0][1], Tpbase=results[0][2], mf=results[0][3], T_T=results[0][4])

    # ---- Step 2: k and Smax (NSE of discharge) ----
    df = snow_module(obs, **best_snow)  # snow and interception do not depend on k, Smax
    df = interception_module(df, sim)

    k_list = [0.01, 0.02, 0.03, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3]
    Smax_list = [50, 100, 200, 300, 500, 750, 1000]

    Q_obs = obs['discharge_spec(mm/d)']
    cal = (obs.index >= '1983-01-01') & (obs.index <= '2009-12-31')  # 1981+1982 = spin-up
    val = obs.index >= '2010-01-01'

    results = []
    for k, Smax in itertools.product(k_list, Smax_list):
        d = discharge_module(storage_module(df, k=k, Smax=Smax, initial_storage=0))
        Q_mod = d['Q_tot_discharge_(mm/d)']

        results.append((nse(Q_obs[cal], Q_mod[cal]), nse(Q_obs[val], Q_mod[val]), k, Smax,
                        nse_log(Q_obs[cal], Q_mod[cal]), nse_log(Q_obs[val], Q_mod[val]),
                        bias(Q_obs[cal], Q_mod[cal]), bias(Q_obs[val], Q_mod[val]),
                        kge(Q_obs[cal], Q_mod[cal]), kge(Q_obs[val], Q_mod[val])))
    results.sort(reverse=True)
    print('Best k, Smax (NSE cal, NSE val, k, Smax, NSE_log cal, NSE_log val, bias cal, bias val, KGE cal, KGE val):')
    for r in results[:5]:
        print(np.round(r, 3))
    print('Selected:', best_snow, 'k =', results[0][2], 'Smax =', results[0][3])
    best_k = results[0][2]
    best_Smax = results[0][3]
    return best_snow, best_k, best_Smax

# best snow includes pest snow params stored as: {'mp': 2, 'Tpbase': 1.5, 'mf': 4, 'T_T': 0}
# results [0][2] is the best k param
# results[0][3]
