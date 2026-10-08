'''
--------------------------------------------------------------------
                        GROUP EXERCISE 2
             Exercise 2a : Single linear storage
 Authors: Antonia Schibbe, Jordi Fornés Mengual, Maxime Siggen
-------------------------------------------------------------------
 Description: In this exercise we simulate the flowerpot model,
where we assume a linear storage, where the discharge is proportional
to the storage. Add a constant precipitation (input) of 10mm per time step
during the first 10 time steps.
'''


# Required packages: numpy, matplotlib
import numpy as np
import matplotlib.pyplot as plt


# FLOWER POT MODEL: Parameters

k = 0.1          # discharge constant [1/step]
n = 50           # number of time steps
p = np.zeros(n); p[:10] = 10   # mm per step
S = np.zeros(n+1)
q = np.zeros(n)


for t in range(n):
    q[t] = k * S[t]
    S[t+1] = S[t] + p[t] - q[t]



# Plot
t = np.arange(n)
fig, ax = plt.subplots(3, 1, figsize=(8, 8), sharex=True)

ax[0].bar(t, p, color="#7fb2ff")
ax[0].set_ylabel("p(t) [mm]")
ax[0].set_title(f"Single linear storage (k = {k})")

ax[1].plot(t, S[:-1], color="#4c9a2a", lw=2)
ax[1].set_ylabel("S(t) [mm]")

ax[2].plot(t, q, color="#1f77b4", lw=2)
ax[2].set_ylabel("q(t) [mm/step]")
ax[2].set_xlabel("time step")

# Mark end of rainfall and add grid
for a in ax:
    a.axvline(10, color="gray", ls="--", lw=1)
    a.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("../flowerpot_plot.png", dpi=150)
plt.show()