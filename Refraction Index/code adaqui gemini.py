import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import dual_annealing


# Programa para poder calcular la funcion dialectrica utilizando el modelo de Adaqui. Prueba 1 para el GaN


#Adaqui function to stablish the data 

def dialectric_function(E, A_0, E_0, alpha_0,   ):

    # Parametros

    # Calculo para la contribucion de la funcion dialectrica de epsilon 0
    A_0 = 41.251
    E_0 = 3.550
    alpha_0 = 1.241

    Gamma_0 = 0.287
    Gamma_0_mod = Gamma_0*np.exp(  -alpha_0*( (  (E-E_0)/Gamma_0     )**2  )  )
    Chi_0 = (E + Gamma_0_mod*1j)/E_0

    e_0 =  A_0* (E_0**(-3/2)) * (Chi_0**(-2))*(  2- ((1+Chi_0)**(1/2)) - (1-Chi_0)**(1/2)       )

    # Calculando la contribucion de la funcion dialectrica de epsilon 0X

    m = 20
    e_0X = 0
    A_0X = 0.249
    G_0X = 0.030

    for i in range(m):
        e_0X = e_0X   + (A_0X /(i+1)**3)    *      (1   /   (  E_0 - (G_0X/(i+1)**2) - E -  Gamma_0_mod*1j     )    ) 


    # Calculando la contribucion de la funcion dialectrica de epsilon 1

    beta_1 = [0.778, 0.103, 0.920  ]
    Gamma_1 = [ 0.743  , 0.428, 0.440  ]
    E_1 = [ 6.010, 8.182, 8.761]
    alpha_1 = [ 0.240, 0.011, 0.005 ]
    Gamma_1_mod = [0,0,0]

    e_1 = 0
    for j in range(3):
        Gamma_1_mod[j] = Gamma_1[j]* np.exp(  -alpha_1[j]*( (  (E-E_1[j])/Gamma_1[j]     )**2  )  )

        shi_1 = ( E + Gamma_1_mod[j]*1j )/E_1[j] 
        e_1 = e_1 +  ( beta_1[j] *(shi_1**(-2)) * np.log(1-shi_1**2)  )

    # Calculando la contribucion de la funcion dialectrica de epsilon 1X
        
    n = 20

    beta_1X = [2.042, 1.024, 1.997]
    G_1X = [ 0.0003, 0.356, 1.962 ]

    e_1X = 0
    for l in range(3):

        for k in range(n):
            e_1X = e_1X + (beta_1X[l] /(  (2*(k+1)-1)**3   )  ) * ( 1/   (   E_1[l] - (  G_1X[l] /( ( 2*((k+1))-1 )**2  )  ) -  E - Gamma_1_mod[l]*1j  ) )  




    e_inf = 0.426
    e_total = e_inf + e_0 + e_0X - e_1 + e_1X
    
    e12_1 = e_total.real
    e12_2 = e_total.imag

    return e12_1, e12_2

Energy = np.linspace (1,7,1000 )

n_result, k_result =  dialectric_function( Energy  )


data_to_save = np.column_stack((Energy, n_result, k_result))

# 2. Save to a CSV file
np.savetxt(
    "optical_results.csv",       # The name of the file you want to create
    data_to_save,                # The stacked data
    delimiter=",",               # This separates the values with a comma
    header="omega,n,k",          # Adds a title row at the top of the file
    comments="",                 # Prevents NumPy from adding a '#' before the header
    fmt="%.6f"                   # Optional: Formats the numbers to 6 decimal places for readability
)

print("Data successfully saved to optical_results.csv")


