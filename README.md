# Hydro_Modelling
Exercices and code for Hydrology Modelling Course.

Authors: Antonia Schibbe, Jordi Fornés Mengual, Maxime Siggen

## GROUP EXERCISE 2
Flowerpot initial models can be found in folder Group Exercise 2.

## GROUP EXERCISE 3
Group Exercise 3 contains two scripts: MAIN_GroupExercise3.py and Station_Comparison_GroupExercise3.py.
MAIN_GroupExercise3.py contains the basic run of the complete flowerpot model for our catchment, with a sample plot.
Station_Comparison_GroupExercise3.py focuses on comparing the results obtained when using CAMELS or MeteoSwiss station data.

- Datasets: contains datasets for CAMELS observed/simulated and the MeteoSwiss Kander station.
- Modules: contains the different functions such as the snow/rain separation, interception, storage and discharge that are called in the MAIN and the comparison scripts. A calibration module it's also included to select the optimal parameters for our catchment.


## GROUP EXERCISE 4
In Group Exercise 4 we compute a thorough calibration of the parameters through the optimization of the performance based on NSE, KGE, Nash-log and Bias. The warmup period is: 1981 - 1982, a calibration period 1983 - 2009, and a validation period: 2010 - 2020.

CODE structure:

- MAIN_GroupExercise4.py : 
- Datasets:
- Modules: we still use the modules from the Group Exercise 3, snow/rain separation module, interception...
- New functions: calibration_g4.py and validation.py. These are the new functions including the code needed specifically for the Group Exercise 4. 
