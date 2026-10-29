import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import pandas as pd
from Modules.snow_module import snow_module
from Modules.interception_module import interception_module
from Modules.storage_module import storage_module



def load_station(path, col='rre150d0'):
    s = pd.read_csv(path, sep=';', usecols=['reference_timestamp', col])
    s.index = pd.to_datetime(s['reference_timestamp'], format='%d.%m.%Y %H:%M')
    return pd.to_numeric(s[col], errors='coerce').rename('precip_station(mm/d)')

def run_model(observed, simulated, precip=None):
    """Run the full chain. precip=None -> CAMELS precipitation, else a Series indexed by date."""
    obs = observed.copy()
    if precip is not None:
        obs['precipitation(mm/d)'] = precip.reindex(obs.index)
    df = snow_module(obs)
    df = interception_module(df, simulated)
    return storage_module(df)

def plot_q(ax, d, title, q_obs, q_mod, p_col):
    ax.plot(d.index, d[q_obs], color='k', label='Q observed')
    ax.plot(d.index, d[q_mod], color='tab:red', label='Q modelled')
    ax.set_ylabel('Discharge (mm/d)'); ax.set_title(title)
    axp = ax.twinx()
    axp.bar(d.index, d[p_col], color='tab:blue', width=1.0)
    axp.set_ylim(d[p_col].max() * 3, 0)          # reversed precipitation on top
    axp.set_ylabel('Precip (mm/d)')

def compare(df_camels, df_station, events, q_obs='discharge_spec(mm/d)',
            q_mod='Water_input(mm/d)', p_col='precipitation(mm/d)'):
    periods = [('full period', df_camels.index.min(), df_camels.index.max())] + \
              [(f'{a} to {b}', a, b) for a, b in events]
    for name, a, b in periods:
        fig, axs = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
        plot_q(axs[0], df_station.loc[a:b], f'With station precip ({name})', q_obs, q_mod, p_col)
        plot_q(axs[1], df_camels.loc[a:b],  'With CAMELS precip',            q_obs, q_mod, p_col)
        axs[0].legend(loc='lower left'); fig.tight_layout()

    p = pd.concat([df_camels[p_col].rename('camels'),
                   df_station[p_col].rename('station')], axis=1).dropna()
    lim = [0, p.max().max()]

    # cumulated precip with 1:1 line
    c = p.cumsum(); cl = [0, c.max().max()]
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.plot(c['station'], c['camels'], label='station vs CAMELS')
    ax.plot(cl, cl, 'k--', label='1:1 line')
    ax.set_xlabel('Cumulated precip station (mm)'); ax.set_ylabel('Cumulated precip CAMELS (mm)')
    ax.set_aspect('equal'); ax.legend(); fig.tight_layout()

    # daily scatter
    fig, ax = plt.subplots(figsize=(5, 5))
    ax.scatter(p['station'], p['camels'], s=6, alpha=0.3)
    ax.plot(lim, lim, 'k--')
    ax.set_xlabel('Precip station (mm/d)'); ax.set_ylabel('Precip CAMELS (mm/d)')
    ax.set_aspect('equal'); fig.tight_layout()
    plt.show()


observed  = pd.read_csv('Datasets/CAMELS_CH_obs_based_2469.csv')
simulated = pd.read_csv('Datasets/CAMELS_CH_sim_based_2469.csv')     # placeholder name
observed.index = simulated.index = pd.to_datetime(observed['date'])

station = load_station('Datasets/ogd-smn-precip_kas_d_historical.csv')

df_camels  = run_model(observed, simulated)                  # CAMELS precipitation
df_station = run_model(observed, simulated, precip=station)  # station precipitation

events = [('2007-06-01', '2007-08-31'), ('2010-05-01', '2010-07-31')]   # pick real events
compare(df_camels, df_station, events)