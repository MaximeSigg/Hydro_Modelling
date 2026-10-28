def storage_module(catchment, initial_storage=0):
    """Adds to the table: total water input to the catchment and the catchment storage."""
    '''Parameters:
            -----------
            catchment : pandas.DataFrame
                Must contain 'Rain_net(mm/d)' (output of interception_module)
                and 'Actual_melt(mm/d)' (output of snow_module)
            initial_storage : float
                Catchment storage at t=0 (mm)'''

    df = catchment.copy()

    # rain not intercepted + unloading (Rain_net) + snowmelt
    df['Water_input(mm/d)'] = df['Rain_net(mm/d)'] + df['Actual_melt(mm/d)']

    # storage so far has only inputs; outputs (transpiration, runoff) come with the soil module
    df['Storage(mm)'] = initial_storage + df['Water_input(mm/d)'].cumsum()

    return df