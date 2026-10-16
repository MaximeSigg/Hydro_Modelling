import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

catchment = pd.read_csv('C:/Users/maxim/OneDrive/Documents/4. Master_Bern/Hydro_Modelling/Projet_hydro_modelling/camels_ch/camels_ch/timeseries/observation_based/CAMELS_CH_obs_based_2469.csv')


## make new snowfall column, out of the equation we learned
Tpbase = 2                      ## upper limit for snowfall
mp = 1                          ## mixed-precip factor = 1

catchment['snowfall'] = (
    catchment['precipitation(mm/d)'] / 
    (1+np.exp(
        (catchment['temperature_mean(degC)']- Tpbase)*mp)
    )
) 

## make new melt column
mf = 3                         ## means melt rate at 3mm/°Cday: the snow is considered between fresh and old
T_T = 2                       ## lower limit for rainfall

melt = []      ## create a new empty column

for temp in catchment['temperature_mean(degC)']:
    if temp > T_T:
        melt.append((temp - T_T) * mf)
    else:
        melt.append(0)


# 3. Calculate Snow Water Equivalent (SWE)
SWE = []                    ## create a new empty column
storage = 0                 # Initial snow storage (mm)

for snowfall, melt in zip(catchment['snowfall'], catchment['melt']):
  storage = storage + snowfall - melt

  if storage < 0:
    storage = 0                  # You cannot melt more snow than what exists!

  SWE.append(storage)

catchment['SWE'] = SWE


if 'date' in catchment.columns:
  catchment['date'] = pd.to_datetime(catchment['date'])
  catchment = catchment.set_index('date')                          ## Without the if, it tries to find the date column which exists only as index now

p1 = catchment.loc['1990-10-01':'2000-09-30']                   # 1. Select the 10-year periods
p2 = catchment.loc['2010-10-01':'2020-09-30']

p1_avg = p1.groupby(p1.index.dayofyear).mean()                        # 2. Calculate daily average over 10 years (Day 1 to 365)
p2_avg = p2.groupby(p2.index.dayofyear).mean()

# 2. Plot Precipitation and SWE on one graph
plt.bar(p1_avg.index, p1_avg['snowfall'], color='blue', label='Snowfall')
plt.plot(p1_avg.index, p1_avg['SWE'], color='red', label='Modelled SWE')
plt.plot(p1_avg.index, p1_avg['swe(mm)'], color= 'grey', label = 'Observed SWE')

plt.xlabel('Date')
plt.ylabel('mm')
plt.title('Modelled SWE evolution based on snow Accumulation and Melt (1990-2000)')
plt.legend()
plt.savefig('SWE-Evolution_1990-2000.png', dpi= 150)
plt.xticks([1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335], ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec',])
plt.show()

# 2. Plot Precipitation and SWE on one graph
plt.bar(p2_avg.index, p2_avg['snowfall'], color='blue', label='Snowfall')
plt.plot(p2_avg.index, p2_avg['SWE'], color='red', label='Modelled SWE')
plt.plot(p2_avg.index, p2_avg['swe(mm)'], color= 'grey', label = 'Observed SWE')

plt.xlabel('Date')
plt.ylabel('mm')
plt.title('Modelled SWE evolution based on snow Accumulation and Melt (2010-2012)')
plt.legend()
plt.savefig("SWE-Evolution_2010-2020.png", dpi=150)
plt.xticks([1, 32, 60, 91, 121, 152, 182, 213, 244, 274, 305, 335], ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec',])
plt.show()


catchment['melt'] = melt
