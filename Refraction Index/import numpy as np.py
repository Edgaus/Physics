import numpy as np
import matplotlib.pyplot as plt

def get_dielectric_constants_smooth(E, material="GaN"):
    # --- Parámetros ajustados para evitar divergencias ---
    if material == "GaN":
        # GaN ya es estable, mantenemos los originales
        A_0, E_0, alpha_0, Gamma_0 = 41.251, 3.550, 1.241, 0.287
        A_0X, G_0X = 0.249, 0.030
        beta_1, E_1, Gamma_1, alpha_1 = [0.778, 0.103, 0.920], [6.010, 8.182, 8.761], [0.743, 0.428, 0.440], [0.240, 0.011, 0.005]
        beta_1X, G_1X = [2.042, 1.024, 1.997], [0.0003, 0.356, 1.962]
        e_inf = 0.426
        
    elif material == "AlN":
        A_0, E_0, alpha_0, Gamma_0 = 5.648, 6.222, 0.465, 0.439
        A_0X, G_0X = 0.600, 0.060
        # AJUSTE: Gamma_1[0] sube de 0.064 a 0.400 para evitar la explosión en 12eV
        beta_1, E_1, Gamma_1, alpha_1 = [0.236, 0.037, 0.230], [12.055, 8.841, 12.900], [0.400, 2.045, 0.411], [0.747, 0.687, 1.913]
        beta_1X, G_1X = [1.393, 1.655, 3.234], [2.880, 0.980, 5.507]
        e_inf = 1.230
        
    elif material == "InN":
        # AJUSTE: Gamma_0 sube de 0.037 a 0.200 para suavizar el gap fundamental
        A_0, E_0, alpha_0, Gamma_0 = 12.256, 2.247, 5.345, 0.200
        A_0X, G_0X = 0.001, 0.024
        # AJUSTE: Gamma_1[0] sube de 0.052 a 0.300
        beta_1, E_1, Gamma_1, alpha_1 = [0.361, 1.074, 0.007], [6.400, 8.230, 7.308], [0.300, 0.120, 2.698], [5.161, 0.574, 1.108]
        beta_1X, G_1X = [1.243, 0.471, 5.528], [1.198, 0.521, 4.801]
        e_inf = 1.314

    # --- Lógica del modelo ---
    G0_m = Gamma_0 * np.exp(-alpha_0 * ((E - E_0) / Gamma_0)**2)
    chi0 = (E + G0_m * 1j) / E_0
    e0 = A_0 * (E_0**-1.5) * (chi0**-2) * (2 - (1 + chi0)**0.5 - (1 - chi0)**0.5)

    e0X = 0
    for i in range(20):
        e0X += (A_0X / (i + 1)**3) * (1 / (E_0 - (G_0X / (i + 1)**2) - E - G0_m * 1j))

    e1, e1X = 0, 0
    for j in range(3):
        G1_m = Gamma_1[j] * np.exp(-alpha_1[j] * ((E - E_1[j]) / Gamma_1[j])**2)
        shi1 = (E + G1_m * 1j) / E_1[j]
        e1 += (beta_1[j] * (shi1**-2) * np.log(1 - shi1**2))
        for k in range(20):
            idx = 2 * (k + 1) - 1
            e1X += (beta_1X[j] / (idx**3)) * (1 / (E_1[j] - (G_1X[j] / (idx**2)) - E - G1_m * 1j))

    e_total = e_inf + e0 + e0X - e1 + e1X
    return e_total.real, e_total.imag

# --- Gráfica ---
Energy = np.linspace(1, 15, 1000)
plt.figure(figsize=(10, 6))

for mat, col in [("GaN", "blue"), ("AlN", "red"), ("InN", "green")]:
    eps1, eps2 = get_dielectric_constants_smooth(Energy, material=mat)
    plt.plot(Energy, eps2, label=f'$\\epsilon_2$ {mat} (Ajustado)', color=col, lw=2)

plt.title("Parte Imaginaria (Absorción) con Ensanchamiento Físico Sugerido")
plt.xlabel("Energía (eV)")
plt.ylabel("$\\epsilon_2$")
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()