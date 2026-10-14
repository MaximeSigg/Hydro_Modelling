'''
--------------------------------------------------------------------
                        GROUP EXERCISE 2
             Exercise 2b : Storage cascade
 Authors: Antonia Schibbe, Jordi Fornés Mengual, Maxime Siggen
-------------------------------------------------------------------
 Description: In this exercise we extend the flowerpot model to a
storage cascade: 2 linear storages connected in series. The outflow
of the first storage is the inflow of the second one. Each storage
has its own parameter k (k1, k2). Precipitation is 10 mm per time
step during the first 10 time steps, afterwards 0.
We compute the maximum discharge for all 9 combinations of
k1, k2 = 0.1, 0.4, 0.7.
-------------------------------------------------------------------
'''

# Required packages: numpy, matplotlib
import numpy as np
import matplotlib.pyplot as plt


# CASCADE MODEL: Parameters

n = 50                          # number of time steps
k_values = [0.1, 0.4, 0.7]      # discharge constants
p = np.zeros(n); p[:10] = 10    # precipitation [mm per step]


def run_cascade(k1, k2, p):
    """Simulate two linear storages in series.

    Storage 1: S1(t+1) = S1(t) + P(t)  - Q1(t),  Q1(t) = k1 * S1(t)
    Storage 2: S2(t+1) = S2(t) + Q1(t) - Q2(t),  Q2(t) = k2 * S2(t)
    Returns the storages S1, S2 and the discharges q1, q2.
    """
    n = len(p)
    S1 = np.zeros(n + 1)
    S2 = np.zeros(n + 1)
    q1 = np.zeros(n)
    q2 = np.zeros(n)

    for t in range(n):
        q1[t] = k1 * S1[t]
        S1[t + 1] = S1[t] + p[t] - q1[t]

        q2[t] = k2 * S2[t]
        S2[t + 1] = S2[t] + q1[t] - q2[t]    # input of storage 2 = outflow of storage 1

    return S1, S2, q1, q2


# Run all 9 combinations of k1 and k2
results = {}
max_q = np.zeros((len(k_values), len(k_values)))   # rows: k1, columns: k2

for i, k1 in enumerate(k_values):
    for j, k2 in enumerate(k_values):
        S1, S2, q1, q2 = run_cascade(k1, k2, p)
        results[(k1, k2)] = (S1, S2, q1, q2)
        max_q[i, j] = q2.max()


# Print table of maximum discharge
print("Maximum discharge Q2 [mm/step] of the cascade")
print("-" * 44)
print(f"{'k1 \\ k2':>8}" + "".join(f"{k2:>10.1f}" for k2 in k_values))
for i, k1 in enumerate(k_values):
    print(f"{k1:>8.1f}" + "".join(f"{max_q[i, j]:>10.3f}" for j in range(len(k_values))))

print()
for i, k1 in enumerate(k_values):
    for j, k2 in enumerate(k_values):
        t_max = int(np.argmax(results[(k1, k2)][3]))
        print(f"k1 = {k1}, k2 = {k2}:  Q_max = {max_q[i, j]:.3f} mm/step at time step {t_max}")


# Plot 1: detailed example (k1 = 0.1, k2 = 0.4)
k1_ex, k2_ex = 0.1, 0.4
S1, S2, q1, q2 = results[(k1_ex, k2_ex)]
t = np.arange(n)

fig, ax = plt.subplots(4, 1, figsize=(8, 10), sharex=True)

ax[0].bar(t, p, color="#7fb2ff")
ax[0].set_ylabel("P(t) [mm/step]")
ax[0].set_title(f"Storage cascade (k1 = {k1_ex}, k2 = {k2_ex})")

ax[1].plot(t, S1[:-1], color="#52A675", lw=2, label="S1(t)")
ax[1].plot(t, S2[:-1], color="#27632A", lw=2, label="S2(t)")
ax[1].set_ylabel("S(t) [mm]")
ax[1].legend()

ax[2].plot(t, q1, color="#4682B4", lw=2)
ax[2].set_ylabel("Q1(t) [mm/step]")

ax[3].plot(t, q2, color="#173F70", lw=2)
ax[3].set_ylabel("Q2(t) [mm/step]")
ax[3].set_xlabel("time step")

for a in ax:
    a.axvline(10, color="gray", ls="--", lw=1)
    a.grid(alpha=0.3)

plt.tight_layout()
plt.savefig("../cascade_example_plot.png", dpi=150)
plt.show()


# Plot 2: discharge of the cascade for all 9 combinations
fig, ax = plt.subplots(len(k_values), len(k_values), figsize=(10, 8),
                       sharex=True, sharey=True)

for i, k1 in enumerate(k_values):
    for j, k2 in enumerate(k_values):
        q2 = results[(k1, k2)][3]
        ax[i, j].plot(t, q2, color="#173F70", lw=2)
        ax[i, j].axvline(10, color="gray", ls="--", lw=1)
        ax[i, j].grid(alpha=0.3)
        ax[i, j].set_title(f"k1 = {k1}, k2 = {k2}", fontsize=9)

for a in ax[-1, :]:
    a.set_xlabel("time step")
for a in ax[:, 0]:
    a.set_ylabel("Q2(t) [mm/step]")

fig.suptitle("Discharge of the storage cascade for all combinations of k1 and k2")
plt.tight_layout()
plt.savefig("../cascade_all_combinations_plot.png", dpi=150)
plt.show()