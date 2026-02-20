import numpy as np
import pandas as pd

# Programa para calcular la funcion dielectrica utilizando el modelo de Adachi.
# Parametros para InN (basado en Djurišić et al.)

def dialectric_function(E):
    # Calculo para la contribucion de la funcion dielectrica de epsilon 0
    A_0 = 12.256
    E_0 = 1.247
    alpha_0 = 5.345

    Gamma_0 = 0.037
    Gamma_0_mod = Gamma_0 * np.exp(-alpha_0 * (((E - E_0) / Gamma_0)**2))
    Chi_0 = (E + Gamma_0_mod * 1j) / E_0

    e_0 = A_0 * (E_0**(-3/2)) * (Chi_0**(-2)) * (2 - ((1 + Chi_0)**(1/2)) - (1 - Chi_0)**(1/2))

    # Calculando la contribucion de la funcion dielectrica de epsilon 0X 
    m = 20
    e_0X = 0
    A_0X = 0.001
    G_0X = 0.024

    for i in range(m):
        # FIX: Using constant Gamma_0 instead of Gamma_0_mod to prevent division by zero
        e_0X = e_0X + (A_0X / (i+1)**3) * (1 / (E_0 - (G_0X / (i+1)**2) - E - Gamma_0 * 1j)) 

    # Calculando la contribucion de la funcion dielectrica de epsilon 1
    beta_1 = [0.361, 1.074, 0.007]
    Gamma_1 = [0.052, 0.012, 2.698]
    E_1 = [6.040, 8.23, 7.308]
    alpha_1 = [5.161, 0.574, 1.108]
    Gamma_1_mod = [0, 0, 0]

    e_1 = 0
    for j in range(3):
        Gamma_1_mod[j] = Gamma_1[j] * np.exp(-alpha_1[j] * (((E - E_1[j]) / Gamma_1[j])**2))
        shi_1 = (E + Gamma_1_mod[j] * 1j) / E_1[j] 
        e_1 = e_1 + (beta_1[j] * (shi_1**(-2)) * np.log(1 - shi_1**2))

    # Calculando la contribucion de la funcion dielectrica de epsilon 1X
    n = 20
    beta_1X = [1.243, 0.471, 5.528]
    G_1X = [1.198, 0.521, 4.801]

    e_1X = 0
    for l in range(3):
        for k in range(n):
            # FIX: Using constant Gamma_1[l] instead of Gamma_1_mod[l] to prevent division by zero
            e_1X = e_1X + (beta_1X[l] / ((2*(k+1) - 1)**3)) * (1 / (E_1[l] - (G_1X[l] / ((2*(k+1) - 1)**2)) - E - Gamma_1[l] * 1j))  

    e_inf = 1.314
    e_total = e_inf + e_0 + e_0X - e_1 + e_1X
    
    e12_1 = e_total.real
    e12_2 = e_total.imag

    n_index = np.sqrt((np.sqrt(e12_1**2 + e12_2**2) + e12_1) / 2)
    k_coef = np.sqrt((np.sqrt(e12_1**2 + e12_2**2) - e12_1) / 2)

    return n_index, k_coef

# Rango de energia
Energy = np.linspace(2, 10, 1000)

n_result, k_result = dialectric_function(Energy)

data_to_save = np.column_stack((Energy, n_result, k_result))

# Guardar a CSV
np.savetxt(
    "asdadasdadas.csv",   
    data_to_save,                
    delimiter=",",               
    header="omega,n,k",          
    comments="",                 
    fmt="%.6f"                   
)

print("Data successfully saved to optical_results_InN.csv")