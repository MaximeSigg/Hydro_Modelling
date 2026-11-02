import pandas as pd

def discharge_module(catchment):
    df = catchment.copy()

  # Total discharge = Base drainage + Surface overflow
    df['Q_tot_discharge_(mm/d)'] = df['Q_base(mm/d)'] + df['Q_overflow(mm/d)']
    
    return df