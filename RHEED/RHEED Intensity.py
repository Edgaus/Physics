# Codigo para simular intensidad:
import numpy as np
from matplotlib import pyplot as plt

plt.rcParams.update({
    "font.size": 16,
    "font.weight": "bold",
    "axes.labelweight": "bold",
    "axes.labelsize": 18,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "legend.fontsize": 14,
    "lines.linewidth": 2.5,
})

theta = np.linspace(0, 0.25, 101)
phis = [ (np.pi, r"$\phi=\pi$")]

fig, ax = plt.subplots(figsize=(5, 4), dpi=200)
for p, lab in phis:
    Ir = 1 - 2*theta*(1 - theta)*(1 - np.cos(p))
    ax.plot(theta, Ir, label=lab)



ax.set_xlabel(r"$\theta$")
ax.set_ylabel(r"$I_r$")
fig.tight_layout()
fig.savefig("Ir_phi.pdf")
plt.show()



