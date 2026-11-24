import numpy as np
from matplotlib import pyplot as plt



tiempo = np.linspace(0, 4, 100)
F_ml = 0.25
phis = [(np.pi*0.8, r"$\phi=\pi$")]

def theta_t(F, t):
    return F*t - np.floor(F*t)



fig, ax = plt.subplots(figsize=(8, 4.5), dpi=1600)
for p, lab in phis:
    th = theta_t(F_ml, tiempo)
    Ir = 1 - 2*th*(1 - th)*(1 - np.cos(p))
    ax.plot(tiempo, Ir)

# Eje Y sin números ni marcas
ax.set_yticks([])

# Eje X sin números ni marcas
ax.set_xticks([])


ax.set_xlim(-1,4.1)
ax.set_ylim(-0.1, 1.1)
plt.show()