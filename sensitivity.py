'''
Sensitivity Analysis:
!has still to be reviewed!
'''


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from Modules.snow_module import snow_module
from Modules.interception_module import interception_module
from Modules.storage_module1 import storage_module
from Modules.discharge_module import discharge_module
from Modules.calibration_module import calibration_module


# --------------------------------------------------
# 1. LOAD DATA
# --------------------------------------------------

observed = pd.read_csv('Datasets/CAMELS_CH_obs_based_2469.csv')
simulated = pd.read_csv('Datasets/CAMELS_CH_sim_based_2469.csv')

observed.index = simulated.index = pd.to_datetime(observed['date'])


# --------------------------------------------------
# 2. CALIBRATION: GET BEST PARAMETERS
# --------------------------------------------------

best_snow, best_k, best_Smax = calibration_module(
    observed.copy(), simulated.copy()
)

baseline = {
    'Tpbase': best_snow['Tpbase'],
    'T_T': best_snow['T_T'],
    'mf': best_snow['mf'],
    'mp': best_snow['mp'],
    'k': best_k,
    'Smax': best_Smax
}

print('\nBest calibrated parameters:')
print(baseline)


# --------------------------------------------------
# 3. DEFINE MODEL
# --------------------------------------------------

def run_model(params):

    df = snow_module(
        observed,
        Tpbase=params['Tpbase'],
        T_T=params['T_T'],
        mf=params['mf'],
        mp=params['mp']
    )

    df = interception_module(df, simulated)

    df = storage_module(
        df,
        k=params['k'],
        Smax=params['Smax'],
        initial_storage=0
    )

    return discharge_module(df)


# --------------------------------------------------
# 4. DEFINE PARAMETER VALUES TO TEST
# --------------------------------------------------

parameter_values = {
    'Tpbase': [-0.5, 0, 0.5, 1, 1.5, 2, 2.5],
    'T_T': [-2, -1, 0, 1, 2],
    'mf': [1, 2, 3, 4, 5, 6, 7],
    'mp': [1, 1.5, 2, 3],
    'k': [0.01, 0.02, 0.03, 0.05, 0.075, 0.1, 0.15, 0.2, 0.3],
    'Smax': [50, 100, 200, 300, 500, 750, 1000]
}


# --------------------------------------------------
# 5. DEFINE PLOT AND EVALUATION PERIOD
# --------------------------------------------------

# Change these dates whenever you want
plot_start = '2010-06-01'
plot_end = '2010-07-31'

# Full validation period (as in calibration_module)
evaluation_start = '2001-01-01'


# Observed discharge for plotting
obs_plot = observed.loc[plot_start:plot_end]


# --------------------------------------------------
# 6. SENSITIVITY ANALYSIS
# --------------------------------------------------

results = {}

for parameter, values in parameter_values.items():

    fig, ax = plt.subplots(figsize=(10, 4))

    # Plot observed discharge
    ax.plot(
        obs_plot.index,
        obs_plot['discharge_spec(mm/d)'],
        color='black',
        linewidth=2,
        label='Observed discharge'
    )

    nse_scores = []

    # Change only one parameter at a time
    for value in values:

        params = baseline.copy()
        params[parameter] = value

        # Run model
        df = run_model(params)

        # Plot modelled discharge
        d_plot = df.loc[plot_start:plot_end]

        ax.plot(
            d_plot.index,
            d_plot['Q_tot_discharge_(mm/d)'],
            label=f'{value}'
        )

        # Calculate NSE over the full validation period
        comparison = pd.concat([
            observed['discharge_spec(mm/d)'],
            df['Q_tot_discharge_(mm/d)']
        ], axis=1)

        comparison = comparison.loc[evaluation_start:].dropna()

        obs = comparison['discharge_spec(mm/d)']
        mod = comparison['Q_tot_discharge_(mm/d)']

        nse = 1 - np.sum((obs - mod)**2) / np.sum((obs - obs.mean())**2)

        nse_scores.append(nse)

        print(f'{parameter} = {value}: NSE = {nse:.3f}')

    # Save results
    results[parameter] = {
        'values': values,
        'NSE': nse_scores,
        'NSE_range': max(nse_scores) - min(nse_scores)
    }

    # Figure settings
    ax.set_title(f'Sensitivity of discharge to {parameter}')
    ax.set_ylabel('Discharge [mm/d]')
    ax.set_xlabel('Date')

    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonthday=[1, 15]))
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    ax.legend(title=parameter)
    ax.grid(True, linestyle=':', alpha=0.5)

    fig.autofmt_xdate()
    fig.tight_layout()


# --------------------------------------------------
# 7. COMPARE PARAMETER INFLUENCE
# --------------------------------------------------

print('\n--------------------------------')
print('PARAMETER SENSITIVITY (NSE RANGE)')
print('--------------------------------')

for parameter, result in sorted(
    results.items(),
    key=lambda x: x[1]['NSE_range'],
    reverse=True
):
    print(f"{parameter}: {result['NSE_range']:.4f}")

plt.show()
