from finite_well import FiniteWell
import matplotlib.pyplot as plt
import numpy as np  


data = np.genfromtxt("data/Pb_vs_L_curvas_ab.csv", delimiter=",", names=True)
plt.semilogy(data["L_A"], data["Pb_a_pct"], data["L_A"], data["Pb_b_pct"])

lp = np.linspace(10, 300, 10)  # Espesor del pozo (Å)
mass = [0.067,0.04]  # Masa efectiva (en unidades de m0)
Pb = []


for l in lp:
    estructura = {
        "V_meV": 224.0,  # altura de la barrera (meV)
        "mass_m0": 0.067,  # masa efectiva (en m0)
        "lp": l,  # espesor del pozo (Å)
    }
    # -----------------------------------------------------

    pozo = FiniteWell(estructura)
    estados = pozo.solve()
    Pb.append(estados[0].P_barrier)

plt.plot(lp, Pb, marker='o')
plt.yscale('log')
plt.title("Probabilidad de tunelamiento vs. espesor del pozo")
plt.xlabel("Espesor del pozo (Å)")
plt.ylabel("Probabilidad de tunelamiento (%)")
plt.show()        

