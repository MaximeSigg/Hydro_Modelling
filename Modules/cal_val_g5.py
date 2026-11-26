
"""
FOR EXERCISE 5 - GR5

Calibration module:
Tune the parameters for the snow/rain separation,
the elevation-band snow module and the linear flowerpot model.

The model is applied to CAMELS observed data,
and calibration is evaluated against observed discharge.
"""

import itertools
import numpy as np
import pandas as pd

# Import the model modules
try:
    from Modules.discharge_module import discharge_module
    from Modules.interception_module import interception_module
    from Modules.snow_module_elevation_gr5 import snow_module_elevation
    from Modules.storage_module1 import storage_module

except ModuleNotFoundError:
    from discharge_module import discharge_module
    from interception_module import interception_module
    from snow_module_elevation_gr5 import snow_module_elevation
    from storage_module1 import storage_module


# Performance criteria
def nse(o, m):
    return 1 - np.sum((o - m) ** 2) / np.sum((o - o.mean()) ** 2)


def nse_log(o, m):
    eps = 0.01 * o.mean()
    return 1 - np.sum((np.log(o + eps) - np.log(m + eps)) ** 2) / np.sum(
        (np.log(o + eps) - np.log(o + eps).mean()) ** 2
    )


def bias(o, m):
    return 100 * np.sum(m - o) / np.sum(o)


def kge(o, m):
    r = np.corrcoef(o, m)[0, 1]
    alpha = m.std() / o.std()
    beta = m.mean() / o.mean()
    return 1 - np.sqrt(
        (r - 1) ** 2 + (alpha - 1) ** 2 + (beta - 1) ** 2
    )


def calibration_module_g5(
    CAL_START, CAL_END, VAL_START,
    mp_list, Tpbase_list, mf_list, T_T_list,
    k_list, Smax_list, obs, sim
):

    obs = obs.copy()
    sim = sim.copy()

    obs['date'] = pd.to_datetime(obs['date'])
    sim['date'] = pd.to_datetime(sim['date'])

    obs.index = obs['date']
    sim.index = sim['date']

    cal = (obs.index >= CAL_START) & (obs.index <= CAL_END)
    val = obs.index >= VAL_START

    # ---- Step 1: Snow parameters ----

    has_swe_cal = obs['swe(mm)'].notna() & cal
    swe_obs = obs.loc[has_swe_cal, 'swe(mm)']

    results = []

    for mp, Tp, mf, TT in itertools.product(
        mp_list, Tpbase_list, mf_list, T_T_list
    ):

        df = snow_module_elevation(
            obs, Tpbase=Tp, mp=mp, mf=mf, T_T=TT
        )

        swe_mod = df.loc[has_swe_cal, 'SWE_modelled(mm)']

        nse_swe = nse(swe_obs, swe_mod)
        nse_log_swe = nse_log(swe_obs, swe_mod)
        bias_swe = bias(swe_obs, swe_mod)
        kge_swe = kge(swe_obs, swe_mod)

        score = (nse_swe + kge_swe) / 2

        if np.isnan(score):
            score = -np.inf

        results.append((
            score, mp, Tp, mf, TT,
            nse_swe, nse_log_swe, bias_swe, kge_swe
        ))

    results.sort(reverse=True)

    print('\n' + '=' * 90)
    print(f'CALIBRATION ({CAL_START} to {CAL_END}): SNOW PARAMETERS')
    print('=' * 90)

    print(
        f"{'rank':>4} | {'mp':>5} | {'Tpbase':>7} | {'mf':>5} | {'T_T':>5} | "
        f"{'NSE':>7} | {'NSE_log':>8} | {'bias %':>8} | {'KGE':>7} | {'score':>7}"
    )

    print('-' * 90)

    for i, r in enumerate(results[:5], 1):
        print(
            f"{i:>4} | {r[1]:>5g} | {r[2]:>7g} | {r[3]:>5g} | {r[4]:>5g} | "
            f"{r[5]:>7.3f} | {r[6]:>8.3f} | {r[7]:>8.1f} | "
            f"{r[8]:>7.3f} | {r[0]:>7.3f}"
        )

    best_snow = dict(
        mp=results[0][1],
        Tpbase=results[0][2],
        mf=results[0][3],
        T_T=results[0][4]
    )

    # ---- Step 2: k and Smax ----

    df = snow_module_elevation(obs, **best_snow)
    df = interception_module(df, sim)

    Q_obs = obs['discharge_spec(mm/d)']

    results = []

    for k, Smax in itertools.product(k_list, Smax_list):

        d = discharge_module(
            storage_module(df, k=k, Smax=Smax, initial_storage=0)
        )

        Q_mod = d['Q_tot_discharge_(mm/d)']

        nse_q = nse(Q_obs[cal], Q_mod[cal])
        nse_log_q = nse_log(Q_obs[cal], Q_mod[cal])
        bias_q = bias(Q_obs[cal], Q_mod[cal])
        kge_q = kge(Q_obs[cal], Q_mod[cal])

        score = (nse_q + kge_q) / 2

        if np.isnan(score):
            score = -np.inf

        results.append((
            score, k, Smax,
            nse_q, nse_log_q, bias_q, kge_q
        ))

    results.sort(reverse=True)

    print('\n' + '=' * 74)
    print(f'CALIBRATION ({CAL_START} to {CAL_END}): k AND Smax')
    print('=' * 74)

    print(
        f"{'rank':>4} | {'k':>6} | {'Smax':>6} | "
        f"{'NSE':>7} | {'NSE_log':>8} | {'bias %':>8} | {'KGE':>7} | {'score':>7}"
    )

    print('-' * 74)

    for i, r in enumerate(results[:5], 1):
        print(
            f"{i:>4} | {r[1]:>6g} | {r[2]:>6g} | "
            f"{r[3]:>7.3f} | {r[4]:>8.3f} | "
            f"{r[5]:>8.1f} | {r[6]:>7.3f} | {r[0]:>7.3f}"
        )

    best_k = results[0][1]
    best_Smax = results[0][2]

    # ---- Step 3: Validation ----

    d = discharge_module(
        storage_module(df, k=best_k, Smax=best_Smax, initial_storage=0)
    )

    Q_mod = d['Q_tot_discharge_(mm/d)']

    has_swe_val = obs['swe(mm)'].notna() & val
    swe_obs_val = obs.loc[has_swe_val, 'swe(mm)']
    swe_mod_val = df.loc[has_swe_val, 'SWE_modelled(mm)']

    print('\n' + '=' * 52)
    print(f'VALIDATION ({VAL_START} onwards), selected parameters')
    print('=' * 52)

    print(
        f"  mp = {best_snow['mp']:g}, Tpbase = {best_snow['Tpbase']:g}, "
        f"mf = {best_snow['mf']:g}, T_T = {best_snow['T_T']:g}, "
        f"k = {best_k:g}, Smax = {best_Smax:g}"
    )

    print('-' * 52)
    print(f"{'variable':<10} | {'NSE':>7} | {'NSE_log':>8} | {'bias %':>8} | {'KGE':>7}")
    print('-' * 52)

    print(
        f"{'SWE':<10} | {nse(swe_obs_val, swe_mod_val):>7.3f} | "
        f"{nse_log(swe_obs_val, swe_mod_val):>8.3f} | "
        f"{bias(swe_obs_val, swe_mod_val):>8.1f} | "
        f"{kge(swe_obs_val, swe_mod_val):>7.3f}"
    )

    print(
        f"{'Discharge':<10} | {nse(Q_obs[val], Q_mod[val]):>7.3f} | "
        f"{nse_log(Q_obs[val], Q_mod[val]):>8.3f} | "
        f"{bias(Q_obs[val], Q_mod[val]):>8.1f} | "
        f"{kge(Q_obs[val], Q_mod[val]):>7.3f}"
    )

    print('=' * 52)

    return best_snow, best_k, best_Smax
