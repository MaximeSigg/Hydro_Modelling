import numpy as np
import pandas as pd


def storage_module(catchment, k=0.1, Smax=100, initial_storage=0):
  """Calculates soil water storage, soil ET, base drainage, and surface overflow."""
  df = catchment.copy()

  # Total liquid water reaching the soil (Net rain + Snowmelt)
  water_input = (df['Rain_net(mm/d)'] + df['Actual_melt(mm/d)']).values
  pet_transp = df['PET_transpiration(mm/d)'].values

  n = len(df)
  S = np.zeros(n + 1)
  q_base = np.zeros(n)
  q_overflow = np.zeros(n)

  S[0] = initial_storage

  for t in range(n):
    available = S[t] + water_input[t]

    # Actual soil evapotranspiration (scaled by S/Smax)
    et = min(pet_transp[t] * np.sqrt(S[t] / Smax), available)

    # Base drainage (from remaining water)
    q_base[t] = min(k * S[t], available - et)

    # Temporary storage update
    S_next = S[t] + water_input[t] - et - q_base[t]

    # Surface overflow check
    if S_next > Smax:
      q_overflow[t] = S_next - Smax
      S_next = Smax

    S[t + 1] = S_next

  # Save outputs to DataFrame
  df['Soil_Storage(mm)'] = S[:-1]
  df['Q_base(mm/d)'] = q_base
  df['Q_overflow(mm/d)'] = q_overflow

  return df