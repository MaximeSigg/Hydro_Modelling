'''
--------------------------------------------------------------------
                        GROUP EXERCISE 2
         Exercise 2c : Storage max capacity & ET
 Authors: Antonia Schibbe, Jordi Fornés Mengual, Maxime Siggen
-------------------------------------------------------------------
 Description: In this exercise we extend the single linear storage
(flowerpot model) of exercise 2a by
  1) a maximum storage capacity Smax: water that does not fit into the
     storage is not ignored but leaves the system as overflow, which is
     added to the discharge (Qtot = Q + Qout),
  2) evapotranspiration: ET = ET0 * (S(t) / Smax)^0.5, ET0 = 2 mm/d.
Precipitation is 10 mm per time step during the first 10 time steps,
afterwards 0.
-------------------------------------------------------------------
'''

# Required packages: numpy, matplotlib
import numpy as np
import matplotlib.pyplot as plt


# FLOWER POT MODEL WITH Smax AND ET: Parameters

k = 0.1          # discharge constant [1/step]
Smax = 50.0      # maximum storage capacity [mm] (arbitrary, can be changed)
ET0 = 2.0        # reference evapotranspiration [mm/step]
n = 50           # number of time steps
p = np.zeros(n); p[:10] = 10   # precipitation [mm per step]

S = np.zeros(n + 1)       # storage
et = np.zeros(n)          # evapotranspiration
q = np.zeros(n)           # regular (linear) discharge
q_out = np.zeros(n)       # overflow when the storage is full
q_tot = np.zeros(n)       # total discharge = q + q_out


for t in range(n):
    available = S[t] + p[t]                  # water that can be used in this step

    # evapotranspiration, limited by the available water
    et[t] = min(ET0 * np.sqrt(S[t] / Smax), available)

    # linear discharge, limited by the water left after ET
    q[t] = min(k * S[t], available - et[t])

    S_new = S[t] + p[t] - et[t] - q[t]

    # if the storage exceeds Smax, the surplus leaves as overflow (not ignored!)
    if S_new > Smax:
        q_out[t] = S_new - Smax
        S_new = Smax

    q_tot[t] = q[t] + q_out[t]
    S[t + 1] = S_new


# Water balance check: P_total = ET_total + Q_total + change in storage
balance = p.sum() - (et.sum() + q_tot.sum() + (S[-1] - S[0]))
print(f"Total precipitation: {p.sum():.2f} mm")
print(f"Total ET:            {et.sum():.2f} mm")
print(f"Total discharge:     {q_tot.sum():.2f} mm (of which overflow: {q_out.sum():.2f} mm)")
print(f"Final storage:       {S[-1]:.2f} mm")
print(f"Water balance error: {balance:.2e} mm")


# Plot
t = np.arange(n)
fig, ax = plt.subplots(4, 1, figsize=(8, 10), sharex=True)

ax[0].bar(t, p, color="#7fb2ff")
ax[0].set_ylabel("P(t) [mm/step]")
ax[0].set_title(f"Linear storage with Smax and ET (k = {k}, Smax = {Smax:g} mm, ET0 = {ET0:g} mm/step)")

ax[1].plot(t, S[:-1], color="#52A675", lw=2)
ax[1].axhline(Smax, color="red", ls=":", lw=1.5, label="Smax")
ax[1].set_ylabel("S(t) [mm]")
ax[1].legend()

ax[2].plot(t, et, color="#e0a800", lw=2)
ax[2].set_ylabel("ET(t) [mm/step]")

ax[3].plot(t, q, color="#4682B4", lw=2, label="Q(t)")
ax[3].plot(t, q_out, color="#d62728", lw=2, label="Q_out(t)")
ax[3].plot(t, q_tot, color="black", lw=1.5, ls="--", label="Q_tot(t)")
ax[3].set_ylabel("Discharge [mm/step]")
ax[3].set_xlabel("time step")
ax[3].legend()

# Mark end of rainfall and add grid
for a in ax:
    a.axvline(10, color="gray", ls="--", lw=1)
    a.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("../flowerpot_Smax_ET_plot.png", dpi=150)
plt.show()